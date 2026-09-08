"""Application setup and render loop."""

from pathlib import Path

import wgpu
from rendercanvas.glfw import RenderCanvas, loop

import struct

SHADER_PATH = Path(__file__).parent / "shaders" / "mesh.wgsl"

from .camera import Camera
from .math3d import Vec3, Mat4
from .mesh import Mesh

class GameApp:
    """Owns the window and the small amount of GPU state needed to draw."""

    def __init__(self) -> None:
        self.canvas = RenderCanvas(size=(1280, 720), title="Factory Game")

        self.camera = Camera()
        
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
        
        vertex_buffers = [
            {
                "array_stride": 12,
                "step_mode": "vertex",
                "attributes": [
                    {
                        "format": "float32x3",
                        "offset": 0,
                        "shader_location": 0
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
                }
            ]
        )

    def update_camera(self) -> None:
        """Calculate and upload the camera view-projection matrix."""
        width, height = self.canvas.get_logical_size()

        if height == 0:
            return
        
        aspect_ratio = width / height

        view_projection = (
            self.camera.projection_matrix(aspect_ratio) @ self.camera.view_matrix()
        )

        matrix = view_projection.to_column_major_floats()

        data = struct.pack(
            "16f",
            *matrix
        )

        self.device.queue.write_buffer(
            self.camera_buffer,
            0,
            data
        )
        

    def draw_frame(self) -> None:
        # Generate Depth Texture        
        width, height = self.canvas.get_physical_size()

        if width == 0 or height == 0:
            return

        if (width, height) != self.depth_size:
            self.create_depth_texture(width, height)

        """ Draw one Frame """        
        self.update_camera()       
        
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
