import pygame

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
    "shoot_sound": "assets/sounds/shoot.wav",
    "explosion_sound": "assets/sounds/explosion.wav",
    "lost_life_sound": "assets/sounds/lost_life.wav",
    "game_over_sound": "assets/sounds/game_over.wav",
    "level_clear_sound": "assets/sounds/level_clear.wav",
    "bonus_sound": "assets/sounds/bonus.wav",
    "power_up_collect_sound": "assets/sounds/power_up.wav",
    "power_up_activate_sound": "assets/sounds/power_activate.wav",
    "power_up_zero_sound": "assets/sounds/power_zero.wav",
    "click_sound": "assets/sounds/click.wav",
    "bgm": "assets/sounds/bgm.mp3",
    "player_image": "assets/images/sprites/player.png",
    "enemy_image": "assets/images/sprites/enemy.png",
    "enemy_fast_image": "assets/images/sprites/enemy_fast.png",
    "player_bullet_image": "assets/images/sprites/player_bullet.png",
    "enemy_bullet_image": "assets/images/sprites/enemy_bullet.png",
    "boss_image": "assets/images/sprites/boss.png",
    "explosion_sheet": "assets/images/sprites/explosion.png",
    "background_image": "assets/images/backgrounds/background.png",
    "heart_full": "assets/images/ui/heart_full.png",
    "heart_empty": "assets/images/ui/heart_empty.png",
    "power_up_life_image": "assets/images/sprites/power_up_life.png",
    "power_up_shield_image": "assets/images/sprites/power_up_shield.png",
    "power_up_spread_image": "assets/images/sprites/power_up_spread.png",
    "space_bg_image": "assets/images/backgrounds/background.png",
    "font": "assets/fonts/menu.ttf",
}

# Background scrolling
SCROLL_SPEED = 2
BACKGROUND_HEIGHT = VIRTUAL_HEIGHT