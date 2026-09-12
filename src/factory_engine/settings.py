# settings.py

import math

from factory_engine.math3d import Vec3

# Engine
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

FIXED_UPDATE_RATE = 1.0 / 60.0
MAX_SIM_UPDATES_PER_FRAME = 5

# Rendering
DIRTY_BATCH_THRESHOLD = 0.25  # the threshold between updating a single entity vs whole batch
VIEW_DISTANCE = 600.0

# Hex Grid
## Terrain Generation
HEX_SIDE_LENGTH = 1.0
HEX_OUTER_RADIUS = HEX_SIDE_LENGTH
HEX_INNER_RADIUS = HEX_SIDE_LENGTH * math.sqrt(3) / 2

HEX_SOLID_FACTOR = 0.75
HEX_BLEND_FACTOR = 1.0 - HEX_SOLID_FACTOR
CHUNK_SIZE = 12

ELEVATION_MULTIPLIER = 30.0

## Transitions
TR_SLOPED = 0.23
TR_TERRACED = 0.75
TR_CLIFF = 10  # Makes no sense, maybe for future variants of each transition

TERRACES_PER_SLOPE = 2
TERRACE_STEPS = TERRACES_PER_SLOPE * 2 + 1
HOR_TERRACE_STEP_SIZE = 1.0 / TERRACE_STEPS
VERT_TERRACE_STEP_SIZE = 1.0 / (TERRACES_PER_SLOPE + 1)

HEX_CORNERS = (
	Vec3(0.0, 0.0, -HEX_OUTER_RADIUS),
	Vec3(HEX_INNER_RADIUS, 0.0, -0.5 * HEX_OUTER_RADIUS),
	Vec3(HEX_INNER_RADIUS, 0.0, 0.5 * HEX_OUTER_RADIUS),
	Vec3(0.0, 0.0, HEX_OUTER_RADIUS),
	Vec3(-HEX_INNER_RADIUS, 0.0, 0.5 * HEX_OUTER_RADIUS),
	Vec3(-HEX_INNER_RADIUS, 0.0, -0.5 * HEX_OUTER_RADIUS),
	Vec3(0.0, 0.0, -HEX_OUTER_RADIUS),
)

CHUNK_NEIGHBOR_OFFSETS = {
	0: (0, -1),
	1: (1, -1),
	2: (1, 0),
	3: (1, 1),
	4: (0, 1),
	5: (-1, 1),
	6: (-1, 0),
	7: (-1, -1),
}

def get_first_corner(direction):
	return HEX_CORNERS[direction]


def get_second_corner(direction):
	return HEX_CORNERS[direction + 1]


def get_first_solid_corner(direction):
	return HEX_CORNERS[direction] * HEX_SOLID_FACTOR


def get_second_solid_corner(direction):
	return HEX_CORNERS[direction + 1] * HEX_SOLID_FACTOR


def get_bridge(direction):
	return (HEX_CORNERS[direction] + HEX_CORNERS[direction + 1]) * HEX_BLEND_FACTOR

def terrace_lerp(a, b, step):
	a = a.copy()
	b = b.copy()
	_step = step

	h = _step * HOR_TERRACE_STEP_SIZE
	a.x += (b.x - a.x) * h
	a.z += (b.z - a.z) * h

	v = ((_step + 1) // 2) * VERT_TERRACE_STEP_SIZE
	a.y += (b.y - a.y) * v
	return a