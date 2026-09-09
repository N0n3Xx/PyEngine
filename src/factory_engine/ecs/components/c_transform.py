# c_transform.py
from factory_engine.math3d import Vec3


class TransformComponent:
	def __init__(
			self,
			position=None,
			rotation=None,
			scale=None,
	):
		self.position = position or Vec3(0,0,0)
		self.rotation = rotation or Vec3(0,0,0)
		self.scale = scale or Vec3(1,1,1)

		# For interpolation
		self.previous_position = Vec3(
			self.position.x,
			self.position.y,
			self.position.z
		)
		self.previous_rotation = Vec3(
			self.rotation.x,
			self.rotation.y,
			self.rotation.z
		)
		self.previous_scale = Vec3(
			self.scale.x,
			self.scale.y,
			self.scale.z
		)

	def save_previous_state(self) -> None:
		self.previous_position = Vec3(
			self.position.x,
			self.position.y,
			self.position.z
		)
		self.previous_rotation = Vec3(
			self.rotation.x,
			self.rotation.y,
			self.rotation.z
		)
		self.previous_scale = Vec3(
			self.scale.x,
			self.scale.y,
			self.scale.z
		)

	def __repr__(self):
		return f"Transform(position={self.position}, rotation={self.rotation}, scale={self.scale})"

	def get_position(self):
		return self.position

	def get_rotation(self):
		return self.rotation

	def get_scale(self):
		return self.scale

	def set_position(self, position):
		self.position = position

	def set_rotation(self, rotation):
		self.rotation = rotation

	def set_scale(self, scale):
		self.scale = scale