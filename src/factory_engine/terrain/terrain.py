# terrain.py
from pathlib import Path
from webbrowser import register

from factory_engine.math3d import Vec3
from factory_engine.terrain.chunk import Chunk
from .terrain_generator import (
	ContinentalityGenerator,
	GeologyGenerator,
	ElevationGenerator,
	TemperatureGenerator,
	HumidityGenerator,
	RainfallGenerator,
	BiomeGenerator,
	WaterGenerator,
	TerrainDetailGenerator,
	FinalHeightGenerator
)
from ..rendering.material import Material
from ..rendering.texture import Texture
from ..settings import VIEW_DISTANCE, CHUNK_NEIGHBOR_OFFSETS


class Terrain:
	def __init__(self, seed, device, world):
		self.seed = seed
		#self.chunk_size = CHUNK_SIZE
		self.device = device
		self.world = world

		self.render_distance = VIEW_DISTANCE
		self.chunks: dict[tuple[int, int], Chunk] = {}
		self.streaming_sources = []  # List of objects to influence e.g. visibility of chunks

		checkerboard = Texture(
			self.device,
			Path(__file__).parents[3]
			/ "assets"
			/ "textures"
			/ "uv_checkerboard.png",
		)

		terrain_material = Material(
			shader_path=Path(__file__).parent / "shaders" / "terrain.wgsl",
			parameters={
				"base_color": (1.0, 1.0, 1.0, 1.0),
				"metallic": 0.0,
				"roughness": 1.0
			},
			textures={
				"albedo": checkerboard
			}
		)

		# The different generators
		self.continentality_generator = None
		self.geology_generator = None
		self.elevation_generator = None
		self.temperature_generator = None
		self.humidity_generator = None
		self.rainfall_generator = None
		self.biome_generator = None
		self.water_generator = None
		self.terrain_detail_generator = None
		self.final_height_generator = None

		self.setup_generators()

		for z in range(0, 3):
			for x in range(0, 3):
				chunk = Chunk(
					self,
					Vec3(x, 0, z),
					terrain_material
				)
				chunk.generate()

				self.register_chunk(chunk)

				chunk.mesh_chunk()

	def register_chunk(self, chunk):
		x = int(chunk.chunk_coords.x)
		z = int(chunk.chunk_coords.z)

		self.chunks[(x, z)] = chunk

		for direction, (dx, dz) in CHUNK_NEIGHBOR_OFFSETS.items():
			neighbor = self.chunks.get((x + dx, z + dz))

			if neighbor is not None:
				chunk.set_neighbor(direction, neighbor)

	def setup_generators(self):
		self.continentality_generator = ContinentalityGenerator(self.seed)

		self.geology_generator = GeologyGenerator(self.seed)
		self.elevation_generator = ElevationGenerator(
			self.seed,
			self.continentality_generator,
			self.geology_generator,
		)
		self.temperature_generator = TemperatureGenerator(
			self.seed,
			self.continentality_generator,
			self.elevation_generator,
		)
		self.humidity_generator = HumidityGenerator(
			self.seed,
			self.continentality_generator,
			self.temperature_generator,
		)
		self.rainfall_generator = RainfallGenerator(
			self.seed,
			self.humidity_generator,
			self.elevation_generator,
		)
		self.biome_generator = BiomeGenerator(
			self.seed,
			self.temperature_generator,
			self.humidity_generator,
			self.rainfall_generator,
			self.elevation_generator,
		)
		self.water_generator = WaterGenerator(
			self.elevation_generator,
		)
		self.terrain_detail_generator = TerrainDetailGenerator(
			self.seed,
			self.elevation_generator,
			self.geology_generator,
			self.biome_generator,
		)
		self.final_height_generator = FinalHeightGenerator(
			self.terrain_detail_generator,
		)

	def generate_height(self, x, z):
		return self.terrain_detail_generator.generate(x, z)
