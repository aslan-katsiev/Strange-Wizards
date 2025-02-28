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

            if move_x != 0 or move_y != 0:
                length = math.sqrt(move_x ** 2 + move_y ** 2)
                if length > 0:
                    move_x = (move_x / length) * self.moveSpeed
                    move_y = (move_y / length) * self.moveSpeed
                    moved = True

            if move_x != 0 and move_y != 0:
                move_x *= 1.1
                move_y *= 1.1

            if move_y < 0 < move_x:
                self.direct = 1
                self.direct_walk = 1
            elif move_x > 0 and move_y > 0:
                self.direct = 3
                self.direct_walk = 1
            elif move_x < 0 < move_y:
                self.direct = 5
                self.direct_walk = 3
            elif move_x < 0 and move_y < 0:
                self.direct = 7
                self.direct_walk = 3
            elif move_x > 0:
                self.direct = 2
                self.direct_walk = 1
            elif move_x < 0:
                self.direct = 6
                self.direct_walk = 3
            elif move_y > 0:
                self.direct = 4
                self.direct_walk = 2
            elif move_y < 0:
                self.direct = 0
                self.direct_walk = 0

        current_time = time.time()

        if keys[self.keyDASH] and self.dashCount > 0 and current_time - self.lastDashUsedTime >= self.dashDelay:
            move_x *= self.dashDistance
            move_y *= self.dashDistance
            self.dashCount -= 1
            self.lastDashUsedTime = current_time

        if self.dashCount < self.maxDashes and current_time - self.lastDashRestoreTime >= self.dashCooldown:
            self.dashCount += 1
            self.lastDashRestoreTime = current_time

        self.rect.x += move_x
        self.rect.y += move_y

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        for obj in objects:
            if obj != self and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldx, oldy

        if self.is_attacking:
            self.update_attack_rect()
            current_time = time.time()
            if current_time - self.attack_last_frame_time >= self.attack_animation_speed:
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_animation_frames):
                    self.is_attacking = False
                    self.attack_frame_index = 0
                self.attack_last_frame_time = current_time

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if keys[self.keyATTACK] and self.attack_cooldown == 0:
            self.attack()

        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0 and self.is_slowed:
                self.moveSpeed = self.original_moveSpeed
                self.is_slowed = False
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0 and self.stunned:
                self.stunned = False
                self.is_stunned = False

        if moved:
            now = time.time()
            elapsed = now - self.last_update_time

            if elapsed >= self.animation_speed:
                self.last_update_time = now
                direction_key = self.current_directions[self.direct_walk]
                self.frame_index = (self.frame_index + 1) % len(self.animation_frames[direction_key])

        else:
            self.frame_index = 0

        if self.shotTimer > 0:
            self.shotTimer -= 1

    def get_rotated_frame(self, frame):
        if self.direct == 0:
            return frame
        elif self.direct == 2:
            return pygame.transform.rotate(frame, -90)
        elif self.direct == 4:
            return pygame.transform.rotate(frame, 180)
        elif self.direct == 6:
            return pygame.transform.rotate(frame, 90)
        elif self.direct == 1:
            return pygame.transform.rotate(frame, -45)
        elif self.direct == 3:
            return pygame.transform.rotate(frame, -135)
        elif self.direct == 5:
            return pygame.transform.rotate(frame, 135)
        elif self.direct == 7:
            return pygame.transform.rotate(frame, 45)

    def draw(self):
        window.blit(self.animation_frames[self.current_directions[self.direct_walk]][self.frame_index],
                    self.rect.topleft)
        if self.is_attacking:
            current_attack_frame = self.attack_animation_frames[self.attack_frame_index]
            rotated_frame = self.get_rotated_frame(current_attack_frame)

            frame_rect = rotated_frame.get_rect(center=self.attack_rect.center)

            window.blit(rotated_frame, frame_rect.topleft)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)
            print(self.color, 'dead')


class Bullet(pygame.sprite.Sprite):
    def __init__(self, parent, px, py, dx, dy, damage, radius=10,
                 slow_duration=0.0, slow_amount=0.0, stun_duration=0.0):
        super().__init__()
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage
        self.radius = radius
        self.rect = pygame.Rect(px - radius, py - radius, radius * 2, radius * 2)
        self.current_frame = 0
        self.last_frame_time = time.time()
        self.frames = []
        self.angle = self.calculate_angle(dx, dy)
        self.slow_duration = slow_duration
        self.slow_amount = slow_amount
        self.stun_duration = stun_duration

    def calculate_angle(self, dx, dy):
        return math.degrees(math.atan2(-dy, dx))

    def get_rotated_frame(self):
        if self.frames:
            frame = self.frames[self.current_frame]
            return pygame.transform.rotate(frame, self.angle - 90)
        else:
            return None

    def update(self):
        self.px += self.dx
        self.py += self.dy
        self.rect.center = (self.px, self.py)

        current_time = time.time()

        if current_time - self.last_frame_time >= 0.1:
            if len(self.frames) > 0:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.last_frame_time = current_time

        for obj in objects:
            if obj != self.parent and self.rect.colliderect(obj.rect):
                obj.damage(self.damage)
                obj.apply_effects(self.slow_duration, self.stun_duration)
                if self in bullets:
                    bullets.remove(self)
                break

        if (self.px - self.radius < 0 or self.px + self.radius > WIDTH or
                self.py - self.radius < 0 or self.py + self.radius > HEIGHT):
            if self in bullets:
                bullets.remove(self)

    def draw(self):
        return


ui = UI()


class FireMag(Mag):
    def __init__(self, color, px, py, direct, keyList):
        super().__init__(color, px, py, direct, keyList)
        self.bulletDamage = 25
        self.attack_damage = 15
        self.stunned = False
        self.shotDelay = 120
        self.attack_delay = 60

        self.animation_frames = {
            'up': [pygame.image.load(f'../Strange Wizards/mag/fire/magup/magup{i}.png') for i in range(1, 5)],
            'down': [pygame.image.load(f'../Strange Wizards/mag/fire/magdown/magdown{i}.png') for i in range(1, 5)],
            'left': [pygame.image.load(f'../Strange Wizards/mag/fire/magleft/magleft{i}.png') for i in range(1, 5)],
            'right': [pygame.image.load(f'../Strange Wizards/mag/fire/magright/magright{i}.png') for i in range(1, 5)],
        }

        for direction in self.animation_frames:
            self.animation_frames[direction] = [
                pygame.transform.scale(frame, (50, 50))
                for frame in self.animation_frames[direction]
            ]

    def attack(self):
        super().attack()
        for obj in objects:
            if obj != self and self.attack_rect.colliderect(obj.rect):
                obj.damage(5)

    def create_bullet(self, px, py, dx, dy):
        bullets.append(FireBullet(self, px, py, dx, dy, self.bulletDamage))


class FireBullet(Bullet):
    def __init__(self, parent, px, py, dx, dy, damage):
        super().__init__(parent, px, py, dx, dy, damage, stun_duration=30)
        self.frames = [pygame.image.load(f'../Strange Wizards/mag/fire/fireball/fire{i}.png' ) for i in range(1, 5)]
        self.frames = [pygame.transform.scale(frame, (50, 50)) for frame in self.frames]

    def update(self):
        super().update()
        current_time = time.time()
        if current_time - self.last_frame_time >= 0.1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_frame_time = current_time

    def draw(self):
        rotated_frame = self.get_rotated_frame()
        if rotated_frame:
            frame_rect = rotated_frame.get_rect(center=self.rect.center)
            window.blit(rotated_frame, frame_rect.topleft)


class WaterMag(Mag):
    def __init__(self, color, px, py, direct, keyList):
        super().__init__(color, px, py, direct, keyList)
        self.bulletDamage = 20
        self.attack_damage = 10
        self.stunned = False
        self.shotDelay = 45

        self.animation_frames = {
            'up': [pygame.image.load(f'../Strange Wizards/mag/water/magup/magup{i}.png' ) for i in range(1, 5)],
            'down': [pygame.image.load(f'../Strange Wizards/mag/water/magdown/magdown{i}.png' ) for i in range(1, 5)],
            'left': [pygame.image.load(f'../Strange Wizards/mag/water/magleft/magleft{i}.png' ) for i in range(1, 5)],
            'right': [pygame.image.load(f'../Strange Wizards/mag/water/magright/magright{i}.png' ) for i in range(1, 5)],
        }

        for direction in self.animation_frames:
            self.animation_frames[direction] = [
                pygame.transform.scale(frame, (50, 50))
                for frame in self.animation_frames[direction]
            ]

        self.attack_animation_frames = \
            [pygame.image.load(f'../Strange Wizards/mag/water/water_attack/water_attack{i}.png' ) for i in range(1, 7)]

        self.attack_animation_frames = [
            pygame.transform.scale(frame, (200, 200)) for frame in self.attack_animation_frames
        ]

    def attack(self):
        super().attack()

    def create_bullet(self, px, py, dx, dy):
        bullets.append(WaterBullet(self, px, py, dx, dy, self.bulletDamage))


class WaterBullet(Bullet):
    def __init__(self, parent, px, py, dx, dy, damage):
        super().__init__(parent, px, py, dx, dy, damage, slow_duration=90, slow_amount=0.6)
        self.frames = [pygame.image.load(f'../Strange Wizards/mag/water/waterball/water{i}.png' ) for i in range(1, 5)]
        self.frames = [pygame.transform.scale(frame, (100, 100)) for frame in self.frames]
        self.slowed = True

    def update(self):
        super().update()
        current_time = time.time()
        if current_time - self.last_frame_time >= 0.1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_frame_time = current_time

    def draw(self):
        rotated_frame = self.get_rotated_frame()
        if rotated_frame:
            frame_rect = rotated_frame.get_rect(center=self.rect.center)
            window.blit(rotated_frame, frame_rect.topleft)


menu_player_1 = Menu(window, ["Fire Mag", "Water Mag"])
menu_player_2 = Menu(window, ["Fire Mag", "Water Mag"])

character_classes = {
    "Fire Mag": FireMag,
    "Water Mag": WaterMag,
}