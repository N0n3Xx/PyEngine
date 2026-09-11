# chunk.py
from pathlib import Path

from factory_engine.ecs.components.c_hex_cell import HexCellComponent
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.math3d import Vec3
from factory_engine.rendering.mesh import Mesh
from factory_engine.settings import HEX_INNER_RADIUS, HEX_OUTER_RADIUS, CHUNK_SIZE
from factory_engine.terrain.chunk_mesher import ChunkMesher


class Chunk:
	def __init__(self, terrain, chunk_coords, terrain_material, lod=0):
		self.terrain = terrain
		self.chunk_coords = chunk_coords
		self.lod = lod

		self.chunk_neighbors = {}
		self.cells = []

		self.mesher = ChunkMesher()
		self.mesh = None

		self.material = terrain_material

	def generate(self):
		for x in range(CHUNK_SIZE):
			for z in range(CHUNK_SIZE):
				self.generate_cell(Vec3(x, 0, z), x * z)

	# x = self.position.x
	# z = self.position.z

	# height = self.terrain.generate_height(x, z)

	# return height

	def mesh_chunk(self):
		vertices, indices = self.mesher.triangulate(self.cells)
		self.mesh = Mesh.create(self.terrain.device, vertices, indices)

	def generate_cell(self, cell_coord, index):
		local_pos = Vec3(
			(cell_coord.x + cell_coord.z * 0.5 - cell_coord.z // 2) * HEX_INNER_RADIUS * 2.0,
			0.0,
			cell_coord.z * HEX_OUTER_RADIUS * 1.5
		)

		pos = self.get_world_position() + local_pos

		q = cell_coord.x - cell_coord.z // 2
		r = cell_coord.z
		s = -q - r

		hex_cell = self.terrain.world.create_entity(f"HexCell{index}")
		hex_cell.add(TransformComponent(position=pos))
		hex_cell.add(HexCellComponent(Vec3(q, r, s)))

		self.cells.append(hex_cell)

	def get_world_position(self):
		return Vec3(
			self.chunk_coords.x * (CHUNK_SIZE * HEX_INNER_RADIUS * 2.0),
			self.chunk_coords.y,
			self.chunk_coords.z * (CHUNK_SIZE * HEX_OUTER_RADIUS * 1.5)
		)
