import pygame
from copy import deepcopy
from Classes import camera, shapes, colliders
from Functions import Geometry, Projecting, Linalg, Angles, SimpleLinAlg
from math import pi, copysign

def sign(x) -> int:
    if x < 0:
        return -1
    elif x > 0:
        return 1
    return 0

def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min

def point_box_collide(point: tuple, box: colliders.BoxCollider) -> bool:
    if box.min_x < point[0] < box.max_x and box.min_y < point[1] < box.max_y and box.min_z < point[2] < box.max_z:
        return True
    return False

def box_box_collide(box1: colliders.BoxCollider, box2: colliders.BoxCollider) -> bool:
    return interval_collide(box1.min_x, box2.min_x, box1.max_x, box2.max_x) and interval_collide(box1.min_y, box2.min_y, box1.max_y, box2.max_y) and interval_collide(box1.min_z, box2.min_z, box1.max_z, box2.max_z)

def interval_collide(minx1, minx2, maxx1, maxx2) -> bool:
    return minx1 < maxx2 and maxx1 > minx2

# Camera setup
camera_pos: tuple = (0, 0, 0)
fov = pi/2 # 90 deg
focal_length: float = 0.000001 # As small as possible

# Player hitbox
BOXHEIGHT = 2
BOXWIDTH = 0.5
small_move = 0.001 # Amount to try to push out of colliding blocks

my_camera: camera.Camera = camera.Camera(camera_pos, focal_length, fov, BOXHEIGHT, BOXWIDTH, small_move)

SPEED: float = 3

view_matrix = SimpleLinAlg.getMatrixInverse(my_camera.translation_matrix)

# PYGAME
pygame.init()
FPS = 1000
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
freecam = False
gravity = 0
y_velocity = 0

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
                if SimpleLinAlg.dotProd(SimpleLinAlg.four_to_three_dim(deepcopy(view_space_triangle.center_coord)), SimpleLinAlg.get_plane_normal(deepcopy(view_space_triangle.points))) < 0:
                    visible_view_space_triangles.append(view_space_triangle)

    # Get triangles sorted by distance to the camera
    final_view_space_triangles: dict[shapes.Triangle, float] = Geometry.get_view_triangles_by_distance(visible_view_space_triangles)

    for triangle in final_view_space_triangles:
        # Lighting
        # Get normal
        normal = SimpleLinAlg.get_plane_normal(triangle.points)
        normal.append(0)
        
        color = triangle.color
        if lighting:
            # Convert light dir from view space into world space

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

    if keys[pygame.K_f]:
        freecam = True
    if keys[pygame.K_g]:
        freecam = False

    if freecam:
        y_velocity = 0
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

    else:
        move_vector: tuple = [0, 0, 0, 1]

        # x axis
        if keys[pygame.K_a] and not keys[pygame.K_d]:
            move_vector[0] = -1
        elif not keys[pygame.K_a] and keys[pygame.K_d]:
            move_vector[0] = 1
            
        # z axis
        if keys[pygame.K_w] and not keys[pygame.K_s]:
            move_vector[2] = 1
        elif not keys[pygame.K_w] and keys[pygame.K_s]:
            move_vector[2] = -1
        
        if not (move_vector[0] == 0 and move_vector[1] == 0 and move_vector[2] == 0): # If moving
            move_vector = SimpleLinAlg.normalize_vector(move_vector)
            move_vector = [x * SPEED * delta_time for x in move_vector]
            
            # Rotate
            move_vector = Angles.rotate_yaw(move_vector, -my_camera.yaw)

            move_vector = [move_vector[0], move_vector[1], move_vector[2]]

            my_camera.move(move_vector)
            
            # Check collision
            # FIXME the axis by axis approach doesn't work
            # for object in objects:
            #     if type(object) == shapes.Cube:
            #         # Check each axis
            #         my_camera.move((move_vector[0], 0, 0))
            #         colliding = interval_collide(my_camera.collider.min_x, object.collider.min_x, my_camera.collider.max_x, object.collider.max_x)
            #         if colliding:
            #             my_camera.move((-move_vector[0] * my_camera.small_move, 0, 0))
            #             colliding = interval_collide(my_camera.collider.min_x, object.collider.min_x, my_camera.collider.max_x, object.collider.max_x)
                        
            #         my_camera.move((0, move_vector[1], 0))
            #         colliding = interval_collide(my_camera.collider.min_y, object.collider.min_y, my_camera.collider.max_y, object.collider.max_y)
            #         if colliding:
            #             my_camera.move((0, -move_vector[1] * my_camera.small_move, 0))
            #             colliding = interval_collide(my_camera.collider.min_y, object.collider.min_y, my_camera.collider.max_y, object.collider.max_y)
                        
            #         my_camera.move((0, 0, move_vector[2]))
            #         colliding = interval_collide(my_camera.collider.min_z, object.collider.min_z, my_camera.collider.max_z, object.collider.max_z)
            #         while colliding:
            #             my_camera.move((0, 0, -move_vector[2] * my_camera.small_move))
            #             colliding = interval_collide(my_camera.collider.min_z, object.collider.min_z, my_camera.collider.max_z, object.collider.max_z)


                    # colliding = box_box_collide(my_camera.collider, object.collider)
                    # while colliding:
                    #     my_camera.move([-x * small_move for x in move_vector])
                    #     colliding = box_box_collide(my_camera.collider, object.collider)
        
        y_velocity -= gravity * delta_time
        my_camera.move((0, y_velocity * delta_time, 0))
        # Check collision

    # Update
    view_matrix = SimpleLinAlg.getMatrixInverse(my_camera.translation_matrix)
    pygame.display.flip()
    delta_time = clock.tick(FPS) / 1000
    print("---END FRAME---\n")