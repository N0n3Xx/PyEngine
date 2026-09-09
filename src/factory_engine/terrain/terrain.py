# terrain.py

from terrain_generator import (
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


class Terrain:
	def __init__(self, seed, chunk_size):
		self.seed = seed
		self.chunk_size = chunk_size

		self.render_distance = 400.0
		self.chunks = {}
		self.streaming_sources = []  # List of objects to influence e.g. visibility of chunks

		self.continentality_generator = ContinentalityGenerator(self.seed)

		self.geology_generator = GeologyGenerator(self.seed)
		self.elevation_generator = ElevationGenerator(
			self.continentality_generator,
			self.geology_generator,
		)
		self.temperature_generator = TemperatureGenerator(
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
