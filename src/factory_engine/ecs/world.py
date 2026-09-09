# world.py

class World:
	def __init__(self):
		self.next_entity_id = 0
		self.entities = {}
		self.components = {}