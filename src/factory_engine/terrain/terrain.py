# terrain.py

class Terrain:
	def __init__(self, seed, chunk_size):
		self.seed = seed
		self.chunk_size = chunk_size

		self.render_distance = 400.0
		self.chunks = {}
		self.streaming_sources = []  # List of objects to influence e.g. visibility of chunks
