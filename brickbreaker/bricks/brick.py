import pygame
from brickbreaker.constants import *

class Baksteen:
    BRICK_TYPES = {
        GREEN: {"health": 1, "points": 10, "label": "1x"},
        YELLOW: {"health": 2, "points": 25, "label": "2x"},
        RED: {"health": 5, "points": 50, "label": "5x"}
    }

    def __init__(self, x, y, width, height, color):
        # Maak rechthoek en eigenschappen voor de baksteen
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.base_color = color
        self.health = self.BRICK_TYPES[color]["health"]
        self.max_health = self.health
        self.points = self.BRICK_TYPES[color]["points"]
        self.label = self.BRICK_TYPES[color]["label"]

    def take_damage(self):
        # Verlies één levenspunt
        self.take_damage_amount(1)

    def take_damage_amount(self, amount):
        # Trek een hoeveelheid schade af
        self.health -= amount
        if self.health > 0 and self.health == self.max_health - 1:
            # Maak kleur iets lichter bij schade
            self.color = tuple(min(c + 30, 255) for c in self.base_color)

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, screen, font):
        # Teken de baksteen met rand
        pygame.draw.rect(screen, self.color, self.rect, border_radius=3)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=3)
