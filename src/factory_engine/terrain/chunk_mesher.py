# chunk_mesher.py
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.settings import HEX_CORNERS


class ChunkMesher:
	def __init__(self):
		self.cells = []
		self.vertices = []
		self.indices = []

		self.uv_scale = 1.0

	def triangulate(self, cells):
		self.cells = cells
		self.vertices.clear()
		self.indices.clear()

		for cell in cells:
			self.triangulate_cell(cell)

		return self.vertices, self.indices

	def triangulate_cell(self, cell):
		center = cell.get(TransformComponent).get_position()

		for i in range(6):
			self.add_triangle(
				center,
				center + HEX_CORNERS[i],
				center + HEX_CORNERS[i+1],
			)

	def add_triangle(self, v1, v2, v3):
		normal = (v2 - v1).cross(v3 - v1).normalize()

		uv1 = (v1.x * self.uv_scale, v1.z * self.uv_scale)
		uv2 = (v2.x * self.uv_scale, v2.z * self.uv_scale)
		uv3 = (v3.x * self.uv_scale, v3.z * self.uv_scale)

		vertex_index = len(self.vertices) // 8

		self.vertices.extend([
			v1.x, v1.y, v1.z,
			normal.x, normal.y, normal.z,
			uv1[0], uv1[1],
			v2.x, v2.y, v2.z,
			normal.x, normal.y, normal.z,
			uv2[0], uv2[1],
			v3.x, v3.y, v3.z,
			normal.x, normal.y, normal.z,
			uv3[0], uv3[1],
		])

		self.indices.extend([
			vertex_index,
			vertex_index + 1,
			vertex_index + 2,
		])
