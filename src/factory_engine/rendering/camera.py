#camera.py

import math

from factory_engine.math3d import Vec3, Mat4

class Camera:
    def __init__(self):
        self.position = Vec3(0, 1.0, 5)
        self.target = Vec3(0, 0, 0)
        self.up = Vec3(0, 1, 0)
        self.fov_y = 60.0
        self.near = 0.1
        self.far = 1000.0
        
        self.yaw = -90.0
        self.pitch = 0.0

    def look(self, delta_x, delta_y, sensitivity):
        self.yaw += delta_x * sensitivity
        self.pitch -= delta_y * sensitivity

        self.pitch = max(-89.0, min(89.0, self.pitch))

        self.update_target_from_angles()

    def update_target_from_angles(self):
        yaw_radians = math.radians(self.yaw)
        pitch_radians = math.radians(self.pitch)

        forward = Vec3(
            math.cos(yaw_radians) * math.cos(pitch_radians),
            math.sin(pitch_radians),
            math.sin(yaw_radians) * math.cos(pitch_radians)
        ).normalize()

        self.target = self.position + forward
    
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
