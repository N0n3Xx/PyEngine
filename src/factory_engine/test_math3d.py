# test_math3d.py

import math

from math3d import Vec3, Mat4


def assert_close(a, b, epsilon=0.000001):
    assert abs(a - b) < epsilon, f"{a} != {b}"


def assert_vec3_close(a, b, epsilon=0.000001):
    assert_close(a.x, b.x, epsilon)
    assert_close(a.y, b.y, epsilon)
    assert_close(a.z, b.z, epsilon)


# --------------------------------------------------
# 1. Vector normalization
# --------------------------------------------------

v = Vec3(3, 0, 4)

normalized = v.normalize()

assert_close(normalized.length(), 1.0)

print("✓ Vector normalization")


# --------------------------------------------------
# 2. Cross product / camera directions
# --------------------------------------------------

forward = Vec3(0, 0, -1)
up = Vec3(0, 1, 0)

right = forward.cross(up)

assert_vec3_close(
    right,
    Vec3(1, 0, 0)
)

# With our convention:
# up × right = forward

calculated_forward = up.cross(right)

assert_vec3_close(
    calculated_forward,
    forward
)

print("✓ Cross product / camera directions")


# --------------------------------------------------
# 3. Identity matrix
# --------------------------------------------------

identity = Mat4.identity()

point = Vec3(5, 7, 11)

# We'll need transform_vec3() for this test.
# For now, this is the function we want Mat4 to have.

result = identity.transform_vec3(point)

assert_vec3_close(
    result,
    point
)

print("✓ Identity matrix")


# --------------------------------------------------
# 4. Translation
# --------------------------------------------------

position = Vec3(10, 20, 30)

translation = Mat4.translation(position)

origin = Vec3(0, 0, 0)

result = translation.transform_vec3(origin)

assert_vec3_close(
    result,
    position
)

print("✓ Translation")

# --------------------------------------------------
# 5. Full projection
# --------------------------------------------------

model = Mat4.identity()

view = Mat4.look_at(
    Vec3(0, 0, 0),
    Vec3(0, 0, -1),
    Vec3(0, 1, 0)
)

projection = Mat4.perspective(
    math.radians(70),
    16 / 9,
    0.1,
    100.0
)

transform = projection @ view @ model

point = Vec3(0, 0, -5)

projected = transform.transform_vec3(point)

print("Projected:", projected)

assert -1.0 <= projected.x <= 1.0
assert -1.0 <= projected.y <= 1.0
assert -1.0 <= projected.z <= 1.0

print("✓ Point successfully projected")

