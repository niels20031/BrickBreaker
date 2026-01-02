import pygame
from enum import Enum
from brickbreaker.constants import *

class PowerupType(Enum):
    WIDER_PADDLE = 1
    MULTI_BALL = 2
    SLOW_BALL = 3
    DOUBLE_DAMAGE = 4

class Powerup:
    def __init__(self, x, y, powerup_type):
        self.rect = pygame.Rect(x, y, 30, 15)
        self.type = powerup_type
        self.velocity = 2
        self.colors = {
            PowerupType.WIDER_PADDLE: BLUE,
            PowerupType.MULTI_BALL: RED,
            PowerupType.SLOW_BALL: PURPLE,
            PowerupType.DOUBLE_DAMAGE: ORANGE
        }
        self.color = self.colors.get(powerup_type, YELLOW)
        self.active = True
    
    def update(self):
        self.rect.y += self.velocity
    
    def is_collected(self, paddle):
        return self.rect.colliderect(paddle.rect)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=3)
        pygame.draw.rect(screen, WHITE, self.rect, 1, border_radius=3)
