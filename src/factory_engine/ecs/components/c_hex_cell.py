# c_hex_cell.py
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.ecs.entity import Entity
from factory_engine.settings import get_transition_type


# Q axis direction:  /
# R axis direction: ––
# S axis direction:  \
class HexCellComponent:
	def __init__(self, coordinates, elevation):
		self.entity: Entity | None = None
		self.coordinates = coordinates
		self.neighbors = [None] * 6
		self.elevation = elevation

	def get_neighbor(self, direction):
		return self.neighbors[direction]

	def set_neighbor(self, direction, neighbor):
		self.neighbors[direction] = neighbor
		neighbor.get(HexCellComponent).neighbors[HexCellComponent.opposite(direction)] = self.entity

	def get_transition_type(self, direction):
		height = self.entity.get(TransformComponent).get_position().y
		other_height = self.neighbors[direction].get(TransformComponent).get_position().y
		return get_transition_type(height, other_height)

	def get_transition_type_from_cell(self, other):
		height = self.entity.get(TransformComponent).get_position().y
		other_height = other.get(TransformComponent).get_position().y
		return get_transition_type(height, other_height)

	@staticmethod
	def opposite(direction):
		if direction < 3:
			return direction + 3
		else:
			return direction - 3

	@staticmethod
	def previous_dir(direction):
		if direction == 0:
			return 5
		else:
			return direction - 1

	@staticmethod
	def next_dir(direction):
		if direction == 5:
			return 0
		else:
			return direction + 1
