# chunk.py
from pathlib import Path

from factory_engine.ecs.components.c_hex_cell import HexCellComponent
from factory_engine.ecs.components.c_material import MaterialComponent
from factory_engine.ecs.components.c_mesh import MeshRenderer
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.math3d import Vec3
from factory_engine.rendering.mesh import Mesh
from factory_engine.settings import HEX_INNER_RADIUS, HEX_OUTER_RADIUS, CHUNK_SIDE_LENGTH, CHUNK_OUTER_RADIUS, \
	CHUNK_INNER_RADIUS


class Chunk:
	def __init__(self, terrain, coordinates, lod=0):
		self.terrain = terrain
		self.coordinates = coordinates
		self.lod = lod

		self.chunk_neighbors = {}
		self.cells = []

		self.cube = Mesh.create_cube(self.terrain.device)

	def generate(self):
		radius = int(CHUNK_SIDE_LENGTH) - 1
		index = 0

		for q in range(-radius, radius + 1):
			r_min = max(-radius, -q - radius)
			r_max = min(radius, -q + radius)

			for r in range(r_min, r_max + 1):
				s = -q - r

				self.generate_cell(q, r, s, index)
				index += 1

	# x = self.position.x
	# z = self.position.z

	# height = self.terrain.generate_height(x, z)

	# return height

	def generate_cell(self, q, r, s, index):
		local_pos = Vec3(
			(r + q * 0.5) * (HEX_INNER_RADIUS * 2.0),
			0.0,
			q * (HEX_OUTER_RADIUS * 1.5)
		)

		pos = self.get_world_position() + local_pos

		hex_cell = self.terrain.world.create_entity(f"HexCell{index}")
		hex_cell.add(TransformComponent(position=pos))
		hex_cell.add(HexCellComponent(Vec3(q, r, s)))
		hex_cell.add(MaterialComponent(shader=Path(__file__).parents[1] / "shaders" / "mesh.wgsl"))
		hex_cell.add(MeshRenderer(self.cube))

		self.cells.append(hex_cell)

	def get_world_position(self):
		return Vec3(
			(self.coordinates.x + self.coordinates.z) * CHUNK_OUTER_RADIUS,
			0,
			self.coordinates.z * CHUNK_INNER_RADIUS * 2
		)
