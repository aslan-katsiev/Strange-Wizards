import pygame
from random import randint
import time
import math

pygame.init()

WIDTH, HEIGHT = 1920, 1080
FPS = 60
TILE = 50

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Strange Wizards')
clock = pygame.time.Clock()

fontUI = pygame.font.Font(None, 30)
fontGameOver = pygame.font.Font(None, 70)

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


class Menu:
    def __init__(self, screen, options, font_size=36):
        self.screen = screen
        self.options = options
        self.font = pygame.font.Font(None, font_size)
        self.selected_index = 0

    def draw(self):
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i != self.selected_index else (255, 0, 0)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 100 + i * 50))
            self.screen.blit(text, text_rect)
            if i == self.selected_index:
                pygame.draw.rect(self.screen, (255, 0, 0), text_rect, width=2)