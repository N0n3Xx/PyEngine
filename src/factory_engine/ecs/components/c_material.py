# c_material.py

from factory_engine.math3d import Vec3

# shader=Path(__file__).parent / "shaders" / "mesh.wgsl"
class MaterialComponent:
	def __init__(self, color=Vec3(0.8, 0.8, 0.8), shader=None):
		self.dirty = True

		self.color = color
		self.shader = shader
