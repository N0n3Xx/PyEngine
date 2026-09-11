# texture.py
from pathlib import Path

import wgpu
from PIL import Image


class Texture:
	def __init__(self, device, path: Path):
		self.device = device
		self.path = path

		image = Image.open(self.path).convert('RGBA')
		width, height = image.size

		self.texture = device.create_texture(
			size=(width, height, 1),
			mip_level_count=1,
			sample_count=1,
			dimension=wgpu.TextureDimension.d2,
			format="rgba8unorm",
			usage=(
					wgpu.TextureUsage.TEXTURE_BINDING |
					wgpu.TextureUsage.COPY_DST
			)
		)

		data = image.tobytes()
		device.queue.write_texture(
			{
				"texture": self.texture
			},
			data,
			{
				"bytes_per_row": width * 4,
				"rows_per_image": height
			},
			(width, height, 1)
		)

		self.view = self.texture.create_view(
			dimension=wgpu.TextureDimension.d2,
		)

		self.sampler = device.create_sampler(
			address_mode_u=wgpu.AddressMode.repeat,
			address_mode_v=wgpu.AddressMode.repeat,
			address_mode_w=wgpu.AddressMode.repeat,
			mag_filter=wgpu.FilterMode.linear,
			min_filter=wgpu.FilterMode.linear,
			mipmap_filter=wgpu.MipmapFilterMode.linear
		)
