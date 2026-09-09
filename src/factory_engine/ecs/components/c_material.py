# c_material.py

from factory_engine.math3d import Vec3


class Material:
	def __init__(self, color=Vec3(0.8, 0.8, 0.8), shader=None):
		self.color = color
		self.shader = shader
