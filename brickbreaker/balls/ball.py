import pygame
import os
import random
from brickbreaker.constants import *


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
            x - self.radius,
            y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        # Afbeelding van de bal
        self.image = None
        self.load_image()

    def load_image(self):
        # Laad de bal-afbeelding als deze bestaat
        BALL_IMAGE = BALL_IMAGE_PATH
        if BALL_IMAGE and os.path.exists(BALL_IMAGE):
            try:
                self.image = pygame.image.load(BALL_IMAGE).convert_alpha()
                # Schaal de afbeelding naar de juiste grootte
                self.image = pygame.transform.scale(
                    self.image, (self.radius * 2, self.radius * 2)
                )
            except Exception as e:
                print(f"Could not load ball image: {e}")
                self.image = None

    def launch(self):
        # Lanceer de bal met een willekeurige hoek
        if not self.launched:
            self.launched = True
            angle = random.uniform(-0.5, 0.5)
            self.vx = self.speed * angle
            self.vy = -self.speed

    def update(self):
        # Update de positie van de bal als deze is gelanceerd
        if self.launched:
            self.x += self.vx
            self.y += self.vy

            # Haal de schermgrootte op
            surf = pygame.display.get_surface()
            sw = surf.get_width() if surf else SCREEN_WIDTH
            sh = surf.get_height() if surf else SCREEN_HEIGHT

            # Botsing met linker- en rechterrand
            if self.x - self.radius < 0 or self.x + self.radius > sw:
                self.vx = -self.vx
                self.x = max(self.radius, min(sw - self.radius, self.x))

            # Botsing met de bovenkant van het scherm
            if self.y - self.radius < 0:
                self.vy = -self.vy
                self.y = max(self.radius, self.y)

        # Update de collision-rect
        self.rect.center = (int(self.x), int(self.y))

    def bounce_paddle(self, paddle):
        # Laat de bal omhoog stuiteren bij botsing met het paddle
        self.vy = -abs(self.vy)

        # Bepaal waar de bal het paddle raakt (links/rechts)
        hit_pos = (self.x - paddle.rect.left) / paddle.rect.width
        self.vx = (hit_pos - 0.5) * 8

        # Zet de bal net boven het paddle
        self.y = paddle.rect.top - self.radius

    def bounce_brick(self):
        # Keer de verticale snelheid om bij botsing met een steen
        self.vy = -self.vy

    def slow_down(self):
        # Verlaag de snelheid van de bal
        self.speed = self.base_speed * 0.7
        self.vx *= 0.7
        self.vy *= 0.7

    def speed_up(self):
        # Zet de snelheid terug naar normaal
        self.speed = self.base_speed
        self.vx = self.vx / 0.7 if self.vx != 0 else 0
        self.vy = self.vy / 0.7 if self.vy != 0 else 0

    def draw(self, screen):
        # Teken de bal (afbeelding of cirkel)
        if self.image:
            screen.blit(
                self.image,
                (int(self.x) - self.radius, int(self.y) - self.radius)
            )
        else:
            pygame.draw.circle(
                screen, WHITE, (int(self.x), int(self.y)), self.radius
            )


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

    def update(self):
        # Update alle ballen
        for ball in self.balls:
            ball.update()

    def draw(self, screen):
        # Teken alle ballen
        for ball in self.balls:
            ball.draw(screen)

    def clear(self):
        # Verwijder alle ballen
        self.balls.clear()
