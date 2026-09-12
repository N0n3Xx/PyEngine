# chunk_mesher.py
from factory_engine.ecs.components.c_hex_cell import HexCellComponent
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.settings import HEX_CORNERS, get_first_corner, get_second_corner, get_first_solid_corner, \
	get_second_solid_corner, get_bridge, ELEVATION_MULTIPLIER, terrace_lerp, get_terrace_steps, CLIFF_SLOPE_HEIGHT


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

		# Slopes
		v3.y = neighbor.get(HexCellComponent).elevation * ELEVATION_MULTIPLIER
		v4.y = neighbor.get(HexCellComponent).elevation * ELEVATION_MULTIPLIER

		if cell.get(HexCellComponent).get_transition_type(direction) == 1:  # SLOPED (AND FLAT)
			self.add_quad(v1, v2, v3, v4)
		elif cell.get(HexCellComponent).get_transition_type(direction) == 2:  # TERRACED
			self.triangulate_edge_terraces(v1, v2, cell, v3, v4, neighbor)
		elif cell.get(HexCellComponent).get_transition_type(direction) == 3:  # CLIFF
			self.triangulate_cliff(v1, v2, bridge, cell, neighbor)

		next_neighbor = cell.get(HexCellComponent).get_neighbor(HexCellComponent.next_dir(direction))
		if direction <= 1 and next_neighbor is not None:
			v5 = v2 + get_bridge(HexCellComponent.next_dir(direction))
			v5.y = next_neighbor.get(HexCellComponent).elevation * ELEVATION_MULTIPLIER

			cell_elevation = cell.get(HexCellComponent).elevation
			neighbor_elevation = neighbor.get(HexCellComponent).elevation
			next_neighbor_elevation = next_neighbor.get(HexCellComponent).elevation

			if cell_elevation <= neighbor_elevation:
				if cell_elevation <= next_neighbor_elevation:
					self.triangulate_corner(v2, cell, v4, neighbor, v5, next_neighbor)
				else:
					self.triangulate_corner(v5, next_neighbor, v2, cell, v4, neighbor)
			elif neighbor_elevation <= next_neighbor_elevation:
				self.triangulate_corner(v4, neighbor, v5, next_neighbor, v2, cell)
			else:
				self.triangulate_corner(v5, next_neighbor, v2, cell, v4, neighbor)

	def triangulate_edge_terraces(
			self,
			begin_left,
			begin_right,
			begin_cell,
			end_left,
			end_right,
			end_cell,
	):
		elevation1 = begin_cell.get(TransformComponent).position.y
		elevation2 = end_cell.get(TransformComponent).position.y

		terraces_per_slope = get_terrace_steps(elevation1, elevation2)[0]
		terrace_steps = get_terrace_steps(elevation1, elevation2)[1]

		v3 = terrace_lerp(begin_left, end_left, 1, terrace_steps, terraces_per_slope)
		v4 = terrace_lerp(begin_right, end_right, 1, terrace_steps, terraces_per_slope)
		self.add_quad(begin_left, begin_right, v3, v4)

		for i in range(2, terrace_steps):
			v1 = v3
			v2 = v4

			v3 = terrace_lerp(begin_left, end_left, i, terrace_steps, terraces_per_slope)
			v4 = terrace_lerp(begin_right, end_right, i, terrace_steps, terraces_per_slope)

			self.add_quad(v1, v2, v3, v4)

		self.add_quad(v3, v4, end_left, end_right)

	def triangulate_cliff(
			self,
			begin_left,
			begin_right,
			bridge,
			cell,
			neighbor
	):
		top_slope_left = begin_left + (bridge * 0.5)
		top_slope_right = begin_right + (bridge * 0.5)
		top_slope_left.y = begin_left.y - CLIFF_SLOPE_HEIGHT
		top_slope_right.y = begin_right.y - CLIFF_SLOPE_HEIGHT

		self.add_quad(begin_left, begin_right, top_slope_left, top_slope_right)

		neighbor_y = neighbor.get(HexCellComponent).elevation * ELEVATION_MULTIPLIER

		bottom_slope_left = begin_left + (bridge * 0.5)
		bottom_slope_right = begin_right + (bridge * 0.5)
		bottom_slope_left.y = neighbor_y + CLIFF_SLOPE_HEIGHT
		bottom_slope_right.y = neighbor_y + CLIFF_SLOPE_HEIGHT

		self.add_quad(top_slope_left, top_slope_right, bottom_slope_left, bottom_slope_right)

		end_left = begin_left + bridge
		end_right = begin_right + bridge
		end_left.y = neighbor_y
		end_right.y = neighbor_y

		self.add_quad(bottom_slope_left, bottom_slope_right, end_left, end_right)

	def triangulate_corner(
			self,
			bottom, bottom_cell,
			left, left_cell,
			right, right_cell,
	):
		left_edge_type = bottom_cell.get(HexCellComponent).get_transition_type_from_cell(left_cell)
		right_edge_type = bottom_cell.get(HexCellComponent).get_transition_type_from_cell(right_cell)
		bottom_edge_type = left_cell.get(HexCellComponent).get_transition_type_from_cell(right_cell)

		# 0: Flat !Not Used
		# 1: Slope !Used instead of flat
		# 2: Terrace
		# 3: Cliff
		if left_edge_type == 1:
			if right_edge_type == 1:
				if bottom_edge_type == 1:
					self.add_triangle(bottom, left, right)
					return  # (1, 1, 1)
				elif bottom_edge_type == 2:
					return  # (1, 1, 2)

			elif right_edge_type == 2:
				if bottom_edge_type == 1:
					self.triangulate_corner_terrace_slopes(right, right_cell, bottom, bottom_cell, left, left_cell)
					return  # (1, 2, 1)
				elif bottom_edge_type == 2:
					self.triangulate_corner_terraces(right, right_cell, bottom, bottom_cell, left, left_cell)
					return  # (1, 2, 2)

		elif left_edge_type == 2:
			if right_edge_type == 1:
				if bottom_edge_type == 1:
					self.triangulate_corner_terrace_slopes(bottom, bottom_cell, left, left_cell, right, right_cell)
					return  # (2, 1, 1)
				elif bottom_edge_type == 2:
					self.triangulate_corner_terraces(left, left_cell, right, right_cell, bottom, bottom_cell)
					return  # (2, 1, 2)

			elif right_edge_type == 2:
				if bottom_edge_type == 1:
					self.triangulate_corner_terraces(bottom, bottom_cell, left, left_cell, right, right_cell)
					return  # (2, 2, 1)
				elif bottom_edge_type == 2:
					return  # (2, 2, 2)

	def triangulate_corner_terrace_slopes(
			self,
			begin, begin_cell,
			left, left_cell,
			right, right_cell
	):
		begin_elevation = begin_cell.get(TransformComponent).position.y
		left_elevation = left_cell.get(TransformComponent).position.y

		terraces_per_slope, terrace_steps = get_terrace_steps(begin_elevation, left_elevation)

		previous = begin

		for step in range(1, terrace_steps + 1):
			current = terrace_lerp(
				begin,
				left,
				step,
				terrace_steps,
				terraces_per_slope
			)

			self.add_triangle(right, previous, current)

			previous = current

	def triangulate_corner_terraces(
			self,
			begin, begin_cell,
			left, left_cell,
			right, right_cell
	):
		begin_elevation = begin_cell.get(TransformComponent).position.y
		left_elevation = left_cell.get(TransformComponent).position.y
		right_elevation = right_cell.get(TransformComponent).position.y

		left_terraces_per_slope, left_terrace_steps = get_terrace_steps(begin_elevation, left_elevation)
		right_terraces_per_slope, right_terrace_steps = get_terrace_steps(begin_elevation, right_elevation)

		print(f"Left Steps: {left_terrace_steps} / Right Steps: {right_terrace_steps}")

		# First step
		left_step = 1
		right_step = 1

		v_left = terrace_lerp(
			begin,
			left,
			left_step,
			left_terrace_steps,
			left_terraces_per_slope,
		)

		v_right = terrace_lerp(
			begin,
			right,
			right_step,
			right_terrace_steps,
			right_terraces_per_slope,
		)

		self.add_triangle(begin, v_left, v_right)

		# Remaining steps
		while left_step < left_terrace_steps or right_step < right_terrace_steps:
			previous_left, previous_right = v_left, v_right

			left_can_advance = left_step < left_terrace_steps
			right_can_advance = right_step < right_terrace_steps

			if left_can_advance:
				left_step += 1
				v_left = terrace_lerp(
					begin, left, left_step, left_terrace_steps, left_terraces_per_slope
				)

			if right_can_advance:
				right_step += 1
				v_right = terrace_lerp(
					begin, right, right_step, right_terrace_steps, right_terraces_per_slope
				)

			if left_can_advance and right_can_advance:
				self.add_quad(previous_left, previous_right, v_left, v_right)
			elif left_can_advance:
				self.add_triangle(previous_left, v_left, previous_right)
			elif right_can_advance:
				self.add_triangle(previous_left, v_right, previous_right)

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
