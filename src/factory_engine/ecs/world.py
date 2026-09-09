# world.py

from .entity import Entity


class World:
	def __init__(self):
		self.next_entity_id = 0
		self.entities = {}

	def create_entity(self, name):
		entity_id = self.next_entity_id
		self.next_entity_id += 1

		entity = Entity(
			entity_id,
			name,
			self
		)

		self.entities[entity_id] = entity

		return entity

	def query(self, *component_types):
		if not component_types:
			return []

		results = []

		for entity in self.entities.values():
			if all(entity.has(component_type) for component_type in component_types):
				components = tuple(
					entity.get(component_type)
					for component_type in component_types
				)

				results.append(
					(entity, *components)
				)

		return results

	def get_entity_by_id(self, entity_id):
		return self.entities.get(entity_id)

	def get_entity_by_name(self, entity_name):
		for entity in self.entities.values():
			if entity.name == entity_name:
				return entity

		return None
