# material.py
from pathlib import Path

from factory_engine.rendering.texture import Texture


class Material:
	def __init__(
			self,
			shader_path: Path,
			parameters: dict | None = None,
			textures: dict[str, Texture] | None = None
	):
		self.dirty = True

		self.shader_path = shader_path
		self.parameters = parameters or {}
		self.textures = textures or {}

	def set_parameter(self, name, value):
		self.parameters[name] = value
		self.dirty = True

	def set_texture(self, name, value):
		self.textures[name] = value
		self.dirty = True

	def get_parameter(self, name, default=None):
		return self.parameters.get(name, default)

	def get_texture(self, name, default=None):
		return self.textures.get(name, default)