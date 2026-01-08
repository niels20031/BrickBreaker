import pygame
from brickbreaker.constants import *

# =========================
# NIELS – BACKEND
# Peddel (de speler-balk onderin)
# =========================
class Peddel:
    def __init__(self, x, y):
        # Basisbreedte en hoogte van de peddel
        self.base_width = 100
        self.width = self.base_width
        self.height = 20

        # Positie van de peddel (x = midden, y = vast onderin)
        self.x = x - self.width // 2
        self.y = y

        # Collision-rect voor botsingen met bal
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Beweegsnelheid
        self.speed = 7

    # -------------------------
    # Beweging
    # -------------------------
    def move(self, direction):
        # direction = -1 (links), 0 (stil), 1 (rechts)
        self.x += direction * self.speed

        # Houd peddel binnen scherm
        surf = pygame.display.get_surface()
        max_w = surf.get_width() if surf else SCREEN_WIDTH
        self.x = max(0, min(self.x, max_w - self.width))

        self.update_rect()

    def update_rect(self):
        # Update de collision rect
        surf = pygame.display.get_surface()
        max_w = surf.get_width() if surf else SCREEN_WIDTH
        self.x = max(0, min(self.x, max_w - self.width))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    # -------------------------
    # Teken de peddel
    # -------------------------
    def draw(self, screen):
        # Oranje als power-up actief, anders blauw
        color = ORANGE if self.wider_duration > 0 else LIGHT_BLUE

        # Vul de peddel
        pygame.draw.rect(screen, color, self.rect, border_radius=5)

        # Rand
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
