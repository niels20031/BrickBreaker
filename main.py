import pygame
import random
import traceback
from enum import Enum
from brickbreaker.balls import Bal, BalBeheer
from brickbreaker.paddles import Peddel
from brickbreaker.bricks import Baksteen
from brickbreaker.constants import *

# Initialiseer pygame en fonts
pygame.init()
res = pygame.display.get_desktop_sizes()

# Gebruik de primaire display als beschikbaar, anders fallback naar pygame.display.Info()
if res:
    width, height = res[0]
else:
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

print(width, height)

# =========================
# NIELS – BACKEND
# Game states (menu, spelen, game over)
# =========================


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3


class Game:
    def __init__(self):
        # Huidige game status
        self.state = GameState.MENU
        self.running = True
        # Clock zorgt voor vaste FPS
        self.clock = pygame.time.Clock()

        # =========================
        # ORKUN – FRONTEND
        # Scherm en fonts
        # =========================
        self.windowed_size = (width, height)
        self.setup_display()

        # Verschillende lettergroottes voor UI
        self.fonts = {
            "l": pygame.font.Font(None, 64),
            "m": pygame.font.Font(None, 48),
            "s": pygame.font.Font(None, 36),
            "t": pygame.font.Font(None, 28),
        }
        

        # Startwaarden instellen
        self.reset_all()

    # =========================
    # ORKUN – FRONTEND
    # Scherm instellen
    # =========================
    def setup_display(self):
        # Windowed mode met vaste resolutie
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Brick Breaker - Reinoud edition - *Limited*")

    
    # =========================
    # NIELS – BACKEND
    # Reset van hele game
    # =========================
    def reset_all(self):
        # Basis game waarden
        self.level = 1
        self.lives = 3
        self.score = 0
        self.reset_game()

    def reset_game(self):
        # Maak peddel aan onderin het scherm
        self.peddel = Peddel(width // 2, height - 50)

        # Beheer van ballen
        self.balls = BalBeheer()
        self.balls.add_ball(Bal(width // 2, height - 80))

        # Genereer bakstenen voor het level
        self.bricks = self.generate_level(self.level)

    # =========================
    # NIELS – BACKEND
    # Level generatie
    # =========================
    def generate_level(self, lvl):
        bricks = []

        # Moeilijkheid neemt toe per level
        rows = min(12, 3 + lvl // 2)
        cols = random.randint(6, 10)

        # Grootte van bakstenen
        bw = max(60, (width - 200) // cols)
        bh = 22

        # Centreer de bakstenen
        start_x = (width - cols * bw) // 2

        for r in range(rows):
            for c in range(cols):
                # Kleur bepaalt sterkte
                color = random.choices(
                    [GREEN, YELLOW, RED],
                    weights=[50, 30 + lvl * 2, 20 + lvl],
                )[0]

                bricks.append(
                    Baksteen(start_x + c * bw, 50 + r * (bh + 4), bw, bh, color)
                )
        return bricks

    # =========================
    # NIELS – BACKEND
    # Input (keyboard)
    # =========================
    def handle_events(self):
        for e in pygame.event.get():
            # Sluit spel via venster
            if e.type == pygame.QUIT:
                self.running = False

            if e.type == pygame.KEYDOWN:
                # ESC: terug naar menu of afsluiten
                if e.key == pygame.K_ESCAPE:
                    if self.state == GameState.MENU:
                       self.running = False
                    else:
                        self.state = GameState.MENU

                # Start spel vanuit menu
                if self.state == GameState.MENU and e.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                ):
                    self.reset_all()
                    self.state = GameState.PLAYING

                # Lanceer bal
                if self.state == GameState.PLAYING and e.key == pygame.K_SPACE:
                    self.balls.launch_all()

    # =========================
    # NIELS – BACKEND
    # Game logica
    # =========================
    def update(self):
        # Alleen updaten tijdens spelen
        if self.state != GameState.PLAYING:
            return

        # Beweeg peddel met pijltjes of A/D
        keys = pygame.key.get_pressed()
        self.peddel.move(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d])
            - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        )

        # Update ballen (volgen peddel indien niet gelanceerd)
        self.balls.update(self.peddel)

        # Check botsingen
        for ball in self.balls.balls[:]:
            # Bal raakt peddel
            if ball.rect.colliderect(self.peddel.rect):
                ball.bounce_paddle(self.peddel)

            # Bal raakt baksteen
            for brick in self.bricks[:]:
                if ball.rect.colliderect(brick.rect):
                    ball.bounce_brick()
                    brick.take_damage_amount(1)

                    # Verwijder baksteen als kapot
                    if brick.is_destroyed():
                        self.bricks.remove(brick)
                        self.score += brick.points

                    break

            # Bal uit scherm
            if ball.rect.top > height:
                self.balls.remove_ball(ball)

        # Geen ballen meer = leven kwijt
        if not self.balls.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                self.balls.add_ball(Bal(self.peddel.rect.centerx, height - 80))

        # Level afgerond
        if not self.bricks:
            self.level += 1
            self.score += 200
            self.bricks = self.generate_level(self.level)

    # =========================
    # ORKUN – FRONTEND
    # Tekenen van schermen
    # =========================
    def draw(self):
        self.screen.fill(DARK_BLUE)

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        else:
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        f = self.fonts
        self.blit_center(f["l"], "BRICK BREAKER", 150)
        self.blit_center(f["s"], "Druk SPATIE om te starten", 320)

    def draw_game(self):
        self.peddel.draw(self.screen)
        self.balls.draw(self.screen)

        for b in self.bricks:
            b.draw(self.screen, self.fonts["t"])

        self.draw_hud()

    def draw_game_over(self):
        self.blit_center(self.fonts["l"], "GAME OVER", 200)
        self.blit_center(self.fonts["m"], f"Score: {self.score}", 300)
        self.blit_center(self.fonts["s"], "Druk SPATIE", 400)

    def draw_hud(self):
        f = self.fonts["s"]
        self.screen.blit(f.render(f"Score: {self.score}", True, YELLOW), (20, 20))
        self.screen.blit(
            f.render(f"Levens: {self.lives}", True, RED), (width - 150, 20)
        )

    def blit_center(self, font, text, y):
        # Tekst horizontaal centreren
        surf = font.render(text, True, WHITE)
        self.screen.blit(surf, ((width - surf.get_width()) // 2, y))

    # =========================
    # NIELS – BACKEND
    # Hoofd game loop
    # =========================
    def run(self):
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception:
                traceback.print_exc()
                self.running = False

            # Beperk FPS
            self.clock.tick(FPS)


# Start het spel
if __name__ == "__main__":
    Game().run()
    pygame.quit()
