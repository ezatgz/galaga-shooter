import pygame
from .constants import *

class Button:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, selected_color=None, scale_factor_y=1.0):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.selected_color = selected_color or GREEN
        self.font = pygame.font.Font(ASSET_PATHS["font"], 16)
        self.hovered = False
        self.selected = False
        self.scale_factor_y = scale_factor_y

    def draw(self, surface):
        color = self.selected_color if self.selected else (self.active_color if self.hovered else self.inactive_color)
        scale = 1.1 if self.hovered else 1.0
        scaled_width = int(self.rect.width * scale)
        scaled_height = int(self.rect.height * scale)
        scaled_rect = pygame.Rect(self.rect.x - (scaled_width - self.rect.width) // 2,
                                self.rect.y - (scaled_height - self.rect.height) // 2,
                                scaled_width, scaled_height)
        pygame.draw.rect(surface, color, scaled_rect)
        pygame.draw.rect(surface, WHITE, scaled_rect, 4)
        scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * self.scale_factor_y))
        text_surface = scaled_font.render(self.text, True, YELLOW)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos, scale_factor_x, scale_factor_y):
        adjusted_x = pos[0] / scale_factor_x
        adjusted_y = pos[1] / scale_factor_y
        return self.rect.collidepoint(adjusted_x, adjusted_y)

class Checkbox:
    def __init__(self, text, x, y, scale_factor_y=1.0):
        self.text = text
        self.rect = pygame.Rect(x, y, 16, 16)
        self.checked = True
        self.font = pygame.font.Font(ASSET_PATHS["font"], 16)
        self.scale_factor_y = scale_factor_y

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        if self.checked:
            pygame.draw.line(surface, YELLOW, (self.rect.left + 4, self.rect.top + 4), (self.rect.right - 4, self.rect.bottom - 4), 2)
            pygame.draw.line(surface, YELLOW, (self.rect.right - 4, self.rect.top + 4), (self.rect.left + 4, self.rect.bottom - 4), 2)
        scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * self.scale_factor_y))
        text_surface = scaled_font.render(self.text, True, YELLOW)
        surface.blit(text_surface, (self.rect.right + 8, self.rect.top - 2))

    def toggle(self, pos, scale_factor_x, scale_factor_y):
        adjusted_x = pos[0] / scale_factor_x
        adjusted_y = pos[1] / scale_factor_y
        if self.rect.collidepoint(adjusted_x, adjusted_y):
            self.checked = not self.checked
            return True
        return False

class CyclingButton:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, options, config_key, scale_factor_y=1.0):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.options = options
        self.current_index = 0  # Will be set by main
        self.config_key = config_key
        self.font = pygame.font.Font(ASSET_PATHS["font"], 16)
        self.hovered = False
        self.scale_factor_y = scale_factor_y

    def draw(self, surface):
        color = self.active_color if self.hovered else self.inactive_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 4)
        scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * self.scale_factor_y))
        display_text = f"{self.text}: {'Normal' if self.options[self.current_index] == 2 else 'Fast'}"
        text_surface = scaled_font.render(display_text, True, YELLOW)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos, scale_factor_x, scale_factor_y):
        adjusted_x = pos[0] / scale_factor_x
        adjusted_y = pos[1] / scale_factor_y
        return self.rect.collidepoint(adjusted_x, adjusted_y)

    def cycle(self, config):
        self.current_index = (self.current_index + 1) % len(self.options)
        new_value = self.options[self.current_index]
        config[self.config_key] = new_value
        return f"{self.text} Speed Saved!"