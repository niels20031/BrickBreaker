import pygame
import os
import random
from brickbreaker.constants import *

# =========================
# NIELS – BACKEND
# Bal en BalBeheer (logica voor ballen)
# =========================

class Bal:
    def __init__(self, x, y):
        # Straal van de bal
        self.radius = 40

        # Positie van de bal (float voor vloeiende beweging)
        self.x = float(x)
        self.y = float(y)

        # Snelheid in x- en y-richting
        self.vx = 0.0
        self.vy = 0.0

        # Geeft aan of de bal al is gelanceerd
        self.launched = False

        # Basis- en huidige snelheid
        self.base_speed = 5.0
        self.speed = self.base_speed

        # Rechthoek voor collision-detectie
        self.rect = pygame.Rect(
            x - self.radius, y - self.radius,
            self.radius * 2, self.radius * 2
        )

        # Afbeelding van de bal
        self.image = None
        self.load_image()

    # -------------------------
    # ORKUN
    # Afbeelding laden
    # -------------------------
    def load_image(self):
        BALL_IMAGE = BALL_IMAGE_PATH
        if BALL_IMAGE and os.path.exists(BALL_IMAGE):
            try:
                self.image = pygame.image.load(BALL_IMAGE).convert_alpha()
                self.image = pygame.transform.scale(
                    self.image, (self.radius * 3, self.radius * 3)
                )
            except Exception as e:
                print(f"Could not load ball image: {e}")
                self.image = None

    # -------------------------
    # Lanceer de bal
    # -------------------------
    def launch(self):
        if not self.launched:
            self.launched = True
            angle = random.uniform(-0.5, 0.5)
            self.vx = self.speed * angle
            self.vy = -self.speed

    # -------------------------
    # Update positie van de bal
    # -------------------------
    def update(self, paddle=None):
        # Volg de peddel zolang de bal niet gelanceerd is
        if not self.launched and paddle:
            self.x = paddle.rect.centerx
            self.y = paddle.rect.top - self.radius
            self.rect.center = (int(self.x), int(self.y))
            return

        # Normale beweging na launch
        self.x += self.vx
        self.y += self.vy

        surf = pygame.display.get_surface()
        sw = surf.get_width() if surf else SCREEN_WIDTH

        # Botsing met linker- en rechterrand
        if self.x - self.radius < 0 or self.x + self.radius > sw:
            self.vx = -self.vx
            self.x = max(self.radius, min(sw - self.radius, self.x))

        # Botsing met bovenkant van scherm
        if self.y - self.radius < 0:
            self.vy = -self.vy
            self.y = self.radius

        self.rect.center = (int(self.x), int(self.y))

    # -------------------------
    # Botsing met peddel
    # -------------------------
    def bounce_paddle(self, paddle):
        self.vy = -abs(self.vy)
        hit_pos = (self.x - paddle.rect.left) / paddle.rect.width
        self.vx = (hit_pos - 0.5) * 8
        self.y = paddle.rect.top - self.radius

    # -------------------------
    # Botsing met baksteen
    # -------------------------
    def bounce_brick(self):
        self.vy = -self.vy

    # -------------------------
    # Snelheid aanpassen
    # -------------------------
    def slow_down(self):
        self.speed = self.base_speed * 0.7
        self.vx *= 0.7
        self.vy *= 0.7

    def speed_up(self):
        self.speed = self.base_speed
        self.vx = self.vx / 0.7 if self.vx != 0 else 0
        self.vy = self.vy / 0.7 if self.vy != 0 else 0

    # -------------------------
    # ORKUN
    # Tekenen
    # -------------------------
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (int(self.x) - self.radius, int(self.y) - self.radius))
        else:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)


# =========================
# Beheer van meerdere ballen
# =========================
class BalBeheer:
    def __init__(self):
        # Lijst met actieve ballen
        self.balls = []

    def add_ball(self, ball):
        # Voeg een bal toe
        self.balls.append(ball)

    def remove_ball(self, ball):
        # Verwijder een bal
        if ball in self.balls:
            self.balls.remove(ball)

    def launch_all(self):
        # Lanceer alle ballen
        for ball in self.balls:
            ball.launch()

    def update(self, paddle):
        # Update alle ballen, volg paddle indien nodig
        for ball in self.balls:
            ball.update(paddle)

    def draw(self, screen):
        # Teken alle ballen
        for ball in self.balls:
            ball.draw(screen)

    def clear(self):
        # Verwijder alle ballen
        self.balls.clear()
