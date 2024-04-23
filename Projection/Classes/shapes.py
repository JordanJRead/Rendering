### RIGHT HANDED ###
from Functions import SimpleLinAlg

class Object:
    """
    Class to be inherited from.
    Contains a transform / update_transform function, scale, color, and an init_triangles function to be overwritten
    """
    def __init__(self, world_pos: tuple = (0, 0, 0), scale: tuple = (1, 1, 1), color: tuple = (255, 255, 255)) -> None:
        self.color = color
        self.scale = scale
        self.init_triangles()
        self.update_transform(world_pos, scale)
    
    def init_triangles(self):
        self.triangles: list[Triangle] = []

    def update_transform(self, world_pos: tuple = (0, 0, 0), scale: tuple = (1, 1, 1)):
        """
        Update's an objects matrices gives properties.
        2x2x2 space, z points inwards
        """
        # Model space: right handed, 2x2x2 space
        # Right handed: z points inwards

        self.scale_matrix = [
            [scale[0], 0, 0, 0],
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]
        ]

        self.translation_matrix = [
            [1, 0, 0, world_pos[0]],
            [0, 1, 0, world_pos[1]],
            [0, 0, 1, world_pos[2]],
            [0, 0, 0, 1]
        ]

        self.model_matrix = SimpleLinAlg.matmul(self.translation_matrix, self.scale_matrix)
        for triangle in self.triangles:
            triangle.model_matrix = self.model_matrix
    
    def move(self, move_by: tuple):
        self.translation_matrix[0][3] += move_by[0]
        self.translation_matrix[1][3] += move_by[1]
        self.translation_matrix[2][3] += move_by[2]
        self.model_matrix = SimpleLinAlg.matmul(self.translation_matrix, self.scale_matrix)

class Triangle_Object(Object):
    def __init__(self, world_pos: tuple = (0, 0, 0), scale: tuple = (1, 1, 1), color: tuple = (255, 255, 255)) -> None:
        super().__init__(world_pos, scale, color)
    
    def init_triangles(self):
        self.triangles: list[Triangle] = []

        bottom = -1
        top = 1
        left = -1
        middle = 0
        right = 1

        self.triangles.append(Triangle([[left, bottom, middle, 1], [left, top, middle, 1], [right, bottom, middle, 1]]))

        self.triangles[0].fourth_corner = [right, top, middle, 1]

class Cube(Object):
    def __init__(self, world_pos: tuple = (0, 0, 0), scale: tuple = (1, 1, 1), color: tuple = (255, 255, 255), faces: dict[str, bool] = {"front": True, "right": True, "back": True, "left": True, "top": True, "bottom": True}) -> None:
        default_faces = ["front", "right", "back", "left", "top", "bottom"]
        for face in default_faces:
            if not face in faces.keys():
                faces[face] = True
        self.faces = faces
        super().__init__(world_pos, scale, color)

    def init_triangles(self):
        self.triangles: list[Triangle] = []

        # Constants
        left = -0.5
        right = 0.5
        bottom = -0.5
        top = 0.5
        back = -0.5
        front = 0.5

        if self.faces["front"]:
            # Front face: x, y, front
                # Left bottom triangle
                # 1: left bottom front
                # 2: left top front
                # 3: right bottom front
            self.triangles.append(Triangle(([left, bottom, front, 1], [right, bottom, front, 1], [left, top, front, 1]), self.color))

                # Right top triangle
                # 1: right top front
                # 2: right bottom front
                # 3: left top front
            self.triangles.append(Triangle(([right, top, front, 1], [left, top, front, 1], [right, bottom, front, 1]), self.color))

        if self.faces["top"]:
            # Top face: x, top, z
                # Left top front triangle
                # 1: left top front
                # 2: right top front
                # 3: left top back
            self.triangles.append(Triangle(([left, top, front, 1], [right, top, front, 1], [left, top, back, 1]), self.color))

                # Right top back triangle
                # 1: right top back
                # 2: left top back
                # 3: right top front
            self.triangles.append(Triangle(([right, top, back, 1], [left, top, back, 1], [right, top, front, 1]), self.color))

        if self.faces["back"]:
            # Back face: x, y, back
                # Left top back triangle
                # 1: left top back
                # 2: right top back
                # 3: left bottom back
            self.triangles.append(Triangle(([left, top, back, 1], [right, top, back, 1], [left, bottom, back, 1]), self.color))

                # Right bottom back triangle
                # 1: right bottom back
                # 2: left bottom back
                # 3: right top back
            self.triangles.append(Triangle(([right, bottom, back, 1], [left, bottom, back, 1], [right, top, back, 1]), self.color))
        
        if self.faces["bottom"]:
            # Bottom face: x, bottom, z
                # Left bottom front triangle
                # 1: left bottom front
                # 2: right bottom front
                # 3: left bottom back
            self.triangles.append(Triangle(([left, bottom, front, 1], [left, bottom, back, 1], [right, bottom, front, 1]), self.color))

                # Right bottom back triangle
                # 1: right bottom back
                # 2: left bottom back
                # 3: right bottom front
            self.triangles.append(Triangle(([right, bottom, back, 1], [right, bottom, front, 1], [left, bottom, back, 1]), self.color))

        if self.faces["right"]:
            # Right face: right, y, z
                # Bottom front triangle
                # 1: right bottom front
                # 2: right top front
                # 3: right bottom back
            self.triangles.append(Triangle(([right, bottom, front, 1], [right, bottom, back, 1], [right, top, front, 1]), self.color))

                # Top back triangle
                # 1: right top back
                # 2: right bottom back
                # 3: right top front
            self.triangles.append(Triangle(([right, top, back, 1], [right, top, front, 1], [right, bottom, back, 1]), self.color))
        
        if self.faces["left"]:
            # Left face: left, y, z
                # Bottom front triangle
                # 1: left bottom front
                # 2: left top front
                # 3: left bottom back
            self.triangles.append(Triangle(([left, bottom, front, 1], [left, top, front, 1], [left, bottom, back, 1]), self.color))

                # Top back triangle
                # 1: left top back
                # 2: left bottom back
                # 3: left top front
            self.triangles.append(Triangle(([left, top, back, 1], [left, bottom, back, 1], [left, top, front, 1]), self.color))

        for i in range(len(self.triangles)):
            if i == 11:
                self.triangles[i].fourth_corner = [left, bottom, front, 1]
            else:
                if i % 2 == 0: # If i is even
                    self.triangles[i].fourth_corner = self.triangles[i + 1].points[0]
                else:
                    self.triangles[i].fourth_corner = self.triangles[i - 1].points[0]

class Plane(Object):
    def __init__(self, world_pos: tuple = (0, 0, 0), scale: tuple = (1, 1, 1), color = (0, 0, 255)):
        self.color = color
        self.init_triangles()
        self.update_transform(world_pos, scale)
        self.scale = scale

    def init_triangles(self):
        self.triangles: list[Triangle] = []

        # Constants
        left = -1
        right = 1
        bottom = -1
        top = 1
        #back = -1
        #front = 1
        middle = 0

        # Front bottom left triangle
            # 1: front bottom left
            # 2: front bottom right
            # 3: front top left
        self.triangles.append(Triangle(([left, bottom, middle, 1], [right, bottom, middle, 1], [left, top, middle, 1]), self.color))
        
        # Front top right triangle
            # 1: front top right
            # 2: front top left
            # 3: front bottom right
        self.triangles.append(Triangle(([right, top, middle, 1], [left, top, middle, 1], [right, bottom, middle, 1]), self.color))

        self.triangles[0].fourth_corner = self.triangles[1].points[0]
        self.triangles[1].fourth_corner = self.triangles[0].points[0]

class Triangle:
    """
    To be used in other classes. To make a single triangle object, use the triangle object class
    """
    def __init__(self, verticies: tuple[tuple], color: tuple = (255, 255, 255)) -> None:
        self.color = color
        self.model_matrix = [[
            0
        ]]
        a = verticies[0]
        b = verticies[1]
        c = verticies[2]
        self.points = [a, b, c]
        self.world_points = []
        center_x = (self.points[0][0] + self.points[1][0] + self.points[2][0]) / 3
        center_y = (self.points[0][1] + self.points[1][1] + self.points[2][1]) / 3
        center_z = (self.points[0][2] + self.points[1][2] + self.points[2][2]) / 3
        self.center_coord = (center_x, center_y, center_z, 1)