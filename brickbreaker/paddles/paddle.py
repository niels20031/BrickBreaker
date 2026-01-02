import pygame
from brickbreaker.constants import *

class Peddel:
    def __init__(self, x, y):
        # Basisinstellingen voor de peddel
        self.base_width = 100
        self.width = self.base_width
        self.height = 20
        self.x = x - self.width // 2
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 7
        self.wider_duration = 0
        self.max_wider_duration = 900

    def move(self, direction):
        # Verplaats de peddel zijwaarts
        self.x += direction * self.speed
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def activate_wider(self):
        # Maak de peddel tijdelijk breder
        self.width = int(self.base_width * 1.5)
        self.wider_duration = self.max_wider_duration
        self.update_rect()

    def deactivate_wider(self):
        # Zet terug naar normale breedte
        self.width = self.base_width
        self.wider_duration = 0
        self.update_rect()

    def update(self):
        # Tel de duur van de bredere peddel af
        if self.wider_duration > 0:
            self.wider_duration -= 1
            if self.wider_duration == 0:
                self.deactivate_wider()

    def draw(self, screen):
        color = ORANGE if self.wider_duration > 0 else LIGHT_BLUE
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
