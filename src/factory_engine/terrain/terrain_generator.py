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

	def generate(self, x, y):
		return self.noise.noise_2d(x, y)

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
	def generate(self, x, y):
		return self.noise.noise_2d(x, y)