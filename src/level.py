import pygame
import random
import math
from .sprites import Enemy, PowerUp
from .constants import *

class Level:
    def __init__(self, scale_factor_x, scale_factor_y):
        self.level = 1
        self.wave = 0
        self.max_waves = 3
        self.enemies = pygame.sprite.Group()
        self.boss_defeated = False
        self.group_dx = 2
        self.move_timer = random.randint(30, 60)
        self.formations = ["rectangle", "triangle", "diamond", "v_shape", "circle"]
        self.group_x_offset = 0
        self.wave_start_time = 0
        self.difficulty_modifier = 1.0
        self.power_ups = pygame.sprite.Group()
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y

    def update_group_movement(self):
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.group_dx = random.choice([-2, 2, 0]) * self.difficulty_modifier
            self.move_timer = random.randint(30, 60)

        leftmost_x = min([enemy.rect.left for enemy in self.enemies], default=0)
        rightmost_x = max([enemy.rect.right for enemy in self.enemies], default=VIRTUAL_WIDTH)
        
        if leftmost_x + self.group_dx < 0:
            self.group_dx = abs(self.group_dx)
        elif rightmost_x + self.group_dx > VIRTUAL_WIDTH:
            self.group_dx = -abs(self.group_dx)

        self.group_x_offset += self.group_dx

    def calculate_difficulty(self, difficulty_mode):
        base_difficulty = {"Easy": 0.8, "Normal": 1.0, "Hard": 1.2}[difficulty_mode]
        self.difficulty_modifier = base_difficulty * (1 + (self.level - 1) * 0.1)

    def spawn_formation(self, formation_type, center_x, center_y, num_enemies):
        spacing = 70
        self.enemies.empty()
        num_enemies = int(num_enemies * self.difficulty_modifier)

        enemy_types = ["basic", "fast"]
        type_weights = [0.7, 0.3]
        level_factor = min(self.level * 0.1, 0.3)
        type_weights[0] = max(0.5, 0.7 - level_factor)
        type_weights[1] = min(0.5, 0.3 + level_factor)

        def get_enemy_type():
            return random.choices(enemy_types, weights=type_weights, k=1)[0]

        if formation_type == "rectangle":
            rows = min(5, (num_enemies + 4) // 5)
            cols = min(7, (num_enemies + rows - 1) // rows)
            for row in range(rows):
                for col in range(min(cols, num_enemies - row * cols)):
                    x = center_x - (cols * spacing) // 2 + col * spacing
                    y = center_y - (rows * spacing) // 2 + row * spacing
                    enemy_type = get_enemy_type()
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier, self.scale_factor_x, self.scale_factor_y))

        elif formation_type == "triangle":
            rows = min(5, (int((2 * num_enemies) ** 0.5) + 1))
            enemy_count = 0
            for row in range(rows):
                enemies_in_row = row + 1
                if enemy_count + enemies_in_row > num_enemies:
                    enemies_in_row = num_enemies - enemy_count
                for col in range(enemies_in_row):
                    x = center_x - (row * spacing) // 2 + col * spacing
                    y = center_y + row * spacing
                    enemy_type = get_enemy_type()
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier, self.scale_factor_x, self.scale_factor_y))
                enemy_count += enemies_in_row
                if enemy_count >= num_enemies:
                    break

        elif formation_type == "diamond":
            rows = min(5, (num_enemies + 1) // 2)
            mid_row = rows // 2
            enemy_count = 0
            for row in range(rows):
                enemies_in_row = row + 1 if row <= mid_row else rows - (row - mid_row)
                if enemy_count + enemies_in_row > num_enemies:
                    enemies_in_row = num_enemies - enemy_count
                for col in range(enemies_in_row):
                    x = center_x - ((enemies_in_row - 1) * spacing) // 2 + col * spacing
                    y = center_y - (mid_row * spacing) + row * spacing
                    enemy_type = get_enemy_type()
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier, self.scale_factor_x, self.scale_factor_y))
                enemy_count += enemies_in_row
                if enemy_count >= num_enemies:
                    break

        elif formation_type == "v_shape":
            rows = min(5, (num_enemies + 1) // 2)
            enemy_count = 0
            for row in range(rows):
                enemies_in_row = 2 if row > 0 else 1
                if enemy_count + enemies_in_row > num_enemies:
                    enemies_in_row = num_enemies - enemy_count
                for col in range(enemies_in_row):
                    x = center_x + (row * spacing if col == 0 else -row * spacing)
                    y = center_y + row * spacing
                    enemy_type = get_enemy_type()
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier, self.scale_factor_x, self.scale_factor_y))
                enemy_count += enemies_in_row
                if enemy_count >= num_enemies:
                    break

        elif formation_type == "circle":
            radius = spacing * 2
            max_enemies = min(num_enemies, 12)
            for i in range(max_enemies):
                angle = 2 * math.pi * i / max_enemies
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                enemy_type = get_enemy_type()
                self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier, self.scale_factor_x, self.scale_factor_y))

    def spawn_wave(self):
        self.wave += 1
        num_enemies = (self.level * 2 + 1)
        formation = random.choice(self.formations)
        self.spawn_formation(formation, VIRTUAL_WIDTH // 2, 100, num_enemies)
        self.group_dx = 2
        self.move_timer = random.randint(30, 60)
        self.group_x_offset = 0
        self.wave_start_time = pygame.time.get_ticks()

    def spawn_boss(self):
        boss = Enemy(VIRTUAL_WIDTH // 2 - 50, 50, "boss", self.difficulty_modifier, self.scale_factor_x, self.scale_factor_y)
        self.enemies.empty()
        self.enemies.add(boss)
        self.boss_defeated = False
        self.group_dx = 1
        self.move_timer = random.randint(30, 60)
        self.group_x_offset = 0
        self.wave_start_time = pygame.time.get_ticks()

    def next_wave(self, game_state, score, bonus_sound):
        current_time = pygame.time.get_ticks()
        wave_duration = (current_time - self.wave_start_time) / 1000

        if self.wave < self.max_waves:
            if not self.enemies and wave_duration < 10:
                score.add_bonus(200, "SPEED CLEAR BONUS!")
                bonus_sound.play()
            self.spawn_wave()
        elif self.wave == self.max_waves and not self.boss_defeated:
            self.spawn_boss()
        elif self.wave == self.max_waves and self.boss_defeated:
            self.level += 1
            self.wave = 0
            game_state[0] = LEVEL_UP
        return game_state

    def spawn_power_up(self, x, y):
        power_types = ["life", "shield", "spread"]
        if random.random() < 0.15:
            power_type = random.choice(power_types)
            self.power_ups.add(PowerUp(x, y, power_type, self.scale_factor_x, self.scale_factor_y))