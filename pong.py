import pygame
import math
import random

pygame.init()

WIDTH = 900
HEIGHT = 800

WS = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game BY Karan")

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 200)
NEON_GREEN = (0, 255, 100)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 120, 0)
NEON_PURPLE = (180, 0, 255)

PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
BALL_RADIUS = 7
SCORE_FONT = pygame.font.SysFont("comicsans", 80)
HIT_FONT = pygame.font.SysFont("comicsans", 22)
WINNING_SCORE = 10

TRAIL_LENGTH = 18
BASE_BALL_SPEED = 5
SPEED_INCREMENT = 0.25
MAX_BALL_SPEED = 12


# ── Glow helper ──────────────────────────────────────────────────────────────
def draw_glow(surface, color, center, radius, layers=4, alpha_step=40):
    glow_surf = pygame.Surface(
        (radius * 2 * layers, radius * 2 * layers), pygame.SRCALPHA
    )
    for i in range(layers, 0, -1):
        alpha = alpha_step * i
        r, g, b = color
        pygame.draw.circle(
            glow_surf,
            (r, g, b, min(alpha, 200)),
            (radius * layers, radius * layers),
            radius + (layers - i) * 6,
        )
    surface.blit(
        glow_surf,
        (center[0] - radius * layers, center[1] - radius * layers),
    )


def draw_rect_glow(surface, color, rect, layers=3, alpha_step=30):
    for i in range(layers, 0, -1):
        alpha = alpha_step * i
        r, g, b = color
        glow_rect = pygame.Rect(
            rect.x - i * 4,
            rect.y - i * 4,
            rect.width + i * 8,
            rect.height + i * 8,
        )
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            glow_surf, (r, g, b, alpha), glow_surf.get_rect(), border_radius=12
        )
        surface.blit(glow_surf, (glow_rect.x, glow_rect.y))


# ── Particle ─────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 7)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.radius = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.93
        self.vy *= 0.93
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        r, g, b = self.color
        glow_surf = pygame.Surface((self.radius * 6, self.radius * 6), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (r, g, b, alpha),
            (self.radius * 3, self.radius * 3),
            self.radius,
        )
        surface.blit(
            glow_surf, (int(self.x) - self.radius * 3, int(self.y) - self.radius * 3)
        )


# ── Paddle ────────────────────────────────────────────────────────────────────
class Paddle:
    VEL = 4

    def __init__(self, x, y, width, height, color):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.color = color
        self.hit_count = 0

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        draw_rect_glow(surface, self.color, rect)
        pygame.draw.rect(surface, self.color, rect, border_radius=10)

        # Hit counter badge
        badge_font = pygame.font.SysFont("comicsans", 18)
        badge = badge_font.render(f"Hits: {self.hit_count}", True, self.color)
        bx = (
            self.x - badge.get_width() - 6
            if self.x > WIDTH // 2
            else self.x + self.width + 6
        )
        surface.blit(badge, (bx, self.y + self.height // 2 - badge.get_height() // 2))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


# ── Ball ───────────────────────────────────────────────────────────────────────
class Ball:
    COLOR = WHITE
    MAX_VEL = BASE_BALL_SPEED

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_VEL = self.MAX_VEL
        self.y_VEL = 0
        self.trail = []
        self.speed_multiplier = 1.0

    @property
    def speed(self):
        return math.hypot(self.x_VEL, self.y_VEL)

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            frac = i / max(len(self.trail), 1)
            alpha = int(180 * frac)
            radius = max(1, int(self.radius * frac))
            r = int(0 + 255 * frac)
            g = int(200 * frac)
            b = int(255 * (1 - frac * 0.5))
            trail_surf = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
            pygame.draw.circle(
                trail_surf, (r, g, b, alpha), (radius * 3, radius * 3), radius
            )
            surface.blit(trail_surf, (int(tx) - radius * 3, int(ty) - radius * 3))

        # Ball glow + core
        draw_glow(surface, NEON_CYAN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)
        self.x += self.x_VEL
        self.y += self.y_VEL

    def reset(self):
        self.trail.clear()
        self.x = self.original_x
        self.y = self.original_y
        self.y_VEL = 0
        self.speed_multiplier = 1.0
        self.x_VEL = BASE_BALL_SPEED * (-1 if self.x_VEL > 0 else 1)

    def increase_speed(self):
        self.speed_multiplier = min(
            self.speed_multiplier + SPEED_INCREMENT / BASE_BALL_SPEED,
            MAX_BALL_SPEED / BASE_BALL_SPEED,
        )
        factor = self.speed_multiplier
        spd = math.hypot(self.x_VEL, self.y_VEL)
        if spd > 0:
            new_spd = min(spd + SPEED_INCREMENT, MAX_BALL_SPEED)
            self.x_VEL = self.x_VEL / spd * new_spd
            self.y_VEL = self.y_VEL / spd * new_spd


# ── Helpers ────────────────────────────────────────────────────────────────────
def spawn_particles(x, y, color, count=25):
    return [Particle(x, y, color) for _ in range(count)]


def draw_center_line(surface):
    seg_h = 28
    gap = 14
    total = seg_h + gap
    n = HEIGHT // total + 1
    for i in range(n):
        y = i * total
        alpha = 160
        seg_surf = pygame.Surface((4, seg_h), pygame.SRCALPHA)
        seg_surf.fill((100, 200, 255, alpha))
        surface.blit(seg_surf, (WIDTH // 2 - 2, y))
        # tiny glow dots at joints
        dot_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (0, 220, 255, 80), (4, 4), 4)
        surface.blit(dot_surf, (WIDTH // 2 - 4, y - 4))


def draw_countdown(surface, count):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))
    font = pygame.font.SysFont("comicsans", 180)
    txt = font.render(str(count), True, NEON_CYAN)
    draw_glow(
        surface, NEON_CYAN, (WIDTH // 2, HEIGHT // 2), 80, layers=5, alpha_step=30
    )
    surface.blit(
        txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2)
    )
    pygame.display.update()


def draw_start_screen(surface):
    surface.fill(BLACK)

    # Title glow
    title_font = pygame.font.SysFont("comicsans", 90)
    sub_font = pygame.font.SysFont("comicsans", 28)
    hint_font = pygame.font.SysFont("comicsans", 22)

    title = title_font.render("PONG", True, NEON_CYAN)
    draw_glow(surface, NEON_CYAN, (WIDTH // 2, 160), 60, layers=5, alpha_step=35)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 110))

    sub = sub_font.render("BY KARAN", True, NEON_PINK)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 215))

    # Controls box
    lines = [
        ("LEFT PLAYER", NEON_GREEN),
        ("W  →  Up        S  →  Down", WHITE),
        ("", WHITE),
        ("RIGHT PLAYER", NEON_PINK),
        ("↑  →  Up        ↓  →  Down", WHITE),
        ("", WHITE),
        ("First to 10 points wins!", NEON_YELLOW),
    ]
    y = 310
    for text, color in lines:
        rendered = hint_font.render(text, True, color)
        surface.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, y))
        y += 36

    # Draw center dashes as decoration
    draw_center_line(surface)

    # Press SPACE prompt (blink)
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        press = sub_font.render("PRESS  SPACE  TO  PLAY", True, NEON_YELLOW)
        draw_glow(surface, NEON_YELLOW, (WIDTH // 2, 660), 20, layers=3, alpha_step=30)
        surface.blit(press, (WIDTH // 2 - press.get_width() // 2, 645))

    pygame.display.update()


def draw_winner_popup(surface, win_text):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("comicsans", 60)
    small_font = pygame.font.SysFont("comicsans", 30)

    lines = win_text.split("\n")
    total_h = len(lines) * 80
    start_y = HEIGHT // 2 - total_h // 2

    for i, line in enumerate(lines):
        color = NEON_GREEN if i == 0 else NEON_PINK
        txt = big_font.render(line.strip(), True, color)
        draw_glow(
            surface, color, (WIDTH // 2, start_y + i * 80), 40, layers=4, alpha_step=30
        )
        surface.blit(
            txt,
            (
                WIDTH // 2 - txt.get_width() // 2,
                start_y + i * 80 - txt.get_height() // 2,
            ),
        )

    restart = small_font.render("Restarting in a moment...", True, NEON_YELLOW)
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT - 100))
    pygame.display.update()


def draw(surface, paddles, ball, left_score, right_score, particles, shake_offset):
    ox, oy = shake_offset
    surface.fill(BLACK)

    # Scores
    left_score_text = SCORE_FONT.render(f"{left_score}", True, NEON_GREEN)
    right_score_text = SCORE_FONT.render(f"{right_score}", True, NEON_PINK)
    surface.blit(
        left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2 + ox, 20 + oy)
    )
    surface.blit(
        right_score_text,
        (WIDTH * 3 // 4 - right_score_text.get_width() // 2 + ox, 20 + oy),
    )

    draw_center_line(surface)

    for paddle in paddles:
        p = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        paddle.draw(p)
        surface.blit(p, (ox, oy))

    # Particles
    for particle in particles:
        particle.draw(surface)

    # Ball
    ball_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ball.draw(ball_surf)
    surface.blit(ball_surf, (ox, oy))

    pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle, particles):
    hit = False
    hit_color = WHITE

    if ball.y + ball.radius >= HEIGHT:
        ball.y_VEL *= -1
    elif ball.y - ball.radius <= 0:
        ball.y_VEL *= -1

    if ball.x_VEL < 0:
        if left_paddle.y <= ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                ball.x_VEL *= -1
                mid_y = left_paddle.y + left_paddle.height / 2
                diff_y = mid_y - ball.y
                reduction = (left_paddle.height / 2) / ball.MAX_VEL
                ball.y_VEL = -diff_y / reduction
                ball.increase_speed()
                left_paddle.hit_count += 1
                hit = True
                hit_color = NEON_GREEN
                particles += spawn_particles(ball.x, ball.y, NEON_GREEN)
    else:
        if right_paddle.y <= ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_VEL *= -1
                mid_y = right_paddle.y + right_paddle.height / 2
                diff_y = mid_y - ball.y
                reduction = (right_paddle.height / 2) / ball.MAX_VEL
                ball.y_VEL = -diff_y / reduction
                ball.increase_speed()
                right_paddle.hit_count += 1
                hit = True
                hit_color = NEON_PINK
                particles += spawn_particles(ball.x, ball.y, NEON_PINK)

    return hit


def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    if (
        keys[pygame.K_s]
        and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT
    ):
        left_paddle.move(up=False)
    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if (
        keys[pygame.K_DOWN]
        and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT
    ):
        right_paddle.move(up=False)


def do_countdown(surface, paddles, ball, left_score, right_score):
    for count in (3, 2, 1):
        draw(surface, paddles, ball, left_score, right_score, [], (0, 0))
        draw_countdown(surface, count)
        pygame.time.delay(900)


def screen_shake(duration=12):
    """Yields (ox, oy) shake offsets for `duration` frames."""
    intensity = 10
    for i in range(duration):
        decay = 1 - i / duration
        ox = random.randint(-intensity, intensity) * decay
        oy = random.randint(-intensity, intensity) * decay
        yield int(ox), int(oy)


def main():
    clock = pygame.time.Clock()

    left_paddle = Paddle(
        10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, NEON_GREEN
    )
    right_paddle = Paddle(
        WIDTH - 10 - PADDLE_WIDTH,
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
        NEON_PINK,
    )
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0
    particles = []
    shake_frames = []
    shake_offset = (0, 0)

    # ── Start screen ──────────────────────────────────────────────────────────
    waiting = True
    while waiting:
        clock.tick(FPS)
        draw_start_screen(WS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

    do_countdown(WS, [left_paddle, right_paddle], ball, left_score, right_score)

    run = True
    while run:
        clock.tick(FPS)

        # Screen shake offset
        if shake_frames:
            shake_offset = shake_frames.pop(0)
        else:
            shake_offset = (0, 0)

        ball.move()

        hit = handle_collision(ball, left_paddle, right_paddle, particles)
        if hit:
            shake_frames = list(screen_shake(8))

        # Update particles
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()

        draw(
            WS,
            [left_paddle, right_paddle],
            ball,
            left_score,
            right_score,
            particles,
            shake_offset,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        # Scoring
        scored = False
        if ball.x < 0:
            right_score += 1
            particles += spawn_particles(50, HEIGHT // 2, NEON_PINK, 40)
            shake_frames = list(screen_shake(18))
            scored = True
        elif ball.x > WIDTH:
            left_score += 1
            particles += spawn_particles(WIDTH - 50, HEIGHT // 2, NEON_GREEN, 40)
            shake_frames = list(screen_shake(18))
            scored = True

        if scored:
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            # Countdown after each score
            do_countdown(WS, [left_paddle, right_paddle], ball, left_score, right_score)

        # Win check
        won = False
        win_text = ""
        if left_score >= WINNING_SCORE:
            won = True
            win_text = "LEFT PLAYER WON \n LOL RIGHT PLAYER "
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "RIGHT PLAYER WON \nLOL LEFT PLAYER "

        if won:
            draw(
                WS,
                [left_paddle, right_paddle],
                ball,
                left_score,
                right_score,
                particles,
                (0, 0),
            )
            draw_winner_popup(WS, win_text)
            pygame.time.delay(5000)
            # Reset everything
            left_score = 0
            right_score = 0
            left_paddle.hit_count = 0
            right_paddle.hit_count = 0
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            particles.clear()
            do_countdown(WS, [left_paddle, right_paddle], ball, left_score, right_score)

    pygame.quit()


if __name__ == "__main__":
    main()
