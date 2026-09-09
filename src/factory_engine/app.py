"""Application setup and render loop."""

from pathlib import Path

import wgpu
from rendercanvas.glfw import RenderCanvas, loop
import time

import struct

SHADER_PATH = Path(__file__).parent / "shaders" / "mesh.wgsl"

from .camera import Camera
from .math3d import Vec3, Mat4
from .mesh import Mesh
from .input_handler import InputHandler

class GameApp:
    """Owns the window and the small amount of GPU state needed to draw."""

    def __init__(self) -> None:        
        self.canvas = RenderCanvas(size=(1280, 720), title="Factory Game", update_mode="continuous", max_fps=60)
        self.camera = Camera()
        self.input = InputHandler()
        self.last_frame_time = time.perf_counter()

        self.camera_speed = 5.0 # Movement speed
        self.sensitivity = 0.15
        self.cube_angle = 0

        self.canvas.add_event_handler(
            self.input.handle_event,
            "key_down",
            "key_up",
            "pointer_down",
            "pointer_up",
            "pointer_move"
        )
        
        adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        self.device = adapter.request_device_sync()
        
        # Create the Cube
        self.cube = Mesh.create_cube(self.device)

        self.context = self.canvas.get_wgpu_context()
        self.texture_format = self.context.get_preferred_format(self.device.adapter)
        self.context.configure(device=self.device, format=self.texture_format)

        width, height = self.canvas.get_physical_size()

        self.depth_size = (0, 0)

        if width > 0 and height > 0:
            self.create_depth_texture(width, height)
        
        self.camera_buffer = self.device.create_buffer(
            size = 64,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
        )

        self.model_buffer = self.device.create_buffer(
            size=64,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
        )

        self.light_buffer = self.device.create_buffer(
            size=16,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST
        )

        # Upload light data
        light_direction = Vec3(-1.0, 2.0, -1.0).normalize()
        self.device.queue.write_buffer(
            self.light_buffer,
            0,
            struct.pack(
                "4f",
                light_direction.x,
                light_direction.y,
                light_direction.z,
                0.0,
            )
        )
        
        vertex_buffers = [
            {
                "array_stride": 24,
                "step_mode": "vertex",
                "attributes": [
                    {
                        "format": "float32x3",
                        "offset": 0,
                        "shader_location": 0
                    },
                    {
                        "format": "float32x3",
                        "offset": 12,
                        "shader_location": 1
                    }
                ]
            }
        ]

        shader = self.device.create_shader_module(code=SHADER_PATH.read_text())

        self.bind_group_layout = self.device.create_bind_group_layout(
            entries=[
                {
                    "binding": 0,
                    "visibility": wgpu.ShaderStage.VERTEX,
                    "buffer": {
                        "type": wgpu.BufferBindingType.uniform
                    }
                },
                {
                    "binding": 1,
                    "visibility": wgpu.ShaderStage.VERTEX,
                    "buffer": {
                        "type": wgpu.BufferBindingType.uniform
                    }
                },
                {
                    "binding": 2,
                    "visibility": wgpu.ShaderStage.FRAGMENT,
                    "buffer": {
                        "type": wgpu.BufferBindingType.uniform
                    }
                }
            ]
        )

        pipeline_layout = self.device.create_pipeline_layout(
            bind_group_layouts=[
                self.bind_group_layout
            ]
        )
        
        self.pipeline = self.device.create_render_pipeline(
            layout=pipeline_layout,
            vertex={
                "module": shader,
                "entry_point": "vs_main",
                "buffers": vertex_buffers
            },
            fragment={
                "module": shader,
                "entry_point": "fs_main",
                "targets": [{"format": self.texture_format}],
            },

            primitive={
                "topology": "triangle-list"
            },

            depth_stencil={
                "format": "depth24plus",
                "depth_write_enabled": True,
                "depth_compare": "less"
            }
        )

        self.bind_group = self.device.create_bind_group(
            layout=self.bind_group_layout,
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": self.camera_buffer
                    }
                },
                {
                    "binding": 1,
                    "resource": {
                        "buffer": self.model_buffer
                    }
                },
                {
                    "binding": 2,
                    "resource": {
                        "buffer": self.light_buffer
                    }
                }
            ]
        )

    def update_camera_movement(self, delta_time):
        mouse_dx, mouse_dy = self.input.consume_mouse_delta()
        self.camera.look(mouse_dx, mouse_dy, self.sensitivity)
        
        forward = (self.camera.target - self.camera.position).normalize()
        right = forward.cross(self.camera.up).normalize()

        movement = Vec3()

        if self.input.is_down("w"):
            movement += forward
        if self.input.is_down("s"):
            movement -= forward
        if self.input.is_down("d"):
            movement += right
        if self.input.is_down("a"):
            movement -= right
        if self.input.is_down(" "):
            movement += self.camera.up
        if self.input.is_down("shift"):
            movement -= self.camera.up

        if movement.length() > 0:
            offset = movement.normalize() * self.camera_speed * delta_time
            self.camera.position += offset
            self.camera.target += offset

    def update_camera(self) -> None:
        """Calculate and upload the camera view-projection matrix."""
        width, height = self.canvas.get_logical_size()

        if height == 0:
            return
        
        aspect_ratio = width / height

        view_projection = (
            self.camera.projection_matrix(aspect_ratio) @ self.camera.view_matrix()
        )

        model_matrix = view_projection.to_column_major_floats()

        data = struct.pack(
            "16f",
            *model_matrix
        )

        self.device.queue.write_buffer(
            self.camera_buffer,
            0,
            data
        )
        

    def draw_frame(self) -> None:
        # Calculate delta time
        current_time = time.perf_counter()
        delta_time = min(current_time - self.last_frame_time, 0.05)
        self.last_frame_time = current_time

        # update camera and movement
        self.update_camera_movement(delta_time)
        self.update_camera()
        
        # Generate Depth Texture        
        width, height = self.canvas.get_physical_size()

        if width == 0 or height == 0:
            return

        if (width, height) != self.depth_size:
            self.create_depth_texture(width, height)

        """ Draw one Frame """
        # Update model matrix
        #rotation_speed = 1.0
        #self.cube_angle += rotation_speed * delta_time
        #model_matrix = Mat4.rotation_z(self.cube_angle) @ Mat4.rotation_y(self.cube_angle * 2) @ Mat4.rotation_x(self.cube_angle * 4)
        model_matrix = Mat4.identity()

        self.device.queue.write_buffer(
            self.model_buffer,
            0,
            struct.pack(
                "16f",
                *model_matrix.to_column_major_floats()
            )
        )
        
        encoder = self.device.create_command_encoder()
        texture_view = self.context.get_current_texture().create_view()
        render_pass = encoder.begin_render_pass(
            color_attachments=[
                {
                    "view": texture_view,
                    "clear_value": (0.02, 0.02, 0.02, 1.0),
                    "load_op": wgpu.LoadOp.clear,
                    "store_op": wgpu.StoreOp.store,
                }
            ],
            depth_stencil_attachment={
                "view": self.depth_view,
                "depth_clear_value": 1.0,
                "depth_load_op": wgpu.LoadOp.clear,
                "depth_store_op": wgpu.StoreOp.store
            }
        )
        render_pass.set_pipeline(self.pipeline)
        render_pass.set_bind_group(
            0,
            self.bind_group
        )
        render_pass.set_vertex_buffer(0, self.cube.vertex_buffer)
        render_pass.set_index_buffer(self.cube.index_buffer, "uint16")
        render_pass.draw_indexed(self.cube.index_count)
        render_pass.end()

        self.device.queue.submit([encoder.finish()])

    def run(self) -> None:
        """Start the window event loop."""
        self.canvas.request_draw(self.draw_frame)
        loop.run()



    ###########
    # HELPERS #
    ###########


    def create_depth_texture(self, width, height):
        self.depth_texture = self.device.create_texture(
            size=(width, height, 1),
            format="depth24plus",
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT
        )

        self.depth_view = self.depth_texture.create_view()
        self.depth_size = (width, height)

def main() -> None:
    """Create and run the game application."""
    GameApp().run()
