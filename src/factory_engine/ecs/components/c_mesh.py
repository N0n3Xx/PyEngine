# c_mesh.py
from factory_engine.ecs.entity import Entity


class MeshRenderer:
	def __init__(self, mesh):
		self.entity: Entity | None = None
		self.dirty = True

		self.mesh = mesh