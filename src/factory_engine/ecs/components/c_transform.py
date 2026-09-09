# c_transform.py
from factory_engine.math3d import Vec3


class Transform:
	def __init__(
			self,
			position=None,
			rotation=None,
			scale=None,
	):
		self.position = position or Vec3(0,0,0)
		self.rotation = rotation or Vec3(0,0,0)
		self.scale = scale or Vec3(0,0,0)