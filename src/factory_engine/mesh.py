#mesh.py

import struct
import wgpu

class Mesh:
    def __init__(self, vertex_buffer, index_buffer, index_count):
        self.vertex_buffer = vertex_buffer
        self.index_buffer = index_buffer
        self.index_count = index_count

    @staticmethod
    def create_cube(device):
        # Eight corners of a unit cube
        # Three float32 values per vertex
        vertices = [
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5,  0.5, -0.5,
            -0.5,  0.5, -0.5,
            
            -0.5, -0.5,  0.5,
             0.5, -0.5,  0.5,
             0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5
        ]

        # Six faces
        indices = [
            # Front
            7, 2, 6,
            7, 3, 2,

            # Back
            5, 0, 4,
            5, 1, 0,

            # Top
            4, 6, 5,
            4, 7, 6,

            # Bottom
            3, 1, 2,
            3, 0, 1,

            # Left
            4, 3, 7,
            4, 0, 3,

            # Right
            6, 1, 5,
            6, 2, 1
        ]

        # Pack positions as float32
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
