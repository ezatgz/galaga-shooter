import pygame
from .constants import *

class Score:
    def __init__(self, player, scale_factor_x, scale_factor_y):
        self.score = 0
        self.font = pygame.font.Font(ASSET_PATHS["font"], 16)
        self.player = player
        self.bonus_text = ""
        self.bonus_timer = 0
        self.difficulty_message = ""
        self.difficulty_timer = 0
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y

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
        scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * self.scale_factor_y))
        score_text = scaled_font.render(f"SCORE: {self.score}", True, YELLOW)
        surface.blit(score_text, (20, 20))

        for i in range(self.player.max_lives):
            x = 20 + i * 30
            y = 60
            scaled_heart_full = pygame.transform.scale(pygame.image.load(ASSET_PATHS["heart_full"]).convert_alpha(), (int(32 * self.scale_factor_x), int(32 * self.scale_factor_y)))
            scaled_heart_empty = pygame.transform.scale(pygame.image.load(ASSET_PATHS["heart_empty"]).convert_alpha(), (int(32 * self.scale_factor_x), int(32 * self.scale_factor_y)))
            if i < self.player.lives:
                surface.blit(scaled_heart_full, (x, y))
            else:
                surface.blit(scaled_heart_empty, (x, y))

        level_text = scaled_font.render(f"LEVEL: {self.player.level.level}", True, YELLOW)
        wave_text = scaled_font.render(f"WAVE: {self.player.level.wave}/{self.player.level.max_waves}", True, YELLOW)
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