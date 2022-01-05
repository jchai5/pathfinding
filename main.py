from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import pygame, sys

class Pathfinder:
    def __init__(self, matrix):
        self.matrix = matrix
        self.grid = Grid(matrix = matrix)
        # for pathfinding
        self.path = []

        # roomba
        self.roomba = pygame.sprite.GroupSingle(Roomba(self.empty_path))

    def empty_path(self):
        self.path = []

    def create_path(self):
        """
        Creates a path from current pos to mouse click
        """
        # start
        start_x, start_y = self.roomba.sprite.get_coord()
        start = self.grid.node(start_x, start_y)

        # end
        mouse_pos = pygame.mouse.get_pos()
        end_x = mouse_pos[0] // 32 
        end_y = mouse_pos[1] // 32 
        end = self.grid.node(end_x, end_y)

        # path
        finder = AStarFinder(diagonal_movement= DiagonalMovement.always) # always move diagonal direction
        self.path,_ = finder.find_path(start, end, self.grid) # this returns the path and the runs
        self.grid.cleanup() # reset the path after a path has been given
        self.roomba.sprite.set_path(self.path) # pass the path to the roomba

    def draw_active_cell(self):
        """
        Display where the mouse is
        """
        mouse_pos = pygame.mouse.get_pos()
        row = mouse_pos[1] // 32 # 32 is the tile(pixel) size
        col = mouse_pos[0] // 32 
        current_cell_val = self.matrix[row][col]
        if current_cell_val == 1:
            # only able to move on '1'
            rect = pygame.Rect((col * 32, row * 32 ), (32, 32)) # (left, top), (width, height)

    def update(self):
        """
        Update the screen 
        """
        self.draw_active_cell()
        self.draw_path()

        # roomba updating and drawing
        self.roomba.update()
        self.roomba.draw(screen)

    def draw_path(self):
        """
        Draw the path on the screen
        """
        if self.path: # if path list is not empty
            points = []
            for point in self.path:
                # +16 so the line points to the middle of the cursor
                x = (point[0] * 32) + 16 # row
                y = (point[1] * 32) + 16 # col
                points.append((x, y))
                # round the corner of the line
                pygame.draw.circle(screen, "red", (x, y), 3)
            
            # (screen, color, if lines are closed or open, grid points, line weight)
            pygame.draw.lines(screen, "red", False, points, 3)


class Roomba(pygame.sprite.Sprite): # we are creating a sprite
    def __init__(self, empty_path):
        super().__init__()
        self.image = pygame.image.load("./pathfinding/assets/robot.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100)) 
        self.rect = self.image.get_rect(center = (160,160)) # 60,60 doesnt really matter that much

        # movement
        self.pos = self.rect.center
        self.speed = 3
        self.direction = pygame.math.Vector2(0,0)

        # path
        self.path = []
        self.collision_rects = []
        self.empty_path = empty_path

    def get_coord(self):
        col = self.rect.centerx // 32
        row = self.rect.centery // 32
        return (col, row)

    def set_path(self, path):
        self.path = path
        self.create_collision_rects()
        self.get_direction()

    def create_collision_rects(self):
        if self.path:
            self.collision_rects = []
            for point in self.path:
                x = (point[0] * 32) + 16
                y = (point[1] * 32) + 16
                rect = pygame.Rect((x - 2, y - 2), (4, 4)) # rect is 4x4 pixels, -2 so we offset the rect to middle
                self.collision_rects.append(rect)

    def get_direction(self):
        if self.collision_rects:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collision_rects[0].center) # first collision rectangle
            self.direction = (end - start).normalize() # start and end are vectors so need to normalize
        else:
            # if no more collision rectangles (end of path)
            self.direction = pygame.math.Vector2(0,0) # no movement
            self.path = []

    def update(self):
        self.pos += self.direction * self.speed
        self.check_coliisions()
        self.rect.center = self.pos

    def check_coliisions(self):
        if self.collision_rects:
            for rect in self.collision_rects:
                if rect.collidepoint(self.pos):
                    # if self.pos is in rect
                    del self.collision_rects[0] # delete the point that is collided
                    self.get_direction()


#pygame setup
pygame.init()
screen = pygame.display.set_mode((1184, 832)) # dimensions (pixels) of the map image
clock = pygame.time.Clock()

#game setup
bg_surf = pygame.image.load('./pathfinding/assets/map2.jpg').convert()
matrix = [
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,0,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,0,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,1,0,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,1,1,1,1,0,0],
    [0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ]
pathfinder = Pathfinder(matrix)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # create path whenever use clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            pathfinder.create_path()

    screen.blit(bg_surf, (0,0))
    pathfinder.update()

    pygame.display.update()
    clock.tick(60)