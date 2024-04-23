from Classes import camera, shapes
from Functions import Angles, SimpleLinAlg

def model_triangle_to_view_space(triangle: shapes.Triangle, view_matrix, camera: camera.Camera) -> shapes.Triangle:
    """
    Converts a triangle object in model space to a triangle object in view space (relative to camera)
    """
    view_space_points: list[list[float]] = [] # Will be filled with the view space points

    for point in triangle.points:
        # Convert to world space
        world_point: list[float] = SimpleLinAlg.vecMatMul(point, triangle.model_matrix) # FIXME

        # Convert to view space
        view_point: list[float] = SimpleLinAlg.vecMatMul(world_point, view_matrix)

        # Rotate with the camera
        view_point = Angles.rotate_yaw(view_point, camera.yaw)
        view_point = Angles.rotate_pitch(view_point, camera.pitch)

        view_space_points.append(view_point)
    view_triangle = shapes.Triangle(view_space_points, triangle.color)

    return view_triangle

def point_to_view_space(point, model_matrix, view_matrix, camera: camera.Camera):
    """
    Converts a modelspace point into view space given 2 matrices
    """

    world_point = SimpleLinAlg.matmul(model_matrix, point)
    view_point = SimpleLinAlg.matmul(view_matrix, world_point)

    view_point = Angles.rotate_yaw(view_point, camera.yaw)
    view_point = Angles.rotate_pitch(view_point, camera.pitch)
    
    return view_point

def project(point: list[float], camera: camera.Camera, width, height) -> tuple[float]:
    """
    Projects a 3 or 4 by 1 point onto a screen with a given width.
    First projects the point onto the front clipping plane.
    Then scales that to the screen width and height.
    Then moves it onto the screen (0, 0 to 600, -600) while invereting the y axis.
    """
    # Project points onto the front clipping plane plane
    x_proj = (camera.focal_length * point[0])/(point[2])
    y_proj = (camera.focal_length * point[1])/(point[2])

    # Scale to cover screen
    x_proj *= width/camera.near_clipping_height
    y_proj *= -height/camera.near_clipping_height

    # Center to screen
    x_proj += width/2
    y_proj += width/2

    return (x_proj, y_proj)