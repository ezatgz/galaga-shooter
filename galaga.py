import pygame
import json
import os
import random
import math

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.mixer.set_num_channels(16)

# Virtual resolution (16:9)
VIRTUAL_WIDTH = 1920
VIRTUAL_HEIGHT = 1080
ASPECT_RATIO = VIRTUAL_WIDTH / VIRTUAL_HEIGHT

# Detect native resolution
info = pygame.display.Info()
NATIVE_WIDTH = info.current_w
NATIVE_HEIGHT = info.current_h
print(f"Native resolution: {NATIVE_WIDTH}x{NATIVE_HEIGHT}")

# Supported resolutions
RESOLUTIONS = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "2K": (2560, 1440),
    "4K": (3840, 2160),
}

current_resolution = "720p"
WINDOW_WIDTH, WINDOW_HEIGHT = NATIVE_WIDTH, NATIVE_HEIGHT  # Default to native resolution for fullscreen

virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)  # Start in fullscreen
pygame.display.set_caption("Starship Commander")
clock = pygame.time.Clock()

is_fullscreen = True  # Default to fullscreen

# Colors
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (85, 85, 85)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

# Load sound effects
SHOOT_SOUND = pygame.mixer.Sound("assets/sounds/shoot.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/explosion.wav")
LOST_LIFE_SOUND = pygame.mixer.Sound("assets/sounds/lost_life.wav")
GAME_OVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")
LEVEL_CLEAR_SOUND = pygame.mixer.Sound("assets/sounds/level_clear.wav")
BONUS_SOUND = pygame.mixer.Sound("assets/sounds/bonus.wav")
POWER_UP_COLLECT_SOUND = pygame.mixer.Sound("assets/sounds/power_up.wav")
POWER_UP_ACTIVATE_SOUND = pygame.mixer.Sound("assets/sounds/power_activate.wav")
POWER_UP_ZERO_SOUND = pygame.mixer.Sound("assets/sounds/power_zero.wav")
CLICK_SOUND = pygame.mixer.Sound("assets/sounds/click.wav")

pygame.mixer.music.load("assets/sounds/bgm.mp3")

LEVEL_CLEAR_DURATION = LEVEL_CLEAR_SOUND.get_length()
MINIMUM_SOUND_DURATION = LEVEL_CLEAR_DURATION + 0.1
# print(f"LEVEL_CLEAR_SOUND duration: {LEVEL_CLEAR_DURATION} seconds, Minimum duration set to: {MINIMUM_SOUND_DURATION} seconds")

# Load sprite images
PLAYER_IMAGE = pygame.image.load("assets/images/sprites/player.png").convert_alpha()
ENEMY_IMAGE = pygame.image.load("assets/images/sprites/enemy.png").convert_alpha()
ENEMY_FAST_IMAGE = pygame.image.load("assets/images/sprites/enemy_fast.png").convert_alpha()
ENEMY_BASE_SIZE = ENEMY_IMAGE.get_size()
ENEMY_FAST_IMAGE = pygame.transform.scale(ENEMY_FAST_IMAGE, ENEMY_BASE_SIZE).convert_alpha()
PLAYER_BULLET_IMAGE = pygame.image.load("assets/images/sprites/player_bullet.png").convert_alpha()
ENEMY_BULLET_IMAGE = pygame.image.load("assets/images/sprites/enemy_bullet.png").convert_alpha()
BOSS_IMAGE = pygame.image.load("assets/images/sprites/boss.png").convert_alpha()
EXPLOSION_SHEET = pygame.image.load("assets/images/sprites/explosion.png").convert_alpha()
BACKGROUND_IMAGE = pygame.image.load("assets/images/backgrounds/background.png").convert()
BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
HEART_FULL = pygame.image.load("assets/images/ui/heart_full.png").convert_alpha()
HEART_EMPTY = pygame.image.load("assets/images/ui/heart_empty.png").convert_alpha()
POWER_UP_LIFE_IMAGE = pygame.image.load("assets/images/sprites/power_up_life.png").convert_alpha()
POWER_UP_SHIELD_IMAGE = pygame.image.load("assets/images/sprites/power_up_shield.png").convert_alpha()
POWER_UP_SPREAD_IMAGE = pygame.image.load("assets/images/sprites/power_up_spread.png").convert_alpha()
SPACE_BG_IMAGE = pygame.image.load("assets/images/backgrounds/background.png").convert()
SPACE_BG_IMAGE = pygame.transform.scale(SPACE_BG_IMAGE, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT * 2))

# Font initialization
PIXEL_FONT = pygame.font.Font("assets/fonts/menu.ttf", 16)
FONT_PATH = "assets/fonts/menu.ttf"

# Background scrolling variables
scroll_speed = 2
background_y = 0

# Create a tiled background surface
background_height = BACKGROUND_IMAGE.get_height()
background_surface = pygame.Surface((VIRTUAL_WIDTH, background_height * 2))
for y in range(0, background_height * 2, background_height):
    background_surface.blit(BACKGROUND_IMAGE, (0, y))

scale_factor_x = 1.0
scale_factor_y = 1.0
letterbox_x = 0
letterbox_y = 0

def update_scaling():
    global scale_factor_x, scale_factor_y, letterbox_x, letterbox_y, screen, WINDOW_WIDTH, WINDOW_HEIGHT
    if is_fullscreen:
        WINDOW_WIDTH, WINDOW_HEIGHT = NATIVE_WIDTH, NATIVE_HEIGHT
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    else:
        WINDOW_WIDTH, WINDOW_HEIGHT = RESOLUTIONS[current_resolution]
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    window_aspect = WINDOW_WIDTH / WINDOW_HEIGHT
    if window_aspect > ASPECT_RATIO:
        scale_factor_y = WINDOW_HEIGHT / VIRTUAL_HEIGHT
        scale_factor_x = scale_factor_y
        scaled_width = VIRTUAL_WIDTH * scale_factor_x
        scaled_height = WINDOW_HEIGHT
        letterbox_x = (WINDOW_WIDTH - scaled_width) / 2
        letterbox_y = 0
    else:
        scale_factor_x = WINDOW_WIDTH / VIRTUAL_WIDTH
        scale_factor_y = scale_factor_x
        scaled_height = VIRTUAL_HEIGHT * scale_factor_y
        scaled_width = WINDOW_WIDTH
        letterbox_x = 0
        letterbox_y = (WINDOW_HEIGHT - scaled_height) / 2

    # print(f"Window: {WINDOW_WIDTH}x{WINDOW_HEIGHT}, Scale factors: ({scale_factor_x}, {scale_factor_y}), Letterbox: ({letterbox_x}, {letterbox_y})")

update_scaling()

# --- Config and High Score File Management ---
CONFIG_FILE = "assets/data/config.json"
HIGHSCORE_FILE = "assets/data/highscores.json"
DEFAULT_CONFIG = {
    "movement_speed": 2,
    "shooting_speed": 2,
    "bullet_speed": 2
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                for key in config_data:
                    if config_data[key] not in [2, 3]:
                        config_data[key] = 2
                return config_data
        except json.JSONDecodeError:
            print("Error loading config file, using defaults")
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error loading high scores, starting fresh")
            return [{"name": "Anonymous", "score": 0} for _ in range(5)]
    else:
        return [{"name": "Anonymous", "score": 0} for _ in range(5)]

def save_highscores(highscores):
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(highscores, f, indent=4)

config = load_config()
highscores = load_highscores()

# Initialize the font after loading config
PIXEL_FONT = pygame.font.Font(FONT_PATH, 16)

# --- PowerUp Class ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.original_image = {
            "life": POWER_UP_LIFE_IMAGE,
            "shield": POWER_UP_SHIELD_IMAGE,
            "spread": POWER_UP_SPREAD_IMAGE
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

# --- Explosion Class ---
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        frame_width = 64
        frame_height = 64
        for i in range(6):
            frame = EXPLOSION_SHEET.subsurface((i * frame_width, 0, frame_width, frame_height))
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

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = PLAYER_IMAGE
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

    def move(self, keys, mouse_pos):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.movement_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < VIRTUAL_WIDTH:
            self.rect.x += self.movement_speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= self.movement_speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < VIRTUAL_HEIGHT:
            self.rect.y += self.movement_speed

        # 直接将玩家位置设置为鼠标位置，而不是渐进式移动
        mouse_x = mouse_pos[0] / scale_factor_x
        mouse_y = mouse_pos[1] / scale_factor_y
        self.rect.centerx = max(0, min(VIRTUAL_WIDTH, mouse_x))
        self.rect.centery = max(0, min(VIRTUAL_HEIGHT, mouse_y))

    def shoot(self):
        if self.shoot_cooldown <= 0:
            if self.power_up_timers["spread"] > 0:
                bullet_straight = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player")
                bullet_left = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player")
                bullet_left.speed_x = -2
                bullet_right = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player")
                bullet_right.speed_x = 2
                self.bullets.add(bullet_straight, bullet_left, bullet_right)
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.base_bullet_speed, "player")
                self.bullets.add(bullet)
            self.shoot_cooldown = self.base_shoot_cooldown
            SHOOT_SOUND.play()

    def collect_power_up(self, power_type):
        if power_type == "life" and self.lives < self.max_lives:
            self.lives += 1
            score.add_bonus(0, "POWER-UP: EXTRA LIFE!")
            POWER_UP_COLLECT_SOUND.play()
        elif power_type in self.power_up_counts:
            if self.power_up_counts[power_type] < self.max_power_ups:
                self.power_up_counts[power_type] += 1
                score.add_bonus(0, f"POWER-UP: {power_type.upper()} COLLECTED! ({self.power_up_counts[power_type]}/5)")
                POWER_UP_COLLECT_SOUND.play()
            else:
                score.add_bonus(0, f"POWER-UP: {power_type.upper()} FULL! (5/5)")

    def activate_power_up(self, power_type):
        if self.power_up_counts[power_type] > 0 and self.power_up_timers[power_type] <= 0:
            self.power_up_counts[power_type] -= 1
            self.power_up_timers[power_type] = 600
            POWER_UP_ACTIVATE_SOUND.play()
            if power_type == "shield":
                self.shield_active = True
                score.add_bonus(0, "POWER-UP: SHIELD ACTIVATED!")
            elif power_type == "spread":
                score.add_bonus(0, "POWER-UP: SPREAD SHOT!")
        elif self.power_up_counts[power_type] == 0:
            POWER_UP_ZERO_SOUND.play()
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
        power_up_images = {"shield": POWER_UP_SHIELD_IMAGE, "spread": POWER_UP_SPREAD_IMAGE}
        for power_type in ["shield", "spread"]:
            icon = pygame.transform.scale(power_up_images[power_type], (int(32 * scale_factor_x), int(32 * scale_factor_y)))
            surface.blit(icon, (20, y_offset))
            count_text = PIXEL_FONT.render(f"{self.power_up_counts[power_type]}/5", True, YELLOW)
            surface.blit(count_text, (60, y_offset + 5))
            y_offset += 60

# --- Button and Checkbox Classes ---
class Button:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, selected_color=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.selected_color = selected_color or GREEN
        self.font = pygame.font.Font("assets/fonts/menu.ttf", 16)
        self.hovered = False
        self.selected = False
        self.scale_factor = 1.0  # For hover scaling

    def draw(self, surface):
        color = self.selected_color if self.selected else (self.active_color if self.hovered else self.inactive_color)
        # Apply slight scaling on hover
        scale = 1.1 if self.hovered else 1.0
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_rect = pygame.Rect(self.rect.x - (scaled_width - self.rect.width) // 2,
                                self.rect.y - (scaled_height - self.rect.height) // 2,
                                scaled_width, scaled_height)
        pygame.draw.rect(surface, color, scaled_rect)
        pygame.draw.rect(surface, WHITE, scaled_rect, 4)
        scaled_font = pygame.font.Font("assets/fonts/menu.ttf", int(16 * scale_factor_y))
        text_surface = scaled_font.render(self.text, True, YELLOW)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        adjusted_x = pos[0] / scale_factor_x
        adjusted_y = pos[1] / scale_factor_y
        return self.rect.collidepoint(adjusted_x, adjusted_y)

class Checkbox:
    def __init__(self, text, x, y):
        self.text = text
        self.rect = pygame.Rect(x, y, 16, 16)
        self.checked = True
        self.font = pygame.font.Font("assets/fonts/menu.ttf", 16)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        if self.checked:
            pygame.draw.line(surface, YELLOW, (self.rect.left + 4, self.rect.top + 4), (self.rect.right - 4, self.rect.bottom - 4), 2)
            pygame.draw.line(surface, YELLOW, (self.rect.right - 4, self.rect.top + 4), (self.rect.left + 4, self.rect.bottom - 4), 2)
        scaled_font = pygame.font.Font("assets/fonts/menu.ttf", int(16 * scale_factor_y))
        text_surface = scaled_font.render(self.text, True, YELLOW)
        surface.blit(text_surface, (self.rect.right + 8, self.rect.top - 2))

    def toggle(self, pos):
        adjusted_x = pos[0] / scale_factor_x
        adjusted_y = pos[1] / scale_factor_y
        if self.rect.collidepoint(adjusted_x, adjusted_y):
            self.checked = not self.checked
            return True
        return False

class CyclingButton:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, options, config_key):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.options = options
        self.current_index = self.options.index(config[config_key])
        self.config_key = config_key
        self.font = pygame.font.Font("assets/fonts/menu.ttf", 16)
        self.hovered = False

    def draw(self, surface):
        color = self.active_color if self.hovered else self.inactive_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 4)
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        display_text = f"{self.text}: {'Normal' if self.options[self.current_index] == 2 else 'Fast'}"
        text_surface = scaled_font.render(display_text, True, YELLOW)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        adjusted_x = pos[0] / scale_factor_x
        adjusted_y = pos[1] / scale_factor_y
        return self.rect.collidepoint(adjusted_x, adjusted_y)

    def cycle(self):
        self.current_index = (self.current_index + 1) % len(self.options)
        new_value = self.options[self.current_index]
        config[self.config_key] = new_value
        save_config(config)
        CLICK_SOUND.play()
        return f"{self.text} Speed Saved!"

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, bullet_type, damage=1):
        super().__init__()
        self.original_image = PLAYER_BULLET_IMAGE if bullet_type == "player" else ENEMY_BULLET_IMAGE
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

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic", difficulty_modifier=1.0):
        super().__init__()
        self.enemy_type = enemy_type
        self.is_boss = (enemy_type == "boss")

        self.original_image = {"basic": ENEMY_IMAGE, "fast": ENEMY_FAST_IMAGE, "boss": BOSS_IMAGE}[enemy_type]
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

    def shoot(self):
        if self.shoot_timer <= 0:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 1.5, "enemy", self.difficulty_modifier)
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
                # print(f"Starting dive from {self.rect}")

        if self.is_diving:
            self.dive_timer += 1
            if self.rect.y < self.dive_target_y:
                self.rect.y += self.dive_speed
                if self.rect.y >= self.dive_target_y:
                    self.rect.y = self.dive_target_y
                self.rect.x = base_x + math.sin(self.dive_timer * 0.2) * 5
                # print(f"Diving: {self.rect}")
            else:
                self.is_diving = False
                self.is_returning = True
                # print(f"Reached dive target, starting return: {self.rect}")

        if self.is_returning:
            target_x = base_x
            target_y = self.original_pos[1]
            if self.rect.y > target_y:
                self.rect.y -= self.return_speed
                self.rect.x = target_x
                # print(f"Returning: {self.rect}, target=({target_x}, {target_y})")
            if self.rect.y <= target_y + 2:
                self.rect.x = target_x
                self.rect.y = target_y
                self.is_returning = False
                # print(f"Snapped to: {self.rect}")

        self.shoot()
        self.bullets.update()
        self.bullets = pygame.sprite.Group([b for b in self.bullets if b.rect.top < VIRTUAL_HEIGHT])

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.bullets.draw(surface)

# --- Level Class ---
class Level:
    def __init__(self):
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

    def calculate_difficulty(self):
        global difficulty_mode
        base_difficulty = {"Easy": 0.8, "Normal": 1.0, "Hard": 1.2}[difficulty_mode]
        self.difficulty_modifier = base_difficulty * (1 + (self.level - 1) * 0.1)
        print(f"Level {self.level} Difficulty Modifier: {self.difficulty_modifier}")

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
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier))

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
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier))
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
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier))
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
                    self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier))
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
                self.enemies.add(Enemy(x, y, enemy_type, self.difficulty_modifier))

    def spawn_wave(self):
        self.wave += 1
        self.calculate_difficulty()
        num_enemies = (self.level * 2 + 1)
        formation = random.choice(self.formations)
        self.spawn_formation(formation, VIRTUAL_WIDTH // 2, 100, num_enemies)
        self.group_dx = 2
        self.move_timer = random.randint(30, 60)
        self.group_x_offset = 0
        self.wave_start_time = pygame.time.get_ticks()
        print(f"Spawned wave {self.wave} of level {self.level}")

    def spawn_boss(self):
        self.calculate_difficulty()
        boss = Enemy(VIRTUAL_WIDTH // 2 - 50, 50, "boss", self.difficulty_modifier)
        self.enemies.empty()
        self.enemies.add(boss)
        self.boss_defeated = False
        self.group_dx = 1
        self.move_timer = random.randint(30, 60)
        self.group_x_offset = 0
        self.wave_start_time = pygame.time.get_ticks()
        print(f"Spawned boss for level {self.level}")

    def next_wave(self):
        global game_state, bonus_text, bonus_timer
        current_time = pygame.time.get_ticks()
        wave_duration = (current_time - self.wave_start_time) / 1000

        if self.wave < self.max_waves:
            if not self.enemies and wave_duration < 10:
                score.add_bonus(200, "SPEED CLEAR BONUS!")
                BONUS_SOUND.play()
            self.spawn_wave()
        elif self.wave == self.max_waves and not self.boss_defeated:
            self.spawn_boss()
        elif self.wave == self.max_waves and self.boss_defeated:
            self.level += 1
            self.wave = 0
            game_state = LEVEL_UP
            print(f"Level up to {self.level}, resetting to wave {self.wave}")

    def spawn_power_up(self, x, y):
        power_types = ["life", "shield", "spread"]
        if random.random() < 0.15:
            power_type = random.choice(power_types)
            self.power_ups.add(PowerUp(x, y, power_type))

# --- Scoring Class ---
class Score:
    def __init__(self, player):
        self.score = 0
        self.font = pygame.font.Font("assets/fonts/menu.ttf", 16)
        self.player = player
        self.bonus_text = ""
        self.bonus_timer = 0
        self.difficulty_message = ""
        self.difficulty_timer = 0

    def add_points(self, points):
        self.score += points

    def add_bonus(self, points, message):
        self.score += points
        self.bonus_text = message
        self.bonus_timer = 120

    def set_difficulty_message(self, message):
        self.difficulty_message = message
        self.difficulty_timer = 180

    def draw(self, surface):
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        score_text = scaled_font.render(f"SCORE: {self.score}", True, YELLOW)
        surface.blit(score_text, (20, 20))

        for i in range(self.player.max_lives):
            x = 20 + i * 30
            y = 60
            scaled_heart_full = pygame.transform.scale(HEART_FULL, (int(HEART_FULL.get_width() * scale_factor_x), int(HEART_FULL.get_height() * scale_factor_y)))
            scaled_heart_empty = pygame.transform.scale(HEART_EMPTY, (int(HEART_EMPTY.get_width() * scale_factor_x), int(HEART_FULL.get_height() * scale_factor_y)))
            if i < self.player.lives:
                surface.blit(scaled_heart_full, (x, y))
            else:
                surface.blit(scaled_heart_empty, (x, y))

        level_text = scaled_font.render(f"LEVEL: {level.level}", True, YELLOW)
        wave_text = scaled_font.render(f"WAVE: {level.wave}/{level.max_waves}", True, YELLOW)
        surface.blit(level_text, (VIRTUAL_WIDTH - 20 - level_text.get_width(), 20))
        surface.blit(wave_text, (VIRTUAL_WIDTH - 20 - wave_text.get_width(), 60))

        if self.bonus_timer > 0:
            bonus_surface = scaled_font.render(self.bonus_text, True, YELLOW)
            bonus_rect = bonus_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 50))
            surface.blit(bonus_surface, bonus_rect)
            self.bonus_timer -= 1

        if self.difficulty_timer > 0:
            difficulty_surface = scaled_font.render(self.difficulty_message, True, YELLOW)
            difficulty_rect = difficulty_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 80))
            surface.blit(difficulty_surface, difficulty_rect)
            self.difficulty_timer -= 1

# --- Game States ---
LANDING = 0
GAME_PLAYING = 1
GAME_OVER = 2
LEVEL_UP = 3
PAUSED = 4
NAME_INPUT = 5

# --- Game Loop ---
def reset_game(play_bgm, difficulty):
    global player, level, score, explosions, background_y, bonus_text, bonus_timer, bgm_position, difficulty_mode, player_name
    difficulty_mode = difficulty
    player = Player()
    level = Level()
    score = Score(player)
    explosions = pygame.sprite.Group()
    background_y = 0
    bonus_text = ""
    bonus_timer = 0
    player_name = ""  # Reset player name
    level.spawn_wave()
    bgm_position = 0
    if play_bgm:
        pygame.mixer.music.play(-1, start=bgm_position)
    return True

def update_highscore(current_score, name):
    global highscores
    highscores.append({"name": name, "score": current_score})
    highscores.sort(key=lambda x: x["score"], reverse=True)
    highscores = highscores[:5]
    save_highscores(highscores)

# Initial setup
player = Player()
level = Level()
score = Score(player)
explosions = pygame.sprite.Group()
game_state = LANDING
play_bgm = True
bonus_text = ""
bonus_timer = 0
level_up_channel = None
level_up_timer = 0
bgm_position = 0
sound_completion_delay = 0
difficulty_mode = "Normal"
running = True
player_name = ""

# UI elements for Landing Page
BUTTON_WIDTH = 192
BUTTON_HEIGHT = 48
CHECKBOX_HEIGHT = 16
DIFFICULTY_BUTTON_WIDTH = 96
DIFFICULTY_BUTTON_HEIGHT = 48
SPACING = 10
TOTAL_HEIGHT = (BUTTON_HEIGHT * 4) + CHECKBOX_HEIGHT + (DIFFICULTY_BUTTON_HEIGHT * 1) + (24 * scale_factor_y) + (SPACING * 5)
START_Y = (VIRTUAL_HEIGHT - TOTAL_HEIGHT) // 2

start_button = Button("START", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN)
bgm_checkbox = Checkbox("MUSIC", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, START_Y + BUTTON_HEIGHT + SPACING)
difficulty_y = START_Y + BUTTON_HEIGHT + CHECKBOX_HEIGHT + (2 * SPACING)
difficulty_easy_button = Button("EASY", VIRTUAL_WIDTH // 2 - (DIFFICULTY_BUTTON_WIDTH * 3 + 2 * SPACING) // 2, difficulty_y, DIFFICULTY_BUTTON_WIDTH, DIFFICULTY_BUTTON_HEIGHT, GRAY, CYAN, GREEN)
difficulty_normal_button = Button("NORMAL", VIRTUAL_WIDTH // 2 - (DIFFICULTY_BUTTON_WIDTH // 2), difficulty_y, DIFFICULTY_BUTTON_WIDTH, DIFFICULTY_BUTTON_HEIGHT, GRAY, CYAN, GREEN)
difficulty_hard_button = Button("HARD", VIRTUAL_WIDTH // 2 + (DIFFICULTY_BUTTON_WIDTH // 2) + SPACING, difficulty_y, DIFFICULTY_BUTTON_WIDTH, DIFFICULTY_BUTTON_HEIGHT, GRAY, CYAN, GREEN)
movement_button = CyclingButton("Movement", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, difficulty_y + DIFFICULTY_BUTTON_HEIGHT + SPACING, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "movement_speed")
shooting_button = CyclingButton("Shooting", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, difficulty_y + DIFFICULTY_BUTTON_HEIGHT + BUTTON_HEIGHT + (2 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "shooting_speed")
bullet_button = CyclingButton("Bullet", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, difficulty_y + DIFFICULTY_BUTTON_HEIGHT + (2 * BUTTON_HEIGHT) + (3 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "bullet_speed")

# UI elements for Pause Menu
PAUSE_TOTAL_HEIGHT = (BUTTON_HEIGHT * 4) + CHECKBOX_HEIGHT + (SPACING * 4)
PAUSE_START_Y = (VIRTUAL_HEIGHT - PAUSE_TOTAL_HEIGHT) // 2

pause_resume_button = Button("RESUME", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN)
pause_quit_button = Button("QUIT", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + BUTTON_HEIGHT + SPACING, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN)
pause_music_checkbox = Checkbox("MUSIC", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (2 * BUTTON_HEIGHT) + (2 * SPACING))
pause_movement_button = CyclingButton("Movement", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (2 * BUTTON_HEIGHT) + CHECKBOX_HEIGHT + (3 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "movement_speed")
pause_shooting_button = CyclingButton("Shooting", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (3 * BUTTON_HEIGHT) + CHECKBOX_HEIGHT + (4 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "shooting_speed")
pause_bullet_button = CyclingButton("Bullet", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (4 * BUTTON_HEIGHT) + CHECKBOX_HEIGHT + (5 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "bullet_speed")

# UI elements for Game Over and Name Input
gameover_restart_button = Button("RESTART", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 80, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN)
gameover_quit_button = Button("QUIT", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 140, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN)
name_submit_button = Button("SUBMIT", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 40, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN)

# Add global variables for landing page enhancements
bg_scroll_y = 0
title_alpha = 0
title_fade_speed = 1
ship_angle = 0
ship_x = VIRTUAL_WIDTH * 0.50
ship_y = VIRTUAL_HEIGHT * 0.1
welcome_text = "Prepare to command your starship against the alien fleet!"
welcome_index = 0
welcome_timer = 0
welcome_visible = False

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                update_scaling()
                player = Player()
                level.enemies = pygame.sprite.Group([Enemy(enemy.rect.x, enemy.rect.y, enemy.enemy_type, level.difficulty_modifier) for enemy in level.enemies])
                explosions = pygame.sprite.Group([Explosion(explosion.rect.centerx / scale_factor_x, explosion.rect.centery / scale_factor_y) for explosion in explosions])

            if game_state == GAME_PLAYING:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_1:
                    player.activate_power_up("shield")
                if event.key == pygame.K_2:
                    player.activate_power_up("spread")
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSED
            elif game_state == NAME_INPUT:
                if event.key == pygame.K_RETURN:
                    update_highscore(score.score, player_name or "Anonymous")
                    reset_game(play_bgm, difficulty_mode)
                    game_state = LANDING
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.unicode.isalnum() or event.unicode in " -_":
                    player_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if game_state == LANDING:
                if start_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    reset_game(play_bgm, difficulty_mode)
                    game_state = GAME_PLAYING
                if bgm_checkbox.toggle(pos):
                    play_bgm = bgm_checkbox.checked
                    if not play_bgm:
                        pygame.mixer.music.stop()
                    else:
                        pygame.mixer.music.play(-1, start=bgm_position)
                if difficulty_easy_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    difficulty_mode = "Easy"
                    difficulty_easy_button.selected = True
                    difficulty_normal_button.selected = False
                    difficulty_hard_button.selected = False
                    print("Difficulty set to Easy")
                if difficulty_normal_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    difficulty_mode = "Normal"
                    difficulty_easy_button.selected = False
                    difficulty_normal_button.selected = True
                    difficulty_hard_button.selected = False
                    print("Difficulty set to Normal")
                if difficulty_hard_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    difficulty_mode = "Hard"
                    difficulty_easy_button.selected = False
                    difficulty_normal_button.selected = False
                    difficulty_hard_button.selected = True
                    print("Difficulty set to Hard")
                if movement_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    bonus_text = movement_button.cycle()
                    bonus_timer = 120
                if shooting_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    bonus_text = shooting_button.cycle()
                    bonus_timer = 120
                if bullet_button.is_clicked(pos):
                    CLICK_SOUND.play()
                    bonus_text = bullet_button.cycle()
                    bonus_timer = 120
            elif game_state == PAUSED:
                if pause_resume_button.is_clicked(pos):
                    game_state = GAME_PLAYING
                if pause_quit_button.is_clicked(pos):
                    running = False
                if pause_music_checkbox.toggle(pos):
                    play_bgm = pause_music_checkbox.checked
                    if not play_bgm:
                        pygame.mixer.music.stop()
                    else:
                        pygame.mixer.music.play(-1, start=bgm_position)
                if pause_movement_button.is_clicked(pos):
                    bonus_text = pause_movement_button.cycle()
                    bonus_timer = 120
                if pause_shooting_button.is_clicked(pos):
                    bonus_text = pause_shooting_button.cycle()
                    bonus_timer = 120
                if pause_bullet_button.is_clicked(pos):
                    bonus_text = pause_bullet_button.cycle()
                    bonus_timer = 120
            elif game_state == GAME_OVER:
                if gameover_restart_button.is_clicked(pos):
                    reset_game(play_bgm, difficulty_mode)
                    game_state = GAME_PLAYING
                if gameover_quit_button.is_clicked(pos):
                    running = False
            elif game_state == NAME_INPUT:
                if name_submit_button.is_clicked(pos):
                    update_highscore(score.score, player_name or "Anonymous")
                    reset_game(play_bgm, difficulty_mode)
                    game_state = LANDING
            elif game_state == GAME_PLAYING and event.button == 1:
                player.shoot()

    # Manage mouse cursor visibility
    if game_state in [LANDING, PAUSED]:
        pygame.mouse.set_visible(True)
    else:
        pygame.mouse.set_visible(False)

    if game_state == LANDING:
        # Dynamic Background: Scrolling space background
        bg_scroll_y += 1
        if bg_scroll_y >= VIRTUAL_HEIGHT:
            bg_scroll_y = 0
        virtual_screen.blit(SPACE_BG_IMAGE, (0, bg_scroll_y - VIRTUAL_HEIGHT), (0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        if bg_scroll_y < VIRTUAL_HEIGHT:
            virtual_screen.blit(SPACE_BG_IMAGE, (0, bg_scroll_y), (0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

        # Animated Title: Fade-in effect
        scaled_font = pygame.font.Font("assets/fonts/menu.ttf", int(24 * scale_factor_y))
        title_text = scaled_font.render("STARSHIP COMMANDER", True, YELLOW)
        title_surface = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
        title_surface.blit(title_text, (0, 0))
        title_surface = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
        title_surface.blit(title_text, (0, 0))
        title_alpha = min(255, title_alpha + title_fade_speed)
        title_surface.set_alpha(title_alpha)
        title_y = START_Y - 40 - title_text.get_height()
        virtual_screen.blit(title_surface, (VIRTUAL_WIDTH // 2 - title_text.get_width() // 2, title_y))

        # Rotating Ship: Slowly rotating player ship
        ship_angle += 1  # Rotate 1 degree per frame for smooth motion
        rotated_ship = pygame.transform.rotate(pygame.transform.scale(PLAYER_IMAGE, (int(PLAYER_IMAGE.get_width() * scale_factor_x), int(PLAYER_IMAGE.get_height() * scale_factor_y))), ship_angle)
        ship_rect = rotated_ship.get_rect(center=(ship_x, ship_y))
        virtual_screen.blit(rotated_ship, ship_rect.topleft)

        # Welcome Message: Typewriter-effect story blurb
        welcome_timer += 1
        if welcome_timer % 5 == 0 and welcome_index < len(welcome_text):
            welcome_index += 1
        if welcome_index > 0:
            welcome_visible = True
        if welcome_visible:
            welcome_font = pygame.font.Font("assets/fonts/menu.ttf", int(12 * scale_factor_y))
            welcome_surface = welcome_font.render(welcome_text[:welcome_index], True, CYAN)
            welcome_box = pygame.Surface((welcome_surface.get_width() + 20, welcome_surface.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(welcome_box, GRAY, welcome_box.get_rect(), border_radius=5)
            welcome_box.blit(welcome_surface, (10, 5))
            virtual_screen.blit(welcome_box, (VIRTUAL_WIDTH // 2 - welcome_box.get_width() // 2, title_y + title_text.get_height() + 2))

        # Reset title alpha when fully opaque
        if title_alpha >= 255:
            title_alpha = 255

        # Display high scores
        highscore_y = START_Y + TOTAL_HEIGHT + 20
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        text = "HIGH SCORE"
        text_width, text_height = scaled_font.size(text)  # Returns (width, height)
        virtual_screen.blit(scaled_font.render(text, True, YELLOW), (VIRTUAL_WIDTH // 2 - text_width // 2, highscore_y - 20))
        for i, entry in enumerate(highscores):
            text = f"{i + 1}. {entry['name']}: {entry['score']}"
            score_surface = scaled_font.render(text, True, YELLOW)
            virtual_screen.blit(score_surface, (VIRTUAL_WIDTH // 2 - score_surface.get_width() // 2, highscore_y + i * 20))

        # Enhanced Buttons: Hover effects
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (mouse_pos[0] / scale_factor_x, mouse_pos[1] / scale_factor_y)
        start_button.hovered = start_button.rect.collidepoint(adjusted_mouse_pos)
        bgm_checkbox.draw(virtual_screen)
        difficulty_easy_button.hovered = difficulty_easy_button.rect.collidepoint(adjusted_mouse_pos)
        difficulty_normal_button.hovered = difficulty_normal_button.rect.collidepoint(adjusted_mouse_pos)
        difficulty_hard_button.hovered = difficulty_hard_button.rect.collidepoint(adjusted_mouse_pos)
        movement_button.hovered = movement_button.rect.collidepoint(adjusted_mouse_pos)
        shooting_button.hovered = shooting_button.rect.collidepoint(adjusted_mouse_pos)
        bullet_button.hovered = bullet_button.rect.collidepoint(adjusted_mouse_pos)

        difficulty_easy_button.selected = (difficulty_mode == "Easy")
        difficulty_normal_button.selected = (difficulty_mode == "Normal")
        difficulty_hard_button.selected = (difficulty_mode == "Hard")

        start_button.draw(virtual_screen)
        bgm_checkbox.draw(virtual_screen)
        difficulty_easy_button.draw(virtual_screen)
        difficulty_normal_button.draw(virtual_screen)
        difficulty_hard_button.draw(virtual_screen)
        movement_button.draw(virtual_screen)
        shooting_button.draw(virtual_screen)
        bullet_button.draw(virtual_screen)

    elif game_state == GAME_PLAYING:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        player.move(keys, mouse_pos)
        player.update()

        level.update_group_movement()
        for enemy in level.enemies:
            enemy.update(player.rect.center, level.group_x_offset)

        enemies_to_remove = []
        for enemy in level.enemies:
            for bullet in player.bullets:
                if pygame.sprite.collide_rect(bullet, enemy):
                    enemy.health -= bullet.damage
                    bullet.kill()
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)
                        points = 50 if not enemy.is_boss else 500
                        score.add_points(points)
                        EXPLOSION_SOUND.play()
                        explosions.add(Explosion(enemy.rect.centerx, enemy.rect.centery))
                        level.spawn_power_up(enemy.rect.centerx, enemy.rect.centery)
                        if enemy.is_boss:
                            level.boss_defeated = True

            for bullet in enemy.bullets:
                if pygame.sprite.collide_rect(bullet, player) and not player.shield_active:
                    player.lives -= 1
                    bullet.kill()
                    LOST_LIFE_SOUND.play()
                    explosions.add(Explosion(player.rect.centerx, player.rect.centery))
                    if player.lives <= 0:
                        pygame.mixer.music.stop()
                        GAME_OVER_SOUND.play()
                        game_state = NAME_INPUT  # Transition to name input instead of GAME_OVER

        for enemy in enemies_to_remove:
            enemy.kill()

        power_up_collisions = pygame.sprite.spritecollide(player, level.power_ups, True)
        for power_up in power_up_collisions:
            player.collect_power_up(power_up.power_type)

        if not level.enemies:
            level.next_wave()

        background_y += scroll_speed
        if background_y >= background_height:
            background_y -= background_height
        source_y = int(background_y) % background_height
        source_rect = pygame.Rect(0, source_y, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        if source_y + VIRTUAL_HEIGHT > background_height:
            first_part_height = background_height - source_y
            virtual_screen.blit(background_surface, (0, 0), pygame.Rect(0, source_y, VIRTUAL_WIDTH, first_part_height))
            second_part_height = VIRTUAL_HEIGHT - first_part_height
            virtual_screen.blit(background_surface, (0, first_part_height), pygame.Rect(0, 0, VIRTUAL_WIDTH, second_part_height))
        else:
            virtual_screen.blit(background_surface, (0, 0), source_rect)

        explosions.update()
        level.power_ups.update()
        player.draw(virtual_screen)
        for enemy in level.enemies:
            enemy.draw(virtual_screen)
        level.power_ups.draw(virtual_screen)
        explosions.draw(virtual_screen)
        score.draw(virtual_screen)

    elif game_state == PAUSED:
        virtual_screen.fill(BLACK)
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        paused_text = scaled_font.render("PAUSED", True, YELLOW)
        paused_y = PAUSE_START_Y - 40 - paused_text.get_height()
        virtual_screen.blit(paused_text, (VIRTUAL_WIDTH // 2 - paused_text.get_width() // 2, paused_y))

        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (mouse_pos[0] / scale_factor_x, mouse_pos[1] / scale_factor_y)
        pause_resume_button.hovered = pause_resume_button.rect.collidepoint(adjusted_mouse_pos)
        pause_quit_button.hovered = pause_quit_button.rect.collidepoint(adjusted_mouse_pos)
        pause_music_checkbox.draw(virtual_screen)
        pause_movement_button.hovered = pause_movement_button.rect.collidepoint(adjusted_mouse_pos)
        pause_shooting_button.hovered = pause_shooting_button.rect.collidepoint(adjusted_mouse_pos)
        pause_bullet_button.hovered = pause_bullet_button.rect.collidepoint(adjusted_mouse_pos)

        pause_resume_button.draw(virtual_screen)
        pause_quit_button.draw(virtual_screen)
        pause_music_checkbox.draw(virtual_screen)
        pause_movement_button.draw(virtual_screen)
        pause_shooting_button.draw(virtual_screen)
        pause_bullet_button.draw(virtual_screen)

    elif game_state == LEVEL_UP:
        virtual_screen.fill(BLACK)
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        level_up_text = scaled_font.render(f"LEVEL UP! LEVEL {level.level}", True, YELLOW)
        virtual_screen.blit(level_up_text, (VIRTUAL_WIDTH // 2 - level_up_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 24))

        if level_up_channel is None:
            # print("Playing LEVEL_CLEAR_SOUND, pausing BGM")
            bgm_position = pygame.mixer.music.get_pos() / 1000
            if play_bgm:
                pygame.mixer.music.pause()
            level_up_channel = LEVEL_CLEAR_SOUND.play()
            level_up_timer = 0
            sound_completion_delay = 0
            score.set_difficulty_message("ENEMIES TOUGHER!")

        level_up_timer += 1

        sound_finished = level_up_channel and not level_up_channel.get_busy()
        min_duration_reached = level_up_timer >= (MINIMUM_SOUND_DURATION * 60)
        timeout_reached = level_up_timer >= 90

        if sound_finished:
            sound_completion_delay += 1
        else:
            sound_completion_delay = 0

        if (min_duration_reached or timeout_reached) and (sound_finished and sound_completion_delay >= 10):
            # print(f"Level up transition: Sound finished: {sound_finished}, Min duration: {min_duration_reached}, Timeout: {timeout_reached}, Delay: {sound_completion_delay}")
            level_up_channel = None
            level_up_timer = 0
            if play_bgm:
                pygame.mixer.music.unpause()
            level.spawn_wave()
            # print(f"Transitioning to level {level.level}, wave {level.wave}")
            game_state = GAME_PLAYING

    elif game_state == NAME_INPUT:
        virtual_screen.fill(BLACK)
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        game_over_text = scaled_font.render("GAME OVER", True, YELLOW)
        score_text = scaled_font.render(f"SCORE: {score.score}", True, YELLOW)
        name_prompt = scaled_font.render("Enter Name:", True, YELLOW)
        name_text = scaled_font.render(player_name + ("" if len(player_name) == 0 else "|"), True, YELLOW)
        virtual_screen.blit(game_over_text, (VIRTUAL_WIDTH // 2 - game_over_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 160))
        virtual_screen.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 120))
        virtual_screen.blit(name_prompt, (VIRTUAL_WIDTH // 2 - name_prompt.get_width() // 2, VIRTUAL_HEIGHT // 2 - 40))
        virtual_screen.blit(name_text, (VIRTUAL_WIDTH // 2 - name_text.get_width() // 2, VIRTUAL_HEIGHT // 2))

        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (mouse_pos[0] / scale_factor_x, mouse_pos[1] / scale_factor_y)
        name_submit_button.hovered = name_submit_button.rect.collidepoint(adjusted_mouse_pos)
        name_submit_button.draw(virtual_screen)

        # Display high scores
        highscore_y = VIRTUAL_HEIGHT // 2 + 120
        text = "HIGH SCORE"
        text_width, text_height = scaled_font.size(text)  # Returns (width, height)
        virtual_screen.blit(scaled_font.render(text, True, YELLOW), (VIRTUAL_WIDTH // 2 - text_width // 2, highscore_y - 20))
        # virtual_screen.blit(scaled_font.render("HIGH SCORES", True, YELLOW), (VIRTUAL_WIDTH // 2 - 80, highscore_y - 20))
        for i, entry in enumerate(highscores):
            text = f"{i + 1}. {entry['name']}: {entry['score']}"
            score_surface = scaled_font.render(text, True, YELLOW)
            virtual_screen.blit(score_surface, (VIRTUAL_WIDTH // 2 - score_surface.get_width() // 2, highscore_y + i * 20))

    elif game_state == GAME_OVER:
        virtual_screen.fill(BLACK)
        scaled_font = pygame.font.Font(FONT_PATH, int(16 * scale_factor_y))
        game_over_text = scaled_font.render("GAME OVER", True, YELLOW)
        score_text = scaled_font.render(f"SCORE: {score.score}", True, YELLOW)
        virtual_screen.blit(game_over_text, (VIRTUAL_WIDTH // 2 - game_over_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 160))
        virtual_screen.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 120))

        # Display high scores
        highscore_y = VIRTUAL_HEIGHT // 2 - 40
        virtual_screen.blit(scaled_font.render("HIGH SCORES", True, YELLOW), (VIRTUAL_WIDTH // 2 - 80, highscore_y - 20))
        for i, entry in enumerate(highscores):
            text = f"{i + 1}. {entry['name']}: {entry['score']}"
            score_surface = scaled_font.render(text, True, YELLOW)
            virtual_screen.blit(score_surface, (VIRTUAL_WIDTH // 2 - score_surface.get_width() // 2, highscore_y + i * 20))

        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (mouse_pos[0] / scale_factor_x, mouse_pos[1] / scale_factor_y)
        gameover_restart_button.hovered = gameover_restart_button.rect.collidepoint(adjusted_mouse_pos)
        gameover_quit_button.hovered = gameover_quit_button.rect.collidepoint(adjusted_mouse_pos)
        gameover_restart_button.draw(virtual_screen)
        gameover_quit_button.draw(virtual_screen)

    # Render the FPS counter
    fps = str(int(clock.get_fps()))
    scaled_font = pygame.font.Font("assets/fonts/menu.ttf", int(16 * scale_factor_y))
    fps_text = scaled_font.render(f"FPS: {fps}", True, YELLOW)
    virtual_screen.blit(fps_text, (20, 100))

    # Final rendering
    screen.fill(BLACK)
    scaled_surface = pygame.transform.scale(virtual_screen, (int(VIRTUAL_WIDTH * scale_factor_x), int(VIRTUAL_HEIGHT * scale_factor_y)))
    screen.blit(scaled_surface, (letterbox_x, letterbox_y))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()