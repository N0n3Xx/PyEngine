# c_material.py
from factory_engine.ecs.entity import Entity
from factory_engine.math3d import Vec3

# shader=Path(__file__).parent / "shaders" / "mesh.wgsl"
class MaterialComponent:
	def __init__(self, material):
		self.entity: Entity | None = None
		self.dirty = True

		self.material = material

	def set_material(self, material):
		self.material = material
		self.dirty = True

	def get_material(self):
		return self.material
