import pygame, json, os, random, traceback
from enum import Enum
from brickbreaker.balls import Bal, BalBeheer
from brickbreaker.paddles import Peddel
from brickbreaker.bricks import Baksteen
from brickbreaker.powerups import Powerup, PowerupType
from brickbreaker.constants import *

pygame.init()
pygame.font.init()

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.running = True
        self.clock = pygame.time.Clock()

        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setup_display()

        self.fonts = {
            "l": pygame.font.Font(None, 64),
            "m": pygame.font.Font(None, 48),
            "s": pygame.font.Font(None, 36),
            "t": pygame.font.Font(None, 28),
        }

        self.reset_all()

    # ---------- SETUP ----------

    def setup_display(self):
    # Start altijd in windowed mode met vaste resolutie
        self.fullscreen = False
        self.screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    pygame.display.set_caption("Brick Breaker")


    # ---------- GAME RESET ----------

    def reset_all(self):
        self.level = 1
        self.lives = 3
        self.score = 0
        self.reset_game()

    def reset_game(self):
        self.peddel = Peddel(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.balls = BalBeheer()
        self.balls.add_ball(Bal(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.bricks = self.generate_level(self.level)
        self.powerups = []
        self.damage_mult = 1
        self.damage_timer = 0
        self.slow_timer = 0

    # ---------- LEVEL ----------

    def generate_level(self, lvl):
        bricks = []
        rows = min(12, 3 + lvl // 2)
        cols = random.randint(6, 10)
        bw = max(60, (SCREEN_WIDTH - 200) // cols)
        bh = 22

        start_x = (SCREEN_WIDTH - cols * bw) // 2
        for r in range(rows):
            for c in range(cols):
                color = random.choices(
                    [GREEN, YELLOW, RED],
                    weights=[50, 30 + lvl * 2, 20 + lvl],
                )[0]
                bricks.append(Baksteen(
                    start_x + c * bw,
                    50 + r * (bh + 4),
                    bw, bh, color
                ))
        return bricks

    # ---------- INPUT ----------

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.state == GameState.MENU:
                        self.running = False   # spel afsluiten
                    else:
                        self.state = GameState.MENU

                if self.state == GameState.MENU and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.reset_all()
                    self.state = GameState.PLAYING

                if self.state == GameState.PLAYING and e.key == pygame.K_SPACE:
                    self.balls.launch_all()

    # ---------- UPDATE ----------

    def update(self):
        if self.state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.peddel.move((keys[pygame.K_RIGHT] or keys[pygame.K_d]) -
                         (keys[pygame.K_LEFT] or keys[pygame.K_a]))
        self.peddel.update()
        self.balls.update(self.peddel)

        if self.damage_timer > 0:
            self.damage_timer -= 1
        else:
            self.damage_mult = 1

        if self.slow_timer > 0:
            self.slow_timer -= 1

        for ball in self.balls.balls[:]:
            if ball.rect.colliderect(self.peddel.rect):
                ball.bounce_paddle(self.peddel)

            for brick in self.bricks[:]:
                if ball.rect.colliderect(brick.rect):
                    ball.bounce_brick()
                    brick.take_damage_amount(self.damage_mult)
                    if brick.is_destroyed():
                        self.bricks.remove(brick)
                        self.score += brick.points
                        if random.random() < 0.15:
                            self.powerups.append(
                                Powerup(brick.rect.centerx, brick.rect.top, random.choice(list(PowerupType)))
                            )
                    break

            if ball.rect.top > SCREEN_HEIGHT:
                self.balls.remove_ball(ball)

        if not self.balls.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                self.balls.add_ball(Bal(self.peddel.rect.centerx, SCREEN_HEIGHT - 80))

        if not self.bricks:
            self.level += 1
            self.score += 200
            self.bricks = self.generate_level(self.level)

    # ---------- DRAW ----------

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
        self.screen.blit(f.render(f"Levens: {self.lives}", True, RED), (SCREEN_WIDTH - 150, 20))

    def blit_center(self, font, text, y):
        surf = font.render(text, True, WHITE)
        self.screen.blit(surf, ((SCREEN_WIDTH - surf.get_width()) // 2, y))

    # ---------- LOOP ----------

    def run(self):
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception:
                traceback.print_exc()
                self.running = False
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
    pygame.quit()
