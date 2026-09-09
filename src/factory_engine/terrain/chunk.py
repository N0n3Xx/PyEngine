# chunk.py
from factory_engine.terrain.terrain import Terrain


class Chunk:
	def __init__(self, terrain: Terrain, position, lod=0):
		self.terrain = terrain
		self.position = position
		self.lod = lod

		self.neighbors = {}

	def generate(self):
		x = self.position.x
		z = self.position.z

		height = self.terrain.generate_height(x, z)

		return height
