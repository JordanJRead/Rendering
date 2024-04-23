import math
from math import sin, cos, tan, pi
from Functions import SimpleLinAlg

def convex_hull(points: list[list[float]]) -> list[list[float]]:
    """
    Given a set of 2d points, returns the convex hull points
    Taken from https://lvngd.com/blog/convex-hull-graham-scan-algorithm-python/
    """
    hull = []
    points.sort(key=lambda x:[x[0],x[1]])
    start = points.pop(0)
    hull.append(start)
    points.sort(key=lambda p: (get_slope(p, start), -p[1],p[0]))
    for point in points:
        hull.append(point)
        while len(hull) > 2 and cross_product_3(hull[-3], hull[-2], hull[-1]) <0:
            hull.pop(-2)
    return hull

def cross_product_3(p1, p2, p3):
    return ((p2[0] - p1[0])*(p3[1] - p1[1])) - ((p2[1] - p1[1])*(p3[0] - p1[0]))

def get_slope(p1, p2):
    if p1[0] == p2[0]:
        return float('inf')
    else:
        return 1.0*(p1[1]-p2[1])/(p1[0]-p2[0])

def rotate_pitch(point: tuple, pitch: float) -> tuple:
    """
    Takes in a 3 / 4 by 1 point and a pitch ange (nodding head).
    Rotates the point by that angle around the origin.
    Returns that point as a 4x1 coordinate.
    """
    y = point[1]
    z = point[2]
    rotated_y = y * cos(pitch) - z * sin(pitch)
    rotated_z = y * sin(pitch) + z * cos(pitch)
    return (point[0], rotated_y, rotated_z, 1)

def rotate_yaw(point: tuple, yaw: float) -> tuple:
    """
    Takes in a 3 / 4 by 1 point and a yaw angle (shaking head).
    Rotates the point by that angle around the origin.
    Returns that point as a 4x1 coordinate.
    """
    x = point[0]
    z = point[2]
    rotated_x = x * cos(yaw) - z * sin(yaw)
    rotated_z = x * sin(yaw) + z * cos(yaw)
    return (rotated_x, point[1], rotated_z, 1)

def find_movement(yaw: float, speed: float) -> tuple[float]:
    """
    Given a yaw, this finds the vector3 of a line with a magnitude of speed pointing in the given angle.
    Only deals with the x-z coordinates.
    """
    A = pi/2 - yaw
    if A != 0:
        x_movement = ( (1/tan(A)) * speed * sin(A))
        z_movement = (speed * sin(A))
    else:
        x_movement = speed
        z_movement = 0
    return (x_movement, 0, z_movement)

def angle_from_3_points(points):
    """In rad from https://stackoverflow.com/questions/19729831/angle-between-3-points-in-3d-space"""
    a = SimpleLinAlg.four_to_three_dim(points[0])
    b = SimpleLinAlg.four_to_three_dim(points[1])
    c = SimpleLinAlg.four_to_three_dim(points[2])

    # Get vectors
    v1 = SimpleLinAlg.vecSub(a, b)
    v2 = SimpleLinAlg.vecSub(c, b)

    return math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])