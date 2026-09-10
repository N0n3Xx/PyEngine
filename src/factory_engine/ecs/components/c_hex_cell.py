# c_hex_cell.py

# Q axis direction:  /
# R axis direction: ––
# S axis direction:  \
class HexCellComponent:
	def __init__(self, coordinates):
		self.coordinates = coordinates
		self.neighbors = [None] * 6
