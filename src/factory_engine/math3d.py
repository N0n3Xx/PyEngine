# math3d.py

import math


class Vec3:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

	def __add__(self, other):
		return Vec3(
			self.x + other.x,
			self.y + other.y,
			self.z + other.z
		)

	def __sub__(self, other):
		return Vec3(
			self.x - other.x,
			self.y - other.y,
			self.z - other.z
		)

	def __mul__(self, other):
		if isinstance(other, Vec3):
			return Vec3(
				self.x * other.x,
				self.y * other.y,
				self.z * other.z
			)
		elif isinstance(other, (int, float)):
			return Vec3(
				self.x * other,
				self.y * other,
				self.z * other
			)
		return NotImplemented

	def __rmul__(self, other):
		return self * other

	def __eq__(self, other):
		if not isinstance(other, Vec3):
			return NotImplemented

		return (
				self.x == other.x
				and self.y == other.y
				and self.z == other.z
		)

	def length(self):
		return math.sqrt(
			self.x * self.x +
			self.y * self.y +
			self.z * self.z
		)

	def normalize(self):
		length = self.length()

		if length == 0:
			return Vec3()

		return Vec3(
			self.x / length,
			self.y / length,
			self.z / length
		)

	def dot(self, other):
		return (
				self.x * other.x +
				self.y * other.y +
				self.z * other.z
		)

	def cross(self, other):
		return Vec3(
			self.y * other.z - self.z * other.y,
			self.z * other.x - self.x * other.z,
			self.x * other.y - self.y * other.x
		)

	def __repr__(self):
		return f"Vec3({self.x}, {self.y}, {self.z})"


class Mat4:
	def __init__(self, values=None):
		if values is None:
			self.values = [
				[0.0, 0.0, 0.0, 0.0],
				[0.0, 0.0, 0.0, 0.0],
				[0.0, 0.0, 0.0, 0.0],
				[0.0, 0.0, 0.0, 0.0]
			]
		else:
			self.values = values

	@staticmethod
	def identity():
		return Mat4([
			[1.0, 0.0, 0.0, 0.0],
			[0.0, 1.0, 0.0, 0.0],
			[0.0, 0.0, 1.0, 0.0],
			[0.0, 0.0, 0.0, 1.0]
		])

	@staticmethod
	def translation(position):
		return Mat4([
			[1.0, 0.0, 0.0, position.x],
			[0.0, 1.0, 0.0, position.y],
			[0.0, 0.0, 1.0, position.z],
			[0.0, 0.0, 0.0, 1.0]
		])

	@staticmethod
	def rotation_x(angle):
		c = math.cos(angle)
		s = math.sin(angle)

		return Mat4([
			[1.0, 0.0, 0.0, 0.0],
			[0.0, c, -s, 0.0],
			[0.0, s, c, 0.0],
			[0.0, 0.0, 0.0, 1.0]
		])

	@staticmethod
	def rotation_y(angle):
		c = math.cos(angle)
		s = math.sin(angle)

		return Mat4([
			[c, 0.0, s, 0.0],
			[0.0, 1.0, 0.0, 0.0],
			[-s, 0.0, c, 0.0],
			[0.0, 0.0, 0.0, 1.0]
		])

	@staticmethod
	def rotation_z(angle):
		c = math.cos(angle)
		s = math.sin(angle)

		return Mat4([
			[c, -s, 0.0, 0.0],
			[s, c, 0.0, 0.0],
			[0.0, 0.0, 1.0, 0.0],
			[0.0, 0.0, 0.0, 1.0]
		])

	@staticmethod
	def scale(size):
		return Mat4([
			[size.x, 0.0, 0.0, 0.0],
			[0.0, size.y, 0.0, 0.0],
			[0.0, 0.0, size.z, 0.0],
			[0.0, 0.0, 0.0, 1.0]
		])

	@staticmethod
	def perspective(fov_y, aspect_ratio, near, far):
		f = 1.0 / math.tan(fov_y / 2.0)

		return Mat4([
			[f / aspect_ratio, 0.0, 0.0, 0.0],
			[0.0, f, 0.0, 0.0],
			[0.0, 0.0, far / (near - far), (far * near) / (near - far)],
			[0.0, 0.0, -1.0, 0.0]
		])

	@staticmethod
	def look_at(eye, target, up):
		forward = (target - eye).normalize()
		right = forward.cross(up).normalize()
		real_up = right.cross(forward)

		return Mat4([
			[right.x, right.y, right.z, -right.dot(eye)],
			[real_up.x, real_up.y, real_up.z, -real_up.dot(eye)],
			[-forward.x, -forward.y, -forward.z, forward.dot(eye)],
			[0.0, 0.0, 0.0, 1.0]
		])

	def transform_vec3(self, point):
		x = (
				self.values[0][0] * point.x +
				self.values[0][1] * point.y +
				self.values[0][2] * point.z +
				self.values[0][3]
		)

		y = (
				self.values[1][0] * point.x +
				self.values[1][1] * point.y +
				self.values[1][2] * point.z +
				self.values[1][3]
		)

		z = (
				self.values[2][0] * point.x +
				self.values[2][1] * point.y +
				self.values[2][2] * point.z +
				self.values[2][3]
		)

		w = (
				self.values[3][0] * point.x +
				self.values[3][1] * point.y +
				self.values[3][2] * point.z +
				self.values[3][3]
		)

		if w != 0.0:
			x /= w
			y /= w
			z /= w

		return Vec3(x, y, z)

	def to_column_major_floats(self):
		return [
			self.values[0][0],
			self.values[1][0],
			self.values[2][0],
			self.values[3][0],

			self.values[0][1],
			self.values[1][1],
			self.values[2][1],
			self.values[3][1],

			self.values[0][2],
			self.values[1][2],
			self.values[2][2],
			self.values[3][2],

			self.values[0][3],
			self.values[1][3],
			self.values[2][3],
			self.values[3][3],
		]

	def __matmul__(self, other):
		result = [
			[0.0, 0.0, 0.0, 0.0],
			[0.0, 0.0, 0.0, 0.0],
			[0.0, 0.0, 0.0, 0.0],
			[0.0, 0.0, 0.0, 0.0]
		]

		for row in range(4):
			for column in range(4):
				for k in range(4):
					result[row][column] += (
							self.values[row][k] * other.values[k][column]
					)

		return Mat4(result)

	def inverse(self):
		m = self.values

		inv = [0.0] * 16

		inv[0] = (
				m[1][1] * m[2][2] * m[3][3]
				- m[1][1] * m[2][3] * m[3][2]
				- m[2][1] * m[1][2] * m[3][3]
				+ m[2][1] * m[1][3] * m[3][2]
				+ m[3][1] * m[1][2] * m[2][3]
				- m[3][1] * m[1][3] * m[2][2]
		)

		inv[4] = (
				-m[0][1] * m[2][2] * m[3][3]
				+ m[0][1] * m[2][3] * m[3][2]
				+ m[2][1] * m[0][2] * m[3][3]
				- m[2][1] * m[0][3] * m[3][2]
				- m[3][1] * m[0][2] * m[2][3]
				+ m[3][1] * m[0][3] * m[2][2]
		)

		inv[8] = (
				m[0][1] * m[1][2] * m[3][3]
				- m[0][1] * m[1][3] * m[3][2]
				- m[1][1] * m[0][2] * m[3][3]
				+ m[1][1] * m[0][3] * m[3][2]
				+ m[3][1] * m[0][2] * m[1][3]
				- m[3][1] * m[0][3] * m[1][2]
		)

		inv[12] = (
				-m[0][1] * m[1][2] * m[2][3]
				+ m[0][1] * m[1][3] * m[2][2]
				+ m[1][1] * m[0][2] * m[2][3]
				- m[1][1] * m[0][3] * m[2][2]
				- m[2][1] * m[0][2] * m[1][3]
				+ m[2][1] * m[0][3] * m[1][2]
		)

		inv[1] = (
				-m[1][0] * m[2][2] * m[3][3]
				+ m[1][0] * m[2][3] * m[3][2]
				+ m[2][0] * m[1][2] * m[3][3]
				- m[2][0] * m[1][3] * m[3][2]
				- m[3][0] * m[1][2] * m[2][3]
				+ m[3][0] * m[1][3] * m[2][2]
		)

		inv[5] = (
				m[0][0] * m[2][2] * m[3][3]
				- m[0][0] * m[2][3] * m[3][2]
				- m[2][0] * m[0][2] * m[3][3]
				+ m[2][0] * m[0][3] * m[3][2]
				+ m[3][0] * m[0][2] * m[2][3]
				- m[3][0] * m[0][3] * m[2][2]
		)

		inv[9] = (
				-m[0][0] * m[1][2] * m[3][3]
				+ m[0][0] * m[1][3] * m[3][2]
				+ m[1][0] * m[0][2] * m[3][3]
				- m[1][0] * m[0][3] * m[3][2]
				- m[3][0] * m[0][2] * m[1][3]
				+ m[3][0] * m[0][3] * m[1][2]
		)

		inv[13] = (
				m[0][0] * m[1][2] * m[2][3]
				- m[0][0] * m[1][3] * m[2][2]
				- m[1][0] * m[0][2] * m[2][3]
				+ m[1][0] * m[0][3] * m[2][2]
				+ m[2][0] * m[0][2] * m[1][3]
				- m[2][0] * m[0][3] * m[1][2]
		)

		inv[2] = (
				m[1][0] * m[2][1] * m[3][3]
				- m[1][0] * m[2][3] * m[3][1]
				- m[2][0] * m[1][1] * m[3][3]
				+ m[2][0] * m[1][3] * m[3][1]
				+ m[3][0] * m[1][1] * m[2][3]
				- m[3][0] * m[1][3] * m[2][1]
		)

		inv[6] = (
				-m[0][0] * m[2][1] * m[3][3]
				+ m[0][0] * m[2][3] * m[3][1]
				+ m[2][0] * m[0][1] * m[3][3]
				- m[2][0] * m[0][3] * m[3][1]
				- m[3][0] * m[0][1] * m[2][3]
				+ m[3][0] * m[0][3] * m[2][1]
		)

		inv[10] = (
				m[0][0] * m[1][1] * m[3][3]
				- m[0][0] * m[1][3] * m[3][1]
				- m[1][0] * m[0][1] * m[3][3]
				+ m[1][0] * m[0][3] * m[3][1]
				+ m[3][0] * m[0][1] * m[1][3]
				- m[3][0] * m[0][3] * m[1][1]
		)

		inv[14] = (
				-m[0][0] * m[1][1] * m[2][3]
				+ m[0][0] * m[1][3] * m[2][1]
				+ m[1][0] * m[0][1] * m[2][3]
				- m[1][0] * m[0][3] * m[2][1]
				- m[2][0] * m[0][1] * m[1][3]
				+ m[2][0] * m[0][3] * m[1][1]
		)

		inv[3] = (
				-m[1][0] * m[2][1] * m[3][2]
				+ m[1][0] * m[2][2] * m[3][1]
				+ m[2][0] * m[1][1] * m[3][2]
				- m[2][0] * m[1][2] * m[3][1]
				- m[3][0] * m[1][1] * m[2][2]
				+ m[3][0] * m[1][2] * m[2][1]
		)

		inv[7] = (
				m[0][0] * m[2][1] * m[3][2]
				- m[0][0] * m[2][2] * m[3][1]
				- m[2][0] * m[0][1] * m[3][2]
				+ m[2][0] * m[0][2] * m[3][1]
				+ m[3][0] * m[0][1] * m[2][2]
				- m[3][0] * m[0][2] * m[2][1]
		)

		inv[11] = (
				-m[0][0] * m[1][1] * m[3][2]
				+ m[0][0] * m[1][2] * m[3][1]
				+ m[1][0] * m[0][1] * m[3][2]
				- m[1][0] * m[0][2] * m[3][1]
				- m[3][0] * m[0][1] * m[1][2]
				+ m[3][0] * m[0][2] * m[1][1]
		)

		inv[15] = (
				m[0][0] * m[1][1] * m[2][2]
				- m[0][0] * m[1][2] * m[2][1]
				- m[1][0] * m[0][1] * m[2][2]
				+ m[1][0] * m[0][2] * m[2][1]
				+ m[2][0] * m[0][1] * m[1][2]
				- m[2][0] * m[0][2] * m[1][1]
		)

		determinant = (
				m[0][0] * inv[0]
				+ m[0][1] * inv[1]
				+ m[0][2] * inv[2]
				+ m[0][3] * inv[3]
		)

		if determinant == 0:
			raise ValueError("Matrix is not invertible")

		determinant = 1.0 / determinant

		result = [
			[
				inv[row * 4 + column] * determinant
				for column in range(4)
			]
			for row in range(4)
		]

		return Mat4(result)

	def __repr__(self):
		return "\n".join(
			str(row)
			for row in self.values
		)
