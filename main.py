import pygame
import os
import sys

# Initialize Pygame
pygame.font.init()
pygame.mixer.init()

# ==================== CONSTANTS ====================
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Fighters")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)

# Game settings
BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
FPS = 60
MAX_HEALTH = 10

# Paths
ASSETS = os.path.join(os.path.dirname(__file__), "Assets")

# Sounds (safe filenames)
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join(ASSETS, "hit.mp3"))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join(ASSETS, "shoot.mp3"))
BULLET_HIT_SOUND.set_volume(0.4)
BULLET_FIRE_SOUND.set_volume(0.3)

# Fonts
HEALTH_FONT = pygame.font.SysFont("comicsans", 28)
WINNER_FONT = pygame.font.SysFont("comicsans", 80)
MENU_FONT = pygame.font.SysFont("comicsans", 50)
SMALL_FONT = pygame.font.SysFont("comicsans", 24)
TITLE_FONT = pygame.font.SysFont("comicsans", 70)

# Custom events
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Load images
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join(ASSETS, "spaceship_yellow.png"))
YELLOW_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90
)

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join(ASSETS, "spaceship_red.png"))
RED_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270
)

SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSETS, "space.png")), (WIDTH, HEIGHT)
)


# ==================== HELPER FUNCTIONS ====================
def draw_text_center(text, font, color, y_offset=0):
    """Draw text centered on screen"""
    surface = font.render(text, True, color)
    x = WIDTH // 2 - surface.get_width() // 2
    y = HEIGHT // 2 - surface.get_height() // 2 + y_offset
    WIN.blit(surface, (x, y))
    return surface


def draw_health_bar(x, y, health, max_health, color):
    """Draw a modern health bar"""
    bar_width = 160
    bar_height = 18
    fill = int((health / max_health) * bar_width)

    # Background
    pygame.draw.rect(WIN, DARK_GRAY, (x, y, bar_width, bar_height), border_radius=4)
    # Fill
    if fill > 0:
        pygame.draw.rect(WIN, color, (x, y, fill, bar_height), border_radius=4)
    # Border
    pygame.draw.rect(WIN, WHITE, (x, y, bar_width, bar_height), 2, border_radius=4)


def draw_window(red, yellow, yellow_bullets, red_bullets, red_health, yellow_health):
    """Draw the main game screen"""
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    # Health bars
    draw_health_bar(10, 10, yellow_health, MAX_HEALTH, YELLOW)
    draw_health_bar(WIDTH - 170, 10, red_health, MAX_HEALTH, RED)

    # Health text
    yellow_text = HEALTH_FONT.render(f"{yellow_health}", True, WHITE)
    red_text = HEALTH_FONT.render(f"{red_health}", True, WHITE)
    WIN.blit(yellow_text, (175, 8))
    WIN.blit(red_text, (WIDTH - 200 - red_text.get_width(), 8))

    # Ships
    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))

    # Bullets
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, RED, bullet, border_radius=2)
    for bullet in red_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet, border_radius=2)

    pygame.display.update()


def yellow_handle_movement(keys, yellow):
    if keys[pygame.K_a] and yellow.x - VEL > 0:
        yellow.x -= VEL
    if keys[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if keys[pygame.K_w] and yellow.y - VEL > 0:
        yellow.y -= VEL
    if keys[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:
        yellow.y += VEL


def red_handle_movement(keys, red):
    if keys[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    if keys[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:
        red.x += VEL
    if keys[pygame.K_UP] and red.y - VEL > 0:
        red.y -= VEL
    if keys[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15:
        red.y += VEL


def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets[:]:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)


def draw_winner(text):
    """Show winner screen with options"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    WIN.blit(overlay, (0, 0))

    draw_text_center(text, WINNER_FONT, WHITE, y_offset=-40)
    draw_text_center("Press R to Restart  |  ESC to Quit", SMALL_FONT, GREEN, y_offset=50)
    pygame.display.update()


def show_menu():
    """Main menu screen"""
    while True:
        WIN.blit(SPACE, (0, 0))

        # Dark overlay for readability
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        WIN.blit(overlay, (0, 0))

        draw_text_center("GALAXY FIGHTERS", TITLE_FONT, YELLOW, y_offset=-100)
        draw_text_center("2-Player Local Battle", MENU_FONT, WHITE, y_offset=-30)

        draw_text_center("Press SPACE to Start", SMALL_FONT, GREEN, y_offset=40)
        draw_text_center("Press ESC to Quit", SMALL_FONT, GRAY, y_offset=80)

        # Controls hint
        controls = SMALL_FONT.render("Yellow: WASD + L-Ctrl   |   Red: Arrows + R-Ctrl", True, WHITE)
        WIN.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def main_game():
    """Main game loop - returns winner text or None"""
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    red_bullets = []
    yellow_bullets = []

    red_health = MAX_HEALTH
    yellow_health = MAX_HEALTH

    clock = pygame.time.Clock()
    run = True
    winner_text = ""

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        yellow.x + yellow.width,
                        yellow.y + yellow.height // 2 - 2,
                        10, 5
                    )
                    yellow_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        red.x,
                        red.y + red.height // 2 - 2,
                        10, 5
                    )
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                BULLET_HIT_SOUND.play()

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                BULLET_HIT_SOUND.play()

        # Check win condition
        if red_health <= 0:
            winner_text = "YELLOW WINS!"
            run = False
        elif yellow_health <= 0:
            winner_text = "RED WINS!"
            run = False

        keys = pygame.key.get_pressed()
        yellow_handle_movement(keys, yellow)
        red_handle_movement(keys, red)
        handle_bullets(yellow_bullets, red_bullets, yellow, red)

        draw_window(red, yellow, yellow_bullets, red_bullets, red_health, yellow_health)

    return winner_text


def main():
    """Main entry point with menu + restart support"""
    while True:
        show_menu()
        winner = main_game()

        # Winner screen loop
        waiting = True
        while waiting:
            draw_winner(winner)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False  # Restart
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main()
