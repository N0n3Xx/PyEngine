# entity.py

class Entity:
	def __init__(self, entity_id, world):
		self.id = entity_id
		self.world = world

		self.components = {}

	def add(self, component):
		self.components[type(component)] = component

	def has(self, component_type):
		return component_type in self.components

	def get(self, component_type):
		return self.components[component_type]