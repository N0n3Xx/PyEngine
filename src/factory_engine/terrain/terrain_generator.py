# terrain_generator.py

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