from typing import Any
from math import tan

class Camera:
    def __init__(self, world_pos: tuple, focal_length: float, fov: float) -> None:
        self.focal_length = focal_length
        self.fov = fov

        # Height (and witdh) of near clipping plane
        self.near_clipping_height = tan(fov/2) * focal_length * 2

        # Defining frustum planes with 3 points on each plane
        # Normals point inward
        # Points are defined as counter-clockwise looking at the frustum
        # If the points are defined counter clockwise (CC), then the normal points in the observer's direction
        self.near_clipping_plane = [
            [0, 0, self.focal_length],
            [10, 0, self.focal_length],
            [0, 10, self.focal_length]
        ]

        self.left_clipping_plane = [
            [0, 0, 0],
            [-self.near_clipping_height/2, 10, self.focal_length],
            [-self.near_clipping_height/2, -10, self.focal_length]
        ]

        self.right_clipping_plane = [
            [0, 0, 0],
            [self.near_clipping_height/2, -10, self.focal_length],
            [self.near_clipping_height/2, 10, self.focal_length]
        ]

        self.top_clipping_plane = [
            [0, 0, 0],
            [10, self.near_clipping_height/2, self.focal_length],
            [-10, self.near_clipping_height/2, self.focal_length]
        ]

        self.bottom_clipping_plane = [
            [0, 0, 0],
            [-10, -self.near_clipping_height/2, self.focal_length],
            [10, -self.near_clipping_height/2, self.focal_length]
        ]

        self.planes = [self.near_clipping_plane,
                       self.left_clipping_plane,
                       self.right_clipping_plane,
                       self.top_clipping_plane,
                       self.bottom_clipping_plane]

        self.pitch = 0
        self.yaw = 0
        self.translation_matrix: list[list] = [
            [1, 0, 0, world_pos[0]],
            [0, 1, 0, world_pos[1]],
            [0, 0, 1, world_pos[2]],
            [0, 0, 0, 1]
        ]
    
    def move(self, move_by: tuple):
        self.translation_matrix[0][3] += move_by[0]
        self.translation_matrix[1][3] += move_by[1]
        self.translation_matrix[2][3] += move_by[2]