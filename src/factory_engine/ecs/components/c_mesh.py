# c_mesh.py

class MeshRenderer:
	def __init__(self, mesh):
		self.dirty = True

		self.mesh = mesh