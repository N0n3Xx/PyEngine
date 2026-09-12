# c_hex_cell.py
from factory_engine.ecs.components.c_transform import TransformComponent
from factory_engine.ecs.entity import Entity





# Q axis direction:  /
# R axis direction: ––
# S axis direction:  \
class HexCellComponent:
	def __init__(self, coordinates):
		self.entity: Entity | None = None
		self.coordinates = coordinates
		self.neighbors = [None] * 6

	def get_neighbor(self, direction):
		return self.neighbors[direction]

	def set_neighbor(self, direction, neighbor):
		self.neighbors[direction] = neighbor
		neighbor.get(HexCellComponent).neighbors[HexCellComponent.opposite(direction)] = self.entity

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
