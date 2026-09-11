# settings.py

import math

from factory_engine.math3d import Vec3

# Engine
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

FIXED_UPDATE_RATE = 1.0 / 60.0
MAX_SIM_UPDATES_PER_FRAME = 5


# Rendering
DIRTY_BATCH_THRESHOLD = 0.25 # the threshold between updating a single entity vs whole batch
VIEW_DISTANCE = 600.0

# Hex Grid
# Terrain Generation
HEX_SIDE_LENGTH = 1.0
HEX_OUTER_RADIUS = HEX_SIDE_LENGTH
HEX_INNER_RADIUS = HEX_SIDE_LENGTH * math.sqrt(3) / 2

CHUNK_SIZE = 12

HEX_CORNERS = (
	Vec3( 0.0,           0.0,  HEX_OUTER_RADIUS),
	Vec3( HEX_INNER_RADIUS, 0.0,  0.5 * HEX_OUTER_RADIUS),
	Vec3( HEX_INNER_RADIUS, 0.0, -0.5 * HEX_OUTER_RADIUS),
	Vec3( 0.0,           0.0, -HEX_OUTER_RADIUS),
	Vec3(-HEX_INNER_RADIUS, 0.0, -0.5 * HEX_OUTER_RADIUS),
	Vec3(-HEX_INNER_RADIUS, 0.0,  0.5 * HEX_OUTER_RADIUS),
	Vec3( 0.0,           0.0,  HEX_OUTER_RADIUS),
)