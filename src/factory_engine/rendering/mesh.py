#mesh.py

import struct
import wgpu

class Mesh:
    def __init__(self, vertex_buffer, index_buffer, index_count):
        self.vertex_buffer = vertex_buffer
        self.index_buffer = index_buffer
        self.index_count = index_count

    @staticmethod
    def create(device, vertices, indices):
        vertex_data = struct.pack(
            f"{len(vertices)}f",
            *vertices
        )

        # Pack indices as unsigned 16-bit ints
        index_data = struct.pack(
            f"{len(indices)}H",
            *indices
        )

        vertex_buffer = device.create_buffer_with_data(
            data=vertex_data,
            usage=wgpu.BufferUsage.VERTEX,
        )

        index_buffer = device.create_buffer_with_data(
            data=index_data,
            usage=wgpu.BufferUsage.INDEX,
        )

        return Mesh(
            vertex_buffer=vertex_buffer,
            index_buffer=index_buffer,
            index_count=len(indices)
        )

    @staticmethod
    def create_cube(device):
        # Each vertex contains:
        #
        #   position: 3 × float32
        #   normal:   3 × float32
        #
        # Total: 6 × float32 = 24 bytes per vertex.
        #
        # We use 4 vertices per face so that each face can have
        # its own flat normal.

        vertices = [
            # Bottom (-Y)
            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0, #  0
             0.5, -0.5, -0.5,  0.0, -1.0,  0.0, #  1
             0.5, -0.5,  0.5,  0.0, -1.0,  0.0, #  2
            -0.5, -0.5,  0.5,  0.0, -1.0,  0.0, #  3

            # Top (+Y)
            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0, #  4
             0.5,  0.5, -0.5,  0.0,  1.0,  0.0, #  5
             0.5,  0.5,  0.5,  0.0,  1.0,  0.0, #  6
            -0.5,  0.5,  0.5,  0.0,  1.0,  0.0, #  7

            # Front (+Z)
            -0.5,  0.5,  0.5,  0.0,  0.0,  1.0, #  8
             0.5,  0.5,  0.5,  0.0,  0.0,  1.0, #  9
             0.5, -0.5,  0.5,  0.0,  0.0,  1.0, # 10
            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0, # 11

            # Back (-Z)
            -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, # 12
             0.5,  0.5, -0.5,  0.0,  0.0, -1.0, # 13
             0.5, -0.5, -0.5,  0.0,  0.0, -1.0, # 14
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, # 15

            # Left (-X)
            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0, # 16
            -0.5,  0.5, -0.5, -1.0,  0.0,  0.0, # 17
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0, # 18
            -0.5, -0.5,  0.5, -1.0,  0.0,  0.0, # 19

            # Right (+X)
             0.5,  0.5,  0.5,  1.0,  0.0,  0.0, # 20
             0.5,  0.5, -0.5,  1.0,  0.0,  0.0, # 21
             0.5, -0.5, -0.5,  1.0,  0.0,  0.0, # 22
             0.5, -0.5,  0.5,  1.0,  0.0,  0.0, # 23
        ]

        # Six Faces, 12 Triangles
        indices = [
            # Bottom
             0,  1,  2,
             0,  2,  3,

            # Top
             4,  6,  5,
             4,  7,  6,

            # Front
             8, 10,  9,
             8, 11, 10,

            # Back
            12, 13, 14,
            12, 14, 15,

            # Left
            16, 18, 19,
            16, 17, 18,

            # Right
            20, 22, 21,
            20, 23, 22 
        ]

        return Mesh.create(device, vertices, indices)
