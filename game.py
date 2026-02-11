import sys
import random
import pygame
from pygame.locals import (
    RLEACCEL,
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_w, K_a, K_s, K_d,
    K_ESCAPE, K_SPACE, K_p, K_r,
    KEYDOWN,
    QUIT
)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge Game")

# ---- sizes (simple) ----
PLAYER_SIZE = (48, 48)
ENEMY_SMALL_SIZE = (30, 22)   # fast
ENEMY_BIG_SIZE = (55, 40)     # slow
CLOUD_SIZE = (50, 35)

# ---- events ----
ADDENEMY = pygame.USEREVENT + 1
ADDCLOUD = pygame.USEREVENT + 2
ADDSHIELD = pygame.USEREVENT + 3

pygame.time.set_timer(ADDENEMY, 350)
pygame.time.set_timer(ADDCLOUD, 900)
pygame.time.set_timer(ADDSHIELD, 4500)

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 64)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base = pygame.image.load("cutie.png").convert()
        self.base = pygame.transform.scale(self.base, PLAYER_SIZE)
        self.base.set_colorkey((255, 255, 255), RLEACCEL)

        self.surf = self.base
        self.rect = self.surf.get_rect(center=(80, SCREEN_HEIGHT // 2))
        self.last_dir = (1, 0)  # facing right

    def update(self, pressed_keys):
        speed = 8 if pressed_keys[K_SPACE] else 5
        dx, dy = 0, 0

        if pressed_keys[K_UP] or pressed_keys[K_w]:
            dy -= speed
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            dy += speed
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            dx -= speed
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            dx += speed

        if dx or dy:
            self.last_dir = (dx, dy)
            self.rect.move_ip(dx, dy)

        self.rect.clamp_ip(screen.get_rect())
        self._rotate()

    def _rotate(self):
        dx, dy = self.last_dir

        # simple 4-direction rotation
        if abs(dx) > abs(dy):
            angle = 0 if dx > 0 else 180
        else:
            angle = -90 if dy > 0 else 90

        center = self.rect.center
        self.surf = pygame.transform.rotate(self.base, angle)
        self.rect = self.surf.get_rect(center=center)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type="small", speed_bonus=0):
        super().__init__()
        raw = pygame.image.load("net.png").convert()
        raw.set_colorkey((255, 255, 255), RLEACCEL)

        if enemy_type == "small":
            self.surf = pygame.transform.scale(raw, ENEMY_SMALL_SIZE)
            self.speed_x = random.randint(6, 9) + speed_bonus
        else:
            self.surf = pygame.transform.scale(raw, ENEMY_BIG_SIZE)
            self.speed_x = random.randint(2, 4) + speed_bonus

        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 160),
                random.randint(30, SCREEN_HEIGHT - 30),
            )
        )
        self.speed_y = random.randint(-1, 1)

    def update(self):
        self.rect.move_ip(-self.speed_x, self.speed_y)
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1
        if self.rect.right < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("carrot.png").convert()
        self.surf = pygame.transform.scale(self.surf, CLOUD_SIZE)
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        )
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class ShieldPowerUp(pygame.sprite.Sprite):
    # no extra image needed
    def __init__(self):
        super().__init__()
        size = 26
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (80, 170, 255, 220), (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.surf, (255, 255, 255, 220), (size // 2, size // 2), size // 2, 2)

        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 160),
                random.randint(40, SCREEN_HEIGHT - 40),
            )
        )
        self.speed = 4

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


def reset_game():
    player = Player()

    enemies = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    for _ in range(8):
        c = Cloud()
        clouds.add(c)
        all_sprites.add(c)

    start_ticks = pygame.time.get_ticks()
    lives = 3
    paused = False

    shield_active = False
    shield_ends_at = 0
    invuln_ends_at = 0

    return {
        "player": player,
        "enemies": enemies,
        "clouds": clouds,
        "powerups": powerups,
        "all_sprites": all_sprites,
        "start_ticks": start_ticks,
        "lives": lives,
        "paused": paused,
        "shield_active": shield_active,
        "shield_ends_at": shield_ends_at,
        "invuln_ends_at": invuln_ends_at,
        "game_over": False,
    }


state = reset_game()
clock = pygame.time.Clock()

running = True
while running:
    now = pygame.time.get_ticks()
    seconds = (now - state["start_ticks"]) // 1000
    difficulty_level = seconds // 12

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

        # pause works even during game over (but doesn't matter)
        if event.type == KEYDOWN and event.key == K_p and not state["game_over"]:
            state["paused"] = not state["paused"]

        # restart only on game over
        if event.type == KEYDOWN and event.key == K_r and state["game_over"]:
            state = reset_game()

        # spawning only when playing (not paused, not game over)
        if (not state["paused"]) and (not state["game_over"]):
            if event.type == ADDENEMY:
                etype = "small" if random.random() < 0.65 else "big"
                e = Enemy(enemy_type=etype, speed_bonus=difficulty_level)
                state["enemies"].add(e)
                state["all_sprites"].add(e)

            elif event.type == ADDCLOUD:
                c = Cloud()
                state["clouds"].add(c)
                state["all_sprites"].add(c)

            elif event.type == ADDSHIELD:
                if random.random() < 0.6:
                    s = ShieldPowerUp()
                    state["powerups"].add(s)
                    state["all_sprites"].add(s)

    # update gameplay only when playing
    if (not state["paused"]) and (not state["game_over"]):
        pressed = pygame.key.get_pressed()
        state["player"].update(pressed)

        state["enemies"].update()
        state["clouds"].update()
        state["powerups"].update()

        # collect shield
        if pygame.sprite.spritecollideany(state["player"], state["powerups"]):
            pygame.sprite.spritecollide(state["player"], state["powerups"], dokill=True)
            state["shield_active"] = True
            state["shield_ends_at"] = now + 5000

        if state["shield_active"] and now >= state["shield_ends_at"]:
            state["shield_active"] = False

        # take damage (with invuln)
        if pygame.sprite.spritecollideany(state["player"], state["enemies"]):
            if (not state["shield_active"]) and (now >= state["invuln_ends_at"]):
                state["lives"] -= 1
                state["invuln_ends_at"] = now + 1200
                if state["lives"] <= 0:
                    state["game_over"] = True

    # draw
    screen.fill((100, 100, 100))

    for s in state["all_sprites"]:
        screen.blit(s.surf, s.rect)

    if state["shield_active"]:
        pygame.draw.circle(screen, (80, 170, 255), state["player"].rect.center, 32, 3)

    # UI
    now = pygame.time.get_ticks()
    seconds = (now - state["start_ticks"]) // 1000
    screen.blit(font.render(f"Score: {seconds}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Lives: {state['lives']}", True, (255, 220, 220)), (10, 45))

    if state["paused"]:
        t = big_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    if state["game_over"]:
        t = big_font.render("GAME OVER", True, (255, 255, 255))
        s = font.render(f"Final Score: {seconds}", True, (255, 255, 255))
        r = font.render("Press R to Restart  |  ESC to Quit", True, (200, 200, 200))
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 200))
        screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, 280))
        screen.blit(r, (SCREEN_WIDTH // 2 - r.get_width() // 2, 340))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
