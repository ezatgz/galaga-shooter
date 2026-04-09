import pygame
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Virtual resolution (16:9)
VIRTUAL_WIDTH = 1920
VIRTUAL_HEIGHT = 1080
ASPECT_RATIO = VIRTUAL_WIDTH / VIRTUAL_HEIGHT

# Supported resolutions
RESOLUTIONS = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "2K": (2560, 1440),
    "4K": (3840, 2160),
}

# Colors
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (85, 85, 85)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

# Game states
LANDING = 0
GAME_PLAYING = 1
GAME_OVER = 2
LEVEL_UP = 3
PAUSED = 4
NAME_INPUT = 5

# Asset paths
ASSET_PATHS = {
    "shoot_sound": resource_path("assets/sounds/shoot.wav"),
    "explosion_sound": resource_path("assets/sounds/explosion.wav"),
    "lost_life_sound": resource_path("assets/sounds/lost_life.wav"),
    "game_over_sound": resource_path("assets/sounds/game_over.wav"),
    "level_clear_sound": resource_path("assets/sounds/level_clear.wav"),
    "bonus_sound": resource_path("assets/sounds/bonus.wav"),
    "power_up_collect_sound": resource_path("assets/sounds/power_up.wav"),
    "power_up_activate_sound": resource_path("assets/sounds/power_activate.wav"),
    "power_up_zero_sound": resource_path("assets/sounds/power_zero.wav"),
    "click_sound": resource_path("assets/sounds/click.wav"),
    "bgm": resource_path("assets/sounds/bgm.mp3"),
    "player_image": resource_path("assets/images/sprites/player.png"),
    "enemy_image": resource_path("assets/images/sprites/enemy.png"),
    "enemy_fast_image": resource_path("assets/images/sprites/enemy_fast.png"),
    "player_bullet_image": resource_path("assets/images/sprites/player_bullet.png"),
    "enemy_bullet_image": resource_path("assets/images/sprites/enemy_bullet.png"),
    "boss_image": resource_path("assets/images/sprites/boss.png"),
    "explosion_sheet": resource_path("assets/images/sprites/explosion.png"),
    "boss_explosion_sheet": resource_path("assets/images/sprites/explosion_boss.png"),
    "background_image": resource_path("assets/images/backgrounds/background.png"),
    "heart_full": resource_path("assets/images/ui/heart_full.png"),
    "heart_empty": resource_path("assets/images/ui/heart_empty.png"),
    "power_up_life_image": resource_path("assets/images/sprites/power_up_life.png"),
    "power_up_shield_image": resource_path("assets/images/sprites/power_up_shield.png"),
    "power_up_spread_image": resource_path("assets/images/sprites/power_up_spread.png"),
    "space_bg_image": resource_path("assets/images/backgrounds/background.png"),
    "font": resource_path("assets/fonts/menu.ttf"),
}

# Background scrolling
SCROLL_SPEED = 2
BACKGROUND_HEIGHT = VIRTUAL_HEIGHT