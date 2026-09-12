# chunk_mesher.py
from factory_engine.ecs.components.c_hex_cell import HexCellComponent
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.settings import HEX_CORNERS, get_first_corner, get_second_corner, get_first_solid_corner, \
	get_second_solid_corner, get_bridge


class ChunkMesher:
	def __init__(self):
		self.cells = []
		self.vertices = []
		self.indices = []

		self.uv_scale = 0.25

	def triangulate(self, cells):
		self.cells = cells
		self.vertices.clear()
		self.indices.clear()

		for cell in cells:
			self.triangulate_cell(cell)

		return self.vertices, self.indices

	def triangulate_cell(self, cell):
		for i in range(6):
			self.triangulate_cell_dir(i, cell)

	def triangulate_cell_dir(self, direction, cell):
		# Triangulate the CENTER of the cell
		center = cell.get(TransformComponent).get_position()
		v1 = center + get_first_solid_corner(direction)
		v2 = center + get_second_solid_corner(direction)

		self.add_triangle(center, v1, v2)

		# Triangulate the CONNECTION between the cells
		if direction <= 2:
			self.triangulate_connection(direction, cell, v1, v2)

	def triangulate_connection(self, direction, cell, v1, v2):
		neighbor = cell.get(HexCellComponent).get_neighbor(direction)

		if not neighbor:
			return

		bridge = get_bridge(direction)
		v3 = v1 + bridge
		v4 = v2 + bridge

		self.add_quad(v1, v2, v3, v4)

		next_neighbor = cell.get(HexCellComponent).get_neighbor(HexCellComponent.next_dir(direction))
		if direction <= 1 and next_neighbor is not None:
			self.add_triangle(v2, v4, v2 + get_bridge(HexCellComponent.next_dir(direction)))

	def add_triangle(self, v1, v2, v3):
		normal = (v3 - v1).cross(v2 - v1).normalize()

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
			vertex_index + 2,
			vertex_index + 1,
		])

	def add_quad(self, v1, v2, v3, v4):
		normal = (v2 - v1).cross(v3 - v1).normalize()

		uv1 = (v1.x * self.uv_scale, v1.z * self.uv_scale)
		uv2 = (v2.x * self.uv_scale, v2.z * self.uv_scale)
		uv3 = (v3.x * self.uv_scale, v3.z * self.uv_scale)
		uv4 = (v4.x * self.uv_scale, v4.z * self.uv_scale)

		vertex_index = len(self.vertices) // 8

		self.vertices.extend([
			# v1
			v1.x, v1.y, v1.z,
			normal.x, normal.y, normal.z,
			uv1[0], uv1[1],

			# v2
			v2.x, v2.y, v2.z,
			normal.x, normal.y, normal.z,
			uv2[0], uv2[1],

			# v3
			v3.x, v3.y, v3.z,
			normal.x, normal.y, normal.z,
			uv3[0], uv3[1],

			# v4
			v4.x, v4.y, v4.z,
			normal.x, normal.y, normal.z,
			uv4[0], uv4[1],
		])

		self.indices.extend([
			vertex_index,
			vertex_index + 1,
			vertex_index + 2,

			vertex_index + 1,
			vertex_index + 3,
			vertex_index + 2,
		])
