import pygame
import random
import sys

from pygame.locals import (
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE,
    KEYDOWN, QUIT
)

# ---------- Setup ----------
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge the Obstacles")

clock = pygame.time.Clock()

# Custom events
ADDOBSTACLE = pygame.USEREVENT + 1
pygame.time.set_timer(ADDOBSTACLE, 700)  # spawn every 700 ms


# ---------- Sprite Classes ----------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.rect.left = 20
        self.rect.centery = SCREEN_HEIGHT // 2
        self.speed = 6

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        w = random.randint(20, 60)
        h = random.randint(20, 60)
        self.surf = pygame.Surface((w, h))
        self.surf.fill((255, 0, 0))  # red obstacle
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH + w, random.randint(0, SCREEN_HEIGHT))
        )
        self.speed = random.randint(4, 9)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()  # remove when off-screen


# ---------- Game Objects ----------
player = Player()

obstacles = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

running = True

# ---------- Main Game Loop ----------
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        elif event.type == QUIT:
            running = False

        elif event.type == ADDOBSTACLE:
            new_obstacle = Obstacle()
            obstacles.add(new_obstacle)
            all_sprites.add(new_obstacle)

    pressed_keys = pygame.key.get_pressed()

    # Update sprites
    player.update(pressed_keys)
    obstacles.update()

    # Collision check: if player hits any obstacle -> end game
    if pygame.sprite.spritecollideany(player, obstacles):
        print("Game Over: You were hit!")
        running = False

    # Draw
    screen.fill((0, 0, 0))  # black background
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
print("Goodbye")
sys.exit()
