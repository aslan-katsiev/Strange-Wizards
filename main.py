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

bullets = []
objects = []
env = []


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

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.selected_index

        return None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return None

                selection = self.handle_input(event)
                if selection is not None:
                    return selection

            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

        return None


class UI:
    def draw(self):
        i = 0
        mags = 0
        for obj in objects:
            if obj.type == 'mag':
                mags += 1
                pygame.draw.rect(window, obj.color, (i * 65, 20, 22, 22))

                text = fontUI.render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center=(5 + i * 65 + 32, 20 + 11))
                window.blit(text, rect)
                i += 1
        if mags < 2:
            text = fontGameOver.render('Игра окончена.', 1, 'white')
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(text, rect)


class Mag(pygame.sprite.Sprite):
    def __init__(self, color, px, py, direct, keyList):
        super().__init__()
        self.type = 'mag'
        self.color = color
        self.rect = pygame.Rect(px, py, 50, 50)
        self.direct = direct
        self.moveSpeed = 2
        self.hp = 100

        self.animation_frames = {
            'up': [],
            'down': [],
            'left': [],
            'right': []
        }

        self.attack_animation_frames = \
            [pygame.image.load(f'../Strange Wizards/mag/fire/fire_attack/fire_attack{i}.png' ) for i in range(1, 6)]

        self.attack_animation_frames = [
            pygame.transform.scale(frame, (200, 200)) for frame in self.attack_animation_frames
        ]

        self.is_attacking = False
        self.attack_frame_index = 0
        self.attack_last_frame_time = time.time()
        self.attack_animation_speed = 0.1

        self.frame_index = 0
        self.last_update_time = time.time()
        self.animation_speed = 0.2
        self.direct_walk = 2

        self.shotTimer = 0
        self.shotDelay = 60
        self.bulletSpeed = 8
        self.bulletDamage = 20

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]
        self.keyDASH = keyList[5]
        self.keyATTACK = keyList[6]

        self.dashDistance = 30
        self.dashCooldown = 3
        self.dashDelay = 0.5
        self.lastDashUsedTime = 0
        self.lastDashRestoreTime = time.time()
        self.maxDashes = 2
        self.dashCount = self.maxDashes

        self.attack_range = 50
        self.attack_damage = 10
        self.attack_cooldown = 0
        self.attack_delay = 30

        self.current_directions = {
            0: 'up',
            1: 'right',
            2: 'down',
            3: 'left',
        }

        self.original_moveSpeed = self.moveSpeed
        self.slow_timer = 0
        self.stun_timer = 0
        self.is_slowed = False
        self.is_stunned = False

    def attack(self):
        if self.attack_cooldown > 0:
            return

        self.is_attacking = True
        self.attack_frame_index = 0

        self.update_attack_rect()

        for obj in objects:
            if obj != self and self.attack_rect.colliderect(obj.rect):
                obj.damage(self.attack_damage)

        self.attack_cooldown = self.attack_delay

    def update_attack_rect(self):
        if self.direct == 0:
            self.attack_rect = pygame.Rect(self.rect.centerx - 35, self.rect.top - 30, 70, 30)
        elif self.direct == 2:
            self.attack_rect = pygame.Rect(self.rect.right - 5, self.rect.centery - 35, self.attack_range - 20, 70)
        elif self.direct == 4:
            self.attack_rect = pygame.Rect(self.rect.centerx - 35, self.rect.bottom, 70, self.attack_range - 20)
        elif self.direct == 6:
            self.attack_rect = pygame.Rect(self.rect.left - 25, self.rect.centery - 35, 30, 70)
        elif self.direct == 1:
            self.attack_rect = pygame.Rect(self.rect.right - 25, self.rect.top - 25, 50, 50)
        elif self.direct == 3:
            self.attack_rect = pygame.Rect(self.rect.right - 25, self.rect.bottom - 25, 50, 50)
        elif self.direct == 5:
            self.attack_rect = pygame.Rect(self.rect.left - 25, self.rect.bottom - 25, 50, 50)
        elif self.direct == 7:
            self.attack_rect = pygame.Rect(self.rect.left - 25, self.rect.top - 25, 50, 50)

    def shoot(self):
        dx, dy = DIRECTS[self.direct]
        dx *= self.bulletSpeed
        dy *= self.bulletSpeed
        if dx != 0 and dy != 0:
            dx = dx // 1.41
            dy = dy // 1.41
        self.create_bullet(self.rect.centerx, self.rect.centery, dx, dy)
        self.shotTimer = self.shotDelay

    def create_bullet(self, px, py, dx, dy):
        pass

    def apply_effects(self, slow_duration, stun_duration):
        if slow_duration > 0 and not self.is_slowed:
            self.apply_slow(slow_duration, 0.5)
        if stun_duration > 0 and not self.is_stunned:
            self.apply_stun(stun_duration)

    def apply_slow(self, duration, amount):
        self.original_moveSpeed = self.moveSpeed
        self.moveSpeed *= (1 - amount)
        self.slow_timer = duration
        self.is_slowed = True

    def apply_stun(self, duration):
        self.stunned = True
        self.stun_timer = duration
        self.is_stunned = True

    def update(self):
        oldx, oldy = self.rect.topleft
        move_x = 0
        move_y = 0
        moved = False

        if not self.stunned:
            if keys[self.keyUP]:
                move_y -= self.moveSpeed
            if keys[self.keyDOWN]:
                move_y += self.moveSpeed
            if keys[self.keyLEFT]:
                move_x -= self.moveSpeed
            if keys[self.keyRIGHT]:
                move_x += self.moveSpeed


