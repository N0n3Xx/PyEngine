"""Application setup and render loop."""

import wgpu
from rendercanvas.glfw import RenderCanvas, loop
import time

from pathlib import Path

import struct

from .ecs.components.c_material import MaterialComponent
from .ecs.components.c_mesh import MeshRenderer
from .ecs.components.c_transform import TransformComponent
from .ecs.world import World

from factory_engine.rendering.camera import Camera
from .math3d import Vec3, Mat4
from .input_handler import InputHandler
from factory_engine.rendering.mesh import Mesh
from .rendering.render_batch import RenderBatch
from .rendering.render_instance import RenderInstance


class GameApp:
	"""Owns the window and the small amount of GPU state needed to draw."""

	def __init__(self) -> None:
		self.canvas = RenderCanvas(
			size=(1280, 720),
			title="Factory Game",
			vsync=False,
			update_mode="fastest"  # Fastest or continuous
		)
		self.world = World()
		self.camera = Camera()
		self.input = InputHandler()
		self.pipeline_cache = {}

		# 60Hz update frequency
		self.FIXED_DT = 1.0 / 60.0
		self.MAX_UPDATES_PER_FRAME = 5
		self.accumulator = 0.0
		self.simulation_time = 0.0
		self.tps = 0.0
		self.tps_timer = 0.0
		self.tps_update_count = 0

		self.last_frame_time = time.perf_counter()
		self.fps = 0.0
		self.fps_timer = 0.0
		self.fps_frame_count = 0

		self.draw_calls = 0
		self.rendered_instances = 0

		self.interpolation_alpha = 0.0

		# TODO: Proper input mapping system and movement abstraction
		self.camera_speed = 5.0  # Movement speed
		self.sensitivity = 0.15

		# TODO: auslagern
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

		self.context = self.canvas.get_wgpu_context()
		self.texture_format = self.context.get_preferred_format(self.device.adapter)
		self.context.configure(device=self.device, format=self.texture_format)

		width, height = self.canvas.get_physical_size()

		self.depth_size = (0, 0)

		if width > 0 and height > 0:
			self.create_depth_texture(width, height)

		self.camera_buffer = self.device.create_buffer(
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
					"binding": 2,
					"visibility": wgpu.ShaderStage.FRAGMENT,
					"buffer": {
						"type": wgpu.BufferBindingType.uniform
					}
				}
			]
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
					"binding": 2,
					"resource": {
						"buffer": self.light_buffer
					}
				}
			]
		)

		# ADD GAMEOBJECTS HERE
		cube_mesh = Mesh.create_cube(self.device)

		self.cube = self.world.create_entity("Cube")
		self.cube.add(TransformComponent(position=Vec3(0.0, 0.0, 0.0)))
		self.cube.add(MaterialComponent(shader=Path(__file__).parent / "shaders" / "mesh.wgsl"))
		self.cube.add(MeshRenderer(cube_mesh))

		cube2 = self.world.create_entity("Cube2")
		cube2.add(TransformComponent(position=Vec3(1.0, 1.0, 0.0)))
		cube2.add(MaterialComponent(shader=Path(__file__).parent / "shaders" / "mesh.wgsl"))
		cube2.add(MeshRenderer(cube_mesh))

		self.cube1angle = 0

	def update(self) -> None:
		"""Update game state EVERY FRAME"""
		# Calculate delta time
		current_time = time.perf_counter()

		frame_time = current_time - self.last_frame_time
		self.last_frame_time = current_time

		self.accumulator += frame_time

		updates = 0

		while self.accumulator >= self.FIXED_DT and updates < self.MAX_UPDATES_PER_FRAME:
			self.save_previous_state()

			self.fixed_update(self.FIXED_DT)

			self.tps_update_count += 1
			self.accumulator -= self.FIXED_DT
			updates += 1

		self.interpolation_alpha = self.accumulator / self.FIXED_DT

		# update camera and movement
		self.update_camera_movement(frame_time)
		self.update_camera()

		# TPS, FPS and Batch stats printing
		self.fps_timer += frame_time
		self.fps_frame_count += 1

		self.tps_timer += frame_time

		if self.fps_timer >= 1.0:
			self.fps = self.fps_frame_count / self.fps_timer
			self.tps = self.tps_update_count / self.tps_timer

			print(
				f"FPS: {self.fps:.1f} | "
				f"TPS: {self.tps:.1f} | "
				f"Draw Calls: {self.draw_calls} | "
				f"Instances: {self.rendered_instances}"
			)

			self.fps_timer = 0.0
			self.fps_frame_count = 0

			self.tps_timer = 0.0
			self.tps_update_count = 0

	def fixed_update(self, delta_time: float) -> None:
		"""Update at CONFIGURED FREQUENCY (Default: 60Hz)"""
		self.cube1angle += 0.3 * delta_time
		self.cube.get(TransformComponent).set_rotation(Vec3(0.0, self.cube1angle, 0.0))

		self.simulation_time += delta_time

	def render(self) -> None:
		self.draw_calls = 0
		self.rendered_instances = 0

		# Generate Depth Texture
		width, height = self.canvas.get_physical_size()

		if width == 0 or height == 0:
			return

		if (width, height) != self.depth_size:
			self.create_depth_texture(width, height)

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
		render_pass.set_bind_group(
			0,
			self.bind_group
		)

		self.render_world(render_pass)

		render_pass.end()

		self.device.queue.submit([encoder.finish()])

	def render_world(self, render_pass):
		batches = self.build_render_batches()

		for batch in batches.values():
			pipeline = self.get_pipeline(batch.material.shader)

			render_pass.set_pipeline(pipeline)

			self.upload_instance_buffer(batch)

			gpu_mesh = batch.mesh

			render_pass.set_vertex_buffer(
				0,
				gpu_mesh.vertex_buffer
			)

			render_pass.set_vertex_buffer(
				1,
				batch.instance_buffer
			)

			render_pass.set_index_buffer(
				gpu_mesh.index_buffer,
				"uint16"
			)

			render_pass.draw_indexed(
				gpu_mesh.index_count,
				len(batch.instances)
			)

			self.draw_calls += 1
			self.rendered_instances += len(batch.instances)

	def draw_frame(self) -> None:
		self.update()
		self.render()

	def run(self) -> None:
		"""Start the window event loop."""
		self.canvas.request_draw(self.draw_frame)
		loop.run()

	###########
	# HELPERS #
	###########

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
		width, height = self.canvas.get_logical_size()

		if height == 0:
			return

		aspect_ratio = width / height

		view_projection = (
				self.camera.projection_matrix(aspect_ratio) @ self.camera.view_matrix()
		)

		view_projection_matrix = view_projection.to_column_major_floats()

		data = struct.pack(
			"16f",
			*view_projection_matrix
		)

		self.device.queue.write_buffer(
			self.camera_buffer,
			0,
			data
		)

	def build_render_batches(self):
		batches = {}

		for entity, transform, mesh_renderer, material in self.world.query(
				TransformComponent,
				MeshRenderer,
				MaterialComponent,
		):
			mesh = mesh_renderer.mesh
			key = (mesh, material.shader)

			if key not in batches:
				batches[key] = RenderBatch(
					mesh,
					material
				)

			render_position = Vec3(

				transform.previous_position.x
				+ (transform.position.x - transform.previous_position.x)
				* self.interpolation_alpha,
				transform.previous_position.y
				+ (transform.position.y - transform.previous_position.y)
				* self.interpolation_alpha,
				transform.previous_position.z
				+ (transform.position.z - transform.previous_position.z)
				* self.interpolation_alpha,
			)
			render_rotation = Vec3(
				transform.previous_rotation.x
				+ (transform.rotation.x - transform.previous_rotation.x)
				* self.interpolation_alpha,
				transform.previous_rotation.y
				+ (transform.rotation.y - transform.previous_rotation.y)
				* self.interpolation_alpha,
				transform.previous_rotation.z
				+ (transform.rotation.z - transform.previous_rotation.z)
				* self.interpolation_alpha,
			)
			render_scale = Vec3(
				transform.previous_scale.x
				+ (transform.scale.x - transform.previous_scale.x)
				* self.interpolation_alpha,
				transform.previous_scale.y
				+ (transform.scale.y - transform.previous_scale.y)
				* self.interpolation_alpha,
				transform.previous_scale.z
				+ (transform.scale.z - transform.previous_scale.z)
				* self.interpolation_alpha,
			)

			model_matrix = (

					Mat4.translation(render_position)
					@ Mat4.rotation_y(render_rotation.y)
					@ Mat4.rotation_x(render_rotation.x)
					@ Mat4.rotation_z(render_rotation.z)
					@ Mat4.scale(render_scale)
			)
			batches[key].instances.append(
				RenderInstance(model_matrix)
			)
		return batches

	def save_previous_state(self):
		for entity, transform in self.world.query(TransformComponent):
			transform.save_previous_state()

	def create_pipeline(self, shader_path):
		shader = self.device.create_shader_module(
			code=shader_path.read_text()
		)

		pipeline_layout = self.device.create_pipeline_layout(
			bind_group_layouts=[
				self.bind_group_layout
			]
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
			},
			{
				"array_stride": 64,
				"step_mode": "instance",
				"attributes": [
					{
						"format": "float32x4",
						"offset": 0,
						"shader_location": 2
					},
					{
						"format": "float32x4",
						"offset": 16,
						"shader_location": 3
					},
					{
						"format": "float32x4",
						"offset": 32,
						"shader_location": 4
					},
					{
						"format": "float32x4",
						"offset": 48,
						"shader_location": 5
					}
				]
			}
		]

		pipeline = self.device.create_render_pipeline(
			layout=pipeline_layout,
			vertex={
				"module": shader,
				"entry_point": "vs_main",
				"buffers": vertex_buffers
			},
			fragment={
				"module": shader,
				"entry_point": "fs_main",
				"targets": [
					{
						"format": self.texture_format
					}
				],
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

		return pipeline

	def get_pipeline(self, shader_path):
		if shader_path not in self.pipeline_cache:
			self.pipeline_cache[shader_path] = self.create_pipeline(shader_path)

		return self.pipeline_cache[shader_path]

	def upload_instance_buffer(self, batch):
		data = b""

		for instance in batch.instances:
			data += struct.pack(
				"16f",
				*instance.model_matrix.to_column_major_floats()
			)

		if batch.instance_buffer is not None:
			batch.instance_buffer.destroy()

		batch.instance_buffer = self.device.create_buffer(
			size=len(data),
			usage=wgpu.BufferUsage.VERTEX | wgpu.BufferUsage.COPY_DST
		)

		self.device.queue.write_buffer(
			batch.instance_buffer,
			0,
			data
		)

	def create_depth_texture(self, width, height):
		self.depth_texture = self.device.create_texture(
			size=(width, height, 1),
			format="depth24plus",
			usage=wgpu.TextureUsage.RENDER_ATTACHMENT
		)

		self.depth_view = self.depth_texture.create_view()
		self.depth_size = (width, height)


def main() -> None:
	GameApp().run()
