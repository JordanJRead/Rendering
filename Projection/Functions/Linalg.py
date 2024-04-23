from Functions import SimpleLinAlg
from Functions import Geometry
from Functions import Angles
from Classes import camera

def is_triangle_visible(triangle_points: list[list], camera):
    """Given a triangle's points in view space, returns whether or not the triangle is visible"""
    lines = []
    lines.append([triangle_points[0], triangle_points[1]])
    lines.append([triangle_points[1], triangle_points[2]])
    lines.append([triangle_points[2], triangle_points[0]])

    return are_points_in_frustum(triangle_points, camera) or do_lines_intersect(lines, camera) # Giving True when triangle is outside F I X M E??

def are_points_in_frustum(points, camera):
    """
    Given a triangle, this will return whether any of the triangle's points are within the frusum
    """
    for point in points:
        if is_point_in_frustum(point, camera):
            return True
    return False

def is_point_in_frustum(point: list[float], camera: camera.Camera) -> bool:
    """
    Returns whether or not a viewspace point is within the view frustum
    """
    # Makes sure that a point is in front of all the plane's normals
    # Plane's normals point inward

    # Convert to 3x1 point
    point = [point[0], point[1], point[2]]

    for plane in camera.planes:
        if not SimpleLinAlg.is_point_infront_of_plane(plane, point):
            return False
    return True

def do_lines_intersect(lines, camera: camera.Camera):
    """
    Returns whether or not a bunch of line segments intersect the camera frustum
    """
    for line in lines:
        for plane in camera.planes:

            # Get the line's intersection points with the current plane
            does_intersect, intersection_point = line_seg_plane_intersect_info(line, plane)

            if does_intersect and is_point_in_frustum(intersection_point, camera):
                return True
    return False

def order_points(points):
    """Given a list of points on a convex polygon in 3d space, returns the points ordered"""
    points = SimpleLinAlg.four_to_three_dim_list(points)

    # Get the two fixed points to compare against
    center_point = SimpleLinAlg.mean_of_points(points)
    top_point = points[0]
    top_vector = SimpleLinAlg.vecSub(top_point, center_point)

    # Get all points' angles
    # Take the dot product of the vector of (centroid to first point) against (centroid to current point)
    point_angles = []
    for point in points:
        #angle = Angles.angle_from_3_points([top_point, center_point, point])
        #point_angles.append([point, angle])
        v = SimpleLinAlg.vecSub(point, center_point)
        dot = SimpleLinAlg.dotProd(top_vector, v)
        point_angles.append([point, dot])

    # Sort and get the points
    point_angles.sort(key=lambda x: x[1]) # Sorts by angle
    points = []
    for point_angle in point_angles:
        points.append(point_angle[0])

    return points
    
# def new_clip_triangle(triangle_points: list[list[float]], camera: camera.Camera) -> list[list[float]]:
#     """Takes a triangle and clips it to the view frustum using the Sutherland-Hodgeman triangle clipping algorithm"""
#     output_points = triangle_points

#     # Clip against each plane
#     for plane in camera.planes:
#         input_points = Angles.convex_hull(output_points)
#         output_points = []

#         # Get lines
#         lines = []
#         for i in range(len(input_points)):
#             lines.append([input_points[i], input_points[(i + 1) % len(input_points)]])

#         for line in lines:
#             for point in line:
#                 # Don't clip points that are already in

#                 # Check if point is in list already
#                 is_in_list = False
#                 for clipped_point in clipped_points:
#                     if SimpleLinAlg.four_to_three_dim(clipped_point) == SimpleLinAlg.four_to_three_dim(point):
#                         is_in_list = True
#                         break

#                 if SimpleLinAlg.is_point_infront_of_plane(plane, point) and not is_in_list:
#                     clipped_points.append(point)

#             # Line intersections
#             intersection_point = SimpleLinAlg.get_line_plane_intersect_point(line, plane[0], SimpleLinAlg.get_plane_normal(plane))
#             if type(intersection_point) != type(None):
#                 clipped_points.append(intersection_point)
#     return points

def clip_triangle(triangle_points: list[list[float]], camera: camera.Camera) -> list[list[float]]:
    """Takes a triangle and clips it to the view frustum using the Sutherland-Hodgeman triangle clipping algorithm. Returns None if there was a problem"""
    output_points = triangle_points

    # Clip against each plane
    for plane in camera.planes:
        if len(output_points) == 0:
             return None
        input_points = Angles.convex_hull(output_points)
        output_points = []

        for i in range(len(input_points)):
            current_point = input_points[i]
            prev_point = input_points[(i - 1) % len(input_points)]

            intersection = SimpleLinAlg.get_line_plane_intersect_point([prev_point, current_point], plane[0], SimpleLinAlg.get_plane_normal(plane))

            if (SimpleLinAlg.is_point_infront_of_plane(plane, current_point)):
                if (not SimpleLinAlg.is_point_infront_of_plane(plane, prev_point)):
                    output_points.append(intersection)
                output_points.append(current_point)
            elif (SimpleLinAlg.is_point_infront_of_plane(plane, prev_point)):
                output_points.append(intersection)

    return output_points

# def clip_triangle(triangle_points: list[list[float]], camera: camera.Camera) -> list[list[float]]:
#     # get lines
#     line_1 = [triangle_points[0], triangle_points[1]]
#     line_2 = [triangle_points[1], triangle_points[2]]
#     line_3 = [triangle_points[2], triangle_points[0]]
#     lines = [line_1, line_2, line_3]

#     insidePoints = 0

#     # If triangle doesn't need to be clipped
#     if not do_lines_intersect(lines, camera):
#         return triangle_points
    
#     # Don't clip points that are already inside
#     for point in triangle_points:
#         if is_point_in_frustum(point, camera):
#             insidePoints += 1

#     final_points: list[list[float]] = []
#     clipped_to_planes = []

#     for line in lines:

#         # Intersections with the frustum for each line
#         line_plane_intersections = line_seg_frustum_intersections(line, camera)

#         # For every point/plane intersection
#         for line_plane_intersection in line_plane_intersections:
#             final_points.append(line_plane_intersection[0])

#             # Log a new plane being clipped to
#             if not line_plane_intersection[1] in clipped_to_planes:
#                 clipped_to_planes.append(line_plane_intersection[1])

#         # Already visible points
#         for point in line:
#             if len(final_points) > 0:

#                 # Check for duplicate
#                 is_in_list = False
#                 for final_point in final_points:
#                     if SimpleLinAlg.four_to_three_dim(final_point) == SimpleLinAlg.four_to_three_dim(point):
#                         is_in_list = True
#                         break

#                 if is_point_in_frustum(point, camera) and not is_in_list:
#                     final_points.append(point)

#     # Corner filling
#     if len(final_points) - insidePoints == 2 and len(clipped_to_planes) == 2: # If there are exactly 2 final points on the frustum AND they are on different planes
#         final_points.append(get_frustum_plane_intersection(clipped_to_planes[0], clipped_to_planes[1], camera))
#         #final_points.append(SimpleLinAlg.intersect_planes(SimpleLinAlg.get_plane_normal(clipped_to_planes[0]), SimpleLinAlg.get_plane_normal(clipped_to_planes[1])))

#     return order_points(final_points)

# def get_frustum_plane_intersection(plane_1, plane_2, camera):
#     """Given 2 different frustum planes, returns the point that lies on both"""
#     p1 = Plane(plane_1[0], SimpleLinAlg.get_plane_normal(plane_1))
#     p2 = Plane(plane_2[0], SimpleLinAlg.get_plane_normal(plane_2))

#     intersection: Line = p1.intersect_plane(p2)
#     return intersection.to_point()

def find_smallest_distance(point_1, points_and_planes):
    """
    Given a point and list of points and planes, return the closest point and its plane
    """
    closest_point_and_plane = points_and_planes[0]
    for intersect_point_and_plane in points_and_planes:
        # Compare and change closest point and plane
        if Geometry.distance_3d(point_1, intersect_point_and_plane[0]) < Geometry.distance_3d(point_1, closest_point_and_plane[0]):
            closest_point_and_plane = intersect_point_and_plane
    return closest_point_and_plane

def line_seg_frustum_intersections(line_seg: list[list[int]], camera: camera.Camera):
    """
    Given the start and end points on a line segment, returns all the intersection points and planes of the segment for all planes on the frustum
    """
    found_points_and_planes = []

    # Check line against each plane
    for plane in camera.planes:
        # Get whether the segment intersects and the intersection point
        does_intersect, intersect_point = line_seg_plane_intersect_info(line_seg, plane)

        if does_intersect and is_point_in_frustum(intersect_point, camera):
            found_points_and_planes.append([intersect_point, plane])
    return found_points_and_planes

def line_seg_plane_intersect_info(line: list[list[float]], plane: list[list[float]]) -> list:
    """
    Returns a list of [bool, list].
    The first one is whether or not the line segment intersects a plane.
    The second one is the intersect point, None if the ENTIRE line doesn't intersect the plane, but otherwise it gives the intersect point of if the line went on forever
    Works by finding the line plane intersection, then seeing if that point lies on the line segment as well
    """

    # Get the plane information
    plane_normal = SimpleLinAlg.get_plane_normal(plane)
    plane_point = plane[0]

    # Get where the line intersects the plane
    intersect_point = SimpleLinAlg.get_line_plane_intersect_point(line, plane_point, plane_normal)

    if type(intersect_point) == type(None): # If there is no intersection
        return [False, None]
    else:
        is_point_on_line_seg = Geometry.is_point_on_line_segment(intersect_point, line)
        return [is_point_on_line_seg, intersect_point]
    
def camera_plane_to_name(plane: list[list], my_camera: camera.Camera) -> str:
    """
    Given a plane, it will return the name of it
    """
    if plane == [
            [0, 0, my_camera.focal_length],
            [10, 0, my_camera.focal_length],
            [0, 10, my_camera.focal_length]
        ]:
            return "near_clipping_plane"
    
    if plane == [
            [0, 0, 0],
            [-my_camera.near_clipping_height/2, 10, my_camera.focal_length],
            [-my_camera.near_clipping_height/2, -10, my_camera.focal_length]
        ]:
            return "left_clipping_plane"
    
    if plane == [[0, 0, 0], [my_camera.near_clipping_height/2, -10, my_camera.focal_length], [my_camera.near_clipping_height/2, 10, my_camera.focal_length]]:
            return "right_clipping_plane"
    
    if plane == [
            [0, 0, 0],
            [10, my_camera.near_clipping_height/2, my_camera.focal_length],
            [-10, my_camera.near_clipping_height/2, my_camera.focal_length]
        ]:
            return "top_clipping_plane"
    
    if plane == [
            [0, 0, my_camera.focal_length],
            [10, 0, my_camera.focal_length],
            [0, 10, my_camera.focal_length]
        ]:
            return "near_clipping_plane"
    if plane == [
            [0, 0, 0],
            [-10, -my_camera.near_clipping_height/2, my_camera.focal_length],
            [10, -my_camera.near_clipping_height/2, my_camera.focal_length]
        ]:
        return "bottom_clipping_plane"
    return "none"