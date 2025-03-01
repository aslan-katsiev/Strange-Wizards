import pygame
from random import randint
import time
from constants import vegetation, bullets, WIDTH, HEIGHT, objects, window, FPS, TILE, env
from menu import Menu, UI
from mag import Mag, Bullet

pygame.init()


pygame.display.set_caption('Strange Wizards')
clock = pygame.time.Clock()

ui = UI()


class FireMag(Mag):
    def __init__(self, color, px, py, direct, keyList, keys):
        super().__init__(color, px, py, direct, keyList, keys)
        self.bulletDamage = 25
        self.attack_damage = 20
        self.shotDelay = 120
        self.attack_delay = 60
        self.dashCooldown = 4
        self.stunned = False

        self.animation_frames = {
            'up': [pygame.image.load(f'mag/fire/magup/magup{i}.png') for i in range(1, 5)],
            'down': [pygame.image.load(f'mag/fire/magdown/magdown{i}.png') for i in range(1, 5)],
            'left': [pygame.image.load(f'mag/fire/magleft/magleft{i}.png') for i in range(1, 5)],
            'right': [pygame.image.load(f'mag/fire/magright/magright{i}.png') for i in range(1, 5)],
        }

        for direction in self.animation_frames:
            self.animation_frames[direction] = [
                pygame.transform.scale(frame, (50, 50))
                for frame in self.animation_frames[direction]
            ]

    def attack(self):
        super().attack()

    def create_bullet(self, px, py, dx, dy):
        bullets.append(FireBullet(self, px, py, dx, dy, self.bulletDamage))


class FireBullet(Bullet):
    def __init__(self, parent, px, py, dx, dy, damage):
        super().__init__(parent, px, py, dx, dy, damage, stun_duration=30)
        self.frames = [pygame.image.load(f'mag/fire/fireball/fire{i}.png' ) for i in range(1, 5)]
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
    def __init__(self, color, px, py, direct, keyList, keys):
        super().__init__(color, px, py, direct, keyList, keys)
        self.bulletDamage = 20
        self.attack_damage = 15
        self.stunned = False
        self.shotDelay = 60
        self.dashCooldown = 4

        self.animation_frames = {
            'up': [pygame.image.load(f'mag/water/magup/magup{i}.png' ) for i in range(1, 5)],
            'down': [pygame.image.load(f'mag/water/magdown/magdown{i}.png' ) for i in range(1, 5)],
            'left': [pygame.image.load(f'mag/water/magleft/magleft{i}.png' ) for i in range(1, 5)],
            'right': [pygame.image.load(f'mag/water/magright/magright{i}.png' ) for i in range(1, 5)],
        }

        for direction in self.animation_frames:
            self.animation_frames[direction] = [
                pygame.transform.scale(frame, (50, 50))
                for frame in self.animation_frames[direction]
            ]

        self.attack_animation_frames = \
            [pygame.image.load(f'mag/water/water_attack/water_attack{i}.png' ) for i in range(1, 7)]

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
        self.frames = [pygame.image.load(f'mag/water/waterball/water{i}.png' ) for i in range(1, 5)]
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


class GroundMag(Mag):
    def __init__(self, color, px, py, direct, keyList, keys):
        super().__init__(color, px, py, direct, keyList, keys)
        self.bulletDamage = 20
        self.attack_damage = 20
        self.stunned = False
        self.shotDelay = 90
        self.attack_delay = 90
        self.hp = 150
        self.bulletSpeed = 6
        self.dashDelay = 1
        self.dashCooldown = 5
        self.dashDistance = 20
        self.moveSpeed = 1.5

        self.animation_frames = {
            'up': [pygame.image.load(f'mag/ground/magup/magup{i}.png') for i in range(1, 5)],
            'down': [pygame.image.load(f'mag/ground/magdown/magdown{i}.png') for i in range(1, 5)],
            'left': [pygame.image.load(f'mag/ground/magleft/magleft{i}.png') for i in range(1, 5)],
            'right': [pygame.image.load(f'mag/ground/magright/magright{i}.png') for i in range(1, 5)],
        }

        for direction in self.animation_frames:
            self.animation_frames[direction] = [
                pygame.transform.scale(frame, (50, 50))
                for frame in self.animation_frames[direction]
            ]

        self.attack_animation_frames = \
            [pygame.image.load(f'mag/ground/ground_attack/ground_attack{i}.png') for i in range(1, 7)]

        self.attack_animation_frames = [
            pygame.transform.scale(frame, (200, 200)) for frame in self.attack_animation_frames
        ]

    def attack(self):
        super().attack()

    def create_bullet(self, px, py, dx, dy):
        bullets.append(GroundBullet(self, px, py, dx, dy, self.bulletDamage))


class GroundBullet(Bullet):
    def __init__(self, parent, px, py, dx, dy, damage):
        super().__init__(parent, px, py, dx, dy, damage)
        self.frames = [pygame.image.load(f'mag/ground/groundball/ground{i}.png') for i in range(1, 5)]
        self.frames = [pygame.transform.scale(frame, (120, 120)) for frame in self.frames]

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


class WindMag(Mag):
    def __init__(self, color, px, py, direct, keyList, keys):
        super().__init__(color, px, py, direct, keyList, keys)
        self.bulletDamage = 15
        self.attack_damage = 15
        self.stunned = False
        self.shotDelay = 45
        self.dashCooldown = 3
        self.bulletSpeed = 9

        self.animation_frames = {
            'up': [pygame.image.load(f'mag/wind/magup/magup{i}.png' ) for i in range(1, 5)],
            'down': [pygame.image.load(f'mag/wind/magdown/magdown{i}.png' ) for i in range(1, 5)],
            'left': [pygame.image.load(f'mag/wind/magleft/magleft{i}.png' ) for i in range(1, 5)],
            'right': [pygame.image.load(f'mag/wind/magright/magright{i}.png' ) for i in range(1, 5)],
        }

        for direction in self.animation_frames:
            self.animation_frames[direction] = [
                pygame.transform.scale(frame, (50, 50))
                for frame in self.animation_frames[direction]
            ]

        self.attack_animation_frames = \
            [pygame.image.load(f'mag/wind/wind_attack/wind_attack{i}.png') for i in range(1, 6)]

        self.attack_animation_frames = [
            pygame.transform.scale(frame, (200, 200)) for frame in self.attack_animation_frames
        ]

    def attack(self):
        super().attack()

    def create_bullet(self, px, py, dx, dy):
        bullets.append(WindBullet(self, px, py, dx, dy, self.bulletDamage))


class WindBullet(Bullet):
    def __init__(self, parent, px, py, dx, dy, damage):
        super().__init__(parent, px, py, dx, dy, damage)
        self.frames = [pygame.image.load(f'mag/wind/windball/wind{i}.png') for i in range(1, 5)]
        self.frames = [pygame.transform.scale(frame, (80, 80)) for frame in self.frames]
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


menu_player_1 = Menu(window, ["Fire Mag", "Water Mag", "Wind Mag", "Ground Mag"])
menu_player_2 = Menu(window, ["Fire Mag", "Water Mag", "Wind Mag", "Ground Mag"])

character_classes = {
    "Fire Mag": FireMag,
    "Water Mag": WaterMag,
    "Wind Mag": WindMag,
    "Ground Mag": GroundMag
}


class Tree:
    def __init__(self, px, py):
        objects.append(self)
        self.moveSpeed = 0
        self.is_stunned = False
        self.is_slowed = False
        self.type = 'tree'

        self.image = pygame.image.load(
            'env/trees/mid_tree_green.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(px, py))
        self.hp = 10

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
        pass

    def draw(self):
        window.blit(self.image, self.rect.topleft)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)


class Vegetation:
    def __init__(self, px, py):
        env.append(self)
        self.type = 'vegetation'

        num = randint(1, 5)
        self.image = pygame.image.load(vegetation[num]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(topleft=(px, py))
        self.hp = 10

    def update(self):
        pass

    def draw(self):
        window.blit(self.image, self.rect.topleft)


for _ in range(20):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect):
                fined = True

        if not fined:
            break

    Tree(x, y)

for _ in range(50):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect):
                fined = True

        if not fined:
            break

    Vegetation(x, y)

running = True
game_started = False

player_1_keys = (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s,
                 pygame.K_f, pygame.K_LSHIFT, pygame.K_q)

player_2_keys = (pygame.K_k, pygame.K_SEMICOLON, pygame.K_o, pygame.K_l,
                 pygame.K_j, pygame.K_RSHIFT, pygame.K_p)

player_1_class_selected = False
player_2_class_selected = False

player_1 = None
player_2 = None

while running:
    keys = pygame.key.get_pressed()
    a = 0
    window.fill((0, 100, 0))
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if not game_started:
            if not player_1_class_selected:
                choice_1 = menu_player_1.run()
                if choice_1 is not None:
                    player_1_class_selected = True
                    player_1_class_name = menu_player_1.options[choice_1]
                    player_1_class = character_classes[player_1_class_name]
                    player_1 = player_1_class("red", 100, 100, 0, player_1_keys, keys)
                    objects.append(player_1)

            elif not player_2_class_selected:
                choice_2 = menu_player_2.run()
                if choice_2 is not None:
                    player_2_class_selected = True
                    player_2_class_name = menu_player_2.options[choice_2]
                    player_2_class = character_classes[player_2_class_name]
                    player_2 = player_2_class("blue", 200, 100, 0, player_2_keys, keys)
                    objects.append(player_2)

            if player_1_class_selected and player_2_class_selected:
                game_started = True

            else:
                font = pygame.font.Font(None, 36)
                text = font.render("Press ENTER to start", True, (255, 255, 255))
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                window.blit(text, text_rect)

        elif game_started:
            if event.type == pygame.KEYDOWN:
                if player_1 and event.key == player_1.keySHOT and player_1.shotTimer == 0:
                    player_1.shoot()
                if player_2 and event.key == player_2.keySHOT and player_2.shotTimer == 0:
                    player_2.shoot()

    if game_started:
        for i in env:
            i.draw()

        for obj in objects:
            obj.update()

        for bullet in bullets:
            bullet.update()
            bullet.draw()

        for obj in objects:
            obj.draw()

        ui.draw()

    pygame.display.update()

pygame.quit()
