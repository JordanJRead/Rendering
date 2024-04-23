import math
from Classes import shapes
from Functions import SimpleLinAlg

def get_centroid(triangle: list[float]) -> list[float]:
    """Given a list of 3 points, returns the mean of its coordinates"""
    average_x = (triangle[0][0] + triangle[1][0] + triangle[2][0]) / 3
    average_y = (triangle[0][1] + triangle[1][1] + triangle[2][1]) / 3
    average_z = (triangle[0][2] + triangle[1][2] + triangle[2][2]) / 3
    return [average_x, average_y, average_z]

def get_points_by_distance(objects: list[shapes.Object], view_matrix):
    """
    Given a list of objects, returns a list of their triangles in order of farthest to closest
    """
    triangle_distances = {} # Every triangle to be drawn this frame + their distances
    for object in objects: 
        for triangle in object.triangles: # triangle is a shapes.Triangle
            # Get the distances from each triangle's centroid to the camera in a dictionary with the triangle as the key and distance as the value

            # Convert centroid to world space then view space
            world_centroid = SimpleLinAlg.matmul(object.model_matrix, triangle.center_coord)
            view_centroid = SimpleLinAlg.matmul(view_matrix, world_centroid)

            # Find distance and add it to the dict
            triangle_distances[triangle] = distance_3d((0, 0, 0), view_centroid)

    # Sort from farthest to closest
    triangle_list = sorted(triangle_distances.items(), key=lambda x:x[1]) # Closest to farthest
    sorted_distances = reversed(dict(triangle_list)) # Reverse

    return sorted_distances

def get_view_triangles_by_distance(triangles: list[shapes.Triangle]) -> dict[shapes.Triangle, float]:
    """Given a list of triangles (triangle objects) in view space, returns them in order of farthest to closest"""
    triangle_distances: dict[shapes.Triangle, float] = {} # Triangle: distance
    for triangle in triangles:
        centroid: list[float] = get_centroid(triangle.points)

        # Add its distance to the dict
        triangle_distances[triangle] = distance_3d((0, 0, 0), centroid)
    
    # Sort
    triangle_list = sorted(triangle_distances.items(), key=lambda x:x[1]) # Closest to farthest
    sorted_distances = reversed(dict(triangle_list)) # Reverse

    return sorted_distances


def distance_3d(point_1: list[int], point_2: list[int]):
    """
    Given 2 points with dimensions 3/4 x 1, returns the distance between them.
    """
    distance = math.sqrt( (point_2[0] - point_1[0])**2 + (point_2[1] - point_1[1])**2 + (point_2[2] - point_1[2])**2 )
    return distance

def is_point_on_line_segment(point: list[float], line: list[list[float]]):
    """
    Given a 3x1 point and a line (2 3x1 points), gives a bool of whether that point lies on the line.
    Works by getting the length of AB (the line), and checks if AP + BP equal it.
    NOW it accounts for floating point error
    """
    a = line[0] # 0
    b = line[1] # 2
    #p = # 2
    # ----------
    # 0  1  2  3
    # a     b
    #       p  
    ab = distance_3d(b, a) # 2
    ap = distance_3d(point, a) # 2
    pb = distance_3d(b, point) # 0

    return math.isclose(ab, ap + pb)