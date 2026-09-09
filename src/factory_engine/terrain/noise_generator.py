# noise_generator.py

import math


def _fade(t):
	return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a, b, t):
	return a + t * (b - a)


def _hash(seed, x, y):
	value = x * 374761393 + y * 668265263 + seed * 1442695041
	value = (value ^ (value >> 13)) * 1274126177
	return value ^ (value >> 16)


class NoiseGenerator:
	def __init__(self, seed=1234, scale=1.0, octaves=1, persistence=0.5, lacunarity=2.0):
		self.seed = seed
		self.scale = scale
		self.octaves = octaves
		self.persistence = persistence
		self.lacunarity = lacunarity

	def noise_2d(self, x, y):
		frequency = self.scale
		amplitude = 1.0
		max_amplitude = 0.0

		value = 0.0

		for _ in range(self.octaves):
			sample = self._perlin_2d(
				x * frequency,
				y * frequency,
			)
			value += sample * amplitude
			max_amplitude += amplitude

			frequency *= self.lacunarity
			amplitude *= self.persistence

		return value / max_amplitude

	def _perlin_2d(self, x, y):
		x0 = math.floor(x)
		y0 = math.floor(y)

		x1 = x0 + 1
		y1 = y0 + 1

		# Fractional position within the grid cell
		sx = x - x0
		sy = y - y0

		g00 = self._gradient(x0, y0)
		g10 = self._gradient(x1, y0)
		g01 = self._gradient(x0, y1)
		g11 = self._gradient(x1, y1)

		dx0 = sx
		dy0 = sy

		dx1 = sx - 1
		dy1 = sy - 1

		dot00 = g00[0] * dx0 + g00[1] * dy0
		dot10 = g10[0] * dx1 + g10[1] * dy0
		dot01 = g01[0] * dx0 + g01[1] * dy1
		dot11 = g11[0] * dx1 + g11[1] * dy1

		u = _fade(sx)
		v = _fade(sy)

		bottom = _lerp(dot00, dot10, u)
		top = _lerp(dot01, dot11, u)

		value = _lerp(bottom, top, v)

		return value

	def _gradient(self, x, y):
		directions = (
			(1, 1),
			(-1, 1),
			(1, -1),
			(-1, -1),
		)

		index = _hash(self.seed, x, y) % len(directions)

		return directions[index]
