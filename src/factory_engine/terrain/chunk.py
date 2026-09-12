# chunk.py
from pathlib import Path

from factory_engine.ecs.components.c_hex_cell import HexCellComponent
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.math3d import Vec3
from factory_engine.rendering.mesh import Mesh
from factory_engine.settings import HEX_INNER_RADIUS, HEX_OUTER_RADIUS, CHUNK_SIZE, ELEVATION_MULTIPLIER
from factory_engine.terrain.chunk_mesher import ChunkMesher


class Chunk:
	def __init__(self, terrain, chunk_coords, terrain_material, lod=0):
		self.terrain = terrain
		self.chunk_coords = chunk_coords
		self.lod = lod

		self.chunk_neighbors = [None] * 8
		self.cells = []

		self.mesher = ChunkMesher()
		self.mesh = None

		self.material = terrain_material

	def generate(self):
		for z in range(CHUNK_SIZE):
			for x in range(CHUNK_SIZE):
				global_x = self.chunk_coords.x * CHUNK_SIZE + x
				global_z = self.chunk_coords.z * CHUNK_SIZE + z

				elevation = self.terrain.generate_height(global_x, -global_z)
				self.generate_cell(Vec3(x, 0, z), z * CHUNK_SIZE + x, elevation)

	def mesh_chunk(self):
		vertices, indices = self.mesher.triangulate(self.cells)
		self.mesh = Mesh.create(self.terrain.device, vertices, indices)

	def generate_cell(self, cell_coord, index, elevation):
		local_pos = Vec3(
			(cell_coord.x + cell_coord.z * 0.5 - cell_coord.z // 2) * HEX_INNER_RADIUS * 2.0,
			elevation * ELEVATION_MULTIPLIER,
			-cell_coord.z * HEX_OUTER_RADIUS * 1.5
		)

		pos = self.get_world_position() + local_pos

		q = cell_coord.x - cell_coord.z // 2
		r = cell_coord.z
		s = -q - r

		hex_cell = self.terrain.world.create_entity(f"{int(self.chunk_coords.x)}_{int(self.chunk_coords.z)}_HexCell{index}")
		hex_cell.add(TransformComponent(position=pos))
		hex_cell.add(HexCellComponent(Vec3(q, r, s), elevation))
		hex_cell_component = hex_cell.get(HexCellComponent)

		if cell_coord.x > 0:
			hex_cell_component.set_neighbor(4, self.cells[index - 1])

		if cell_coord.z > 0:
			if (int(cell_coord.z) & 1) == 0:
				hex_cell_component.set_neighbor(2, self.cells[index - CHUNK_SIZE])
				if cell_coord.x > 0:
					hex_cell_component.set_neighbor(3, self.cells[index - CHUNK_SIZE - 1])
			else:
				hex_cell_component.set_neighbor(3, self.cells[index - CHUNK_SIZE])
				if cell_coord.x < CHUNK_SIZE - 1:
					hex_cell_component.set_neighbor(2, self.cells[index - CHUNK_SIZE + 1])

		self.cells.append(hex_cell)

	def get_world_position(self):
		return Vec3(
			self.chunk_coords.x * (CHUNK_SIZE * HEX_INNER_RADIUS * 2.0),
			self.chunk_coords.y,
			-self.chunk_coords.z * (CHUNK_SIZE * HEX_OUTER_RADIUS * 1.5)
		)

	def get_neighbor(self, direction):
		return self.chunk_neighbors[direction]

	def set_neighbor(self, direction, neighbor):
		self.chunk_neighbors[direction] = neighbor
		neighbor.chunk_neighbors[Chunk.opposite(direction)] = self

	@staticmethod
	def opposite(direction):
		if direction < 4:
			return direction + 4
		else:
			return direction - 4

	@staticmethod
	def previous_dir(direction):
		if direction == 0:
			return 7
		else:
			return direction - 1

	@staticmethod
	def next_dir(direction):
		if direction == 7:
			return 0
		else:
			return direction + 1
