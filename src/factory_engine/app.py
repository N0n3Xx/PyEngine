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
from factory_engine.rendering.skybox import Skybox
from .rendering.render_batch import RenderBatch
from .rendering.render_instance import RenderInstance
from .settings import WINDOW_HEIGHT, WINDOW_WIDTH, FIXED_UPDATE_RATE, MAX_SIM_UPDATES_PER_FRAME
from .terrain.terrain import Terrain


class GameApp:
	"""Owns the window and the small amount of GPU state needed to draw."""

	def __init__(self) -> None:
		self.canvas = RenderCanvas(
			size=(WINDOW_WIDTH, WINDOW_HEIGHT),
			title="Factory Game",
			vsync=False,
			update_mode="fastest"  # Fastest or continuous
		)
		self.world = World()
		self.camera = Camera()
		self.input = InputHandler()
		self.pipeline_cache = {}

		self.render_batches = {}
		self.entity_render_batches = {}
		self.render_batches_built = False

		# 60Hz update frequency
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
		self.batch_count = 0
		self.rendered_instances = 0
		self.rendered_triangles = 0

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

		self.skybox = Skybox(
			self.device,
			Path(__file__).parents[2] / "assets" / "skybox" / "sample_skybox"
		)
		self.skybox_vertex_buffer = Skybox.create_skybox_mesh(self.device)

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

		self.skybox_buffer = self.device.create_buffer(
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

		self.skybox_bind_group_layout = self.device.create_bind_group_layout(
			entries=[
				{
					"binding": 0,
					"visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
					"buffer": {
						"type": wgpu.BufferBindingType.uniform
					}
				},
				{
					"binding": 1,
					"visibility": wgpu.ShaderStage.FRAGMENT,
					"sampler": {
						"type": wgpu.SamplerBindingType.filtering
					}
				},
				{
					"binding": 2,
					"visibility": wgpu.ShaderStage.FRAGMENT,
					"texture": {
						"sample_type": wgpu.TextureSampleType.float,
						"view_dimension": wgpu.TextureViewDimension.cube
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

		self.skybox_bind_group = self.device.create_bind_group(
			layout=self.skybox_bind_group_layout,
			entries=[
				{
					"binding": 0,
					"resource": {
						"buffer": self.skybox_buffer
					}
				},
				{
					"binding": 1,
					"resource": self.skybox.sampler
				},
				{
					"binding": 2,
					"resource": self.skybox.view
				}
			]
		)

		# Create skybox
		self.skybox_pipeline = self.create_skybox_pipeline()

		# ADD GAMEOBJECTS HERE
		self.terrain = Terrain(
			seed=1234,
			device=self.device,
			world=self.world
		)

		print(self.world.entities)

	def update(self) -> None:
		"""Update game state EVERY FRAME"""
		# Calculate delta time
		current_time = time.perf_counter()

		frame_time = current_time - self.last_frame_time
		self.last_frame_time = current_time

		self.accumulator += frame_time

		updates = 0

		while self.accumulator >= FIXED_UPDATE_RATE and updates < MAX_SIM_UPDATES_PER_FRAME:
			self.fixed_update(FIXED_UPDATE_RATE)

			self.tps_update_count += 1
			self.accumulator -= FIXED_UPDATE_RATE
			updates += 1

		# update camera and movement
		self.update_camera_movement(frame_time)
		self.update_camera()

		# Statistic Printing
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
				f"Batches: {self.batch_count} | "
				f"Instances: {self.rendered_instances} | "
				f"Triangles: {self.rendered_triangles}"
			)

			self.fps_timer = 0.0
			self.fps_frame_count = 0

			self.tps_timer = 0.0
			self.tps_update_count = 0

	def fixed_update(self, delta_time: float) -> None:
		"""Update at CONFIGURED FREQUENCY (Default: 60Hz)"""

		self.simulation_time += delta_time

	def render(self) -> None:
		self.draw_calls = 0
		self.batch_count = 0
		self.rendered_instances = 0
		self.rendered_triangles = 0

		# Generate Depth Texture
		width, height = self.canvas.get_physical_size()

		if width == 0 or height == 0:
			return

		if (width, height) != self.depth_size:
			self.create_depth_texture(width, height)

		self.build_render_batches()

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
		self.render_skybox(render_pass)

		render_pass.end()

		self.device.queue.submit([encoder.finish()])

	def render_world(self, render_pass):
		batches = self.render_batches

		self.batch_count = len(batches)

		# Make sure all batch GPU buffers exist before
		# processing individual dirty instances.
		for batch in batches.values():
			if batch.dirty:
				self.upload_instance_buffer(batch)
				batch.dirty = False

				for entity in batch.entity_instances:
					entity.clear_dirty()

		self.update_dirty_entities()

		for batch in batches.values():
			pipeline = self.get_pipeline(batch.material.shader)

			render_pass.set_pipeline(pipeline)

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

			instance_count = len(batch.instances)

			render_pass.draw_indexed(
				gpu_mesh.index_count,
				instance_count
			)

			self.draw_calls += 1
			self.rendered_instances += instance_count
			self.rendered_triangles += (gpu_mesh.index_count // 3) * instance_count

	def render_skybox(self, render_pass):
		render_pass.set_pipeline(self.skybox_pipeline)

		render_pass.set_bind_group(
			0,
			self.skybox_bind_group
		)

		render_pass.set_vertex_buffer(
			0,
			self.skybox_vertex_buffer
		)

		render_pass.draw(
			36,
			1
		)

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

		skybox_view = self.camera.view_matrix()
		skybox_view.values[0][3] = 0.0
		skybox_view.values[1][3] = 0.0
		skybox_view.values[2][3] = 0.0

		skybox_view_projection = (
				self.camera.projection_matrix(aspect_ratio)
				@ skybox_view
		)

		skybox_data = struct.pack(
			"16f",
			*skybox_view_projection.to_column_major_floats()
		)

		self.device.queue.write_buffer(
			self.skybox_buffer,
			0,
			skybox_data
		)

	def build_render_batches(self):
		if self.render_batches_built:
			return self.render_batches

		for entity, transform, mesh_renderer, material in self.world.query(
				TransformComponent,
				MeshRenderer,
				MaterialComponent,
		):
			# if not self.is_entity_visible(transform):
			#	continue
			key = (mesh_renderer.mesh, material.shader)

			batch = self.render_batches.get(key)

			if batch is None:
				batch = RenderBatch(
					mesh_renderer.mesh,
					material
				)

				self.render_batches[key] = batch

			instance = RenderInstance(self.create_model_matrix(transform), len(batch.instances))
			batch.instances.append(instance)
			batch.entity_instances[entity] = instance
			self.entity_render_batches[entity] = batch

		self.render_batches_built = True

		return self.render_batches

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
				"topology": "triangle-list",
				"cull_mode": "back"
			},
			depth_stencil={
				"format": "depth24plus",
				"depth_write_enabled": True,
				"depth_compare": "less"
			}
		)

		return pipeline

	def create_skybox_pipeline(self):
		shader_path = Path(__file__).parent / "shaders" / "skybox.wgsl"

		shader = self.device.create_shader_module(
			code=shader_path.read_text()
		)

		pipeline_layout = self.device.create_pipeline_layout(
			bind_group_layouts=[
				self.skybox_bind_group_layout
			]
		)

		return self.device.create_render_pipeline(
			layout=pipeline_layout,
			vertex={
				"module": shader,
				"entry_point": "vs_main",
				"buffers": [
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
			},
			fragment={
				"module": shader,
				"entry_point": "fs_main",
				"targets": [
					{
						"format": self.texture_format
					}
				]
			},
			primitive={
				"topology": "triangle-list",
				"cull_mode": "front"
			},
			depth_stencil={
				"format": "depth24plus",
				"depth_write_enabled": False,
				"depth_compare": "less-equal"
			}
		)

	def get_pipeline(self, shader_path):
		if shader_path not in self.pipeline_cache:
			self.pipeline_cache[shader_path] = self.create_pipeline(shader_path)

		return self.pipeline_cache[shader_path]

	def create_model_matrix(self, transform):
		return (
				Mat4.translation(transform.position)
				@ Mat4.rotation_y(transform.rotation.y)
				@ Mat4.rotation_x(transform.rotation.x)
				@ Mat4.rotation_z(transform.rotation.z)
				@ Mat4.scale(transform.scale)
		)

	def upload_instance_buffer(self, batch):
		instance_count = len(batch.instances)

		if instance_count == 0:
			return

		data = b"".join(
			struct.pack(
				"16f",
				*instance.model_matrix.to_column_major_floats()
			)
			for instance in batch.instances
		)

		required_size = instance_count * 64

		if batch.instance_buffer is None or required_size > batch.instance_capacity:
			if batch.instance_buffer is not None:
				batch.instance_buffer.destroy()

			batch.instance_capacity = max(
				64,
				2 ** (required_size - 1).bit_length()
			)

			batch.instance_buffer = self.device.create_buffer(
				size=batch.instance_capacity,
				usage=wgpu.BufferUsage.VERTEX | wgpu.BufferUsage.COPY_DST
			)

		self.device.queue.write_buffer(
			batch.instance_buffer,
			0,
			data
		)

	def upload_instance(self, batch, instance):
		data = struct.pack(
			"16f",
			*instance.model_matrix.to_column_major_floats()
		)

		self.device.queue.write_buffer(
			batch.instance_buffer,
			instance.index * 64,
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

	def update_dirty_entities(self):
		dirty_batches = {}

		for entity in self.world.entities.values():
			if not entity.is_dirty():
				continue

			transform = entity.get(TransformComponent)

			if transform is None or not transform.dirty:
				entity.clear_dirty()
				continue

			batch = self.entity_render_batches.get(entity)

			if batch is None:
				entity.clear_dirty()
				continue

			instance = batch.entity_instances[entity]

			instance.model_matrix = self.create_model_matrix(
				transform
			)

			if batch not in dirty_batches:
				dirty_batches[batch] = []

			dirty_batches[batch].append(instance)

			entity.clear_dirty()

		for batch, dirty_instances in dirty_batches.items():
			dirty_count = len(dirty_instances)
			instance_count = len(batch.instances)

			dirty_ratio = dirty_count / instance_count

			if dirty_ratio >= self.DIRTY_BATCH_THRESHOLD:
				self.upload_instance_buffer(batch)
			else:
				for instance in dirty_instances:
					self.upload_instance(
						batch,
						instance
					)

	# TODO: this is distance culling and not frustum culling
	def is_entity_visible(self, transform):
		position = transform.position

		camera_to_object = position - self.camera.position

		return camera_to_object.length() < self.camera.far


def main() -> None:
	GameApp().run()
