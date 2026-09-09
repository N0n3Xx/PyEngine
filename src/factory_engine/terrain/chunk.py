# chunk.py

class Chunk:
	def __init__(self, chunk_x, chunk_y, lod=0):
		self.chunk_x = chunk_x
		self.chunk_y = chunk_y
		self.lod = lod

		self.neighbors = {}
