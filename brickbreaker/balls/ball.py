import pygame
import os
import random
from brickbreaker.constants import *


class Bal:
    def __init__(self, x, y):
        self.radius = 6
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.launched = False
        self.base_speed = 5.0
        self.speed = self.base_speed
        self.rect = pygame.Rect(x - self.radius, y -
                                self.radius, self.radius * 2, self.radius * 2)
        self.image = None
        self.load_image()

    def load_image(self):
        BALL_IMAGE = BALL_IMAGE_PATH
        if BALL_IMAGE and os.path.exists(BALL_IMAGE):
            try:
                self.image = pygame.image.load(BALL_IMAGE).convert_alpha()
                self.image = pygame.transform.scale(
                    self.image, (self.radius * 2, self.radius * 2))
            except Exception as e:
                print(f"Could not load ball image: {e}")
                self.image = None

    def launch(self):
        if not self.launched:
            self.launched = True
            angle = random.uniform(-0.5, 0.5)
            self.vx = self.speed * angle
            self.vy = -self.speed

    def update(self):
        if self.launched:
            self.x += self.vx
            self.y += self.vy

            surf = pygame.display.get_surface()
            sw = surf.get_width() if surf else SCREEN_WIDTH
            sh = surf.get_height() if surf else SCREEN_HEIGHT

            if self.x - self.radius < 0 or self.x + self.radius > sw:
                self.vx = -self.vx
                self.x = max(self.radius, min(sw - self.radius, self.x))

            if self.y - self.radius < 0:
                self.vy = -self.vy
                self.y = max(self.radius, self.y)

        self.rect.center = (int(self.x), int(self.y))

    def bounce_paddle(self, paddle):
        self.vy = -abs(self.vy)
        hit_pos = (self.x - paddle.rect.left) / paddle.rect.width
        self.vx = (hit_pos - 0.5) * 8
        self.y = paddle.rect.top - self.radius

    def bounce_brick(self):
        self.vy = -self.vy

    def slow_down(self):
        self.speed = self.base_speed * 0.7
        self.vx *= 0.7
        self.vy *= 0.7

    def speed_up(self):
        self.speed = self.base_speed
        self.vx = self.vx / 0.7 if self.vx != 0 else 0
        self.vy = self.vy / 0.7 if self.vy != 0 else 0

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (int(self.x) - self.radius,
                        int(self.y) - self.radius))
        else:
            pygame.draw.circle(
                screen, WHITE, (int(self.x), int(self.y)), self.radius)


class BalBeheer:
    def __init__(self):
        # Lijst met actieve ballen
        self.balls = []

    def add_ball(self, ball):
        self.balls.append(ball)

    def remove_ball(self, ball):
        if ball in self.balls:
            self.balls.remove(ball)

    def launch_all(self):
        for ball in self.balls:
            ball.launch()

    def update(self):
        for ball in self.balls:
            ball.update()

    def draw(self, screen):
        for ball in self.balls:
            ball.draw(screen)

    def clear(self):
        self.balls.clear()
