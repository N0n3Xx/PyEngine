# render_batch.py

class RenderBatch:
	def __init__(self, mesh, material):
		self.mesh = mesh
		self.material = material

		self.instances = []
		self.entity_instances = {}

		self.instance_buffer = None
		self.instance_capacity = 0

		self.dirty = True
