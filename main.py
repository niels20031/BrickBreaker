# yo

from brickbreaker.balls import Bal, BalBeheer
from brickbreaker.paddles import Peddel
from brickbreaker.bricks import Baksteen
from brickbreaker.powerups import Powerup, PowerupType
from brickbreaker.constants import *
import pygame
import json
import os
import random
import math
from enum import Enum

# Enum voor spelstatussen


class GameState(Enum):
    MENU = 1
    SETTINGS = 2
    LEVEL_SELECT = 3
    PLAYING = 4
    LEVEL_COMPLETE = 5
    GAME_OVER = 6


# Pygame setup
pygame.init()
# animaties verwijderd

# Settings removed
HIGH_SCORE_FILE = "high_score.json"

# High score data
DEFAULT_HIGH_SCORE = {
    "score": 0,
    "level": 1,
    "date": "Never",
    "infinite_score": 0,
    "infinite_date": "Never"
}


class Game:
    def __init__(self):
        # Instellingen verwijderd; hou minimale staat
        self.settings = {}
        self.high_score_data = self.load_high_score()
        # remember preferred windowed size from constants
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setup_display()
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.current_level = 1
        self.lives = 3
        self.score = 0
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 28)

        # Geluid verwijderd

        # Initialiseer spelobjecten
        self.reset_game()

    def setup_display(self):
        # Try to open fullscreen at the monitor's native resolution.
        # Fall back to the configured SCREEN_WIDTH/HEIGHT when necessary.
        try:
            info = pygame.display.Info()
            native_w, native_h = info.current_w, info.current_h
            # Use native fullscreen mode
            self.screen = pygame.display.set_mode((native_w, native_h), pygame.FULLSCREEN)
            # update module-level width/height so rest of code uses new values
            globals()['SCREEN_WIDTH'] = native_w
            globals()['SCREEN_HEIGHT'] = native_h
            # store sizes for toggling
            self.native_size = (native_w, native_h)
            self.fullscreen = True
        except Exception:
            # fallback
            self.screen = pygame.display.set_mode(self.windowed_size)
            self.native_size = self.windowed_size
            self.fullscreen = False

        pygame.display.set_caption("Brick Breaker")

    # Instellingen verwijderd: load_settings en save_settings verwijderd

    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return DEFAULT_HIGH_SCORE.copy()
        return DEFAULT_HIGH_SCORE.copy()

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(self.high_score_data, f, indent=2)

    def update_high_score(self):
        from datetime import datetime
        # Werk normale of oneindige highscore bij, afhankelijk van modus
        if getattr(self, 'infinite_mode', False):
            if self.score > self.high_score_data.get("infinite_score", 0):
                self.high_score_data["infinite_score"] = self.score
                self.high_score_data["infinite_date"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M")
                self.save_high_score()
        else:
            if self.score > self.high_score_data.get("score", 0):
                self.high_score_data["score"] = self.score
                self.high_score_data["level"] = self.current_level
                self.high_score_data["date"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M")
                self.save_high_score()

    # Geluidsafhandeling verwijderd

    def apply_powerup(self, powerup):
        if powerup.type == PowerupType.WIDER_PADDLE:
            self.peddel.activate_wider()
        elif powerup.type == PowerupType.MULTI_BALL:
            # Dupliceer alle bestaande ballen
            new_balls = []
            for bal in self.bal_beheer.balls:
                new_bal = Bal(bal.x, bal.y)
                new_bal.vx = -bal.vx
                new_bal.vy = bal.vy
                new_bal.launched = bal.launched
                new_balls.append(new_bal)
            for bal in new_balls:
                self.bal_beheer.add_ball(bal)
        elif powerup.type == PowerupType.SLOW_BALL:
            self.slow_ball_active = True
            self.slow_ball_duration = 300
            for bal in self.bal_beheer.balls:
                bal.slow_down()
        elif powerup.type == PowerupType.DOUBLE_DAMAGE:
            # dubbele schade voor een tijd
            self.damage_multiplier = 2
            self.damage_duration = 600  # frames (~10s bij 60fps)

    def reset_game(self):
        self.peddel = Peddel(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.bal_beheer = BalBeheer()
        self.bal_beheer.add_ball(Bal(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.bricks = self.create_level(self.current_level)
        self.powerups = []
        # animations removed
        self.game_active = True
        self.slow_ball_active = False
        self.slow_ball_duration = 0
        self.damage_multiplier = 1
        self.damage_duration = 0

    def create_level(self, level):
        bricks = []
        rows = 2 + level
        cols = 8
        brick_width = 140
        brick_height = 25
        padding = 5
        start_x = (SCREEN_WIDTH - (cols * (brick_width + padding))) // 2
        start_y = 50

        # Distribute brick colors: Green (1 hit), Yellow (2 hits), Red (5 hits)
        brick_colors = []
        for row in range(rows):
            if row < rows // 3:
                brick_colors.extend([GREEN] * cols)
            elif row < 2 * rows // 3:
                brick_colors.extend([YELLOW] * cols)
            else:
                brick_colors.extend([RED] * cols)

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_width + padding)
                y = start_y + row * (brick_height + padding)
                color = [GREEN, YELLOW, RED][min(
                    row // (max(1, rows // 3)), 2)]
                bricks.append(Baksteen(x, y, brick_width, brick_height, color))

        return bricks

    def create_infinite_level(self, level_index):
        """Generate a random brick layout for infinite mode.
        Difficulty scales with level_index: more rows/stronger bricks.
        """
        bricks = []
        # Increase rows slowly with level, add randomness
        base_rows = 3
        rows = min(12, base_rows + level_index // 2 + random.randint(0, 2))
        cols = random.randint(6, 10)
        padding = 4
        # Make brick width fit the screen based on cols
        total_padding = (cols - 1) * padding
        brick_width = max(60, (SCREEN_WIDTH - 200 - total_padding) // cols)
        brick_height = 22
        start_x = (SCREEN_WIDTH -
                   (cols * (brick_width + padding) - padding)) // 2
        start_y = 40

        # Randomize brick strengths with higher chance for stronger bricks as level increases
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (brick_width + padding)
                y = start_y + row * (brick_height + padding)
                # probability weights for GREEN, YELLOW, RED
                red_chance = min(0.15 + level_index * 0.01, 0.5)
                yellow_chance = min(0.25 + level_index * 0.02, 0.5)
                r = random.random()
                if r < red_chance:
                    color = RED
                elif r < red_chance + yellow_chance:
                    color = YELLOW
                else:
                    color = GREEN
                bricks.append(Baksteen(x, y, brick_width, brick_height, color))

        return bricks

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # save progress and exit
                try:
                    self.update_high_score()
                except Exception:
                    pass
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Toggle fullscreen with F11
                if event.key == pygame.K_F11:
                    try:
                        if getattr(self, 'fullscreen', False):
                            # switch to windowed
                            self.screen = pygame.display.set_mode(self.windowed_size)
                            globals()['SCREEN_WIDTH'], globals()['SCREEN_HEIGHT'] = self.windowed_size
                            self.fullscreen = False
                        else:
                            # switch to native fullscreen
                            self.screen = pygame.display.set_mode(self.native_size, pygame.FULLSCREEN)
                            globals()['SCREEN_WIDTH'], globals()['SCREEN_HEIGHT'] = self.native_size
                            self.fullscreen = True
                    except Exception:
                        pass

                if event.key == pygame.K_ESCAPE:
                    # From menu: quit. From other screens: back to menu.
                    if self.state == GameState.MENU:
                        try:
                            self.update_high_score()
                        except Exception:
                            pass
                        self.running = False
                    elif self.state == GameState.PLAYING:
                        self.state = GameState.MENU
                    elif self.state in [GameState.LEVEL_SELECT]:
                        self.state = GameState.MENU
                    elif self.state in [GameState.LEVEL_COMPLETE, GameState.GAME_OVER]:
                        self.state = GameState.MENU
                        self.current_level = 1
                        self.lives = 3
                        self.score = 0

                # Menu/Settings input
                if self.state == GameState.MENU:
                    # Start infinite mode on SPACE/RETURN
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_i:
                        self.infinite_mode = True
                        self.current_level = 1
                        self.lives = 3
                        self.score = 0
                        self.reset_game()
                        # replace bricks with an infinite-generated level
                        self.bricks = self.create_infinite_level(
                            self.current_level)
                        self.state = GameState.PLAYING

                # Settings removed

                # Level select input
                elif self.state == GameState.LEVEL_SELECT:
                    if event.key == pygame.K_1:
                        self.current_level = 1
                        self.lives = 3
                        self.score = 0
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_2:
                        self.current_level = 2
                        self.lives = 3
                        self.score = 0
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_3:
                        self.current_level = 3
                        self.lives = 3
                        self.score = 0
                        self.reset_game()
                        self.state = GameState.PLAYING

                # Game input
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.bal_beheer.launch_all()

                # Level complete
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.current_level += 1
                        if self.current_level > 5:
                            self.state = GameState.MENU
                            self.current_level = 1
                            self.lives = 3
                            self.score = 0
                        else:
                            self.reset_game()
                            self.state = GameState.PLAYING

                # Game over
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.current_level = 1
                        self.lives = 3
                        self.score = 0
                        self.reset_game()
                        self.state = GameState.LEVEL_SELECT

    def update(self):
        if self.state == GameState.PLAYING and self.game_active:
            # Verplaats peddel
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.peddel.move(-1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.peddel.move(1)

            self.peddel.update()

            # Update ballen
            self.bal_beheer.update()

            # Update slow ball effect
            if self.slow_ball_active:
                self.slow_ball_duration -= 1
                if self.slow_ball_duration <= 0:
                    self.slow_ball_active = False
                    for ball in self.bal_beheer.balls:
                        ball.speed_up()

            # Update double-damage effect
            if getattr(self, 'damage_duration', 0) > 0:
                self.damage_duration -= 1
                if self.damage_duration <= 0:
                    self.damage_multiplier = 1

            # Update power-ups
            for powerup in self.powerups[:]:
                powerup.update()
                if powerup.is_collected(self.peddel):
                    self.apply_powerup(powerup)
                    self.powerups.remove(powerup)
                elif powerup.rect.top > SCREEN_HEIGHT:
                    self.powerups.remove(powerup)

            # animations removed

            # Check each ball
            balls_to_remove = []
            for ball in self.bal_beheer.balls:
                # Ball-paddle collision
                if ball.rect.colliderect(self.peddel.rect):
                    ball.bounce_paddle(self.peddel)

                # Ball-brick collision
                for brick in self.bricks[:]:
                    if ball.rect.colliderect(brick.rect):
                        ball.bounce_brick()
                        # Pas schadevermenigvuldiger toe als actief
                        try:
                            dmg = int(getattr(self, 'damage_multiplier', 1))
                        except Exception:
                            dmg = 1
                        brick.take_damage_amount(dmg)

                        if brick.is_destroyed():
                            # verwijder baksteen zonder animatie
                            self.bricks.remove(brick)
                            self.score += brick.points
                            # Update high score immediately when score increases
                            try:
                                self.update_high_score()
                            except Exception:
                                pass
                            # kans op power-up
                            if random.random() < 0.15:  # 15% kans
                                powerup_type = random.choice(
                                    [PowerupType.WIDER_PADDLE, PowerupType.MULTI_BALL, PowerupType.SLOW_BALL])
                                # spawn power-up iets boven de vernietigde baksteen zodat hij naar beneden valt
                                spawn_x = brick.rect.centerx
                                spawn_y = brick.rect.top - 20
                                pu = Powerup(spawn_x, spawn_y, powerup_type)
                                pu.velocity = 3
                                self.powerups.append(pu)
                        break

                # Bal uit scherm
                if ball.rect.top > SCREEN_HEIGHT:
                    balls_to_remove.append(ball)

            # Verwijder ballen die uit het scherm zijn
            for ball in balls_to_remove:
                self.bal_beheer.remove_ball(ball)

            # Als er geen ballen meer zijn, verlies een leven
            if len(self.bal_beheer.balls) == 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                    self.update_high_score()
                else:
                    new_ball = Bal(int(self.peddel.rect.centerx),
                                   SCREEN_HEIGHT - 80)
                    self.bal_beheer.add_ball(new_ball)

            # Level complete
            if len(self.bricks) == 0:
                # Oneindige modus: genereer nieuw niveau
                if getattr(self, 'infinite_mode', False):
                    self.current_level += 1
                    self.score += 200 * self.current_level
                    try:
                        self.update_high_score()
                    except Exception:
                        pass
                    # generate next infinite level
                    self.bricks = self.create_infinite_level(
                        self.current_level)
                else:
                    self.state = GameState.LEVEL_COMPLETE
                    self.score += 500 * self.current_level
                    try:
                        self.update_high_score()
                    except Exception:
                        pass

    def draw(self):
        self.screen.fill(DARK_BLUE)

        if self.state == GameState.MENU:
            self.draw_menu()

        elif self.state == GameState.LEVEL_SELECT:
            self.draw_level_select()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        title = self.font_large.render("BRICK BREAKER", True, WHITE)
        self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 150))

        high_score_text = self.font_small.render(
            f"Top Score: {self.high_score_data.get('score',0)}", True, YELLOW)
        self.screen.blit(
            high_score_text, ((SCREEN_WIDTH - high_score_text.get_width()) // 2, 240))

        infinite_text = self.font_small.render(
            f"Oneindige Top: {self.high_score_data.get('infinite_score',0)}", True, LIGHT_BLUE)
        self.screen.blit(
            infinite_text, ((SCREEN_WIDTH - infinite_text.get_width()) // 2, 280))

        start_text = self.font_medium.render(
            "Druk SPATIE om Oneindige Modus te starten", True, LIGHT_BLUE)
        self.screen.blit(
            start_text, ((SCREEN_WIDTH - start_text.get_width()) // 2, 320))

        quit_text = self.font_tiny.render(
            "Druk ESC om af te sluiten", True, GRAY)
        self.screen.blit(
            quit_text, ((SCREEN_WIDTH - quit_text.get_width()) // 2, 500))

    def draw_level_select(self):
        title = self.font_large.render("KIES NIVEAU", True, WHITE)
        self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 100))

        for level in range(1, 6):
            if level <= 3:
                y = 300
                x = 300 + (level - 1) * 250
                color = YELLOW if level <= 3 else GRAY
                level_text = self.font_medium.render(
                    f"Niveau {level}", True, color)
                self.screen.blit(
                    level_text, (x - level_text.get_width() // 2, y))

        level_3_text = self.font_medium.render("Niveau 3", True, GRAY)
        self.screen.blit(
            level_3_text, ((SCREEN_WIDTH - level_3_text.get_width()) // 2, 400))

        instructions = self.font_small.render(
            "Druk 1, 2, of 3 om te starten", True, LIGHT_BLUE)
        self.screen.blit(
            instructions, ((SCREEN_WIDTH - instructions.get_width()) // 2, 550))

    def draw_game(self):
        self.peddel.draw(self.screen)
        self.bal_beheer.draw(self.screen)

        for brick in self.bricks:
            brick.draw(self.screen, self.font_tiny)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        # HUD
        level_text = self.font_small.render(
            f"Niveau: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (20, 20))

        lives_text = self.font_small.render(f"Levens: {self.lives}", True, RED)
        self.screen.blit(lives_text, (SCREEN_WIDTH -
                         lives_text.get_width() - 20, 20))

        score_text = self.font_small.render(
            f"Score: {self.score}", True, YELLOW)
        self.screen.blit(
            score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 20))

        # Show high score
        high_score_text = self.font_tiny.render(
            f"Top Score: {self.high_score_data['score']}", True, LIGHT_BLUE)
        self.screen.blit(high_score_text, (20, 70))

        # Show ball count if multiple balls
        if len(self.bal_beheer.balls) > 1:
            balls_text = self.font_tiny.render(
                f"Ballen: {len(self.bal_beheer.balls)}", True, LIGHT_BLUE)
            self.screen.blit(balls_text, (20, 110))

        # Show paddle boost status
        if self.peddel.wider_duration > 0:
            boost_text = self.font_tiny.render("BREDERE PEDDEL", True, ORANGE)
            self.screen.blit(
                boost_text, ((SCREEN_WIDTH - boost_text.get_width()) // 2, 70))

        # Show slow ball status
        if self.slow_ball_active:
            slow_text = self.font_tiny.render("TRAAGMODUS", True, PURPLE)
            self.screen.blit(slow_text, (SCREEN_WIDTH -
                             slow_text.get_width() - 20, 70))

        if len(self.bal_beheer.balls) > 0 and not self.bal_beheer.balls[0].launched:
            launch_text = self.font_tiny.render(
                "Druk SPATIE om te lanceren", True, LIGHT_BLUE)
            self.screen.blit(
                launch_text, ((SCREEN_WIDTH - launch_text.get_width()) // 2, SCREEN_HEIGHT - 30))

    def draw_level_complete(self):
        complete_text = self.font_large.render("NIVEAU VOLTOOID!", True, GREEN)
        self.screen.blit(
            complete_text, ((SCREEN_WIDTH - complete_text.get_width()) // 2, 150))

        score_text = self.font_medium.render(
            f"Score: {self.score}", True, YELLOW)
        self.screen.blit(
            score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 300))

        if self.current_level >= 5:
            next_text = self.font_small.render(
                "Je hebt alle niveaus verslagen!", True, LIGHT_BLUE)
        else:
            next_text = self.font_small.render(
                f"Volgende: Niveau {self.current_level + 1}", True, LIGHT_BLUE)
        self.screen.blit(
            next_text, ((SCREEN_WIDTH - next_text.get_width()) // 2, 400))

        continue_text = self.font_small.render(
            "Druk SPATIE om door te gaan", True, YELLOW)
        self.screen.blit(
            continue_text, ((SCREEN_WIDTH - continue_text.get_width()) // 2, 500))

    def draw_game_over(self):
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        self.screen.blit(
            game_over_text, ((SCREEN_WIDTH - game_over_text.get_width()) // 2, 150))

        score_text = self.font_medium.render(
            f"Uiteindelijke Score: {self.score}", True, YELLOW)
        self.screen.blit(
            score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 300))

        level_text = self.font_small.render(
            f"Niveau bereikt: {self.current_level}", True, LIGHT_BLUE)
        self.screen.blit(
            level_text, ((SCREEN_WIDTH - level_text.get_width()) // 2, 400))

        restart_text = self.font_small.render(
            "Druk SPATIE om terug naar menu", True, YELLOW)
        self.screen.blit(
            restart_text, ((SCREEN_WIDTH - restart_text.get_width()) // 2, 500))

    def run(self):
        dt = 0
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            dt = self.clock.tick(FPS) / 1000


# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
