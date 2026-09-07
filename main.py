import pygame
import os
import sys
import random
import math

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
RED = (255, 60, 60)
YELLOW = (255, 230, 50)
GREEN = (80, 255, 120)
CYAN = (100, 220, 255)
ORANGE = (255, 140, 40)
PURPLE = (180, 80, 255)
PINK = (255, 100, 180)
DARK = (15, 15, 30)

# Game settings
BORDER = pygame.Rect(WIDTH // 2 - 4, 0, 8, HEIGHT)
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
VEL = 5
BULLET_VEL = 9
MAX_BULLETS = 3
FPS = 60
MAX_HEALTH = 10

ASSETS = os.path.join(os.path.dirname(__file__), "Assets")

# Sounds
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join(ASSETS, "hit.mp3"))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join(ASSETS, "shoot.mp3"))
BULLET_HIT_SOUND.set_volume(0.35)
BULLET_FIRE_SOUND.set_volume(0.25)

# Fonts
HEALTH_FONT = pygame.font.SysFont("comicsans", 26)
WINNER_FONT = pygame.font.SysFont("comicsans", 78)
MENU_FONT = pygame.font.SysFont("comicsans", 42)
SMALL_FONT = pygame.font.SysFont("comicsans", 22)
TITLE_FONT = pygame.font.SysFont("comicsans", 68)
TINY_FONT = pygame.font.SysFont("comicsans", 18)

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Images
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join(ASSETS, "spaceship_yellow.png")).convert_alpha()
YELLOW_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90
)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join(ASSETS, "spaceship_red.png")).convert_alpha()
RED_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270
)
SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join(ASSETS, "space.png")).convert(), (WIDTH, HEIGHT)
)


# ==================== EFFECTS ====================
class Particle:
    def __init__(self, x, y, color, velocity=None, life=None, size=None, shape="circle"):
        self.x = x
        self.y = y
        self.color = color
        self.shape = shape  # "circle", "square", "spark"
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.2, 6.5)
        self.vx = math.cos(angle) * speed if velocity is None else velocity[0]
        self.vy = math.sin(angle) * speed if velocity is None else velocity[1]
        self.life = life if life else random.randint(18, 42)
        self.max_life = self.life
        self.size = size if size else random.uniform(2.0, 5.5)
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.vy += 0.04  # slight gravity
        self.life -= 1
        self.size = max(0.4, self.size * 0.97)
        self.rot += self.rot_speed

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        s = max(1, int(self.size))
        # Outer soft glow
        glow_size = s * 3
        glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color[:3], alpha // 4), (glow_size, glow_size), glow_size)
        surface.blit(glow, (int(self.x) - glow_size, int(self.y) - glow_size))

        if self.shape == "spark":
            # Thin elongated spark
            length = s * 3
            points = [
                (self.x + math.cos(math.radians(self.rot)) * length,
                 self.y + math.sin(math.radians(self.rot)) * length),
                (self.x - math.cos(math.radians(self.rot)) * length * 0.4,
                 self.y - math.sin(math.radians(self.rot)) * length * 0.4),
            ]
            if alpha > 30:
                pygame.draw.line(surface, (*self.color[:3], alpha), points[0], points[1], max(1, s // 2))
        elif self.shape == "square":
            rect = pygame.Rect(int(self.x) - s, int(self.y) - s, s * 2, s * 2)
            pygame.draw.rect(surface, (*self.color[:3], alpha), rect)
        else:
            pygame.draw.circle(surface, (*self.color[:3], alpha), (int(self.x), int(self.y)), s)


class Star:
    def __init__(self):
        self.reset(full=True)

    def reset(self, full=False):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT) if full else -5
        self.speed = random.uniform(0.25, 1.9)
        self.size = random.choice([1, 1, 1, 2, 2, 3])
        self.brightness = random.randint(100, 255)
        self.twinkle = random.uniform(0, 2 * math.pi)

    def update(self):
        self.y += self.speed
        self.twinkle += 0.09
        if self.y > HEIGHT + 5:
            self.reset()

    def draw(self, surface):
        b = int(self.brightness * (0.55 + 0.45 * math.sin(self.twinkle)))
        color = (b, b, min(255, b + 40))
        if self.size >= 2:
            glow = pygame.Surface((self.size * 5, self.size * 5), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 35), (self.size * 2, self.size * 2), self.size * 2)
            surface.blit(glow, (int(self.x) - self.size * 2, int(self.y) - self.size * 2))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class ShipAfterImage:
    """Motion blur / after-image trail for ships"""
    def __init__(self, max_images=6):
        self.images = []  # list of (surface, rect, alpha)
        self.max_images = max_images

    def add(self, ship_surf, rect):
        # Store a faded copy
        self.images.append([ship_surf.copy(), rect.copy(), 140])
        if len(self.images) > self.max_images:
            self.images.pop(0)

    def update(self):
        for img in self.images:
            img[2] = max(0, img[2] - 18)  # fade speed
        self.images = [img for img in self.images if img[2] > 10]

    def draw(self, surface):
        for surf, rect, alpha in self.images:
            temp = surf.copy()
            temp.set_alpha(alpha)
            surface.blit(temp, rect)


class Shield:
    """Animated energy shield that appears briefly on hit"""
    def __init__(self, rect, color):
        self.rect = rect.copy()
        self.color = color
        self.life = 22
        self.max_life = 22
        self.radius_offset = 0

    def update(self, ship_rect):
        self.rect = ship_rect.copy()
        self.life -= 1
        self.radius_offset += 1.2

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(180 * (self.life / self.max_life))
        cx, cy = self.rect.centerx, self.rect.centery
        base_r = max(self.rect.width, self.rect.height) // 2 + 8

        for i in range(3):
            r = int(base_r + self.radius_offset * 0.6 + i * 4)
            a = max(0, alpha - i * 50)
            shield_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*self.color, a), (r + 2, r + 2), r, 2)
            # Soft fill
            pygame.draw.circle(shield_surf, (*self.color, a // 5), (r + 2, r + 2), r)
            surface.blit(shield_surf, (cx - r - 2, cy - r - 2))


class Bullet:
    """Custom shaped glowing bullet"""
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.dir = direction  # 1 = right (yellow), -1 = left (red)
        self.color = color
        self.width = 16
        self.height = 7
        self.rect = pygame.Rect(x, y - self.height // 2, self.width, self.height)
        self.trail = []

    def update(self):
        self.x += BULLET_VEL * self.dir
        self.rect.x = int(self.x)
        self.rect.y = int(self.y - self.height // 2)
        # Trail points
        self.trail.append((self.x - self.dir * 4, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            a = int(40 + i * 12)
            s = max(1, 3 - i // 3)
            pygame.draw.circle(surface, (*self.color, a), (int(tx), int(ty)), s)

        # Core glow
        glow = pygame.Surface((self.width + 14, self.height + 14), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*self.color, 60), (0, 0, self.width + 14, self.height + 14))
        surface.blit(glow, (self.rect.x - 7, self.rect.y - 7))

        # Bullet body (elongated capsule)
        pygame.draw.ellipse(surface, self.color, self.rect)
        # Bright core
        core = self.rect.inflate(-6, -3)
        pygame.draw.ellipse(surface, (255, 255, 220), core)

    def off_screen(self):
        return self.x < -20 or self.x > WIDTH + 20


# ==================== HELPERS ====================
def draw_text_center(text, font, color, y_offset=0):
    surf = font.render(text, True, color)
    x = WIDTH // 2 - surf.get_width() // 2
    y = HEIGHT // 2 - surf.get_height() // 2 + y_offset
    WIN.blit(surf, (x, y))
    return surf


def draw_health_bar(x, y, health, max_health, color):
    bar_width = 170
    bar_height = 16
    fill = max(0, int((health / max_health) * bar_width))

    glow = pygame.Surface((bar_width + 12, bar_height + 12), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*color, 45), (0, 0, bar_width + 12, bar_height + 12), border_radius=7)
    WIN.blit(glow, (x - 6, y - 6))

    pygame.draw.rect(WIN, (18, 18, 32), (x, y, bar_width, bar_height), border_radius=5)

    if fill > 0:
        pygame.draw.rect(WIN, color, (x, y, fill, bar_height), border_radius=5)
        shine = pygame.Surface((fill, bar_height // 2), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 55), (0, 0, fill, bar_height // 2), border_radius=3)
        WIN.blit(shine, (x, y))

    pygame.draw.rect(WIN, WHITE, (x, y, bar_width, bar_height), 2, border_radius=5)
    txt = HEALTH_FONT.render(str(health), True, WHITE)
    WIN.blit(txt, (x + bar_width + 8, y - 4))


def create_explosion(x, y, base_color, particles, count=22):
    colors = [base_color, ORANGE, (255, 200, 80), WHITE, PINK]
    shapes = ["circle", "circle", "spark", "square", "spark"]
    for _ in range(count):
        c = random.choice(colors)
        sh = random.choice(shapes)
        particles.append(Particle(x, y, c, life=random.randint(16, 45), size=random.uniform(1.5, 6), shape=sh))


def draw_ship_glow(surface, ship_rect, color, facing_right=True):
    glow = pygame.Surface((36, 44), pygame.SRCALPHA)
    if facing_right:
        for i in range(10):
            a = 28 - i * 2
            pygame.draw.ellipse(glow, (*color, max(0, a)), (i * 2, 6 + i, 22 - i * 2, 28 - i * 2))
        surface.blit(glow, (ship_rect.x - 22, ship_rect.y - 2))
    else:
        for i in range(10):
            a = 28 - i * 2
            pygame.draw.ellipse(glow, (*color, max(0, a)), (12 - i * 2, 6 + i, 22 - i * 2, 28 - i * 2))
        surface.blit(glow, (ship_rect.x + ship_rect.width - 8, ship_rect.y - 2))


# ==================== DRAW ====================
def draw_window(red, yellow, yellow_bullets, red_bullets, red_health, yellow_health,
                particles, stars, yellow_after, red_after, shields, shake_x=0, shake_y=0):
    # Apply screen shake by shifting everything
    offset = (shake_x, shake_y)

    WIN.blit(SPACE, offset)

    for star in stars:
        # manual offset for stars
        ox, oy = int(star.x + shake_x), int(star.y + shake_y)
        b = int(star.brightness * (0.55 + 0.45 * math.sin(star.twinkle)))
        color = (b, b, min(255, b + 40))
        if star.size >= 2:
            glow = pygame.Surface((star.size * 5, star.size * 5), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 35), (star.size * 2, star.size * 2), star.size * 2)
            WIN.blit(glow, (ox - star.size * 2, oy - star.size * 2))
        pygame.draw.circle(WIN, color, (ox, oy), star.size)

    # Border with glow
    bx = BORDER.x + shake_x
    border_surf = pygame.Surface((BORDER.width + 16, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (70, 110, 255, 35), (0, 0, BORDER.width + 16, HEIGHT))
    pygame.draw.rect(border_surf, (130, 170, 255, 100), (5, 0, BORDER.width + 6, HEIGHT))
    WIN.blit(border_surf, (bx - 8, shake_y))
    pygame.draw.rect(WIN, (190, 210, 255), (bx, shake_y, BORDER.width, HEIGHT))

    # Health
    draw_health_bar(12 + shake_x, 12 + shake_y, yellow_health, MAX_HEALTH, YELLOW)
    draw_health_bar(WIDTH - 182 + shake_x, 12 + shake_y, red_health, MAX_HEALTH, RED)
    y_label = TINY_FONT.render("YELLOW", True, YELLOW)
    r_label = TINY_FONT.render("RED", True, RED)
    WIN.blit(y_label, (12 + shake_x, 32 + shake_y))
    WIN.blit(r_label, (WIDTH - 182 + shake_x, 32 + shake_y))

    # After-images (motion blur)
    yellow_after.draw(WIN)
    red_after.draw(WIN)

    # Engine glow
    y_rect = yellow.move(shake_x, shake_y)
    r_rect = red.move(shake_x, shake_y)
    draw_ship_glow(WIN, y_rect, (255, 200, 40), facing_right=True)
    draw_ship_glow(WIN, r_rect, (255, 70, 40), facing_right=False)

    # Ships
    WIN.blit(YELLOW_SPACESHIP, y_rect)
    WIN.blit(RED_SPACESHIP, r_rect)

    # Shields
    for shield in shields:
        # temporarily offset
        orig = shield.rect.copy()
        shield.rect = shield.rect.move(shake_x, shake_y)
        shield.draw(WIN)
        shield.rect = orig

    # Bullets
    for b in yellow_bullets:
        # offset draw
        old_x, old_y = b.x, b.y
        b.x += shake_x
        b.y += shake_y
        b.draw(WIN)
        b.x, b.y = old_x, old_y

    for b in red_bullets:
        old_x, old_y = b.x, b.y
        b.x += shake_x
        b.y += shake_y
        b.draw(WIN)
        b.x, b.y = old_x, old_y

    # Particles
    for p in particles:
        old_x, old_y = p.x, p.y
        p.x += shake_x
        p.y += shake_y
        p.draw(WIN)
        p.x, p.y = old_x, old_y

    pygame.display.update()


# ==================== MOVEMENT ====================
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


def handle_bullets(yellow_bullets, red_bullets, yellow, red, particles):
    for b in yellow_bullets[:]:
        b.update()
        if red.colliderect(b.rect):
            pygame.event.post(pygame.event.Event(RED_HIT))
            create_explosion(b.x, b.y, RED, particles, count=18)
            create_explosion(b.x, b.y, ORANGE, particles, count=10)
            yellow_bullets.remove(b)
        elif b.off_screen():
            yellow_bullets.remove(b)

    for b in red_bullets[:]:
        b.update()
        if yellow.colliderect(b.rect):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            create_explosion(b.x, b.y, YELLOW, particles, count=18)
            create_explosion(b.x, b.y, ORANGE, particles, count=10)
            red_bullets.remove(b)
        elif b.off_screen():
            red_bullets.remove(b)


# ==================== SCREENS ====================
def draw_winner(text, particles, stars):
    WIN.blit(SPACE, (0, 0))
    for star in stars:
        star.update()
        star.draw(WIN)
    for p in particles[:]:
        p.update()
        p.draw(WIN)
        if p.life <= 0:
            particles.remove(p)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 25, 200))
    WIN.blit(overlay, (0, 0))

    glow = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 240, 100, 50), (WIDTH // 2 - 280, 0, 560, 140))
    WIN.blit(glow, (0, HEIGHT // 2 - 100))

    draw_text_center(text, WINNER_FONT, WHITE, y_offset=-55)
    draw_text_center("Press  R  to Restart    |    ESC to Quit", SMALL_FONT, GREEN, y_offset=45)
    pygame.display.update()


def show_menu(stars):
    clock = pygame.time.Clock()
    pulse = 0
    while True:
        clock.tick(FPS)
        pulse += 0.07

        WIN.blit(SPACE, (0, 0))
        for star in stars:
            star.update()
            star.draw(WIN)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 35, 110))
        WIN.blit(overlay, (0, 0))

        p = 0.65 + 0.35 * math.sin(pulse)
        title_color = (int(255 * p), int(225 * p), int(40 * p))

        shadow = TITLE_FONT.render("GALAXY FIGHTERS", True, (0, 0, 0))
        WIN.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 4, HEIGHT // 2 - 125 + 4))
        draw_text_center("GALAXY FIGHTERS", TITLE_FONT, title_color, y_offset=-115)
        draw_text_center("2-Player Local Battle", MENU_FONT, CYAN, y_offset=-45)

        if int(pulse * 2.2) % 2 == 0:
            draw_text_center("▶  Press SPACE to Start", SMALL_FONT, GREEN, y_offset=35)
        else:
            draw_text_center("   Press SPACE to Start", SMALL_FONT, (50, 160, 90), y_offset=35)

        draw_text_center("Press ESC to Quit", TINY_FONT, (130, 130, 160), y_offset=75)

        box = pygame.Surface((540, 58), pygame.SRCALPHA)
        pygame.draw.rect(box, (15, 15, 45, 180), (0, 0, 540, 58), border_radius=12)
        pygame.draw.rect(box, (90, 140, 255, 120), (0, 0, 540, 58), 2, border_radius=12)
        WIN.blit(box, (WIDTH // 2 - 270, HEIGHT - 78))
        controls = SMALL_FONT.render("Yellow: WASD + L-Ctrl      Red: Arrows + R-Ctrl", True, WHITE)
        WIN.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 62))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def main_game(stars):
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    yellow_bullets = []
    red_bullets = []
    particles = []
    shields = []

    yellow_after = ShipAfterImage(max_images=7)
    red_after = ShipAfterImage(max_images=7)

    red_health = MAX_HEALTH
    yellow_health = MAX_HEALTH

    clock = pygame.time.Clock()
    run = True
    winner_text = ""
    shake_timer = 0
    frame = 0

    while run:
        clock.tick(FPS)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    b = Bullet(yellow.x + yellow.width, yellow.centery, 1, RED)
                    yellow_bullets.append(b)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    b = Bullet(red.x, red.centery, -1, YELLOW)
                    red_bullets.append(b)
                    BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                BULLET_HIT_SOUND.play()
                shake_timer = 14
                create_explosion(red.centerx, red.centery, RED, particles, count=14)
                shields.append(Shield(red, RED))

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                BULLET_HIT_SOUND.play()
                shake_timer = 14
                create_explosion(yellow.centerx, yellow.centery, YELLOW, particles, count=14)
                shields.append(Shield(yellow, YELLOW))

        if red_health <= 0:
            winner_text = "YELLOW WINS!"
            create_explosion(red.centerx, red.centery, RED, particles, count=55)
            create_explosion(red.centerx, red.centery, ORANGE, particles, count=35)
            run = False
        elif yellow_health <= 0:
            winner_text = "RED WINS!"
            create_explosion(yellow.centerx, yellow.centery, YELLOW, particles, count=55)
            create_explosion(yellow.centerx, yellow.centery, ORANGE, particles, count=35)
            run = False

        keys = pygame.key.get_pressed()
        yellow_handle_movement(keys, yellow)
        red_handle_movement(keys, red)
        handle_bullets(yellow_bullets, red_bullets, yellow, red, particles)

        # After-images every few frames when moving
        if frame % 2 == 0:
            yellow_after.add(YELLOW_SPACESHIP, yellow)
            red_after.add(RED_SPACESHIP, red)
        yellow_after.update()
        red_after.update()

        # Update stars & particles
        for star in stars:
            star.update()
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # Shields
        for s in shields[:]:
            s.update(s.rect)  # will be refreshed below
            if s.life <= 0:
                shields.remove(s)
        # Keep shield rects synced to ships
        for s in shields:
            if s.color == YELLOW:
                s.rect = yellow.copy()
            else:
                s.rect = red.copy()

        # Screen shake
        shake_x = shake_y = 0
        if shake_timer > 0:
            shake_timer -= 1
            mag = shake_timer * 0.7
            shake_x = random.randint(int(-mag), int(mag))
            shake_y = random.randint(int(-mag), int(mag))

        draw_window(red, yellow, yellow_bullets, red_bullets, red_health, yellow_health,
                    particles, stars, yellow_after, red_after, shields, shake_x, shake_y)

    return winner_text, particles


def main():
    stars = [Star() for _ in range(100)]

    while True:
        show_menu(stars)
        winner, particles = main_game(stars)

        waiting = True
        clock = pygame.time.Clock()
        while waiting:
            clock.tick(FPS)
            draw_winner(winner, particles, stars)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


if __name__ == "__main__":
    main()
