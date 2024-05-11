class BoxCollider:
    def __init__(self, world_pos: tuple, scale: tuple = (1, 1, 1)) -> None:
        x_width = scale[0]
        self.min_x = world_pos[0] - x_width / 2
        self.max_x = world_pos[0] + x_width / 2
        
        y_width = scale[1]
        self.min_y = world_pos[1] - y_width / 2
        self.max_y = world_pos[1] + y_width / 2
        
        z_width = scale[2]
        self.min_z = world_pos[2] - z_width / 2
        self.max_z = world_pos[2] + z_width / 2