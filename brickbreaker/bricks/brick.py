import pygame
from brickbreaker.constants import *

# =========================
# ORKUN – FRONTEND
# Baksteen (visueel object op het speelveld)
# =========================
class Baksteen:
    # Definieer type bakstenen met gezondheid, punten en label
    BRICK_TYPES = {
        GREEN: {"health": 1, "points": 10, "label": "1x"},
        YELLOW: {"health": 2, "points": 25, "label": "2x"},
        RED: {"health": 5, "points": 50, "label": "5x"}
    }

    def __init__(self, x, y, width, height, color):
        # Rechthoek en eigenschappen
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.base_color = color  # originele kleur onthouden
        self.health = self.BRICK_TYPES[color]["health"]
        self.max_health = self.health
        self.points = self.BRICK_TYPES[color]["points"]
        self.label = self.BRICK_TYPES[color]["label"]

    # -------------------------
    # Schade logica
    # -------------------------
    def take_damage(self):
        # Verlies 1 levenspunt
        self.take_damage_amount(1)

    def take_damage_amount(self, amount):
        # Trek een aantal punten af
        self.health -= amount

        # Licht de kleur iets op bij eerste schade
        if self.health > 0 and self.health == self.max_health - 1:
            self.color = tuple(min(c + 30, 255) for c in self.base_color)

    def is_destroyed(self):
        # Terug True als de baksteen kapot is
        return self.health <= 0

    # -------------------------
    # Tekenen
    # -------------------------
    def draw(self, screen, font):
        # Vul de baksteen
        pygame.draw.rect(screen, self.color, self.rect, border_radius=3)

        # Rand
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=3)
