# terrain_generator.py

# Order of operations:
#  1. Continentality
#  2. Geological Map
#  3. Elevation Map
#  4. Temperature Map
#  5. Humidity Map
#  6. Rainfall Map
#  7. Biome Map
#  8. Water Map
#  9. Terrain Detail
# 10. Final Height Map
# 11. Mesh Generation

from noise_generator import NoiseGenerator


class ContinentalityGenerator:
	def __init__(self, seed):
		self.seed = seed

		self.noise = NoiseGenerator(
			seed=seed,
			scale=0.001,
			octaves=4,
			persistence=0.5,
			lacunarity=2.0,
		)

	def generate(self, x, z):
		return self.noise.noise_2d(x, z)


class GeologyGenerator:
	def __init__(self, seed):
		self.seed = seed

		self.noise = NoiseGenerator(
			seed=seed,
			scale=0.003,
			octaves=4,
			persistence=0.5,
			lacunarity=2.0,
		)

	def generate(self, x, z):
		return self.noise.noise_2d(x, z)


class ElevationGenerator:
	def __init__(self, seed, continentality_generator, geology_generator):
		self.seed = seed
		self.continentality_generator = continentality_generator
		self.geology_generator = geology_generator

	def generate(self, x, z):
		continentality = self.continentality_generator.generate(x, z)
		geology = self.geology_generator.generate(x, z)

		# Simple equation for now
		elevation = continentality * 0.5 + geology * 0.5

		return elevation


class TemperatureGenerator:
	def __init__(self, seed, continentality_generator, geology_generator):
		self.seed = seed
		self.continentality_generator = continentality_generator
		self.geology_generator = geology_generator

	def generate(self, x, z):
		continentality = self.continentality_generator.generate(x, z)
		geology = self.geology_generator.generate(x, z)

		# Simple equation for now
		temperature = continentality * 0.7 + geology * 0.3

		return temperature


class HumidityGenerator:
	def __init__(self, seed, continentality_generator, temperature_generator):
		self.seed = seed
		self.continentality_generator = continentality_generator
		self.temperature_generator = temperature_generator

	def generate(self, x, z):
		continentality = self.continentality_generator.generate(x, z)
		temperature = self.temperature_generator.generate(x, z)

		humidity = -continentality * 0.7 + temperature * 0.3

		return humidity


class RainfallGenerator:
	def __init__(self, seed, humidity_generator, elevation_generator):
		self.seed = seed
		self.humidity_generator = humidity_generator
		self.elevation_generator = elevation_generator

	def generate(self, x, z):
		humidity = self.humidity_generator.generate(x, z)
		elevation = self.elevation_generator.generate(x, z)

		rainfall = humidity * 0.8 + elevation * 0.2

		return rainfall


class BiomeGenerator:
	def __init__(
			self,
			seed,
			temperature_generator,
			humidity_generator,
			rainfall_generator,
			elevation_generator
	):
		self.seed = seed
		self.temperature_generator = temperature_generator
		self.humidity_generator = humidity_generator
		self.rainfall_generator = rainfall_generator
		self.elevation_generator = elevation_generator

	def generate(self, x, z):
		temperature = self.temperature_generator.generate(x, z)
		humidity = self.humidity_generator.generate(x, z)
		rainfall = self.rainfall_generator.generate(x, z)
		elevation = self.elevation_generator.generate(x, z)

		# TODO: Placeholder definition
		if temperature < -0.5:
			biome = "tundra"
		elif temperature > 0.5 and humidity < -0.2:
			biome = "desert"
		elif temperature > 0.4 and humidity > 0.4:
			biome = "jungle"
		elif humidity > 0.2:
			biome = "forest"
		else:
			biome = "grassland"

		return biome


class WaterGenerator:
	def __init__(self, elevation_generator):
		self.elevation_generator = elevation_generator

	def generate(self, x, z):
		elevation = self.elevation_generator.generate(x, z)

		sea_level = 0.0

		if elevation < sea_level:
			return True

		return False


class TerrainDetailGenerator:
	def __init__(
			self,
			seed,
			elevation_generator,
			geology_generator,
			biome_generator,
	):
		self.seed = seed
		self.elevation_generator = elevation_generator
		self.geology_generator = geology_generator
		self.biome_generator = biome_generator

		self.noise = NoiseGenerator(
			seed=seed,
			scale=0.03,
			octaves=3,
			persistence=0.5,
			lacunarity=2.0
		)

	def generate(self, x, z):
		elevation = self.elevation_generator.generate(x, z)
		geology = self.geology_generator.generate(x, z)
		geology_factor = (geology + 1.0) / 2.0
		biome = self.biome_generator.generate(x, z)

		detail = self.noise.noise_2d(x, z)

		# TODO: Temporary detail strength dictionary
		detail_strength = {
			"tundra": 0.15,
			"desert": 0.08,
			"jungle": 0.20,
			"forest": 0.18,
			"grassland": 0.10,
		}

		strength = detail_strength.get(biome, 0.10)

		elevation += detail * strength * geology_factor

		return elevation


class FinalHeightGenerator:
	def __init__(self, terrain_detail_generator):
		self.terrain_detail_generator = terrain_detail_generator

	def generate(self, x, z):
		return self.terrain_detail_generator.generate(x, z)