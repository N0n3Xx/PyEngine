# c_transform.py
import math

from factory_engine.math3d import Vec3


class TransformComponent:
	def __init__(
			self,
			position=None,
			rotation=None,
			scale=None,
	):
		self.dirty = True

		self.position = position or Vec3(0, 0, 0)
		self.rotation = rotation or Vec3(0, 0, 0)
		self.scale = scale or Vec3(1, 1, 1)

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
		self.dirty = True

	def set_rotation(self, rotation):
		self.rotation = rotation
		self.dirty = True

	def set_scale(self, scale):
		self.scale = scale
		self.dirty = True

	def add_position(self, delta):
		self.position += delta
		self.dirty = True

	def add_rotation(self, delta):
		self.rotation += delta
		self.dirty = True

	def add_scale(self, delta):
		self.scale += delta
		self.dirty = True

	def look_at(self, target):
		direction = (target - self.position).normalize()

		yaw = math.atan2(direction.x, direction.z)
		pitch = math.asin(-direction.y)

		self.rotation = Vec3(
			pitch,
			yaw,
			0.0
		)

		self.dirty = True