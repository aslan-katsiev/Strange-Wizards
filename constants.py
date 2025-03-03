import pygame

pygame.init()

DIRECTS = [
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1)
]

DIRECTIONS = {
    "up": (0, -5),
    "down": (0, 5),
    "left": (-5, 0),
    "right": (5, 0),
    "up_left": (-5, -5),
    "up_right": (5, -5),
    "down_left": (-5, 5),
    "down_right": (5, 5),
}

vegetation = {
    1: 'env/vegetation/bush.png',
    2: 'env/vegetation/clover.png',
    3: 'env/vegetation/mushroom.png',
    4: 'env/vegetation/rock.png',
    5: 'env/vegetation/small_rock.png'
}

trees = {
    1: 'env/trees/small_tree.png',
    2: 'env/trees/tree.png',
    3: 'env/trees/large_tree.png'
}

paths = {
    1: 'env/paths/path.png',
    2: 'env/paths/large_path.png',
    3: 'env/paths/path2.png',
    4: 'env/paths/broken_path.png'
}

WIDTH, HEIGHT = 1920, 1080
FPS = 60
TILE = 50

bullets = []
objects = []
env = []

window = pygame.display.set_mode((WIDTH, HEIGHT))

fontUI = pygame.font.Font(None, 30)
fontGameOver = pygame.font.Font(None, 70)