#camera.py

import math

from .math3d import Vec3, Mat4

class Camera:
    def __init__(self):
        self.position = Vec3(0, 1.0, 5)
        self.target = Vec3(0, 0, 0)
        self.up = Vec3(0, 1, 0)
        self.fov_y = 60.0
        self.near = 0.1
        self.far = 1000.0

    def view_matrix(self):
        return Mat4.look_at(
            self.position,
            self.target,
            self.up
        )

    def projection_matrix(self, aspect_ratio):
        return Mat4.perspective(
            math.radians(self.fov_y),
            aspect_ratio,
            self.near,
            self.far
        )
