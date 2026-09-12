# entity.py

class Entity:
	def __init__(self, entity_id, name, world):
		self.id = entity_id
		self.name = name
		self.world = world

		self.components = {}

	def add(self, component):
		component.entity = self
		self.components[type(component)] = component

	def has(self, component_type):
		return component_type in self.components

	def get(self, component_type):
		return self.components[component_type]

	def get_name(self):
		return self.name

	def is_dirty(self):
		return any(
			component.dirty
			for component in self.components.values()
		)

	def clear_dirty(self):
		for component in self.components.values():
			component.dirty = False
