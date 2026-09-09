# skybox.py
import struct
from pathlib import Path

from PIL import Image
import wgpu


class Skybox:
	def __init__(self, device, path: Path):
		self.device = device

		faces = self.load_faces(path)

		width, height = faces[0].size

		if width != height:
			raise ValueError(
				f"Skybox faces must be square, got {width}x{height}"
			)

		for face in faces:
			if face.size != (width, height):
				raise ValueError(
					"All skybox faces must have the same dimensions"
				)

		self.texture = device.create_texture(
			size=(width, height, 6),
			mip_level_count=1,
			sample_count=1,
			dimension=wgpu.TextureDimension.d2,
			format="rgba8unorm",
			usage=(
					wgpu.TextureUsage.TEXTURE_BINDING |
					wgpu.TextureUsage.COPY_DST
			),
		)

		for layer, image in enumerate(faces):
			data = image.tobytes()

			device.queue.write_texture(
				{
					"texture": self.texture,
					"origin": (0, 0, layer),
				},
				data,
				{
					"bytes_per_row": width * 4,
					"rows_per_image": height,
				},
				(width, height, 1),
			)

		self.view = self.texture.create_view(
			dimension=wgpu.TextureViewDimension.cube,
			base_array_layer=0,
			array_layer_count=6,
		)

		self.sampler = device.create_sampler(
			address_mode_u=wgpu.AddressMode.clamp_to_edge,
			address_mode_v=wgpu.AddressMode.clamp_to_edge,
			address_mode_w=wgpu.AddressMode.clamp_to_edge,
			mag_filter=wgpu.FilterMode.linear,
			min_filter=wgpu.FilterMode.linear,
			mipmap_filter=wgpu.MipmapFilterMode.linear,
		)

	def load_faces(self, path: Path):
		if self.has_six_faces(path):
			return self.load_six_faces(path)

		return self.load_cross_layout(path)

	def has_six_faces(self, path: Path):
		required = [
			"px",
			"nx",
			"py",
			"ny",
			"pz",
			"nz",
		]

		return all(
			(path / f"{face}.png").exists()
			for face in required
		)

	def load_six_faces(self, path: Path):
		names = [
			"px",
			"nx",
			"py",
			"ny",
			"pz",
			"nz",
		]

		return [
			Image.open(path / f"{name}.png").convert("RGBA")
			for name in names
		]

	def load_cross_layout(self, path: Path):
		images = list(path.glob("*.png"))

		if len(images) != 1:
			raise ValueError(
				"Skybox must contain either "
				"px/nx/py/ny/pz/nz PNG files "
				"or exactly one cross-layout PNG"
			)

		image = Image.open(images[0]).convert("RGBA")

		width, height = image.size

		if width != height * 4:
			raise ValueError(
				"Cross-layout skybox must have a 4:1 aspect ratio"
			)

		face_size = height

		faces = {
			"px": (2, 0),
			"nx": (0, 0),
			"py": (1, 0),
			"ny": (1, 2),
			"pz": (1, 1),
			"nz": (3, 1),
		}

		return [
			image.crop((
				x * face_size,
				y * face_size,
				(x + 1) * face_size,
				(y + 1) * face_size,
			))
			for x, y in [
				faces["px"],
				faces["nx"],
				faces["py"],
				faces["ny"],
				faces["pz"],
				faces["nz"],
			]
		]

	@staticmethod
	def create_skybox_mesh(device):
		vertices = struct.pack(
			"108f",
			# Front
			-1, 1, 1,
			-1, -1, 1,
			1, 1, 1,
			-1, -1, 1,
			1, -1, 1,
			1, 1, 1,

			# Right
			1, 1, 1,
			1, -1, 1,
			1, 1, -1,
			1, -1, 1,
			1, -1, -1,
			1, 1, -1,

			# Back
			1, 1, -1,
			1, -1, -1,
			-1, 1, -1,
			1, -1, -1,
			-1, -1, -1,
			-1, 1, -1,

			# Left
			-1, 1, -1,
			-1, -1, -1,
			-1, 1, 1,
			-1, -1, -1,
			-1, -1, 1,
			-1, 1, 1,

			# Top
			-1, 1, -1,
			-1, 1, 1,
			1, 1, -1,
			-1, 1, 1,
			1, 1, 1,
			1, 1, -1,

			# Bottom
			-1, -1, 1,
			-1, -1, -1,
			1, -1, 1,
			-1, -1, -1,
			1, -1, -1,
			1, -1, 1,
		)

		buffer = device.create_buffer(
			size=len(vertices),
			usage=wgpu.BufferUsage.VERTEX | wgpu.BufferUsage.COPY_DST
		)

		device.queue.write_buffer(
			buffer,
			0,
			vertices
		)

		return buffer
