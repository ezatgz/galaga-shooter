import pygame
import math
import random
from .constants import *

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type, scale_factor_x, scale_factor_y):
        super().__init__()
        self.power_type = power_type
        self.original_image = {
            "life": pygame.image.load(ASSET_PATHS["power_up_life_image"]).convert_alpha(),
            "shield": pygame.image.load(ASSET_PATHS["power_up_shield_image"]).convert_alpha(),
            "spread": pygame.image.load(ASSET_PATHS["power_up_spread_image"]).convert_alpha()
        }[power_type]
        self.image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * scale_factor_x), int(self.original_image.get_height() * scale_factor_y)))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > VIRTUAL_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale_factor_x, scale_factor_y):
        super().__init__()
        self.frames = []
        frame_width = 64
        frame_height = 64
        explosion_sheet = pygame.image.load(ASSET_PATHS["explosion_sheet"]).convert_alpha()
        for i in range(6):
            frame = explosion_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (int(frame_width * scale_factor_x), int(frame_height * scale_factor_y)))
            self.frames.append(frame)
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame_index = 0
        self.frame_rate = 5
        self.frame_counter = 0

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.frame_counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]

class Player(pygame.sprite.Sprite):
    def __init__(self, config, scale_factor_x, scale_factor_y):
        super().__init__()
        self.original_image = pygame.image.load(ASSET_PATHS["player_image"]).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * scale_factor_x), int(self.original_image.get_height() * scale_factor_y)))
        self.rect = self.image.get_rect()
        self.rect.centerx = VIRTUAL_WIDTH // 2
        self.rect.centery = VIRTUAL_HEIGHT - 100
        self.base_movement_speed = 6 * config["movement_speed"]
        self.movement_speed = self.base_movement_speed
        self.base_shoot_cooldown = 20 / config["shooting_speed"]
        self.shoot_cooldown = self.base_shoot_cooldown
        self.base_bullet_speed = -5 * config["bullet_speed"]
        self.lives = 3
        self.max_lives = 5
        self.bullets = pygame.sprite.Group()
        self.power_up_counts = {"shield": 0, "spread": 0}
        self.power_up_timers = {"shield": 0, "spread": 0}
        self.shield_active = False
        self.max_power_ups = 5
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y

    def move(self, keys, mouse_pos):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.movement_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < VIRTUAL_WIDTH:
            self.rect.x += self.movement_speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= self.movement_speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < VIRTUAL_HEIGHT:
            self.rect.y += self.movement_speed

        mouse_x = mouse_pos[0] / self.scale_factor_x
        mouse_y = mouse_pos[1] / self.scale_factor_y
        self.rect.centerx = max(0, min(VIRTUAL_WIDTH, mouse_x))
        self.rect.centery = max(0, min(VIRTUAL_HEIGHT, mouse_y))

    def shoot(self):
        if self.shoot_cooldown <= 0:
            shoot_sound = pygame.mixer.Sound(ASSET_PATHS["shoot_sound"])
            if self.power_up_timers["spread"] > 0:
                bullet_straight = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player", self.scale_factor_x, self.scale_factor_y)
                bullet_left = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player", self.scale_factor_x, self.scale_factor_y)
                bullet_left.speed_x = -2
                bullet_right = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player", self.scale_factor_x, self.scale_factor_y)
                bullet_right.speed_x = 2
                self.bullets.add(bullet_straight, bullet_left, bullet_right)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player", self.scale_factor_x, self.scale_factor_y)
                self.bullets.add(bullet)
            self.shoot_cooldown = self.base_shoot_cooldown
            shoot_sound.play()

    def collect_power_up(self, power_type, score):
        power_up_collect_sound = pygame.mixer.Sound(ASSET_PATHS["power_up_collect_sound"])
        if power_type == "life" and self.lives < self.max_lives:
            self.lives += 1
            score.add_bonus(0, "POWER-UP: EXTRA LIFE!")
            power_up_collect_sound.play()
        elif power_type in self.power_up_counts:
            if self.power_up_counts[power_type] < self.max_power_ups:
                self.power_up_counts[power_type] += 1
                score.add_bonus(0, f"POWER-UP: {power_type.upper()} COLLECTED! ({self.power_up_counts[power_type]}/5)")
                power_up_collect_sound.play()
            else:
                score.add_bonus(0, f"POWER-UP: {power_type.upper()} FULL! (5/5)")

    def activate_power_up(self, power_type, score):
        power_up_activate_sound = pygame.mixer.Sound(ASSET_PATHS["power_up_activate_sound"])
        power_up_zero_sound = pygame.mixer.Sound(ASSET_PATHS["power_up_zero_sound"])
        if self.power_up_counts[power_type] > 0 and self.power_up_timers[power_type] <= 0:
            self.power_up_counts[power_type] -= 1
            self.power_up_timers[power_type] = 600
            power_up_activate_sound.play()
            if power_type == "shield":
                self.shield_active = True
                score.add_bonus(0, "POWER-UP: SHIELD ACTIVATED!")
            elif power_type == "spread":
                score.add_bonus(0, "POWER-UP: SPREAD SHOT!")
        elif self.power_up_counts[power_type] == 0:
            power_up_zero_sound.play()
            score.add_bonus(0, f"NO {power_type.upper()} POWER-UPS LEFT!")

    def update(self):
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.bullets.update()
        self.bullets = pygame.sprite.Group([b for b in self.bullets if b.rect.bottom > 0])

        for power_type in ["shield", "spread"]:
            if self.power_up_timers[power_type] > 0:
                self.power_up_timers[power_type] -= 1
                if self.power_up_timers[power_type] <= 0:
                    self.revert_power_up(power_type)
                    if power_type == "shield":
                        self.shield_active = False

    def revert_power_up(self, power_type):
        if power_type == "shield":
            pass
        elif power_type == "spread":
            pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.bullets.draw(surface)
        if self.shield_active and self.power_up_timers["shield"] > 0:
            pygame.draw.rect(surface, CYAN, self.rect.inflate(10, 10), 2)

        y_offset = 120
        power_up_images = {
            "shield": pygame.image.load(ASSET_PATHS["power_up_shield_image"]).convert_alpha(),
            "spread": pygame.image.load(ASSET_PATHS["power_up_spread_image"]).convert_alpha()
        }
        font = pygame.font.Font(ASSET_PATHS["font"], int(16 * self.scale_factor_y))
        for power_type in ["shield", "spread"]:
            icon = pygame.transform.scale(power_up_images[power_type], (int(32 * self.scale_factor_x), int(32 * self.scale_factor_y)))
            surface.blit(icon, (20, y_offset))
            count_text = font.render(f"{self.power_up_counts[power_type]}/5", True, YELLOW)
            surface.blit(count_text, (60, y_offset + 5))
            y_offset += 60

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, bullet_type, scale_factor_x, scale_factor_y, damage=1):
        super().__init__()
        self.original_image = pygame.image.load(ASSET_PATHS["player_bullet_image"] if bullet_type == "player" else ASSET_PATHS["enemy_bullet_image"]).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * scale_factor_x), int(self.original_image.get_height() * scale_factor_y)))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = speed
        self.speed_x = 0
        self.damage = damage

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.speed_x

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic", difficulty_modifier=1.0, scale_factor_x=1.0, scale_factor_y=1.0):
        super().__init__()
        self.enemy_type = enemy_type
        self.is_boss = (enemy_type == "boss")
        self.original_image = {
            "basic": pygame.image.load(ASSET_PATHS["enemy_image"]).convert_alpha(),
            "fast": pygame.image.load(ASSET_PATHS["enemy_fast_image"]).convert_alpha(),
            "boss": pygame.image.load(ASSET_PATHS["boss_image"]).convert_alpha()
        }[enemy_type]
        if enemy_type == "fast":
            self.original_image = pygame.transform.scale(self.original_image, pygame.image.load(ASSET_PATHS["enemy_image"]).get_size()).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (int(self.original_image.get_width() * scale_factor_x), int(self.original_image.get_height() * scale_factor_y)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        if self.is_boss:
            self.health = int(3 * difficulty_modifier)
            self.shoot_timer = int(180 / difficulty_modifier)
            self.sway_amplitude = 20
            self.sway_speed = 0.05
        else:
            if enemy_type == "basic":
                self.health = int(1 * difficulty_modifier)
                self.shoot_timer = int(180 / difficulty_modifier)
                self.sway_amplitude = 20
                self.sway_speed = 0.05
            elif enemy_type == "fast":
                self.health = int(1 * difficulty_modifier)
                self.shoot_timer = int(360 / difficulty_modifier)
                self.sway_amplitude = 30
                self.sway_speed = 0.08

        self.shoot_timer = random.randint(0, self.shoot_timer)
        self.bullets = pygame.sprite.Group()
        self.can_dive = (not self.is_boss)
        self.is_diving = False
        self.is_returning = False
        self.dive_target_y = VIRTUAL_HEIGHT - 50
        base_dive_speed = 3 if enemy_type != "fast" else 5
        self.dive_speed = base_dive_speed * difficulty_modifier
        self.return_speed = 6
        self.original_pos = (x, y)
        self.dive_timer = 0
        self.sway_offset = random.uniform(0, 2 * math.pi)
        self.difficulty_modifier = difficulty_modifier
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y

    def shoot(self):
        if self.shoot_timer <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 1.5, "enemy", self.scale_factor_x, self.scale_factor_y, self.difficulty_modifier)
            self.bullets.add(bullet)
            self.shoot_timer = int(180 / self.difficulty_modifier) if self.is_boss else {"basic": int(180 / self.difficulty_modifier), "fast": int(360 / self.difficulty_modifier)}[self.enemy_type]
        self.shoot_timer -= 1

    def update(self, player_pos, group_dx):
        self.sway_offset += self.sway_speed
        sway_delta = math.sin(self.sway_offset) * self.sway_amplitude
        base_x = self.original_pos[0] + group_dx

        if not self.is_diving and not self.is_returning and self.can_dive:
            dive_chance = 0.001 * self.difficulty_modifier if self.enemy_type == "basic" else 0.003 * self.difficulty_modifier
            if random.random() < dive_chance:
                self.is_diving = True
                self.dive_timer = 0

        if self.is_diving:
            self.dive_timer += 1
            if self.rect.y < self.dive_target_y:
                self.rect.y += self.dive_speed
                if self.rect.y >= self.dive_target_y:
                    self.rect.y = self.dive_target_y
                self.rect.x = base_x + math.sin(self.dive_timer * 0.2) * 5
            else:
                self.is_diving = False
                self.is_returning = True

        if self.is_returning:
            target_x = base_x
            target_y = self.original_pos[1]
            if self.rect.y > target_y:
                self.rect.y -= self.return_speed
                self.rect.x = target_x
            if self.rect.y <= target_y + 2:
                self.rect.x = target_x
                self.rect.y = target_y
                self.is_returning = False

        self.shoot()
        self.bullets.update()
        self.bullets = pygame.sprite.Group([b for b in self.bullets if b.rect.top < VIRTUAL_HEIGHT])

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.bullets.draw(surface)