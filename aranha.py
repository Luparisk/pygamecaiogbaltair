import math
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import pygame

# ============================================================
# HALLOWEEN ADVENTURES - Boss Fight (PNG sprites)
# ------------------------------------------------------------
# Corrigido para:
#   1) carregar o fundo da caverna como imagem
#   2) usar projéteis de teia em formato de web
#   3) usar sprites da aranha sem a teia presa ao corpo
#
# Controles:
#   WASD / Setas  -> mover
#   ESPAÇO        -> atirar
#   ESC           -> sair
# ============================================================

WINDOW_W = 1280
WINDOW_H = 720
FPS = 60
TITLE = "Halloween Adventures - Boss Fight"

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

BACKGROUND_IMAGE_PATH = ASSET_DIR / "backgrounds" / "cave_background.png"
PLAYER_IMAGE_PATH = BASE_DIR / "player.png"
WIN_IMAGE_PATH = BASE_DIR / "minha_imagem_final.png"
SPIDER_SPRITE_DIR = ASSET_DIR / "boss_spider"
WEB_PROJECTILE_IMAGE_PATH = ASSET_DIR / "projectiles" / "spider_web.png"

PLAYER_SIZE = (96, 96)
PLAYER_SPEED = 360
PLAYER_MAX_HP = 8
PLAYER_SHOT_COOLDOWN = 0.18
PLAYER_PROJECTILE_SPEED = 760
PLAYER_PROJECTILE_DAMAGE = 1

SPIDER_MAX_HP = 30
SPIDER_MOVE_RADIUS_X = 220
SPIDER_MOVE_RADIUS_Y = 90
SPIDER_MOVE_SPEED = 1.15
SPIDER_ATTACK_COOLDOWN = (0.9, 1.6)
SPIDER_BALL_SPEED = 300
SPIDER_BALL_DAMAGE = 1

CIRCLE_CLOSE_DURATION = 1.6

BG_COLOR = (19, 16, 31)
ARENA_FLOOR = (70, 58, 52)
ARENA_WALL = (39, 33, 45)
UI_TEXT = (245, 235, 220)

PLAYER_BODY = (92, 196, 255)
PLAYER_BODY_DARK = (45, 126, 181)
PLAYER_OUTLINE = (17, 26, 40)
PLAYER_PROJECTILE_COLOR = (255, 232, 110)

SPIDER_WEB_SHOT = (222, 222, 235)


def clamp(value, low, high):
    return max(low, min(high, value))


def load_image_or_none(path, size=None):
    if not path or not Path(path).exists():
        return None
    try:
        img = pygame.image.load(str(path)).convert_alpha()
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None


def load_frames(folder, pattern, scale_to=None):
    frames = []
    idx = 1
    while True:
        path = folder / pattern.format(idx)
        if not path.exists():
            break
        img = pygame.image.load(str(path)).convert_alpha()
        if scale_to is not None:
            img = pygame.transform.smoothscale(img, scale_to)
        frames.append(img)
        idx += 1
    return frames


def draw_text(surface, text, size, color, x, y, center=True, bold=True):
    font = pygame.font.SysFont("arial", size, bold=bold)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)
    return rect


def make_player_sprite(size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size
    cx, cy = w // 2, h // 2
    pygame.draw.ellipse(surf, PLAYER_OUTLINE, (18, 20, w - 36, h - 20))
    pygame.draw.ellipse(surf, PLAYER_BODY, (22, 24, w - 44, h - 28))
    pygame.draw.ellipse(surf, PLAYER_BODY_DARK, (34, 36, w - 68, h - 60))
    pygame.draw.circle(surf, (245, 245, 245), (cx - 14, cy - 10), 14)
    pygame.draw.circle(surf, (245, 245, 245), (cx + 14, cy - 10), 14)
    pygame.draw.circle(surf, PLAYER_OUTLINE, (cx - 10, cy - 8), 5)
    pygame.draw.circle(surf, PLAYER_OUTLINE, (cx + 18, cy - 8), 5)
    pygame.draw.arc(surf, PLAYER_OUTLINE, (cx - 18, cy + 4, 36, 20), math.pi * 0.1, math.pi * 0.9, 3)
    pygame.draw.line(surf, PLAYER_OUTLINE, (28, 60), (8, 36), 8)
    pygame.draw.line(surf, PLAYER_OUTLINE, (w - 28, 60), (w - 8, 36), 8)
    pygame.draw.line(surf, PLAYER_BODY, (30, 60), (12, 38), 4)
    pygame.draw.line(surf, PLAYER_BODY, (w - 30, 60), (w - 12, 38), 4)
    pygame.draw.line(surf, PLAYER_OUTLINE, (42, h - 32), (18, h - 10), 8)
    pygame.draw.line(surf, PLAYER_OUTLINE, (w - 42, h - 32), (w - 18, h - 10), 8)
    pygame.draw.line(surf, PLAYER_BODY, (42, h - 32), (20, h - 12), 4)
    pygame.draw.line(surf, PLAYER_BODY, (w - 42, h - 32), (w - 20, h - 12), 4)
    pygame.draw.rect(surf, (255, 128, 128), (cx - 16, cy + 10, 32, 18), border_radius=8)
    pygame.draw.rect(surf, PLAYER_OUTLINE, (cx - 16, cy + 10, 32, 18), 2, border_radius=8)
    return surf


def make_web_projectile_sprite(size=96):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    web = (245, 245, 250, 255)
    outline = (90, 90, 110, 255)
    for r, width in [(34, 3), (24, 2), (14, 2), (7, 1)]:
        pygame.draw.circle(surf, web, (c, c), r, width)
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        x = c + int(math.cos(rad) * 36)
        y = c + int(math.sin(rad) * 36)
        pygame.draw.line(surf, web, (c, c), (x, y), 3)
        pygame.draw.line(surf, outline, (c, c), (x, y), 1)
    # pequena cauda para dar sensação de movimento
    for i in range(3):
        pygame.draw.line(surf, (200, 200, 215, 120), (c - 6 - i * 6, c + 4 + i * 3), (c - 26 - i * 6, c + 16 + i * 3), 2)
    return surf


def draw_cave_bg(surface, background_image=None):
    if background_image is not None:
        surface.blit(background_image, (0, 0))
        return
    surface.fill(BG_COLOR)
    pygame.draw.rect(surface, ARENA_WALL, (0, 0, WINDOW_W, 120))
    pygame.draw.polygon(surface, ARENA_WALL, [(0, 0), (170, 140), (0, 300)])
    pygame.draw.polygon(surface, ARENA_WALL, [(WINDOW_W, 0), (WINDOW_W - 170, 140), (WINDOW_W, 300)])
    pygame.draw.rect(surface, ARENA_FLOOR, (0, 470, WINDOW_W, 250))
    pygame.draw.ellipse(surface, (92, 79, 72), (250, 520, 780, 220))
    for x in range(0, WINDOW_W, 90):
        y = 470 + int(8 * math.sin(x * 0.06))
        pygame.draw.circle(surface, (98, 84, 76), (x + 18, y + 20), 8)
        pygame.draw.circle(surface, (80, 70, 64), (x + 40, y + 26), 5)
    pygame.draw.ellipse(surface, (255, 201, 137), (70, 150, 210, 220))
    pygame.draw.ellipse(surface, (255, 230, 170), (108, 185, 120, 150))


def draw_circular_close(surface, progress):
    if progress <= 0:
        return
    overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    radius = int(max(WINDOW_W, WINDOW_H) * 0.8 * (1.0 - progress))
    center = (WINDOW_W // 2, WINDOW_H // 2)
    pygame.draw.circle(overlay, (0, 0, 0, 0), center, radius)
    surface.blit(overlay, (0, 0))


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    image: pygame.Surface | None
    radius: int
    damage: int
    color: tuple
    from_player: bool = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def rect(self):
        if self.image is not None:
            w, h = self.image.get_size()
            return pygame.Rect(int(self.x - w // 2), int(self.y - h // 2), w, h)
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def draw(self, surface):
        if self.image is not None:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, rect)
            return
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 3), int(self.y - 3)), max(2, self.radius // 3))


class Player:
    def __init__(self, x, y, image=None):
        self.x = x
        self.y = y
        self.w, self.h = PLAYER_SIZE
        self.hp = PLAYER_MAX_HP
        self.image = image
        self.shoot_timer = 0.0
        self.invuln_timer = 0.0
        self.dead = False
        self.facing = 1
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt, keys, projectiles):
        if self.dead:
            return
        mx = 0
        my = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: mx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: mx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]: my -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: my += 1
        if mx != 0 or my != 0:
            length = math.hypot(mx, my)
            mx /= length
            my /= length
            self.x += mx * PLAYER_SPEED * dt
            self.y += my * PLAYER_SPEED * dt
            if mx != 0:
                self.facing = 1 if mx > 0 else -1
        self.x = clamp(self.x, 40, WINDOW_W - self.w - 40)
        self.y = clamp(self.y, 330, WINDOW_H - self.h - 40)
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
        if keys[pygame.K_SPACE] and self.shoot_timer <= 0:
            self.shoot_timer = PLAYER_SHOT_COOLDOWN
            px = self.x + self.w * 0.52 + self.facing * 34
            py = self.y + self.h * 0.42
            projectiles.append(Projectile(px, py, PLAYER_PROJECTILE_SPEED * self.facing, 0, None, 8, PLAYER_PROJECTILE_DAMAGE, PLAYER_PROJECTILE_COLOR, True))
        self.rect.update(int(self.x), int(self.y), self.w, self.h)

    def hit(self, damage):
        if self.invuln_timer > 0 or self.dead:
            return
        self.hp -= damage
        self.invuln_timer = 0.65
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface):
        if self.dead:
            return
        sprite = self.image if self.image is not None else make_player_sprite(PLAYER_SIZE)
        if self.invuln_timer > 0 and int(self.invuln_timer * 20) % 2 == 0:
            tinted = sprite.copy()
            tinted.fill((255, 120, 120, 120), special_flags=pygame.BLEND_RGBA_ADD)
            sprite = tinted
        if self.facing < 0:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, (int(self.x), int(self.y)))


class SpiderBoss:
    def __init__(self, x, y, frames, web_ball_image=None):
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.frames = frames if frames else []
        self.web_ball_image = web_ball_image
        self.frame_index = 0.0
        self.frame_speed = 6.0
        self.w, self.h = self.frames[0].get_size() if self.frames else (320, 320)
        self.hp = SPIDER_MAX_HP
        self.max_hp = SPIDER_MAX_HP
        self.attack_timer = random.uniform(0.8, 1.6)
        self.move_time = 0.0
        self.flash_timer = 0.0
        self.dead = False
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt, player, projectiles):
        if self.dead:
            return
        self.move_time += dt * SPIDER_MOVE_SPEED
        self.x = self.base_x + math.sin(self.move_time) * SPIDER_MOVE_RADIUS_X
        self.y = self.base_y + math.sin(self.move_time * 1.7) * SPIDER_MOVE_RADIUS_Y
        self.x = clamp(self.x, 90, WINDOW_W - self.w - 50)
        self.y = clamp(self.y, 20, WINDOW_H - self.h - 230)
        self.frame_index = (self.frame_index + dt * self.frame_speed) % max(1, len(self.frames))
        if self.attack_timer > 0:
            self.attack_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.attack_timer <= 0:
            self.attack_timer = random.uniform(*SPIDER_ATTACK_COOLDOWN)
            self.shoot_at(player, projectiles)
        self.rect.update(int(self.x), int(self.y), self.w, self.h)

    def shoot_at(self, player, projectiles):
        if player.dead:
            return
        sx = self.x + self.w * 0.55
        sy = self.y + self.h * 0.65
        dx = (player.x + player.w * 0.5) - sx
        dy = (player.y + player.h * 0.5) - sy
        dist = max(1.0, math.hypot(dx, dy))
        vx = dx / dist * SPIDER_BALL_SPEED
        vy = dy / dist * SPIDER_BALL_SPEED
        image = self.web_ball_image.copy() if self.web_ball_image is not None else make_web_projectile_sprite()
        projectiles.append(Projectile(sx, sy, vx, vy, image, 16, SPIDER_BALL_DAMAGE, SPIDER_WEB_SHOT, False))

    def hit(self, damage):
        if self.dead:
            return
        self.hp -= damage
        self.flash_timer = 0.15
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface):
        if self.frames:
            frame = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            frame = None
        if frame is not None:
            if self.flash_timer > 0:
                flash = frame.copy()
                flash.fill((255, 255, 255, 70), special_flags=pygame.BLEND_RGBA_ADD)
                frame = flash
            surface.blit(frame, (int(self.x), int(self.y)))
        else:
            pygame.draw.circle(surface, (20, 20, 20), (int(self.x), int(self.y)), 100)

        bar_w = 420
        bar_h = 18
        bx = WINDOW_W // 2 - bar_w // 2
        by = 18
        pygame.draw.rect(surface, (20, 20, 20), (bx, by, bar_w, bar_h), border_radius=8)
        fill_w = int(bar_w * max(0, self.hp) / self.max_hp)
        pygame.draw.rect(surface, (190, 52, 76), (bx, by, fill_w, bar_h), border_radius=8)
        pygame.draw.rect(surface, (240, 220, 220), (bx, by, bar_w, bar_h), 2, border_radius=8)
        draw_text(surface, "ARANHA SOMBRIA", 18, UI_TEXT, WINDOW_W // 2, by + 9, center=True)


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock = pygame.time.Clock()

    background_image = load_image_or_none(BACKGROUND_IMAGE_PATH, (WINDOW_W, WINDOW_H))
    player_image = load_image_or_none(PLAYER_IMAGE_PATH, PLAYER_SIZE)
    win_image = load_image_or_none(WIN_IMAGE_PATH, (WINDOW_W, WINDOW_H))
    web_ball = load_image_or_none(WEB_PROJECTILE_IMAGE_PATH, (96, 96))
    spider_frames = load_frames(SPIDER_SPRITE_DIR, "spider_idle_{}.png", scale_to=(320, 320))

    player = Player(150, WINDOW_H - 210, image=player_image)
    spider = SpiderBoss(WINDOW_W - 420, 40, spider_frames, web_ball_image=web_ball)
    projectiles = []

    state = "fight"
    close_progress = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()

        if state == "fight":
            player.update(dt, keys, projectiles)
            spider.update(dt, player, projectiles)

            for proj in projectiles[:]:
                proj.update(dt)
                if proj.x < -150 or proj.x > WINDOW_W + 150 or proj.y < -150 or proj.y > WINDOW_H + 150:
                    projectiles.remove(proj)
                    continue
                if proj.from_player and not spider.dead and spider.rect.colliderect(proj.rect()):
                    spider.hit(proj.damage)
                    if proj in projectiles:
                        projectiles.remove(proj)
                    continue
                if not proj.from_player and not player.dead and player.rect.colliderect(proj.rect()):
                    player.hit(proj.damage)
                    if proj in projectiles:
                        projectiles.remove(proj)
                    continue

            if spider.dead:
                state = "transition"
                close_progress = 0.0
            if player.dead:
                state = "gameover"

        elif state == "transition":
            close_progress += dt / CIRCLE_CLOSE_DURATION
            if close_progress >= 1.0:
                close_progress = 1.0
                state = "win"

        draw_cave_bg(screen, background_image)
        for proj in projectiles:
            proj.draw(screen)
        spider.draw(screen)
        player.draw(screen)

        hp_bar_w = 260
        hp_bar_h = 18
        px = 20
        py = WINDOW_H - 30
        pygame.draw.rect(screen, (20, 20, 20), (px, py, hp_bar_w, hp_bar_h), border_radius=8)
        pygame.draw.rect(screen, (82, 214, 118), (px, py, int(hp_bar_w * max(0, player.hp) / PLAYER_MAX_HP), hp_bar_h), border_radius=8)
        pygame.draw.rect(screen, (240, 220, 220), (px, py, hp_bar_w, hp_bar_h), 2, border_radius=8)
        draw_text(screen, "JOGADOR", 18, UI_TEXT, px + hp_bar_w + 62, py + 9, center=True)
        draw_text(screen, "WASD / SETAS para mover  |  ESPACO para atirar  |  ESC para sair", 20, UI_TEXT, WINDOW_W // 2, WINDOW_H - 18)

        if state == "transition":
            draw_circular_close(screen, close_progress)

        if state == "win":
            if win_image is not None:
                screen.blit(win_image, (0, 0))
            else:
                screen.fill((15, 12, 20))
                draw_text(screen, "VITORIA!", 72, (255, 210, 90), WINDOW_W // 2, WINDOW_H // 2 - 30)
                draw_text(screen, "Coloque sua imagem em WIN_IMAGE_PATH", 28, UI_TEXT, WINDOW_W // 2, WINDOW_H // 2 + 35)
                draw_text(screen, "e/ou troque os sprites no codigo.", 26, UI_TEXT, WINDOW_W // 2, WINDOW_H // 2 + 70)

        if state == "gameover":
            overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "GAME OVER", 72, (255, 92, 110), WINDOW_W // 2, WINDOW_H // 2 - 20)
            draw_text(screen, "Pressione ESC para sair", 28, UI_TEXT, WINDOW_W // 2, WINDOW_H // 2 + 40)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
