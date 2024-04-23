import pygame
from copy import deepcopy
from Classes import camera, shapes
from Functions import Geometry, Projecting, Linalg, Angles, SimpleLinAlg
from math import pi, copysign
from numpy.linalg import inv

#TODO dont use np

def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min

# Camera setup
camera_pos: tuple = (0, 0, 0)
fov = pi/2 # 90 deg
focal_length: float = 0.000001 # As small as possible
my_camera: camera.Camera = camera.Camera(camera_pos, focal_length, fov)

SPEED: float = 3

view_matrix = inv(my_camera.translation_matrix)

# PYGAME
pygame.init()
FPS = 60
WIDTH, HEIGHT = 600, 600
screen: pygame.Surface = pygame.display.set_mode((WIDTH + 100, HEIGHT + 100))
clock: pygame.time.Clock = pygame.time.Clock()

# Colors
WHITE: tuple = (255, 255, 255)
BLACK: tuple = (0, 0, 0)
RED: tuple = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

lighting = True
light_dir = [0, -0.5, 1, 0]
light_dir = SimpleLinAlg.normalize_vector(light_dir)
ambient_light = 0.3

## OBJECTS ##
objects: list[shapes.Object] = []

#objects.append(shapes.Triangle_Object())
objects.append(shapes.Cube(world_pos=(0, 0, 0), color=GREEN, scale=(3, 1, 3)))

objects.append(shapes.Cube(world_pos=(0, 1, 0), color=(150, 75, 0), faces={"bottom": False, "top": False}))
objects.append(shapes.Cube(world_pos=(0, 2, 0), color=(150, 75, 0), faces={"bottom": False, "top": False}))
objects.append(shapes.Cube(world_pos=(0, 3, 0), color=(150, 75, 0), faces={"bottom": False}))

# Mouse pos setup
prev_mouse_x: tuple[int, int] = pygame.mouse.get_pos()[0]
prev_mouse_y: tuple[int, int] = pygame.mouse.get_pos()[1]
delta_time = 0
while True:
    print("---START FRAME---")
    print(clock.get_fps())
    screen.fill(BLACK)

    ### Mouse ###

    # Difference
    mouse_pos = pygame.mouse.get_pos()

    delta_mouse_x = mouse_pos[0] - prev_mouse_x
    delta_mouse_y = mouse_pos[1] - prev_mouse_y

    prev_mouse_x = mouse_pos[0]
    prev_mouse_y = mouse_pos[1]

    # Keep mouse from moving off screen
    if not (WIDTH/4 < mouse_pos[0] < 3 * (WIDTH/4)):
        pygame.mouse.set_pos(WIDTH/2, HEIGHT/2)
    if not (HEIGHT/4 < mouse_pos[1] < 3 * (HEIGHT/4)):
        pygame.mouse.set_pos(WIDTH/2, HEIGHT/2)

    mouse_pos = pygame.mouse.get_pos()
    prev_mouse_x = mouse_pos[0]
    prev_mouse_y = mouse_pos[1]

    # Rotation
    my_camera.yaw += delta_mouse_x * 0.01
    my_camera.pitch -= delta_mouse_y * 0.01

    # Keep mouse from going too high up
    if abs(my_camera.pitch) > pi/2:
        my_camera.pitch = pi/2 * copysign(1, my_camera.pitch)
    
    # Event handler
    for event in pygame.event.get():
        # Quitting
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()
    
    # Get visible triangles
    visible_view_space_triangles: list[shapes.Triangle] = []
    for object in objects:
        for triangle in object.triangles:
            view_space_triangle: shapes.Triangle = Projecting.model_triangle_to_view_space(triangle, view_matrix, my_camera)
            if Linalg.is_triangle_visible(view_space_triangle.points, my_camera):
                # Back-face culling
                visible_view_space_triangles.append(view_space_triangle)
                # if np.dot(SimpleLinAlg.four_to_three_dim(deepcopy(view_space_triangle.center_coord)), SimpleLinAlg.get_plane_normal(deepcopy(view_space_triangle.points))) < 0:
                #     visible_view_space_triangles.append(view_space_triangle)

    # Get triangles sorted by distance to the camera
    final_view_space_triangles: dict[shapes.Triangle, float] = Geometry.get_view_triangles_by_distance(visible_view_space_triangles)

    for triangle in final_view_space_triangles:
        # Lighting
        # Get normal
        normal = SimpleLinAlg.get_plane_normal(triangle.points)
        normal.append(0)
        
        color = triangle.color
        if lighting:
            # Convert light dir to view spacefrom view space into world space

            world_space_light_dir = SimpleLinAlg.vecMatMul(light_dir, view_matrix)
            # Rotate
            world_space_light_dir = Angles.rotate_yaw(light_dir, my_camera.yaw)
            world_space_light_dir = Angles.rotate_pitch(world_space_light_dir, my_camera.pitch)

            alignment = -1 * SimpleLinAlg.dotProd(normal, world_space_light_dir)
            alignment = remap(alignment, -1, 1, 0, 1)
            if alignment + ambient_light > 1:
                ambient_light = 1 - alignment
            color = [x * (alignment + ambient_light) for x in triangle.color]

        # Clip the points
        clipped_points = Linalg.clip_triangle(deepcopy(triangle.points), my_camera)
        if type(clipped_points) != type(None):

            # Project the points
            projected_points = []
            for clipped_point in clipped_points:
                projected_points.append(Projecting.project(clipped_point, my_camera, WIDTH, HEIGHT))

            if len(projected_points) > 2:
                # Order points
                projected_points = Angles.convex_hull(projected_points)
                
                # Draw polygon
                pygame.draw.polygon(screen, color, projected_points)

                # Draw border of polygons
                # for i in range(len(projected_points)):
                #     pygame.draw.line(screen, RED, projected_points[i], projected_points[(i + 1) % len(projected_points)], 1)

            # Screen border for debuging
            pygame.draw.line(screen, WHITE, (0, 0), (WIDTH, 0))
            pygame.draw.line(screen, WHITE, (WIDTH, 0), (WIDTH, HEIGHT))
            pygame.draw.line(screen, WHITE, (WIDTH, HEIGHT), (0, HEIGHT))
            pygame.draw.line(screen, WHITE, (0, HEIGHT), (0, 0))

    ### MOVEMENT ###

    # Controls
    keys = pygame.key.get_pressed()

    # Left
    if keys[pygame.K_a]:
        movement = Angles.find_movement(my_camera.yaw + pi/2, SPEED * delta_time)
        neg_movement = [-x for x in movement]
        my_camera.move(neg_movement)
    
    # Right
    if keys[pygame.K_d]:
        my_camera.move(Angles.find_movement(my_camera.yaw + pi/2, SPEED * delta_time))

    # Forward
    if keys[pygame.K_w]:
        my_camera.move(Angles.find_movement(my_camera.yaw, SPEED * delta_time))

    # Backwards
    if keys[pygame.K_s]:
        movement = Angles.find_movement(my_camera.yaw, SPEED * delta_time)
        neg_movement = [-x for x in movement]
        my_camera.move(neg_movement)

    # Up
    if keys[pygame.K_SPACE]:
        my_camera.move((0, SPEED * delta_time, 0))

    # Down
    if keys[pygame.K_LSHIFT]:
        my_camera.move((0, -SPEED * delta_time, 0))
    
    # FPS controls
    if keys[pygame.K_e]:
        FPS = 1

    if keys[pygame.K_r]:
        FPS = 60

    # Update
    view_matrix = inv(my_camera.translation_matrix)
    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000
    print("---END FRAME---\n")