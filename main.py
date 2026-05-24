import sys
import math
import random
from dataclasses import dataclass

import pygame

# ============================================================
# INIT
# ============================================================
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

WIDTH, HEIGHT = 1280, 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Halloween Adventures")
clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (220,  40,  40)
DARK_RED   = (140,   0,   0)
GREEN      = (50,  200,  80)
BLUE       = (60,  120, 220)
YELLOW     = (255, 220,  50)
ORANGE     = (255, 140,   0)
PURPLE     = (180,  60, 220)
PINK       = (255, 100, 180)
CYAN       = (60,  220, 220)
DARK_BLUE  = (20,   20,  60)
GRAY       = (120, 120, 120)
LIGHT_GRAY = (200, 200, 200)
BG_TOP     = (30,   10,  60)
BG_BOT     = (80,   20,  20)
GOLD       = (255, 200,   0)
TEAL       = (0,   180, 160)
DARK       = (20,   20,  30)
BOLT_C     = (200, 240, 255)
# ============================================================
# CORES MENU / HISTÓRIA
# ============================================================

COR_TITULO_FB  = (255, 160, 20)
COR_BOTAO_FB   = (120, 50, 10)
COR_BOTAO_HV   = (200, 90, 20)
COR_BOTAO_TXT  = (255, 220, 80)
COR_PARTICULA  = (255, 120, 20)
COR_HISTORIA   = (255, 165, 0)

# ============================================================
# FONTS
# ============================================================
font_big   = pygame.font.SysFont("impact", 52)
font_med   = pygame.font.SysFont("impact", 32)
font_small = pygame.font.SysFont("arial", 22)
font_tiny  = pygame.font.SysFont("arial", 16)
font_lg    = pygame.font.SysFont("monospace", 36, bold=True)
font_sm    = pygame.font.SysFont("monospace", 20)

# ============================================================
# SHAKES / UTILS
# ============================================================
SHAKE_FRAMES = 0
SHAKE_POWER = 0


def add_screen_shake(frames=8, power=5):
    global SHAKE_FRAMES, SHAKE_POWER
    SHAKE_FRAMES = max(SHAKE_FRAMES, frames)
    SHAKE_POWER = max(SHAKE_POWER, power)


def get_screen_shake_offset():
    global SHAKE_FRAMES, SHAKE_POWER
    if SHAKE_FRAMES <= 0:
        return 0, 0
    SHAKE_FRAMES -= 1
    return random.randint(-SHAKE_POWER, SHAKE_POWER), random.randint(-SHAKE_POWER, SHAKE_POWER)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def normalize(dx, dy):
    d = math.hypot(dx, dy)
    if d == 0:
        return 0.0, 0.0
    return dx / d, dy / d


def draw_text(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_text_shadow(surf, text, font, color, x, y, shadow_col=BLACK):
    sh = font.render(text, True, shadow_col)
    surf.blit(sh, (x + 2, y + 2))
    img = font.render(text, True, color)
    surf.blit(img, (x, y))


def draw_gradient_rect(surf, color_top, color_bot, rect):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (
            int(color_top[0] + (color_bot[0] - color_top[0]) * t),
            int(color_top[1] + (color_bot[1] - color_top[1]) * t),
            int(color_top[2] + (color_bot[2] - color_top[2]) * t),
        )
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ============================================================
# GLOBAL ARENA SETTINGS
# ============================================================
GROUND_Y = HEIGHT - 80
TESLA_XS = [160, WIDTH // 2, WIDTH - 160]
CLOWN_PLATFORMS = [
    pygame.Rect(100, 500, 160, 18),
    pygame.Rect(360, 430, 160, 18),
    pygame.Rect(700, 360, 160, 18),
    pygame.Rect(980, 460, 160, 18),
    pygame.Rect(250, 310, 140, 18),
    pygame.Rect(620, 260, 180, 18),
]

# ============================================================
# CHARACTERS
# ============================================================
CHARACTERS = [
    {
        "name": "Bruxinha",
        "body_color": (150, 70, 200),
        "head_color": (230, 200, 170),
        "bullet_color": (180, 220, 255),
        "speed": 5,
        "max_hp": 200,
        "shot_style": "potion",
        "shot_cd": 14,
        "shot_speed": 15,
        "shot_damage": 8,
        "bullet_radius": 7,
    },
    {
        "name": "Vampiro",
        "body_color": (120, 20, 40),
        "head_color": (220, 190, 170),
        "bullet_color": (255, 80, 120),
        "speed": 5,
        "max_hp": 200,
        "shot_style": "triple",
        "shot_cd": 24,
        "shot_speed": 10,
        "shot_damage": 6,
        "bullet_radius": 5,
    },
    {
        "name": "Dragaozinho",
        "body_color": (40, 160, 90),
        "head_color": (255, 170, 70),
        "bullet_color": (255, 120, 40),
        "speed": 5,
        "max_hp": 200,
        "shot_style": "fireball",
        "shot_cd": 16,
        "shot_speed": 0,
        "shot_damage": 0,
        "bullet_radius": 0,
        "max_charge_frames": 60,
        "min_fire_speed": 10,
        "max_fire_speed": 20,
        "min_fire_damage": 10,
        "max_fire_damage": 30,
        "min_fire_radius": 8,
        "max_fire_radius": 18,
    },
    {
        "name": "Esqueleto",
        "body_color": (210, 210, 210),
        "head_color": (245, 245, 245),
        "bullet_color": (220, 220, 220),
        "speed": 5,
        "max_hp": 200,
        "shot_style": "boomerang",
        "shot_cd": 22,
        "shot_speed": 12,
        "shot_damage": 7,
        "bullet_radius": 5,
    },
]

WEAPON_NAMES = {
    "potion": "Potion",
    "triple": "Triple Shot",
    "fireball": "Fireball",
    "boomerang": "Boomerang",
}
# ============================================================
# CHARACTER SELECT SPRITES
# ============================================================

def load_select_sprite(path, size=120):

    img = pygame.image.load(path).convert_alpha()

    w, h = img.get_size()

    scale = size / max(w, h)

    new_w = int(w * scale)
    new_h = int(h * scale)

    img = pygame.transform.scale(img, (new_w, new_h))

    return img


SELECT_SPRITES = {

    "Bruxinha":
        load_select_sprite(
            "assets/bruxinha_transparent.png",
            120
        ),

    "Vampiro":
        load_select_sprite(
            "assets/vampirinho_transparent.png",
            120
        ),

    "Dragaozinho":
        load_select_sprite(
            "assets/dragaozinho_transparent.png",
            120
        ),

    "Esqueleto":
        load_select_sprite(
            "assets/esqueletinho_transparent.png",
            120
        ),
}
# ============================================================
# STORIES
# ============================================================
INTRO_STORY = [
    "A noite começou.\nUma energia estranha tomou conta da floresta amaldiçoada.",
    "Criaturas antigas despertaram.\nTeias, circos macabros e experimentos proibidos aguardam.",
    "Escolha seu herói.\nO mesmo aventureiro enfrentará todos os terrores da noite.",
    "Sobreviva...\nse conseguir."
]

STORY_AFTER_SPIDER = [
    "A aranha caiu...\nmas a floresta ainda sussurra seu nome.",
    "Ao longe, luzes estranhas aparecem na escuridão.",
    "O circo amaldiçoado abriu suas portas."
]

STORY_AFTER_CLOWN = [
    "O palhaço foi derrotado...\nmas os gritos ainda ecoam no circo.",
    "Relâmpagos iluminam o céu.",
    "Algo terrível desperta no laboratório de Frankenstein."
]

STORY_AFTER_FRANK = [
    "O monstro caiu.\nO laboratório finalmente ficou em silêncio.",
    "Mas a própria noite começa a se distorcer.",
    "Uma presença ancestral desperta das sombras.",
    "O verdadeiro mestre do pesadelo apareceu."
]

FINAL_BOSS_STORY = [
    "As sombras pararam de se mover.",
    "Algo antigo e faminto abriu os olhos no coração da noite.",
    "A aranha, o circo e o laboratório eram apenas sinais do que estava por vir.",
    "Encare o verdadeiro mestre do pesadelo."
]

# ============================================================
# UI SHARED
# ============================================================
def draw_heart(surf, x, y, filled=True):
    col = RED if filled else DARK_RED
    pygame.draw.circle(surf, col, (x - 6, y - 4), 6)
    pygame.draw.circle(surf, col, (x + 6, y - 4), 6)
    pygame.draw.polygon(surf, col, [(x - 12, y - 1), (x + 12, y - 1), (x, y + 14)])


def draw_character_portrait(surf, char, x, y, scale=1.0, facing=1):
    w = int(40 * scale)
    h = int(52 * scale)
    body = pygame.Rect(x + int(4 * scale), y + int(16 * scale), w, h)
    pygame.draw.rect(surf, char["body_color"], body, border_radius=max(2, int(5 * scale)))
    head = pygame.Rect(x + int(8 * scale), y, w - int(8 * scale), int(20 * scale))
    pygame.draw.rect(surf, char["head_color"], head, border_radius=max(2, int(5 * scale)))
    pygame.draw.circle(surf, BLACK, (head.centerx - int(5 * facing * scale), head.centery), max(1, int(2 * scale)))
    pygame.draw.circle(surf, BLACK, (head.centerx + int(5 * facing * scale), head.centery), max(1, int(2 * scale)))
    name = char["name"]
    if name == "Bruxinha":
        hat = [(head.centerx - int(14 * scale), head.top + 2), (head.centerx + int(14 * scale), head.top + 2), (head.centerx, head.top - int(20 * scale))]
        pygame.draw.polygon(surf, PURPLE, hat)
        pygame.draw.circle(surf, YELLOW, (head.centerx, head.top - int(22 * scale)), max(2, int(3 * scale)))
    elif name == "Vampiro":
        pygame.draw.polygon(surf, (60, 60, 80), [(body.left - int(5 * scale), body.top + int(12 * scale)), (body.left + int(10 * scale), body.top + int(40 * scale)), (body.left + int(16 * scale), body.top + int(10 * scale))])
        pygame.draw.polygon(surf, (60, 60, 80), [(body.right + int(5 * scale), body.top + int(12 * scale)), (body.right - int(10 * scale), body.top + int(40 * scale)), (body.right - int(16 * scale), body.top + int(10 * scale))])
    elif name == "Dragaozinho":
        pygame.draw.polygon(surf, (20, 120, 60), [(body.left - int(8 * scale), body.top + int(10 * scale)), (body.left + int(8 * scale), body.top + int(28 * scale)), (body.left + int(10 * scale), body.top + int(2 * scale))])
        pygame.draw.polygon(surf, (20, 120, 60), [(body.right + int(8 * scale), body.top + int(10 * scale)), (body.right - int(8 * scale), body.top + int(28 * scale)), (body.right - int(10 * scale), body.top + int(2 * scale))])
    elif name == "Esqueleto":
        pygame.draw.line(surf, BLACK, (body.centerx, body.top + int(4 * scale)), (body.centerx, body.bottom), max(1, int(2 * scale)))
        pygame.draw.line(surf, BLACK, (body.left + int(4 * scale), body.top + int(14 * scale)), (body.right - int(4 * scale), body.top + int(14 * scale)), max(1, int(2 * scale)))


def draw_player_sprite(surf, player):
    r = player.rect
    cx = r.centerx
    top = r.top
    body = pygame.Rect(r.x, r.y + 10, r.w, r.h - 10)
    pygame.draw.rect(surf, player.body_color, body, border_radius=5)
    head = pygame.Rect(body.x + 4, body.y - 18, body.w - 8, 18)
    pygame.draw.rect(surf, player.head_color, head, border_radius=5)
    pygame.draw.circle(surf, BLACK, (head.centerx - 4 * player.facing, head.centery), 2)

    name = player.character["name"]
    if name == "Bruxinha":
        hat = [(cx - 12, top + 10), (cx + 12, top + 10), (cx, top - 10)]
        pygame.draw.polygon(surf, PURPLE, hat)
        pygame.draw.line(surf, YELLOW, (cx - 10, top + 10), (cx + 10, top + 10), 2)
    elif name == "Vampiro":
        pygame.draw.polygon(surf, (20, 20, 30), [(body.left - 4, body.top + 10), (body.left + 6, body.top + 28), (body.left + 12, body.top + 8)])
        pygame.draw.polygon(surf, (20, 20, 30), [(body.right + 4, body.top + 10), (body.right - 6, body.top + 28), (body.right - 12, body.top + 8)])
    elif name == "Dragaozinho":
        pygame.draw.polygon(surf, (20, 120, 60), [(body.left - 5, body.top + 12), (body.left + 5, body.top + 24), (body.left + 8, body.top + 6)])
        pygame.draw.polygon(surf, (20, 120, 60), [(body.right + 5, body.top + 12), (body.right - 5, body.top + 24), (body.right - 8, body.top + 6)])
        pygame.draw.polygon(surf, (60, 180, 100), [(body.centerx - 6, body.bottom - 2), (body.centerx + 8, body.bottom + 6), (body.centerx + 2, body.bottom - 10)])
    elif name == "Esqueleto":
        pygame.draw.line(surf, BLACK, (body.centerx, body.top + 4), (body.centerx, body.bottom + 2), 2)
        pygame.draw.line(surf, BLACK, (body.left + 3, body.top + 12), (body.right - 3, body.top + 12), 2)

    if player.shot_style == "fireball" and player.is_charging:
        power = max(0.25, min(1.0, player.charge_frames / max(1, player.max_charge_frames)))
        aura_r = int(16 + 26 * power)
        aura = pygame.Surface((aura_r * 4, aura_r * 4), pygame.SRCALPHA)
        c = (aura.get_width() // 2, aura.get_height() // 2)
        pygame.draw.circle(aura, (255, 80, 20, 70), c, aura_r + 8)
        pygame.draw.circle(aura, (255, 180, 50, 110), c, aura_r + 3)
        surf.blit(aura, (body.centerx - c[0], body.centery - c[1] - 8))


def draw_hp_panel(surf, player):
    panel = pygame.Rect(8, 8, 250, 78)
    pygame.draw.rect(surf, (20, 20, 35), panel, border_radius=12)
    pygame.draw.rect(surf, (90, 90, 120), panel, 2, border_radius=12)
    draw_character_portrait(surf, player.character, 16, 14, scale=0.75, facing=1)
    draw_text_shadow(surf, player.character["name"], font_small, WHITE, 76, 14)
    bar_x, bar_y, bar_w, bar_h = 76, 34, 154, 14
    pygame.draw.rect(surf, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    pygame.draw.rect(surf, GREEN, (bar_x, bar_y, int(bar_w * max(0, player.hp) / player.MAX_HP), bar_h), border_radius=4)
    filled = max(0, min(3, int(math.ceil((player.hp / player.MAX_HP) * 3))))
    for i in range(3):
        draw_heart(surf, 78 + i * 26, 60, i < filled)


def draw_top_right_name(surf, player):
    draw_text_shadow(surf, f"Hero: {player.character['name']}", font_sm, CYAN, WIDTH - 250, 12)


def draw_center_top_title(surf, title, subtitle=""):
    draw_text_shadow(surf, title, font_med, YELLOW, WIDTH // 2 - len(title) * 8, 10)
    if subtitle:
        draw_text_shadow(surf, subtitle, font_sm, CYAN, WIDTH // 2 - len(subtitle) * 5, 42)


def draw_controls_panel(surf, lines):

    panel = pygame.Rect(8, 96, 250, 88)

    pygame.draw.rect(
        surf,
        (20, 20, 35),
        panel,
        border_radius=12
    )

    pygame.draw.rect(
        surf,
        (90, 90, 120),
        panel,
        2,
        border_radius=12
    )

    y = 108

    for line in lines:

        draw_text_shadow(
            surf,
            line,
            font_tiny,
            WHITE,
            20,
            y
        )

        y += 18


def draw_weapon_icon(surf, player, x, y):
    style = player.shot_style
    if style == "potion":
        pygame.draw.circle(surf, (90, 170, 255), (x, y), 16)
        pygame.draw.circle(surf, WHITE, (x, y), 16, 2)
        pygame.draw.circle(surf, WHITE, (x - 4, y - 4), 4)
    elif style == "triple":
        for off in (-14, 0, 14):
            pygame.draw.circle(surf, (255, 80, 120), (x + off, y), 7)
            pygame.draw.circle(surf, WHITE, (x + off, y), 7, 2)
    elif style == "fireball":
        pygame.draw.circle(surf, (255, 110, 20), (x, y), 16)
        pygame.draw.circle(surf, (255, 180, 50), (x, y), 10)
        pygame.draw.circle(surf, WHITE, (x - 3, y - 3), 3)
    elif style == "boomerang":
        pygame.draw.arc(surf, (220, 220, 220), (x - 16, y - 14, 28, 24), math.radians(25), math.radians(335), 4)
        pygame.draw.circle(surf, WHITE, (x + 10, y), 3)


def draw_weapon_panel(surf, player):

    panel = pygame.Rect(8, 194, 250, 88)

    pygame.draw.rect(
        surf,
        (20, 20, 35),
        panel,
        border_radius=12
    )

    pygame.draw.rect(
        surf,
        (90, 90, 120),
        panel,
        2,
        border_radius=12
    )

    ix = 36
    iy = 238

    draw_weapon_icon(
        surf,
        player,
        ix,
        iy
    )

    draw_text_shadow(
        surf,
        WEAPON_NAMES.get(player.shot_style, player.shot_style),
        font_small,
        WHITE,
        68,
        208
    )

    draw_text_shadow(
        surf,
        f"Damage: {player.get_weapon_damage()}",
        font_tiny,
        LIGHT_GRAY,
        68,
        236
    )

    draw_text_shadow(
        surf,
        f"Cadence: {player.shot_cd_max}f",
        font_tiny,
        LIGHT_GRAY,
        68,
        256
    )

    if player.shot_style == "fireball":

        draw_text_shadow(
            surf,
            "Hold click",
            font_tiny,
            YELLOW,
            68,
            276
        )

def draw_bottom_hearts(surf, player):
    cx = WIDTH // 2
    y = HEIGHT - 56
    filled = max(0, min(3, int(math.ceil((player.hp / player.MAX_HP) * 3))))
    for i in range(3):
        draw_heart(surf, cx + (i - 1) * 70, y, i < filled)


def draw_common_hud(surf, player, boss_title, boss_hp=None, boss_max_hp=None, sub_title=""):
    draw_hp_panel(surf, player)
    draw_top_right_name(surf, player)
    draw_center_top_title(surf, boss_title, sub_title)
    if boss_hp is not None and boss_max_hp is not None:
        bar_w = 420
        bar_x = WIDTH // 2 - bar_w // 2
        bar_y = 52
        pygame.draw.rect(surf, GRAY, (bar_x, bar_y, bar_w, 18), border_radius=6)
        ratio = max(0, boss_hp) / boss_max_hp
        pygame.draw.rect(surf, RED, (bar_x, bar_y, int(bar_w * ratio), 18), border_radius=6)
        pygame.draw.rect(surf, GOLD, (bar_x, bar_y, bar_w, 18), 2, border_radius=6)
    draw_controls_panel(surf, [
        "W A S D or Arrows: move",
        "SPACE: jump",
        "Mouse click: attack",
    ])
    draw_bottom_hearts(surf, player)
    draw_weapon_panel(surf, player)


# ============================================================
# MENU / SCREENS
# ============================================================
class StoryPlayer:
    def __init__(self, slides, title="STORY"):
        self.slides = slides
        self.title = title
        self.idx = 0
        self.timer = 0.0
        self.phase = "in"
        self.alpha = 0
        self.done = False

    def update(self, dt, events):
        if self.done:
            return
        self.timer += dt
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.timer = 999
        fade = 0.45
        show = 3.2
        if self.phase == "in":
            self.alpha = min(255, int(255 * self.timer / fade))
            if self.timer >= fade:
                self.phase = "show"
                self.timer = 0.0
        elif self.phase == "show":
            self.alpha = 255
            if self.timer >= show:
                self.phase = "out"
                self.timer = 0.0
        elif self.phase == "out":
            self.alpha = max(0, 255 - int(255 * self.timer / fade))
            if self.timer >= fade:
                self.idx += 1
                if self.idx >= len(self.slides):
                    self.done = True
                else:
                    self.phase = "in"
                    self.timer = 0.0

    def draw(self, surf):
        draw_gradient_rect(surf, (12, 6, 24), (32, 10, 40), (0, 0, WIDTH, HEIGHT))
        for i in range(6):
            pygame.draw.circle(surf, (40, 0, 60), (120 + i * 220, HEIGHT // 2), 90 + i * 8, 3)
        title = font_lg.render(self.title, True, WHITE)
        surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))
        if self.idx < len(self.slides):
            slide = self.slides[self.idx]
            lines = []
            for part in slide.split("\n"):
                lines.extend(wrap_text(part, font_med, WIDTH - 260))
            total_h = len(lines) * (font_med.get_height() + 8)
            y = HEIGHT // 2 - total_h // 2
            box = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for line in lines:
                txt = font_med.render(line, True, ORANGE)
                box.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))
                y += font_med.get_height() + 8
            box.set_alpha(self.alpha)
            surf.blit(box, (0, 0))
        hint = font_tiny.render("SPACE or ENTER to skip / continue", True, (130, 100, 60))
        surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 28))
        # dots
        n = len(self.slides)
        for i in range(n):
            c = (255, 165, 0) if i == self.idx else (60, 45, 20)
            pygame.draw.circle(surf, c, (WIDTH // 2 - (n - 1) * 14 + i * 28, HEIGHT - 50), 6)


def run_story(slides, title="STORY"):
    sp = StoryPlayer(slides, title)
    while not sp.done:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        sp.update(dt, events)
        sp.draw(screen)
        pygame.display.flip()


class MenuButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 140, int(HEIGHT * 0.78), 280, 90)
        self.hover = False
        self.t = 0.0

    def update(self, mpos):
        self.hover = self.rect.collidepoint(mpos)
        self.t += 0.06

    def clicked(self, ev):
        return ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos)

    def draw(self, surf):
        esc = 1.06 if self.hover else 1.0 + 0.02 * math.sin(self.t)
        w = int(self.rect.w * esc)
        h = int(self.rect.h * esc)
        rx = self.rect.centerx - w // 2
        ry = self.rect.centery - h // 2
        glow = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        glow.fill((255, 120, 0, 50 if self.hover else 25))
        surf.blit(glow, (rx - 10, ry - 10))
        pygame.draw.rect(surf, (0, 0, 0), (rx + 4, ry + 5, w, h), border_radius=14)
        pygame.draw.rect(surf, (255, 160, 40) if self.hover else (120, 50, 10), (rx, ry, w, h), border_radius=14)
        pygame.draw.rect(surf, GOLD if self.hover else (180, 100, 20), (rx, ry, w, h), 2, border_radius=14)
        txt = font_med.render("START", True, WHITE)
        surf.blit(txt, (rx + (w - txt.get_width()) // 2, ry + (h - txt.get_height()) // 2))


def render_menu(button, t):
    draw_gradient_rect(screen, (18, 6, 34), (6, 4, 14), (0, 0, WIDTH, HEIGHT))
    for i in range(5):
        pygame.draw.circle(screen, (40, 0, 60), (120 + i * 260, HEIGHT // 2), 90 + i * 10, 3)
    # title
    title = font_big.render("HALLOWEEN ADVENTURES", True, COR_TITULO_FB)
    shadow = font_big.render("HALLOWEEN ADVENTURES", True, BLACK)
    y = int(120 + math.sin(t * 1.3) * 8)
    screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, y + 3))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y))
    subtitle = font_sm.render("Menu -> Story -> Bosses", True, GRAY)
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, y + 72))
    button.update(pygame.mouse.get_pos())
    button.draw(screen)
    hint = font_tiny.render("Click START to begin", True, LIGHT_GRAY)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 42))

def load_png(path):
    return pygame.image.load(path).convert_alpha()


BRUXA_FRAMES = [
    load_png("assets/bruxinha idle1.png"),
    load_png("assets/bruxinha idle2.png"),
    load_png("assets/bruxinha idle3.png"),
    load_png("assets/bruxinha idle4.png"),
]

VAMPIRO_FRAMES = [
    load_png("assets/vampirinho idle1.png"),
    load_png("assets/vampirinho idle2.png"),
    load_png("assets/vampirinho idle3.png"),
    load_png("assets/vampirinho idle4.png"),
]

DRAGAO_FRAMES = [
    load_png("assets/dragãozinho idle1.png"),
    load_png("assets/dragãozinho idle2.png"),
    load_png("assets/dragãozinho idle3.png"),
    load_png("assets/dragãozinho idle4.png"),
]

ESQUELETO_FRAMES = [
    load_png("assets/esqueletinho idle1.png"),
    load_png("assets/esqueletinho idle2.png"),
    load_png("assets/esqueletinho idle3.png"),
    load_png("assets/esqueletinho idle4.png"),
]


def character_select():
    selected = 0
    anim_timer = 0

    sprites = {
        "Bruxinha": BRUXA_FRAMES,
        "Vampiro": VAMPIRO_FRAMES,
        "Dragaozinho": DRAGAO_FRAMES,
        "Esqueleto": ESQUELETO_FRAMES,
    }

    while True:
        dt = clock.tick(FPS) / 1000.0
        anim_timer += 1
        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(CHARACTERS)
                elif ev.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(CHARACTERS)
                elif ev.key == pygame.K_RETURN:
                    return CHARACTERS[selected]
                elif ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        draw_gradient_rect(screen, (22, 8, 40), (10, 6, 20), (0, 0, WIDTH, HEIGHT))
        for i in range(5):
            pygame.draw.circle(screen, (40, 0, 60), (120 + i * 260, HEIGHT // 2), 90 + i * 10, 3)

        draw_text(screen, "CHOOSE YOUR HERO", font_lg, WHITE, WIDTH // 2, 90)
        draw_text(screen, "Use LEFT / RIGHT and press ENTER", font_sm, GRAY, WIDTH // 2, 135)
        draw_text(screen, "The same hero will fight all bosses.", font_sm, YELLOW, WIDTH // 2, 162)

        spacing = 260
        start_x = WIDTH // 2 - spacing * 1.5
        styles = {"potion": "Potion", "triple": "Triple", "fireball": "Fireball", "boomerang": "Boomerang"}

        for i, char in enumerate(CHARACTERS):
            x = int(start_x + i * spacing)
            y = HEIGHT // 2 + 30
            sel = i == selected

            card = pygame.Rect(x - 78, y - 95, 156, 210)
            pygame.draw.rect(screen, (18, 18, 30), card, border_radius=14)
            pygame.draw.rect(screen, GOLD if sel else (80, 80, 110), card, 2, border_radius=14)

            frame_list = sprites.get(char["name"])
            if frame_list:
                if sel:
                    frame = frame_list[(anim_timer // 10) % len(frame_list)]
                else:
                    frame = frame_list[0]
                img = pygame.transform.smoothscale(frame, (120, 120))
                screen.blit(img, (x - img.get_width() // 2, y - 85))
            else:
                draw_character_portrait(screen, char, x - 48, y - 58, scale=1.35)

            draw_text(screen, char["name"], font_small, WHITE if sel else GRAY, x, y + 78)
            draw_text(screen, styles.get(char["shot_style"], char["shot_style"]), font_tiny, (180, 180, 200), x, y + 110)

        draw_text(screen, "LEFT/RIGHT choose   ENTER confirm   ESC quit", font_sm, GRAY, WIDTH // 2, HEIGHT - 50)
        pygame.display.flip()


def final_screen(title, subtitle):
    while True:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    return True
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        draw_gradient_rect(screen, (0, 40, 0), (0, 80, 40), (0, 0, WIDTH, HEIGHT))
        draw_text(screen, title, font_big, GREEN, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(screen, subtitle, font_med, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text(screen, "Press R to restart or ESC to quit", font_sm, GRAY, WIDTH // 2, HEIGHT // 2 + 70)
        pygame.display.flip()
        clock.tick(FPS)


# ============================================================
# PLAYER / BULLET
# ============================================================
class PlayerBullet:
    def __init__(self, x, y, vx, vy, color, damage=10, radius=6, kind="normal"):
        self.fx = float(x)
        self.fy = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.damage = damage
        self.radius = radius
        self.kind = kind
        self.life = 180
        self.age = 0
        self.trail = []
        self.can_damage = True
        self.returning = False
        self.return_started = False
        size = max(2, radius * 2)
        self.rect = pygame.Rect(int(x) - radius, int(y) - radius, size, size)

    def update(self):
        self.age += 1
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 10:
            self.trail.pop(0)

        if self.kind == "potion":
            self.vy += 0.12
        elif self.kind == "fireball":
            self.vy += 0.05
        elif self.kind == "boomerang":

    # demora mais para voltar
            if self.age > 65 and not self.return_started:

                self.returning = True
                self.return_started = True

                # volta mais rápido
                self.vx = -self.vx * 1.15
                self.vy = -self.vy * 0.9

            # mantém velocidade
            if self.returning:

                self.vx *= 0.999
                self.vy *= 0.999

        self.fx += self.vx
        self.fy += self.vy
        self.rect.center = (int(self.fx), int(self.fy))
        self.life -= 1
        if self.rect.right < -60 or self.rect.left > WIDTH + 60 or self.rect.top > HEIGHT + 60 or self.rect.bottom < -60:
            self.life = 0

    def draw(self, surf):
        if self.kind == "boomerang":
            ang = -math.degrees(math.atan2(self.vy, self.vx))
            bo = pygame.Surface((44, 30), pygame.SRCALPHA)
            pygame.draw.arc(bo, (*self.color, 220), (3, 4, 30, 18), math.radians(25), math.radians(335), 4)
            pygame.draw.arc(bo, (255, 255, 255, 120), (7, 8, 22, 10), math.radians(30), math.radians(330), 2)
            pygame.draw.circle(bo, self.color, (32, 14), 3)
            bo = pygame.transform.rotate(bo, ang)
            surf.blit(bo, (self.rect.centerx - bo.get_width() // 2, self.rect.centery - bo.get_height() // 2))
            return

        if self.kind in ("potion", "fireball"):
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(170 * i / max(1, len(self.trail)))
                r = max(1, self.radius * i // max(1, len(self.trail)))
                trail_s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_s, (*self.color, alpha), (r + 2, r + 2), max(1, r))
                surf.blit(trail_s, (tx - r - 2, ty - r - 2))

        if self.kind == "potion":
            glow = pygame.Surface((self.radius * 4 + 16, self.radius * 4 + 16), pygame.SRCALPHA)
            gc = (glow.get_width() // 2, glow.get_height() // 2)
            pygame.draw.circle(glow, (100, 240, 255, 70), gc, self.radius + 9)
            pygame.draw.circle(glow, (160, 255, 255, 90), gc, self.radius + 5)
            surf.blit(glow, (self.rect.centerx - gc[0], self.rect.centery - gc[1]))
            pygame.draw.circle(surf, self.color, self.rect.center, self.radius)
            pygame.draw.circle(surf, WHITE, self.rect.center, max(2, self.radius // 2))
            return

        if self.kind == "fireball":
            glow = pygame.Surface((self.radius * 4 + 20, self.radius * 4 + 20), pygame.SRCALPHA)
            gcx, gcy = glow.get_width() // 2, glow.get_height() // 2
            pygame.draw.circle(glow, (255, 90, 20, 70), (gcx, gcy), self.radius + 10)
            pygame.draw.circle(glow, (255, 170, 40, 110), (gcx, gcy), self.radius + 5)
            surf.blit(glow, (self.rect.centerx - gcx, self.rect.centery - gcy))
            pygame.draw.circle(surf, (255, 80, 20), self.rect.center, self.radius)
            pygame.draw.circle(surf, (255, 200, 60), self.rect.center, max(2, self.radius - 3))
            pygame.draw.circle(surf, WHITE, self.rect.center, max(1, self.radius - 6))
            return

        col = YELLOW if (self.age // 2) % 2 == 0 else ORANGE
        pygame.draw.ellipse(surf, col, self.rect)
        pygame.draw.ellipse(surf, WHITE, self.rect.inflate(-6, -2), 2)


class Player:
    W, H = 36, 52

    def __init__(self, character):
        self.character = character
        self.SPEED = character["speed"]
        self.MAX_HP = character["max_hp"]
        self.body_color = character["body_color"]
        self.head_color = character["head_color"]
        self.bullet_color = character["bullet_color"]
        self.shot_style = character["shot_style"]
        self.shot_cd_max = character["shot_cd"]
        self.shot_speed = character["shot_speed"]
        self.shot_damage = character["shot_damage"]
        self.bullet_radius = character["bullet_radius"]
        self.max_charge_frames = character.get("max_charge_frames", 0)
        self.min_fire_speed = character.get("min_fire_speed", 0)
        self.max_fire_speed = character.get("max_fire_speed", 0)
        self.min_fire_damage = character.get("min_fire_damage", 0)
        self.max_fire_damage = character.get("max_fire_damage", 0)
        self.min_fire_radius = character.get("min_fire_radius", 0)
        self.max_fire_radius = character.get("max_fire_radius", 0)
        self.rect = pygame.Rect(100, GROUND_Y - self.H, self.W, self.H)
        self.hp = self.MAX_HP
        self.vel_y = 0.0
        self.on_ground = False
        self.invincible_frames = 0
        self.bullets = []
        self.shoot_cd = 0
        self.facing = 1
        self.dead = False
        self.anim_t = 0.0
        self.is_charging = False
        self.charge_frames = 0

    def get_weapon_damage(self):
        if self.shot_style == "fireball":
            return self.max_fire_damage
        return self.shot_damage

    def handle_physics(self, keys, platforms, ground_y):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.SPEED
        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        self.rect.x += dx
        self.rect.x = clamp(self.rect.x, 0, WIDTH - self.W)
        self.vel_y += 0.55
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            self.on_ground = True
        for plat in platforms:
            if self.vel_y >= 0 and self.rect.colliderect(plat) and self.rect.bottom - int(self.vel_y) <= plat.top + 6:
                self.rect.bottom = plat.top
                self.vel_y = 0
                self.on_ground = True
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -15

    def _rotate(self, vx, vy, ang):
        ca, sa = math.cos(ang), math.sin(ang)
        return vx * ca - vy * sa, vx * sa + vy * ca

    def _shoot_mouse(self, mx, my):
        ox, oy = self.rect.centerx, self.rect.centery
        dx = mx - ox
        dy = my - oy
        dist = math.hypot(dx, dy) or 1
        nx, ny = dx / dist, dy / dist

        if self.shot_style == "potion":
            self.bullets.append(PlayerBullet(ox, oy, nx * self.shot_speed, ny * self.shot_speed, self.bullet_color, damage=self.shot_damage, radius=self.bullet_radius, kind="potion"))
        elif self.shot_style == "triple":
            for ang in (-0.18, 0, 0.18):
                rvx, rvy = self._rotate(nx * self.shot_speed, ny * self.shot_speed, ang)
                self.bullets.append(PlayerBullet(ox, oy, rvx, rvy, self.bullet_color, damage=self.shot_damage, radius=self.bullet_radius, kind="normal"))
        elif self.shot_style == "fireball":
            power = max(0.25, min(1.0, self.charge_frames / max(1, self.max_charge_frames)))
            speed = lerp(self.min_fire_speed, self.max_fire_speed, power)
            damage = int(lerp(self.min_fire_damage, self.max_fire_damage, power))
            radius = int(lerp(self.min_fire_radius, self.max_fire_radius, power))
            self.bullets.append(PlayerBullet(ox, oy, nx * speed, ny * speed, self.bullet_color, damage=damage, radius=radius, kind="fireball"))
        elif self.shot_style == "boomerang":
            self.bullets.append(PlayerBullet(ox, oy, nx * self.shot_speed, ny * self.shot_speed, self.bullet_color, damage=self.shot_damage, radius=self.bullet_radius, kind="boomerang"))

    def update_frank(self, events, ground_y=None, platforms=None):
        if platforms is None:
            platforms = []
        if ground_y is None:
            ground_y = GROUND_Y
        keys = pygame.key.get_pressed()
        self.handle_physics(keys, platforms, ground_y)
        self.shoot_cd = max(0, self.shoot_cd - 1)
        mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]

        if self.shot_style == "fireball":
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.shoot_cd == 0 and not self.is_charging:
                    self.is_charging = True
                    self.charge_frames = 0
            if self.is_charging:
                if mouse_down:
                    self.charge_frames = min(self.max_charge_frames, self.charge_frames + 1)
                else:
                    mx, my = pygame.mouse.get_pos()
                    self._shoot_mouse(mx, my)
                    self.is_charging = False
                    self.shoot_cd = self.shot_cd_max
        else:
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.shoot_cd == 0:
                    mx, my = pygame.mouse.get_pos()
                    self._shoot_mouse(mx, my)
                    self.shoot_cd = self.shot_cd_max

        for b in self.bullets[:]:
            b.update()
            if b.life <= 0:
                self.bullets.remove(b)

        if self.invincible_frames > 0:
            self.invincible_frames -= 1
        self.anim_t += 0.016

    def take_damage(self, dmg):
        if self.invincible_frames == 0:
            self.hp -= dmg
            self.invincible_frames = 45
            if self.hp <= 0:
                self.dead = True

    def draw(self, surf):
        if self.invincible_frames > 0 and (self.invincible_frames // 5) % 2 == 0:
            return
        draw_player_sprite(surf, self)
        for b in self.bullets:
            b.draw(surf)

    def draw_current_sprite(self, surf):
        draw_player_sprite(surf, self)


# ============================================================
# BOSS 0 - SPIDER
# ============================================================
class SpiderWebProjectile:
    def __init__(self, x, y, vx, vy, damage=12):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.life = 220
        self.rect = pygame.Rect(int(x) - 12, int(y) - 12, 24, 24)
        self.spin = random.uniform(0, math.pi * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.spin += 0.2
        self.life -= 1
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surf):
        pygame.draw.circle(surf, (235, 235, 245), self.rect.center, 11)
        pygame.draw.circle(surf, (190, 190, 205), self.rect.center, 11, 2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang) + self.spin
            x2 = self.rect.centerx + int(math.cos(rad) * 12)
            y2 = self.rect.centery + int(math.sin(rad) * 12)
            pygame.draw.line(surf, (235, 235, 245), self.rect.center, (x2, y2), 1)


class SpiderBoss:
    def __init__(self):
        self.max_hp = 650
        self.hp = self.max_hp
        self.rage = False
        self.dead = False
        self.t = 0.0
        self.attack_cd = 0.0
        self.x = WIDTH * 0.62
        self.y = 140
        self.webs = []
        self.flash = 0.0
        self.movement_phase = 0.0
        self.rect = pygame.Rect(int(self.x) - 120, int(self.y) - 80, 240, 180)

    def take_damage(self, dmg):
        self.hp -= dmg
        self.flash = 0.14
        self.rage = self.hp <= self.max_hp * 0.45
        if self.hp <= 0:
            self.dead = True
        return self.dead

    def _spawn_web(self, player, offset_x=0, offset_y=0):
        sx = self.x + 5 + offset_x
        sy = self.y + 40 + offset_y
        dx = player.rect.centerx - sx
        dy = player.rect.centery - sy
        dist = math.hypot(dx, dy) or 1
        spd = 5.3 if not self.rage else 6.6
        self.webs.append(
            SpiderWebProjectile(
                sx, sy,
                dx / dist * spd,
                dy / dist * spd,
                damage=12 if not self.rage else 15
            )
        )

    def update(self, dt, player):
        self.t += dt
        self.flash = max(0.0, self.flash - dt)
        self.movement_phase += dt * (1.2 if not self.rage else 1.75)

        self.x = WIDTH * 0.52 + math.sin(self.movement_phase * 1.6) * 420
        self.y = 120 + math.sin(self.movement_phase * 2.2) * 110

        if self.rage:
            self.x += math.sin(self.movement_phase * 4.5) * 50
            self.y += math.cos(self.movement_phase * 3.8) * 28

        self.x = clamp(self.x, 120, WIDTH - 180)
        self.y = clamp(self.y, 60, 300)
        self.rect.update(int(self.x) - 120, int(self.y) - 80, 240, 180)

        self.attack_cd -= dt
        if self.attack_cd <= 0:
            self.attack_cd = random.uniform(0.95, 1.7) if not self.rage else random.uniform(0.55, 1.0)
            self._spawn_web(player)
            if self.rage:
                self._spawn_web(player, offset_x=-25, offset_y=10)
                self._spawn_web(player, offset_x=25, offset_y=10)

        for w in self.webs[:]:
            w.update()
            if (
                w.life <= 0
                or w.rect.right < -50
                or w.rect.left > WIDTH + 50
                or w.rect.bottom < -50
                or w.rect.top > HEIGHT + 50
            ):
                self.webs.remove(w)

    def draw_bg(self, surf):
        surf.fill((19, 16, 31))
        for i in range(80):
            x = (i * 167) % WIDTH
            y = (i * 41) % (HEIGHT // 2)
            c = 50 + (i % 4) * 20
            pygame.draw.circle(surf, (c, c, c), (x, y), 1)
        pygame.draw.rect(surf, (39, 33, 45), (0, 520, WIDTH, 200))
        pygame.draw.ellipse(surf, (92, 79, 72), (250, 520, 780, 220))
        pygame.draw.polygon(surf, (39, 33, 45), [(0, 0), (170, 140), (0, 300)])
        pygame.draw.polygon(surf, (39, 33, 45), [(WIDTH, 0), (WIDTH - 170, 140), (WIDTH, 300)])
        for x in range(0, WIDTH, 90):
            y = 470 + int(8 * math.sin(x * 0.06))
            pygame.draw.circle(surf, (98, 84, 76), (x + 18, y + 20), 8)
            pygame.draw.circle(surf, (80, 70, 64), (x + 40, y + 26), 5)

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        body_col = (40, 40, 40) if not self.rage else (65, 25, 25)
        pygame.draw.circle(surf, body_col, (cx, cy + 35), 58)
        pygame.draw.circle(surf, (25, 25, 25), (cx, cy + 35), 58, 4)

        for side in (-1, 1):
            for i in range(4):
                ang = -0.9 + i * 0.35
                x1 = cx + side * 40
                y1 = cy + 40 + i * 6
                x2 = x1 + int(side * math.cos(ang) * 100)
                y2 = y1 + int(math.sin(ang) * 70)
                pygame.draw.line(surf, (30, 30, 30), (x1, y1), (x2, y2), 7)
                pygame.draw.line(surf, (70, 70, 70), (x1, y1), (x2, y2), 2)

        pygame.draw.circle(surf, (25, 25, 25), (cx, cy), 44)
        pygame.draw.circle(surf, (245, 245, 250), (cx - 18, cy - 8), 11)
        pygame.draw.circle(surf, (245, 245, 250), (cx + 18, cy - 8), 11)
        pygame.draw.circle(surf, RED if self.rage else BLACK, (cx - 18, cy - 8), 5)
        pygame.draw.circle(surf, RED if self.rage else BLACK, (cx + 18, cy - 8), 5)

        bw = 420
        bx = WIDTH // 2 - bw // 2
        by = 18
        pygame.draw.rect(surf, (20, 20, 20), (bx, by, bw, 18), border_radius=8)
        pygame.draw.rect(surf, (190, 52, 76), (bx, by, int(bw * max(0, self.hp) / self.max_hp), 18), border_radius=8)
        pygame.draw.rect(surf, (240, 220, 220), (bx, by, bw, 18), 2, border_radius=8)
        draw_text(surf, "SPIDER BOSS", font_tiny, WHITE, WIDTH // 2, by + 9)

        if self.rage:
            draw_text(surf, "[RAGE]", font_tiny, ORANGE, WIDTH // 2 + 150, by + 9)

        for w in self.webs:
            w.draw(surf)


# ============================================================
# BOSS 1 - CLOWN
# ============================================================
# ============================================================
# SPIKES
# ============================================================

class Spike:
    SPEED = 5
    LIFE = 2.5

    def __init__(self, x, y, dx, dy):
        self.x = float(x)
        self.y = float(y)

        self.dx = dx * self.SPEED
        self.dy = dy * self.SPEED

        self.life = self.LIFE

        self.rect = pygame.Rect(
            int(self.x) - 5,
            int(self.y) - 5,
            10,
            10
        )

    def update(self, dt):
        self.x += self.dx
        self.y += self.dy

        self.life -= dt

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    def draw(self, surf):

        col = (
            255,
            min(255, 80 + int(175 * (1 - self.life / self.LIFE))),
            0
        )

        cx, cy = int(self.x), int(self.y)

        pts = [
            (cx, cy - 8),
            (cx + 3, cy - 2),
            (cx + 8, cy),
            (cx + 3, cy + 2),
            (cx, cy + 8),
            (cx - 3, cy + 2),
            (cx - 8, cy),
            (cx - 3, cy - 2)
        ]

        pygame.draw.polygon(surf, col, pts)


def spawn_spikes(x, y, spikes_list):

    dirs = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (-1, 1),
        (1, -1),
        (-1, -1)
    ]

    for dx, dy in dirs:
        spikes_list.append(
            Spike(x, y, dx, dy)
        )
        
class VerticalBalloon:
    def __init__(self):
        self.x = random.randint(60, WIDTH - 60)
        self.y = float(HEIGHT + 40)
        self.speed = random.uniform(2.0, 3.5)
        self.radius = 22
        self.color = random.choice([RED, PINK, CYAN, YELLOW, PURPLE, ORANGE])
        self.popped = False
        self.rect = pygame.Rect(self.x - self.radius, int(self.y) - self.radius, self.radius * 2, self.radius * 2)

    def update(self, dt):
        self.y -= self.speed
        self.rect.center = (self.x, int(self.y))

    def draw(self, surf):
        if self.popped:
            return
        pygame.draw.circle(surf, self.color, (self.x, int(self.y)), self.radius)
        pygame.draw.circle(surf, WHITE, (self.x, int(self.y)), self.radius, 2)
        pygame.draw.circle(surf, WHITE, (self.x - 6, int(self.y) - 6), 5)
        pygame.draw.line(surf, GRAY, (self.x, int(self.y) + self.radius), (self.x, int(self.y) + self.radius + 14), 2)


class TrackerBalloon:
    SPEED = 3.0

    def __init__(self, sx, sy, tx, ty):
        self.x, self.y = float(sx), float(sy)
        dx, dy = normalize(tx - sx, ty - sy)
        self.vx = dx * self.SPEED
        self.vy = dy * self.SPEED
        self.radius = 16
        self.color = (255, 80, 80)
        self.popped = False
        self.rect = pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius, self.radius * 2, self.radius * 2)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surf):
        if self.popped:
            return
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        ex, ey = int(self.x), int(self.y)
        pygame.draw.circle(surf, BLACK, (ex - 4, ey - 3), 3)
        pygame.draw.circle(surf, BLACK, (ex + 4, ey - 3), 3)
        pygame.draw.arc(surf, BLACK, (ex - 5, ey + 1, 10, 6), math.pi, 0, 2)


class BossBall:
    SPEED = 5.0
    RADIUS = 14

    def __init__(self, sx, sy, tx, ty):
        self.x, self.y = float(sx), float(sy)
        dx, dy = normalize(tx - sx, ty - sy)
        self.vx = dx * self.SPEED
        self.vy = dy * self.SPEED
        self.color = random.choice([ORANGE, RED, PURPLE, CYAN])
        self.t = 0.0
        self.rect = pygame.Rect(int(self.x) - self.RADIUS, int(self.y) - self.RADIUS, self.RADIUS * 2, self.RADIUS * 2)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.t += dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        pulse = int(3 * math.sin(self.t * 8))
        pygame.draw.circle(surf, self.color, (cx, cy), self.RADIUS + pulse)
        pygame.draw.circle(surf, WHITE, (cx, cy), self.RADIUS + pulse, 2)
        pygame.draw.circle(surf, WHITE, (cx - 4, cy - 4), 4)


class ClownBoss:
    W, H = 90, 120
    MAX_HP = 3500

    def __init__(self):
        self.hp = self.MAX_HP
        self.phase = 1
        self.rect = pygame.Rect(WIDTH // 2 - self.W // 2, GROUND_Y - self.H, self.W, self.H)
        self.facing = -1
        self.t = 0.0
        self.p1_survive_time = 30.0
        self.p1_timer = 0.0
        self.vert_balloon_cd = 0.0
        self.track_balloon_cd = 0.0
        self.vel_x = 3.0
        self.ball_cd = 0.0
        self.balls = []
        self.hit_flash = 0.0
        self.rage = False

    def take_damage(self, dmg):
        self.hp -= dmg
        self.hit_flash = 0.12
        self.rage = self.hp <= self.MAX_HP * 0.35
        return self.hp <= 0

    def update_phase1(self, dt, player, vert_balloons, track_balloons):
        self.phase = 1
        self.t += dt
        self.hit_flash = max(0, self.hit_flash - dt)
        self.p1_timer += dt
        self.rect.centerx = WIDTH // 2 + int(26 * math.sin(self.t * 1.6))
        self.rect.bottom = GROUND_Y

        self.vert_balloon_cd -= dt
        if self.vert_balloon_cd <= 0:
            vert_balloons.append(VerticalBalloon())
            self.vert_balloon_cd = random.uniform(1.0, 2.2)

        self.track_balloon_cd -= dt
        if self.track_balloon_cd <= 0:
            track_balloons.append(TrackerBalloon(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))
            self.track_balloon_cd = random.uniform(2.8, 5.0)

    def update_phase2(self, dt, player):
        self.phase = 2
        self.t += dt
        self.hit_flash = max(0, self.hit_flash - dt)
        self.rage = self.hp <= self.MAX_HP * 0.35
        speed_mul = 1.0 if not self.rage else 1.35
        self.rect.x += int(self.vel_x * speed_mul)
        if self.rect.right >= WIDTH - 30:
            self.rect.right = WIDTH - 30
            self.vel_x *= -1
        elif self.rect.left <= 30:
            self.rect.left = 30
            self.vel_x *= -1
        self.rect.bottom = GROUND_Y

        self.ball_cd -= dt
        if self.ball_cd <= 0:
            self.balls.append(BossBall(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))
            if self.rage:
                self.balls.append(BossBall(self.rect.centerx, self.rect.centery, player.rect.centerx + 40, player.rect.centery))
                self.balls.append(BossBall(self.rect.centerx, self.rect.centery, player.rect.centerx - 40, player.rect.centery))
            self.ball_cd = random.uniform(0.95, 1.6) if self.rage else random.uniform(1.3, 2.5)

        for b in self.balls[:]:
            b.update(dt)
            if b.rect.right < -50 or b.rect.left > WIDTH + 50 or b.rect.bottom < -50 or b.rect.top > HEIGHT + 50:
                self.balls.remove(b)

    def draw(self, surf):
        flash = self.hit_flash > 0
        cx = self.rect.centerx
        head_y = self.rect.top - 38 + 10 + int(math.sin(self.t * 2) * 4)
        body_col = (255, 80, 200) if not flash else WHITE
        pygame.draw.ellipse(surf, body_col, self.rect.inflate(-10, 0))
        for i in range(3):
            sy = self.rect.top + 30 + i * 25
            col = YELLOW if i % 2 == 0 else ORANGE
            pygame.draw.rect(surf, col, (self.rect.left, sy, self.W, 15))
        pygame.draw.circle(surf, (255, 220, 180), (cx, head_y), 38)
        pygame.draw.ellipse(surf, WHITE, (cx - 20, head_y - 10, 40, 24))
        for ex in [cx - 12, cx + 12]:
            pygame.draw.circle(surf, BLACK, (ex, head_y - 4), 7)
            pygame.draw.circle(surf, WHITE, (ex, head_y - 6), 3)
        mouth_col = RED if not flash else DARK_RED
        if self.phase == 2:
            pygame.draw.arc(surf, mouth_col, (cx - 18, head_y + 8, 36, 20), math.pi, 2 * math.pi, 4)
        else:
            pygame.draw.arc(surf, mouth_col, (cx - 18, head_y + 4, 36, 20), 0, math.pi, 4)
        nose_bob = int(math.sin(self.t * 3) * 2)
        pygame.draw.circle(surf, RED, (cx, head_y + nose_bob + 2), 8)
        hat_pts = [(cx - 28, head_y - 38 + 4), (cx + 28, head_y - 38 + 4), (cx, head_y - 38 - 50)]
        pygame.draw.polygon(surf, PURPLE, hat_pts)
        pygame.draw.circle(surf, YELLOW, (cx, head_y - 38 - 50), 8)
        arm_angle = math.sin(self.t * 2) * 0.4
        for side in [-1, 1]:
            ax = cx + side * (self.W // 2)
            ay = self.rect.top + 40
            ex2 = ax + side * int(40 * math.cos(arm_angle))
            ey2 = ay + int(40 * math.sin(arm_angle + 0.5))
            pygame.draw.line(surf, (255, 180, 80), (ax, ay), (ex2, ey2), 8)
            pygame.draw.circle(surf, WHITE, (ex2, ey2), 10)
        if self.phase == 2:
            bar_w = 240
            bar_x = cx - bar_w // 2
            bar_y = self.rect.top - 24
            pygame.draw.rect(surf, DARK_RED, (bar_x, bar_y, bar_w, 10), border_radius=5)
            hp_ratio = max(0, self.hp / self.MAX_HP)
            pygame.draw.rect(surf, RED, (bar_x, bar_y, int(bar_w * hp_ratio), 10), border_radius=5)
            pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, 10), 2, border_radius=5)


# ============================================================
# BOSS 2 - FRANKENSTEIN
# ============================================================
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = float(x), float(y)
        a = random.uniform(0, 2 * math.pi)
        sp = random.uniform(2, 7)
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp
        self.life = random.uniform(0.4, 1.0)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(3, 8)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= dt

    def draw(self, surf):
        ratio = self.life / self.max_life
        c = tuple(int(v * ratio) for v in self.color)
        r = max(1, int(self.size * ratio))
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), r)


def draw_detailed_pillar(surf, center_x, base_y, height=235, pulse=0, active=True):
    x = center_x - 42
    w = 84
    y = base_y - height
    shadow = pygame.Surface((w + 60, 34), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 6, w + 50, 18))
    surf.blit(shadow, (x - 30, base_y - 8))
    pygame.draw.rect(surf, (55, 40, 25), pygame.Rect(x - 8, base_y - 18, w + 16, 22), border_radius=6)
    pygame.draw.rect(surf, (95, 75, 45), pygame.Rect(x - 2, base_y - 24, w + 4, 10), border_radius=4)
    pygame.draw.rect(surf, (70, 52, 34), pygame.Rect(x, y, w, height), border_radius=8)
    pygame.draw.rect(surf, (100, 82, 52), pygame.Rect(x + 8, y + 6, 10, height - 12), border_radius=4)
    pygame.draw.rect(surf, (90, 70, 42), pygame.Rect(x - 8, y - 14, w + 16, 16), border_radius=5)
    pygame.draw.rect(surf, (120, 100, 62), pygame.Rect(x - 3, y - 20, w + 6, 10), border_radius=4)
    coil_cx = x + w // 2
    for i in range(6):
        yy = y + 24 + i * 28
        pygame.draw.arc(surf, (180, 220, 255) if active else (90, 120, 140), pygame.Rect(coil_cx - 20, yy - 8, 40, 18), 0, math.radians(360), 2)
    if active:
        glow = 50 + int(35 * abs(math.sin((pulse + center_x) * 0.15)))
        pygame.draw.circle(surf, (180, 240, 255), (coil_cx, y + 8), 10)
        pygame.draw.circle(surf, (80, glow, 255), (coil_cx, y + 8), 16, 2)
        for _ in range(3):
            ex = coil_cx + random.randint(-28, 28)
            ey = y + random.randint(6, height - 20)
            pygame.draw.line(surf, (150, 220, 255), (coil_cx, y + 8), (ex, ey), 1)


def draw_lab_bg(surf, tick, rage=False):
    top = (12, 14, 24) if not rage else (22, 10, 12)
    surf.fill(top)
    for y in range(0, HEIGHT, 28):
        alpha = 18 + (y % 56) // 2
        band = pygame.Surface((WIDTH, 28), pygame.SRCALPHA)
        band.fill((20, 40, 60, alpha))
        surf.blit(band, (0, y))
    for i in range(7):
        wx = 60 + i * 180
        window = pygame.Rect(wx, 58, 110, 150)
        pygame.draw.rect(surf, (16, 16, 36), window, border_radius=6)
        pygame.draw.rect(surf, (48, 38, 88), window, 2, border_radius=6)
        for j in range(4):
            pygame.draw.line(surf, (26, 22, 52), (wx + 10, 92 + j * 32), (wx + 100, 92 + j * 32), 1)
        pygame.draw.line(surf, (26, 22, 52), (wx + 37, 64), (wx + 37, 206), 1)
        pygame.draw.line(surf, (26, 22, 52), (wx + 74, 64), (wx + 74, 206), 1)
        if (tick // 22 + i) % 6 == 0:
            for _ in range(2):
                lx = wx + random.randint(12, 95)
                pygame.draw.line(surf, BOLT_C, (lx, 64), (lx + random.randint(-20, 20), 208), 2)
    ground = pygame.Rect(0, HEIGHT - 80, WIDTH, 80)
    pygame.draw.rect(surf, (30, 22, 12), ground)
    pygame.draw.line(surf, (70, 48, 22), (0, HEIGHT - 80), (WIDTH, HEIGHT - 80), 3)
    if rage:
        red_glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        red_glow.fill((120, 0, 0, 24))
        surf.blit(red_glow, (0, 0))


def draw_monster_bg(surf, tick, rage=False):
    pulse = abs(math.sin(tick * 0.04)) * 16
    base = (10 + int(pulse), 38 + int(pulse), 10 + int(pulse))
    if rage:
        base = (26 + int(pulse), 18 + int(pulse * 0.2), 10 + int(pulse * 0.1))
    surf.fill(base)
    cx = WIDTH // 2
    head_col = (40, 110, 40) if not rage else (86, 58, 28)
    outline = (28, 70, 28) if not rage else (120, 40, 18)
    pygame.draw.ellipse(surf, head_col, pygame.Rect(cx - 420, -190, 840, 600))
    pygame.draw.ellipse(surf, outline, pygame.Rect(cx - 420, -190, 840, 600), 5)
    for ex in [cx - 145, cx + 145]:
        ey = 140
        glow = int(180 + 60 * abs(math.sin(tick * 0.05)))
        pygame.draw.circle(surf, (glow, glow, 0), (ex, ey), 58)
        pygame.draw.circle(surf, (255, 220, 0), (ex, ey), 40)
        pygame.draw.circle(surf, BLACK, (ex, ey), 22)
        pygame.draw.circle(surf, (255, 255, 200), (ex - 10, ey - 10), 7)
    pygame.draw.polygon(surf, (25, 75, 25), [(cx, 230), (cx - 30, 288), (cx + 30, 288)])
    pygame.draw.ellipse(surf, (10, 10, 10), pygame.Rect(cx - 120, 286, 240, 80))
    for i in range(6):
        tx = cx - 110 + i * 38
        pygame.draw.rect(surf, WHITE, pygame.Rect(tx, 288, 28, 34), border_radius=3)
    for px in [140, WIDTH - 140]:
        draw_detailed_pillar(surf, px, HEIGHT - 80, 220, pulse=tick, active=True)
    pygame.draw.rect(surf, (18, 36, 18), pygame.Rect(0, HEIGHT - 80, WIDTH, 80))
    pygame.draw.line(surf, (48, 82, 48), (0, HEIGHT - 80), (WIDTH, HEIGHT - 80), 3)


class TeleportParticle:
    def __init__(self, x, y):
        a = random.uniform(0, math.pi * 2)
        sp = random.uniform(1.5, 5)
        self.fx, self.fy = float(x), float(y)
        self.vx, self.vy = math.cos(a) * sp, math.sin(a) * sp
        self.life = random.randint(15, 35)
        self.max_life = self.life
        self.color = random.choice([BOLT_C, CYAN, PURPLE, WHITE])
        self.r = random.randint(3, 7)

    def update(self):
        self.fx += self.vx
        self.fy += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        ratio = self.life / self.max_life
        r = max(1, int(self.r * ratio))
        pygame.draw.circle(surf, self.color, (int(self.fx), int(self.fy)), r)


class DrBullet:
    def __init__(self, x, y, vx, vy, damage=10):
        self.fx, self.fy = float(x), float(y)
        self.rect = pygame.Rect(x - 7, y - 7, 14, 14)
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.trail = []

    def update(self):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 10:
            self.trail.pop(0)
        self.fx += self.vx
        self.fy += self.vy
        self.rect.centerx = int(self.fx)
        self.rect.centery = int(self.fy)

    def draw(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(180 * i / len(self.trail))
            r = max(2, 5 * i // len(self.trail))
            ts = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (120, 220, 255, alpha), (r + 1, r + 1), r)
            surf.blit(ts, (tx - r - 1, ty - r - 1))
        pygame.draw.circle(surf, ORANGE, self.rect.center, 7)
        pygame.draw.circle(surf, YELLOW, self.rect.center, 3)


class DrFrankenstein:
    W, H = 60, 100
    MAX_HP = 500
    TELEPORT_INTERVAL = 170
    RAGE_TELEPORT_INTERVAL = 120
    SHOOT_INTERVAL = 54
    RAGE_SHOOT_INTERVAL = 34
    BURST_INTERVAL = 110
    RAGE_THRESHOLD = 220

    def __init__(self):
        self.pillar_idx = 1
        self.rect = self._pillar_rect(1)
        self.hp = self.MAX_HP
        self.teleport_cd = self.TELEPORT_INTERVAL
        self.shoot_cd = self.SHOOT_INTERVAL
        self.burst_cd = self.BURST_INTERVAL
        self.bullets = []
        self.particles = []
        self.teleport_flash = 0
        self.visible = True
        self.rage = False
        self.bg_anim = 0

    def _pillar_rect(self, idx):
        x = TESLA_XS[idx] - self.W // 2
        y = HEIGHT - 80 - self.H - 210
        return pygame.Rect(x, y, self.W, self.H)

    def _spawn_particles(self, rect, count=40):
        cx, cy = rect.centerx, rect.centery
        for _ in range(count):
            self.particles.append(TeleportParticle(cx + random.randint(-self.W // 2, self.W // 2), cy + random.randint(-self.H // 2, self.H // 2)))

    def _shoot_one(self, player, speed=None, damage=None, spread=0.0):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        ang = math.atan2(dy, dx) + spread
        spd = speed if speed is not None else (7 if self.rage else 5.5)
        dmg = damage if damage is not None else (13 if self.rage else 10)
        self.bullets.append(DrBullet(self.rect.centerx, self.rect.centery, math.cos(ang) * spd, math.sin(ang) * spd, damage=dmg))

    def _shoot_burst(self, player):
        for spread in (-0.22, 0, 0.22):
            self._shoot_one(player, speed=6.7 if self.rage else 6.0, damage=12 if self.rage else 9, spread=spread)

    def update(self, player):
        self.bg_anim += 1
        self.rage = self.hp <= self.RAGE_THRESHOLD
        t_int = self.RAGE_TELEPORT_INTERVAL if self.rage else self.TELEPORT_INTERVAL
        s_int = self.RAGE_SHOOT_INTERVAL if self.rage else self.SHOOT_INTERVAL
        b_int = max(42, self.BURST_INTERVAL - 25) if self.rage else self.BURST_INTERVAL

        self.teleport_cd -= 1
        if self.teleport_cd <= 0:
            self._spawn_particles(self.rect, count=60 if self.rage else 50)
            choices = [i for i in range(3) if i != self.pillar_idx]
            self.pillar_idx = random.choice(choices)
            self.rect = self._pillar_rect(self.pillar_idx)
            self.teleport_cd = t_int
            self.teleport_flash = 25
            self.shoot_cd = 18 if self.rage else 25
            self.burst_cd = b_int
            self._spawn_particles(self.rect, count=60 if self.rage else 50)
            add_screen_shake(5 if self.rage else 3, 4 if self.rage else 2)

        if self.teleport_flash > 0:
            self.teleport_flash -= 1
            self.visible = (self.teleport_flash // 4) % 2 == 0
        else:
            self.visible = True

        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            self.shoot_cd = s_int
            self._shoot_one(player)

        if self.rage:
            self.burst_cd -= 1
            if self.burst_cd <= 0:
                self._shoot_burst(player)
                self.burst_cd = b_int

        for b in self.bullets[:]:
            b.update()
            if not screen.get_rect().colliderect(b.rect):
                self.bullets.remove(b)
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def take_damage(self, dmg):
        self.hp -= dmg

    def draw(self, surf):
        for px in TESLA_XS:
            draw_detailed_pillar(surf, px, HEIGHT - 80, 235, pulse=self.bg_anim, active=True)
        for p in self.particles:
            p.draw(surf)
        if not self.visible:
            r = self.rect
            ghost = pygame.Surface((r.w, r.h + 40), pygame.SRCALPHA)
            ghost.fill((130, 30, 200, 60))
            surf.blit(ghost, (r.x, r.y - 40))
            return
        r = self.rect
        if self.teleport_flash == 0:
            glow_s = pygame.Surface((r.w + 20, r.h + 60), pygame.SRCALPHA)
            glow_s.fill((130, 30, 200, 40))
            surf.blit(glow_s, (r.x - 10, r.y - 40))
        pygame.draw.rect(surf, WHITE, r, border_radius=6)
        head = pygame.Rect(r.x + 8, r.y - 40, r.w - 16, 40)
        pygame.draw.rect(surf, (210, 180, 160), head, border_radius=5)
        pygame.draw.rect(surf, (20, 20, 20), pygame.Rect(head.x - 2, head.y - 6, head.w + 4, 16), border_radius=4)
        pygame.draw.circle(surf, (40, 30, 20), (head.centerx - 8, head.centery - 4), 4)
        pygame.draw.circle(surf, (40, 30, 20), (head.centerx + 8, head.centery - 4), 4)
        pygame.draw.line(surf, (40, 30, 20), (head.centerx - 4, head.centery), (head.centerx + 4, head.centery), 2)
        coat = pygame.Rect(r.x - 2, r.y + 20, r.w + 4, r.h - 10)
        pygame.draw.rect(surf, (240, 240, 250), coat, border_radius=5)
        pygame.draw.rect(surf, (50, 50, 60), pygame.Rect(r.x + 10, r.y + 38, r.w - 20, r.h - 28), border_radius=4)
        pygame.draw.rect(surf, (110, 80, 150), pygame.Rect(r.x + 22, r.y + 24, 16, 48), border_radius=4)
        pygame.draw.line(surf, (50, 50, 60), (r.centerx, r.y + 24), (r.centerx, r.bottom - 12), 2)
        if self.rage:
            rg = pygame.Surface((r.w + 40, r.h + 80), pygame.SRCALPHA)
            rg.fill((255, 40, 20, 36))
            surf.blit(rg, (r.x - 20, r.y - 50))
        self._draw_hp(surf)

    def _draw_hp(self, surf):
        bar_w = 320
        bar_x = WIDTH // 2 - bar_w // 2
        bar_y = 12
        pygame.draw.rect(surf, GRAY, (bar_x, bar_y, bar_w, 22), border_radius=5)
        ratio = max(0, self.hp) / self.MAX_HP
        col = PURPLE if not self.rage else (255, 90, 50)
        pygame.draw.rect(surf, col, (bar_x, bar_y, int(bar_w * ratio), 22), border_radius=5)
        txt = f"Dr. Frankenstein  {self.hp}/{self.MAX_HP}"
        if self.rage:
            txt += "  [RAGE]"
        draw_text(surf, txt, font_sm, WHITE, WIDTH // 2, bar_y + 11)


HAND_Y_REST = HEIGHT - 80 - 140
HAND_Y_SMASH = HEIGHT - 80 - 30


class StompAttack:
    def __init__(self, x, rage=False):
        self.x = x
        self.rage = rage
        self.state = "warn"
        self.timer = 34 if not rage else 24
        self.strike_frames = 18 if not rage else 24
        self.recover_frames = 16
        self.radius = 0
        self.max_radius = 620 if not rage else 760
        self.hit_done = False
        self.done = False

    def update(self):
        self.timer -= 1
        if self.state == "warn":
            self.radius = 80
            if self.timer <= 0:
                self.state = "strike"
                self.timer = self.strike_frames
                add_screen_shake(10 if self.rage else 7, 7 if self.rage else 5)
        elif self.state == "strike":
            self.radius = min(self.max_radius, self.radius + (70 if self.rage else 52))
            if self.timer <= 0:
                self.state = "recover"
                self.timer = self.recover_frames
        elif self.state == "recover":
            if self.timer <= 0:
                self.done = True

    def can_hit_player(self, player):
        if self.state != "strike" or self.hit_done:
            return False
        return player.rect.bottom >= HEIGHT - 155 and abs(player.rect.centerx - self.x) <= self.radius

    def mark_hit(self):
        self.hit_done = True

    def draw(self, surf):
        ground_y = HEIGHT - 80
        if self.state == "warn":
            glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            glow.fill((255, 120, 20, 28))
            surf.blit(glow, (0, 0))
            pygame.draw.circle(surf, (255, 180, 60), (self.x, ground_y + 8), 30)
            pygame.draw.circle(surf, (255, 255, 180), (self.x, ground_y + 8), 14)
            if (self.timer // 6) % 2 == 0:
                draw_text(surf, "PISAO!", font_lg, ORANGE, self.x, ground_y - 70)
        elif self.state in ("strike", "recover"):
            alpha = 200 if self.state == "strike" else 90
            ring = pygame.Surface((self.radius * 2 + 12, 120), pygame.SRCALPHA)
            rect = pygame.Rect(6, 34, self.radius * 2, 38)
            pygame.draw.ellipse(ring, (255, 200, 80, alpha), rect, 6)
            surf.blit(ring, (self.x - self.radius - 6, ground_y - 26))
            if self.state == "strike":
                pygame.draw.line(surf, (255, 170, 50), (self.x - self.radius, ground_y - 6), (self.x + self.radius, ground_y - 6), 4)


class MonsterHand:
    W, H = 110, 90

    def __init__(self, side):
        self.side = side
        self.x = 120 if side == "left" else WIDTH - 120 - self.W
        self.y = float(HAND_Y_REST)
        self.state = "rest"
        self.timer = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def start_attack(self, player_x):
        if self.state == "rest":
            self.state = "windup"
            self.timer = 45
            self.x = max(0, min(WIDTH - self.W, player_x - self.W // 2))

    def update(self, rage=False):
        if self.state == "windup":
            self.y = lerp(self.y, HAND_Y_REST - (180 if rage else 165), 0.18 if not rage else 0.22)
            self.timer -= 1
            if self.timer <= 0:
                self.state = "smash"
        elif self.state == "smash":
            self.y = lerp(self.y, HAND_Y_SMASH, 0.40 if not rage else 0.48)
            if self.y >= HAND_Y_SMASH - 4:
                self.state = "recover"
                self.timer = 35 if not rage else 28
        elif self.state == "recover":
            self.y = lerp(self.y, HAND_Y_REST, 0.12 if not rage else 0.16)
            self.timer -= 1
            if self.timer <= 0:
                self.state = "rest"

    def is_smashing(self):
        return self.state == "smash" and self.y >= HAND_Y_SMASH - 10

    def draw(self, surf):
        r = self.rect
        color = (30, 110, 30)
        if self.state == "windup":
            glow = pygame.Surface((r.w + 60, r.h + 60), pygame.SRCALPHA)
            glow.fill((255, 120, 20, 44))
            surf.blit(glow, (r.x - 30, r.y - 30))
        pygame.draw.rect(surf, color, r, border_radius=10)
        finger_w = (r.w - 10) // 4
        for i in range(4):
            fx = r.x + 5 + i * (finger_w + 2)
            fh = [28, 32, 30, 26][i]
            pygame.draw.rect(surf, color, pygame.Rect(fx, r.y - fh, finger_w, fh), border_radius=6)
        pygame.draw.rect(surf, (10, 60, 10), r, 3, border_radius=10)


class LightningSafeZone:
    def __init__(self, rage=False):
        self.rage = rage
        self.SAFE_W = 95 if rage else 120
        self.WARN_FRAMES = 60 if rage else 75
        self.STRIKE_FRAMES = 92 if rage else 80
        self.FADE_FRAMES = 18
        self.reset()

    def reset(self):
        self.safe_x = random.randint(60, WIDTH - self.SAFE_W - 60)
        self.state = "warn"
        self.timer = self.WARN_FRAMES
        self.bolts = []
        self.done = False
        self._bolt_cd = 0

    @property
    def safe_rect(self):
        return pygame.Rect(self.safe_x, 0, self.SAFE_W, HEIGHT)

    def update(self):
        self.timer -= 1
        if self.state == "warn":
            if self.timer <= 0:
                self.state = "strike"
                self.timer = self.STRIKE_FRAMES
                self._spawn_bolts()
        elif self.state == "strike":
            self._bolt_cd -= 1
            if self._bolt_cd <= 0:
                self._spawn_bolts()
                self._bolt_cd = 5 if self.rage else 7
            if self.timer <= 0:
                self.state = "fade"
                self.timer = self.FADE_FRAMES
        elif self.state == "fade":
            if self.timer <= 0:
                self.done = True
        for b in self.bolts[:]:
            b["life"] -= 1
            if b["life"] <= 0:
                self.bolts.remove(b)

    def _spawn_bolts(self):
        if self.safe_x > 40:
            for _ in range(random.randint(4 if self.rage else 3, 6 if self.rage else 5)):
                self.bolts.append(self._make_bolt(random.randint(10, self.safe_x - 10)))
        right_start = self.safe_x + self.SAFE_W
        if right_start < WIDTH - 40:
            for _ in range(random.randint(4 if self.rage else 3, 6 if self.rage else 5)):
                self.bolts.append(self._make_bolt(random.randint(right_start + 10, WIDTH - 10)))

    def _make_bolt(self, x):
        segs = []
        cy, cx = 0, x
        while cy < HEIGHT:
            ny = cy + random.randint(18, 45)
            nx = cx + random.randint(-22, 22)
            segs.append(((cx, cy), (nx, ny)))
            cx, cy = nx, ny
        return {"segs": segs, "life": random.randint(8, 18)}

    def player_in_danger(self, player_rect):
        return self.state == "strike" and not self.safe_rect.colliderect(player_rect)

    def draw(self, surf):
        if self.state == "warn":
            progress = 1 - self.timer / self.WARN_FRAMES
            alpha = int(80 + 80 * abs(math.sin(progress * math.pi * 6)))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 50, 0, alpha))
            surf.blit(overlay, (0, 0))
            sz = pygame.Surface((self.SAFE_W, HEIGHT), pygame.SRCALPHA)
            sz.fill((0, 220, 80, 60))
            surf.blit(sz, (self.safe_x, 0))
            pygame.draw.rect(surf, (0, 255, 100), pygame.Rect(self.safe_x, 0, self.SAFE_W, HEIGHT), 3)
            if (self.timer // 10) % 2 == 0:
                draw_text(surf, "LIGHTNING WARNING", font_lg, YELLOW, WIDTH // 2, HEIGHT // 2 - 60)
        elif self.state == "strike":
            left_w = self.safe_x
            right_x = self.safe_x + self.SAFE_W
            right_w = WIDTH - right_x
            if left_w > 0:
                ds = pygame.Surface((left_w, HEIGHT), pygame.SRCALPHA)
                ds.fill((255, 200, 0, 120))
                surf.blit(ds, (0, 0))
            if right_w > 0:
                ds = pygame.Surface((right_w, HEIGHT), pygame.SRCALPHA)
                ds.fill((255, 200, 0, 120))
                surf.blit(ds, (right_x, 0))
            sz = pygame.Surface((self.SAFE_W, HEIGHT), pygame.SRCALPHA)
            sz.fill((0, 220, 80, 35))
            surf.blit(sz, (self.safe_x, 0))
            pygame.draw.rect(surf, (0, 255, 100), pygame.Rect(self.safe_x, 0, self.SAFE_W, HEIGHT), 3)
            for b in self.bolts:
                for (ax, ay), (bx2, by) in b["segs"]:
                    pygame.draw.line(surf, BOLT_C, (ax, ay), (bx2, by), 3)
                    pygame.draw.line(surf, WHITE, (ax, ay), (bx2, by), 1)
        elif self.state == "fade":
            for b in self.bolts:
                for (ax, ay), (bx2, by) in b["segs"]:
                    pygame.draw.line(surf, BOLT_C, (ax, ay), (bx2, by), 2)


class MonsterPhase:
    MAX_HP = 850
    SMASH_DURATION = 300
    PAUSE_DURATION = 35
    HAND_ATTACK_INTERVAL = 42
    RAGE_THRESHOLD = 320
    STOMP_INTERVAL = 230

    def __init__(self):
        self.hp = self.MAX_HP
        self.hands = [MonsterHand("left"), MonsterHand("right")]
        self.bg_anim = 0
        self.state = "smash"
        self.state_cd = self.SMASH_DURATION
        self.attack_cd = self.HAND_ATTACK_INTERVAL
        self.next_hand = 0
        self.safe_zone = None
        self.stomp = None
        self.stomp_cd = self.STOMP_INTERVAL
        self.rage = False

    def take_damage(self, dmg):
        self.hp -= dmg

    def update(self, player):
        self.bg_anim += 1
        self.rage = self.hp <= self.RAGE_THRESHOLD
        self.state_cd -= 1

        if self.stomp:
            self.stomp.update()
            if self.stomp.done:
                self.stomp = None
                self.stomp_cd = 165 if self.rage else self.STOMP_INTERVAL

        if self.state_cd <= 0 and self.stomp is None:
            if self.state == "smash":
                self.state = "pause_after_smash"
                self.state_cd = self.PAUSE_DURATION
            elif self.state == "pause_after_smash":
                self.state = "lightning"
                self.state_cd = 9999
                self.safe_zone = LightningSafeZone(rage=self.rage)
            elif self.state == "lightning":
                self.state = "pause_after_lightning"
                self.state_cd = self.PAUSE_DURATION
                self.safe_zone = None
            elif self.state == "pause_after_lightning":
                self.state = "smash"
                self.state_cd = self.SMASH_DURATION

        if self.state == "smash":
            hand_interval = 28 if self.rage else self.HAND_ATTACK_INTERVAL
            self.attack_cd -= 1
            if self.attack_cd <= 0:
                self.hands[self.next_hand].start_attack(player.rect.centerx)
                self.next_hand = 1 - self.next_hand
                self.attack_cd = hand_interval
            self.stomp_cd -= 1
            if self.stomp_cd <= 0 and self.stomp is None:
                self.stomp = StompAttack(player.rect.centerx, rage=self.rage)
                self.stomp_cd = 9999
                add_screen_shake(10 if self.rage else 8, 6 if self.rage else 4)
        elif self.state == "lightning" and self.safe_zone:
            self.safe_zone.update()
            if self.safe_zone.done:
                self.state_cd = 0

        for hand in self.hands:
            hand.update(rage=self.rage)

    def check_hits(self, player):
        for hand in self.hands:
            if hand.is_smashing() and player.rect.colliderect(hand.rect):
                player.take_damage(28 if not self.rage else 32)
        if self.safe_zone and self.safe_zone.player_in_danger(player.rect):
            player.take_damage(16 if not self.rage else 20)
        if self.stomp and self.stomp.can_hit_player(player):
            player.take_damage(24 if not self.rage else 30)
            self.stomp.mark_hit()

    def draw_bg(self, surf, tick):
        draw_monster_bg(surf, tick, rage=self.rage)

    def draw(self, surf):
        if self.safe_zone:
            self.safe_zone.draw(surf)
        if self.stomp:
            self.stomp.draw(surf)
        for hand in self.hands:
            hand.draw(surf)
        self._draw_hp(surf)

    def _draw_hp(self, surf):
        bar_w = 380
        bar_x = WIDTH // 2 - bar_w // 2
        bar_y = 12
        pygame.draw.rect(surf, GRAY, (bar_x, bar_y, bar_w, 22), border_radius=5)
        ratio = max(0, self.hp) / self.MAX_HP
        col = GREEN if not self.rage else (255, 90, 50)
        pygame.draw.rect(surf, col, (bar_x, bar_y, int(bar_w * ratio), 22), border_radius=5)
        txt = f"MONSTER  {self.hp}/{self.MAX_HP}"
        if self.rage:
            txt += "  [RAGE]"
        draw_text(surf, txt, font_sm, WHITE, WIDTH // 2, bar_y + 11)


# ============================================================
# BOSS RUNS
# ============================================================

def run_boss0_spider(character, carried_player=None):
    player = Player(character)
    if carried_player is not None:
        player.hp = min(player.MAX_HP, carried_player.hp + 40)

    spider = SpiderBoss()
    particles = []
    bg_tick = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        bg_tick += 1

        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        player.update_frank(events, ground_y=GROUND_Y, platforms=[])
        spider.update(dt, player)

        for b in player.bullets[:]:
            if b.can_damage and b.rect.colliderect(spider.rect):
                spider.take_damage(b.damage * 5)
                add_screen_shake(2, 1)
                for _ in range(8):
                    particles.append(Particle(b.rect.centerx, b.rect.centery, YELLOW))

                if b.kind == "boomerang":
                    b.can_damage = False
                    b.returning = True
                    b.return_started = True
                    b.vx = -b.vx
                    b.vy = -b.vy * 0.9
                else:
                    if b in player.bullets:
                        player.bullets.remove(b)

        for w in spider.webs[:]:
            if w.rect.colliderect(player.rect):
                player.take_damage(w.damage)
                add_screen_shake(2, 1)
                for _ in range(6):
                    particles.append(Particle(w.rect.centerx, w.rect.centery, CYAN))
                if w in spider.webs:
                    spider.webs.remove(w)

        if spider.hp <= 0:
            return True, player
        if player.hp <= 0 or player.dead:
            return False, player

        for p in particles[:]:
            p.update(dt)
            if p.life <= 0:
                particles.remove(p)

        spider.draw_bg(screen)
        spider.draw(screen)
        player.draw(screen)
        for p in particles:
            p.draw(screen)

        draw_common_hud(screen, player, "BOSS 0 - SPIDER", spider.hp, spider.max_hp, "Forest of webs")

        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(screen, CYAN, (mx, my), 10, 2)
        pygame.draw.line(screen, CYAN, (mx - 14, my), (mx + 14, my), 1)
        pygame.draw.line(screen, CYAN, (mx, my - 14), (mx, my + 14), 1)

        dx, dy = get_screen_shake_offset()
        if dx or dy:
            sh = pygame.Surface((WIDTH, HEIGHT))
            sh.fill(BLACK)
            sh.blit(screen, (dx, dy))
            screen.blit(sh, (0, 0))

        pygame.display.flip()


def run_boss1_clown(character, carried_player=None):
    player = Player(character)
    if carried_player is not None:
        player.hp = min(player.MAX_HP, carried_player.hp + 50)
    boss = ClownBoss()
    particles = []
    spikes = []
    vert_balloons = []
    track_balloons = []
    clown_phase = 1
    survive_time = boss.p1_survive_time
    tick = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        tick += 1
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        plats = CLOWN_PLATFORMS if clown_phase == 2 else []
        player.update_frank(events, ground_y=GROUND_Y, platforms=plats)

        if clown_phase == 1:
            boss.update_phase1(dt, player, vert_balloons, track_balloons)
            for vb in vert_balloons[:]:
                vb.update(dt)
                for b in player.bullets[:]:
                    if vb.rect.colliderect(b.rect) and not vb.popped:
                        vb.popped = True
                        spawn_spikes(vb.x, vb.y, spikes)
                        for _ in range(10):
                            particles.append(Particle(vb.x, vb.y, vb.color))
                        if b in player.bullets:
                            player.bullets.remove(b)
                        break
                if not vb.popped and vb.y < -40:
                    vb.popped = True
                    spawn_spikes(vb.x, max(0, vb.y), spikes)
                if vb.popped or vb.y < -80:
                    if vb in vert_balloons:
                        vert_balloons.remove(vb)

            for tb in track_balloons[:]:
                tb.update(dt)
                if not tb.popped and tb.rect.colliderect(player.rect):
                    tb.popped = True
                    player.take_damage(10)
                    add_screen_shake(3, 2)
                    for _ in range(8):
                        particles.append(Particle(tb.x, tb.y, RED))
                if tb.popped or tb.rect.x < -80 or tb.rect.x > WIDTH + 80 or tb.rect.y > HEIGHT + 80:
                    if tb in track_balloons:
                        track_balloons.remove(tb)

            for sp in spikes[:]:
                sp.update(dt)
                if sp.rect.colliderect(player.rect):
                    player.take_damage(6)
                    add_screen_shake(2, 1)
                    if sp in spikes:
                        spikes.remove(sp)
                    continue
                if sp.life <= 0 and sp in spikes:
                    spikes.remove(sp)

            if boss.p1_timer >= survive_time:
                clown_phase = 2
                boss.phase = 2
                boss.rect.x = 50
                player.bullets.clear()
                vert_balloons.clear(); track_balloons.clear(); spikes.clear()

        else:
            boss.update_phase2(dt, player)
            for ball in boss.balls[:]:
                if ball.rect.colliderect(player.rect):
                    player.take_damage(14 if not boss.rage else 18)
                    add_screen_shake(4 if not boss.rage else 6, 3 if not boss.rage else 5)
                    for _ in range(8):
                        particles.append(Particle(ball.x, ball.y, ball.color))
                    if ball in boss.balls:
                        boss.balls.remove(ball)
            if boss.rect.colliderect(player.rect):
                player.take_damage(8)

            for b in player.bullets[:]:
                if b.can_damage and b.rect.colliderect(boss.rect):
                    boss.take_damage(b.damage * 5)
                    add_screen_shake(2, 1)
                    for _ in range(6):
                        particles.append(Particle(b.rect.centerx, b.rect.centery, YELLOW))
                    if b.kind == "boomerang":
                        b.can_damage = False
                        b.returning = True
                        b.return_started = True
                        b.vx = -b.vx
                        b.vy = -b.vy * 0.9
                    else:
                        if b in player.bullets:
                            player.bullets.remove(b)

            if boss.hp <= 0:
                return True, player

        if player.hp <= 0 or player.dead:
            return False, player

        for p in particles[:]:
            p.update(dt)
            if p.life <= 0:
                particles.remove(p)

        draw_gradient_rect(screen, (18, 6, 34), (8, 5, 18), (0, 0, WIDTH, HEIGHT))
        for i in range(80):
            x = (i * 167 + tick * 2) % WIDTH
            y = (i * 41) % (HEIGHT // 2)
            pygame.draw.circle(screen, (220, 220, 220), (int(x), y), 1)
        pygame.draw.rect(screen, (55, 28, 10), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.line(screen, GOLD, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        for i in range(0, WIDTH, 60):
            col = (80, 40, 10) if (i // 60) % 2 == 0 else (50, 20, 5)
            pygame.draw.rect(screen, col, (i, GROUND_Y, 60, HEIGHT - GROUND_Y))
        if clown_phase == 2:
            for plat in CLOWN_PLATFORMS:
                pygame.draw.rect(screen, (120, 60, 20), plat, border_radius=4)
                pygame.draw.rect(screen, GOLD, plat, 2, border_radius=4)

        for vb in vert_balloons: vb.draw(screen)
        for tb in track_balloons: tb.draw(screen)
        for sp in spikes: sp.draw(screen)
        for ball in boss.balls: ball.draw(screen)
        boss.draw(screen)
        player.draw(screen)
        for p in particles: p.draw(screen)

        if clown_phase == 1:
            sub = f"Survive time: {max(0, survive_time - boss.p1_timer):.1f}s"
        else:
            sub = f"Clown HP: {boss.hp}/{boss.MAX_HP}"
        draw_common_hud(screen, player, "BOSS 1 - CLOWN", None, None, sub)

        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(screen, YELLOW, (mx, my), 10, 2)
        pygame.draw.line(screen, YELLOW, (mx - 14, my), (mx + 14, my), 1)
        pygame.draw.line(screen, YELLOW, (mx, my - 14), (mx, my + 14), 1)

        dx, dy = get_screen_shake_offset()
        if dx or dy:
            sh = pygame.Surface((WIDTH, HEIGHT))
            sh.fill(BLACK)
            sh.blit(screen, (dx, dy))
            screen.blit(sh, (0, 0))
        pygame.display.flip()


def run_boss2_frankenstein(character, carried_player=None):
    player = Player(character)
    player.rect.centerx = WIDTH // 2
    player.rect.bottom = HEIGHT - 80
    if carried_player is not None:
        player.hp = min(player.MAX_HP, carried_player.hp + 50)
    doctor = DrFrankenstein()
    monster = MonsterPhase()
    phase = 1
    tick = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        tick += 1
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        if player.hp <= 0 or player.dead:
            return False, player

        player.update_frank(events, ground_y=HEIGHT - 80)

        if phase == 1:
            doctor.update(player)
            for b in player.bullets[:]:
                if b.can_damage and b.rect.colliderect(doctor.rect) and doctor.visible:
                    doctor.take_damage(b.damage)
                    add_screen_shake(2, 1)
                    if b.kind == "boomerang":
                        b.can_damage = False
                        b.returning = True
                        b.return_started = True
                        b.vx = -b.vx
                        b.vy = -b.vy * 0.9
                    else:
                        if b in player.bullets:
                            player.bullets.remove(b)
            for b in doctor.bullets[:]:
                if b.rect.colliderect(player.rect):
                    player.take_damage(b.damage)
                    add_screen_shake(2, 1)
                    if b in doctor.bullets:
                        doctor.bullets.remove(b)
            if doctor.hp <= 0:
                phase = 2
                player.hp = min(player.MAX_HP, player.hp + 50)
                player.bullets.clear()
                doctor.bullets.clear()
        else:
            monster.update(player)
            monster.check_hits(player)
            for b in player.bullets[:]:
                for hand in monster.hands:
                    if b.can_damage and b.rect.colliderect(hand.rect):
                        monster.take_damage(b.damage)
                        add_screen_shake(2, 1)
                        if b.kind == "boomerang":
                            b.can_damage = False
                            b.returning = True
                            b.return_started = True
                            b.vx = -b.vx
                            b.vy = -b.vy * 0.9
                        else:
                            if b in player.bullets:
                                player.bullets.remove(b)
                        break
            if monster.hp <= 0:
                return True, player

        canvas = pygame.Surface((WIDTH, HEIGHT))
        if phase == 1:
            draw_lab_bg(canvas, tick, rage=doctor.rage)
            doctor.draw(canvas)
            for b in doctor.bullets:
                b.draw(canvas)
            boss_title = "BOSS 2 - DR. FRANKENSTEIN"
            sub = f"Doctor HP: {doctor.hp}/{doctor.MAX_HP}"
        else:
            monster.draw_bg(canvas, tick)
            monster.draw(canvas)
            boss_title = "BOSS 2 - THE MONSTER"
            sub = f"Monster HP: {monster.hp}/{monster.MAX_HP}"
        for b in player.bullets:
            b.draw(canvas)
        player.draw(canvas)
        draw_common_hud(canvas, player, boss_title, None, None, sub)
        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(canvas, CYAN, (mx, my), 10, 2)
        pygame.draw.line(canvas, CYAN, (mx - 14, my), (mx + 14, my), 1)
        pygame.draw.line(canvas, CYAN, (mx, my - 14), (mx, my + 14), 1)
        dx, dy = get_screen_shake_offset()
        screen.fill(BLACK)
        screen.blit(canvas, (dx, dy))
        pygame.display.flip()
# ============================================================
# FINAL BOSS - LORD OF NIGHTMARES
# ============================================================

class NightmareProjectile:

    def __init__(self, x, y, vx, vy, color, damage=18):

        self.x = float(x)
        self.y = float(y)

        self.vx = vx
        self.vy = vy

        self.damage = damage
        self.life = 260

        self.color = color

        self.rect = pygame.Rect(
            int(x)-12,
            int(y)-12,
            24,
            24
        )

    def update(self):

        self.x += self.vx
        self.y += self.vy

        self.life -= 1

        self.rect.center = (
            int(self.x),
            int(self.y)
        )

    def draw(self, surf):

        pygame.draw.circle(
            surf,
            self.color,
            self.rect.center,
            12
        )

        pygame.draw.circle(
            surf,
            WHITE,
            self.rect.center,
            12,
            2
        )


# ============================================================
# FINAL BOSS - LORD OF NIGHTMARES
# ============================================================

class NightmareProjectile:
    def __init__(self, x, y, vx, vy, color, damage=18, kind="bolt"):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.damage = damage
        self.kind = kind
        self.life = 240
        self.age = 0
        self.spin = random.uniform(0, math.pi * 2)
        self.trail = []

        if kind == "wave":
            self.rect = pygame.Rect(int(x) - 150, int(y) - 18, 300, 36)
        elif kind == "rain":
            self.rect = pygame.Rect(int(x) - 8, int(y) - 8, 16, 22)
        else:
            self.rect = pygame.Rect(int(x) - 12, int(y) - 12, 24, 24)

    def update(self):
        self.age += 1
        self.life -= 1

        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 8:
            self.trail.pop(0)

        if self.kind == "rain":
            self.vy += 0.18

        self.x += self.vx
        self.y += self.vy

        if self.kind == "wave":
            self.rect.x = int(self.x) - 150
            self.rect.y = int(self.y) - 18
        else:
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surf):
        if self.kind == "wave":
            glow = pygame.Surface((320, 70), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (*self.color, 70), (10, 12, 300, 34))
            pygame.draw.ellipse(glow, (255, 255, 255, 120), (30, 20, 260, 18), 2)
            surf.blit(glow, (self.rect.centerx - 160, self.rect.centery - 35))
            pygame.draw.ellipse(surf, self.color, self.rect, 0)
            pygame.draw.ellipse(surf, WHITE, self.rect, 2)
            return

        if self.kind == "rain":
            drop = pygame.Surface((24, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(drop, (*self.color, 220), (6, 3, 12, 18))
            pygame.draw.polygon(drop, (*self.color, 220), [(12, 0), (20, 12), (12, 26), (4, 12)])
            pygame.draw.circle(drop, WHITE, (12, 8), 2)
            surf.blit(drop, (self.rect.centerx - 12, self.rect.centery - 15))
            return

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(180 * i / max(1, len(self.trail)))
            r = max(1, 4 * i // max(1, len(self.trail)))
            trail_s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(trail_s, (*self.color, alpha), (r + 2, r + 2), max(1, r))
            surf.blit(trail_s, (tx - r - 2, ty - r - 2))

        pygame.draw.circle(surf, self.color, self.rect.center, 10)
        pygame.draw.circle(surf, WHITE, self.rect.center, 10, 2)
        pygame.draw.circle(surf, WHITE, (self.rect.centerx - 3, self.rect.centery - 3), 2)


class LordOfNightmares:
    MAX_HP = 1800

    def __init__(self):
        self.hp = self.MAX_HP
        self.phase = 1
        self.rage = False
        self.phase_flash = 0

        self.t = 0
        self.x = WIDTH // 2
        self.y = 170
        self.scale = 1.0
        self.scale_target = 1.0
        self.anchor_y = 170

        self.attack_cd = 0
        self.special_cd = 0
        self.projectiles = []

        self.rect = pygame.Rect(0, 0, 180, 260)
        self._sync_rect()

    def _sync_rect(self):
        w = int(210 * self.scale)
        h = int(280 * self.scale)
        self.rect = pygame.Rect(int(self.x - w // 2), int(self.y - h // 2), w, h)

    def _shoot_bolt(self, player, spread=0.0, speed=8.0, color=PURPLE, damage=16):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        ang = math.atan2(dy, dx) + spread
        vx = math.cos(ang) * speed
        vy = math.sin(ang) * speed
        self.projectiles.append(
            NightmareProjectile(self.rect.centerx, self.rect.centery, vx, vy, color, damage, "bolt")
        )

    def _shoot_ring(self, count, speed, color, damage=14):
        for i in range(count):
            ang = (math.tau / count) * i + self.t * 0.015
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed
            self.projectiles.append(
                NightmareProjectile(self.rect.centerx, self.rect.centery, vx, vy, color, damage, "bolt")
            )

    def _spawn_rain(self, player, count=4):
        for _ in range(count):
            rx = clamp(player.rect.centerx + random.randint(-260, 260), 40, WIDTH - 40)
            vy = random.uniform(5.5, 7.5)
            vx = random.uniform(-0.3, 0.3)
            self.projectiles.append(
                NightmareProjectile(rx, -30, vx, vy, CYAN, 15 if not self.rage else 20, "rain")
            )

    def _spawn_wave(self, player, direction=1):
        y = clamp(player.rect.centery + random.randint(-80, 60), 120, HEIGHT - 150)
        x = -120 if direction > 0 else WIDTH + 120
        vx = 11 if direction > 0 else -11
        self.projectiles.append(
            NightmareProjectile(x, y, vx, 0, ORANGE, 22 if not self.rage else 28, "wave")
        )

    def _update_phase(self):
        ratio = self.hp / self.MAX_HP
        old_phase = self.phase

        if ratio > 0.66:
            self.phase = 1
            self.scale_target = 1.00
            self.anchor_y = 170
        elif ratio > 0.33:
            self.phase = 2
            self.scale_target = 1.35
            self.anchor_y = 255
        else:
            self.phase = 3
            self.scale_target = 1.85
            self.anchor_y = 335

        self.rage = ratio <= 0.22

        if self.phase != old_phase:
            self.phase_flash = 24
            self.projectiles.clear()
            self.attack_cd = 18
            self.special_cd = 36
            add_screen_shake(10 if self.phase == 3 else 6, 5 if self.phase == 3 else 3)

    def update(self, player):
        self.t += 1
        self._update_phase()

        move_amp = 230 if self.phase == 1 else 320 if self.phase == 2 else 380
        move_speed = 0.020 if self.phase == 1 else 0.028 if self.phase == 2 else 0.036
        y_amp = 18 if self.phase == 1 else 28 if self.phase == 2 else 14

        target_x = WIDTH // 2 + math.sin(self.t * move_speed) * move_amp
        target_y = self.anchor_y + math.sin(self.t * (move_speed * 1.7)) * y_amp

        if self.phase == 3:
            target_y += math.sin(self.t * 0.11) * 10

        self.x = lerp(self.x, target_x, 0.05 if self.phase < 3 else 0.07)
        self.y = lerp(self.y, target_y, 0.04 if self.phase < 3 else 0.06)
        self.scale = lerp(self.scale, self.scale_target, 0.05)

        self._sync_rect()

        self.attack_cd -= 1
        self.special_cd -= 1

        if self.phase == 1:
            if self.attack_cd <= 0:
                self.attack_cd = 42 if not self.rage else 28
                self._shoot_bolt(player, 0.0, 8.0 if not self.rage else 10.0, PURPLE, 16 if not self.rage else 20)
                self._shoot_bolt(player, -0.12, 8.0 if not self.rage else 10.0, PURPLE, 16 if not self.rage else 20)
                self._shoot_bolt(player, 0.12, 8.0 if not self.rage else 10.0, PURPLE, 16 if not self.rage else 20)

            if self.special_cd <= 0:
                self.special_cd = 110 if not self.rage else 75
                self._spawn_rain(player, 3 if not self.rage else 5)

        elif self.phase == 2:
            if self.attack_cd <= 0:
                self.attack_cd = 30 if not self.rage else 22
                self._shoot_ring(8, 6.8 if not self.rage else 8.2, RED, 16 if not self.rage else 20)
                self._shoot_bolt(player, 0.0, 9.0 if not self.rage else 11.0, RED, 18 if not self.rage else 22)

            if self.special_cd <= 0:
                self.special_cd = 85 if not self.rage else 60
                self._spawn_wave(player, 1 if (self.t // 60) % 2 == 0 else -1)
                if self.rage:
                    self._spawn_wave(player, -1 if (self.t // 60) % 2 == 0 else 1)

        else:
            if self.attack_cd <= 0:
                self.attack_cd = 20 if not self.rage else 14
                self._shoot_ring(12, 7.5 if not self.rage else 9.2, ORANGE, 20 if not self.rage else 24)

            if self.special_cd <= 0:
                self.special_cd = 55 if not self.rage else 38
                self._spawn_wave(player, 1)
                self._spawn_wave(player, -1)
                self._spawn_rain(player, 5 if not self.rage else 8)

        for p in self.projectiles[:]:
            p.update()
            if (
                p.life <= 0
                or p.rect.right < -80
                or p.rect.left > WIDTH + 80
                or p.rect.bottom < -80
                or p.rect.top > HEIGHT + 80
            ):
                self.projectiles.remove(p)

    def draw_bg(self, surf):
        if self.phase == 1:
            surf.fill((8, 0, 18))
            for i in range(90):
                x = (i * 153 + self.t * 2) % WIDTH
                y = (i * 67) % (HEIGHT // 2)
                pygame.draw.circle(surf, (70, 20, 110), (int(x), y), 1)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((40, 0, 70, 22))
            surf.blit(overlay, (0, 0))

        elif self.phase == 2:
            surf.fill((14, 0, 8))
            for x in range(0, WIDTH, 90):
                pygame.draw.rect(surf, (50, 0, 30), (x, 0, 42, HEIGHT), 0)
                pygame.draw.rect(surf, (90, 0, 50), (x + 42, 0, 20, HEIGHT), 0)
            for i in range(100):
                px = (i * 137) % WIDTH
                py = (i * 53) % (HEIGHT // 2)
                pygame.draw.circle(surf, (130, 30, 30), (px, py), 1)
            fog = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fog.fill((120, 0, 0, 18 if not self.rage else 30))
            surf.blit(fog, (0, 0))

        else:
            surf.fill((3, 0, 10))
            for i in range(160):
                px = (i * 79 + self.t * 3) % WIDTH
                py = (i * 41 + (i % 7) * 23) % HEIGHT
                c = 40 + (i % 5) * 12
                pygame.draw.circle(surf, (c, 0, c + 20), (int(px), int(py)), 1)
            for _ in range(10):
                rx = random.randint(0, WIDTH)
                ry = random.randint(0, HEIGHT)
                pygame.draw.circle(surf, (120, 0, 160), (rx, ry), random.randint(20, 45), 1)

    def draw(self, surf):
        self.draw_bg(surf)

        if self.phase_flash > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 120, 35))
            surf.blit(flash, (0, 0))
            self.phase_flash -= 1

        w = int(220 * self.scale)
        h = int(320 * self.scale)
        body = pygame.Rect(0, 0, w, h)
        body.center = (int(self.x), int(self.y))

        aura = pygame.Surface((w + 180, h + 220), pygame.SRCALPHA)
        aura_col = (130, 0, 190, 70) if self.phase < 3 else (255, 40, 20, 80)
        pygame.draw.ellipse(aura, aura_col, (30, 40, aura.get_width() - 60, aura.get_height() - 80))
        surf.blit(aura, (body.centerx - aura.get_width() // 2, body.centery - aura.get_height() // 2))

        cloak_col = (20, 16, 30) if not self.rage else (40, 10, 16)
        cloak_outline = (80, 0, 120) if self.phase < 3 else (255, 40, 60)
        hood_col = (30, 24, 42) if not self.rage else (60, 14, 24)

        pygame.draw.ellipse(surf, cloak_col, body.inflate(0, -20))
        pygame.draw.ellipse(surf, cloak_outline, body.inflate(0, -20), 4)

        hood = pygame.Rect(
            body.centerx - int(72 * self.scale),
            body.top + int(12 * self.scale),
            int(144 * self.scale),
            int(122 * self.scale)
        )
        pygame.draw.ellipse(surf, hood_col, hood)
        pygame.draw.ellipse(surf, cloak_outline, hood, 3)

        eye_y = hood.centery
        eye_dx = int(20 * self.scale)
        pygame.draw.circle(surf, RED if self.rage else PURPLE, (hood.centerx - eye_dx, eye_y), max(3, int(7 * self.scale)))
        pygame.draw.circle(surf, RED if self.rage else PURPLE, (hood.centerx + eye_dx, eye_y), max(3, int(7 * self.scale)))
        pygame.draw.circle(surf, WHITE, (hood.centerx - eye_dx - 2, eye_y - 2), max(1, int(2 * self.scale)))
        pygame.draw.circle(surf, WHITE, (hood.centerx + eye_dx - 2, eye_y - 2), max(1, int(2 * self.scale)))

        arm_w = max(6, int(14 * self.scale))
        for side in (-1, 1):
            ax = body.centerx + side * int(65 * self.scale)
            ay = body.top + int(120 * self.scale)
            bx = ax + side * int(95 * self.scale)
            by = ay + int(45 * math.sin(self.t * 0.05 + side))
            pygame.draw.line(surf, (50, 40, 70), (ax, ay), (bx, by), arm_w)
            pygame.draw.line(surf, cloak_outline, (ax, ay), (bx, by), max(2, arm_w // 3))

        if self.phase >= 2:
            sigil_r = int(70 * self.scale)
            pygame.draw.circle(surf, (100, 0, 140), (body.centerx, body.bottom - int(40 * self.scale)), sigil_r, 3)
            pygame.draw.circle(surf, (255, 0, 120), (body.centerx, body.bottom - int(40 * self.scale)), sigil_r - 18, 1)

        if self.phase == 3:
            for side in (-1, 1):
                horn = [
                    (hood.centerx + side * int(24 * self.scale), hood.top + int(12 * self.scale)),
                    (hood.centerx + side * int(70 * self.scale), hood.top - int(34 * self.scale)),
                    (hood.centerx + side * int(48 * self.scale), hood.top + int(18 * self.scale)),
                ]
                pygame.draw.polygon(surf, (140, 0, 180), horn)
                pygame.draw.polygon(surf, (255, 70, 80), horn, 2)

        for p in self.projectiles:
            p.draw(surf)

        bw = 520
        bx = WIDTH // 2 - bw // 2
        pygame.draw.rect(surf, GRAY, (bx, 20, bw, 22), border_radius=8)
        ratio = max(0, self.hp) / self.MAX_HP
        hp_col = PURPLE if self.phase < 3 else (255, 80, 40)
        pygame.draw.rect(surf, hp_col, (bx, 20, int(bw * ratio), 22), border_radius=8)
        pygame.draw.rect(surf, WHITE, (bx, 20, bw, 22), 2, border_radius=8)

        title = "LORD OF NIGHTMARES"
        draw_text(surf, title, font_sm, WHITE, WIDTH // 2, 31)
        phase_name = "Forma Sombria" if self.phase == 1 else "Palco do Caos" if self.phase == 2 else "Forma Verdadeira"
        draw_text(surf, f"Fase {self.phase} - {phase_name}", font_tiny, CYAN if self.phase < 3 else ORANGE, WIDTH // 2, 58)

def run_boss3_final(character, carried_player=None):

    player = Player(character)

    if carried_player is not None:
        player.hp = min(player.MAX_HP, carried_player.hp + 70)

    player.rect.centerx = WIDTH // 2
    player.rect.bottom = GROUND_Y

    boss = LordOfNightmares()

    particles = []

    while True:

        dt = clock.tick(FPS) / 1000.0

        events = pygame.event.get()

        for ev in events:

            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        player.update_frank(events, ground_y=GROUND_Y)

        boss.update(player)

        # =========================
        # COLISÕES PLAYER -> BOSS
        # =========================

        for b in player.bullets[:]:

            if b.can_damage and b.rect.colliderect(boss.rect):

                damage = b.damage * 4

                if boss.phase == 3:
                    damage = int(damage * 0.8)

                boss.hp -= damage

                add_screen_shake(3, 2)

                if b.kind == "boomerang":

                    b.can_damage = False
                    b.returning = True
                    b.return_started = True

                    b.vx = -b.vx
                    b.vy = -b.vy * 0.9

                else:

                    if b in player.bullets:
                        player.bullets.remove(b)

        # =========================
        # COLISÕES BOSS -> PLAYER
        # =========================

        for p in boss.projectiles[:]:

            if p.rect.colliderect(player.rect):

                player.take_damage(p.damage)

                add_screen_shake(4, 3)

                if p in boss.projectiles:
                    boss.projectiles.remove(p)

        # =========================
        # MORTE
        # =========================

        if player.dead or player.hp <= 0:
            return False, player

        if boss.hp <= 0:
            return True, player

        # =========================
        # DRAW
        # =========================

        boss.draw(screen)

        player.draw(screen)

        draw_common_hud(
            screen,
            player,
            "BOSS FINAL - LORD OF NIGHTMARES",
            boss.hp,
            boss.MAX_HP,
            f"FASE {boss.phase}"
        )

        # mira
        mx, my = pygame.mouse.get_pos()

        pygame.draw.circle(screen, RED, (mx, my), 10, 2)

        pygame.draw.line(screen, RED, (mx - 14, my), (mx + 14, my), 1)

        pygame.draw.line(screen, RED, (mx, my - 14), (mx, my + 14), 1)

        dx, dy = get_screen_shake_offset()

        if dx or dy:

            shake = pygame.Surface((WIDTH, HEIGHT))

            shake.blit(screen, (dx, dy))

            screen.blit(shake, (0, 0))

        pygame.display.flip()
# ============================================================
# FLOW
# ============================================================

def run_game():
    # menu
    button = MenuButton()
    menu_t = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        menu_t += dt
        events = pygame.event.get()

        clicked_start = False

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if button.clicked(ev):
                clicked_start = True

        render_menu(button, menu_t)
        pygame.display.flip()

        if clicked_start:
            break

    # character select
    character = character_select()

    # intro story
    run_story(INTRO_STORY, "HISTÓRIA INICIAL")

    # boss 0 spider
    win, player = run_boss0_spider(character)
    if not win:
        if final_screen("FIM DE JOGO", "A aranha venceu"):
            return run_game()
        return

    run_story(STORY_AFTER_SPIDER, "DEPOIS DA ARANHA")

    # boss 1 clown
    win, player = run_boss1_clown(character, carried_player=player)
    if not win:
        if final_screen("FIM DE JOGO", "O palhaço venceu"):
            return run_game()
        return

    run_story(STORY_AFTER_CLOWN, "DEPOIS DO PALHAÇO")

    # boss 2 frankenstein
    win, player = run_boss2_frankenstein(character, carried_player=player)
    if not win:
        if final_screen("FIM DE JOGO", "Frankenstein venceu"):
            return run_game()
        return

    run_story(STORY_AFTER_FRANK, "DEPOIS DE FRANKENSTEIN")

    # final boss
    run_story(FINAL_BOSS_STORY, "BOSS FINAL")

    win, player = run_boss3_final(character, carried_player=player)
    if not win:
        if final_screen("FIM DE JOGO", "O Senhor dos Pesadelos venceu"):
            return run_game()
        return

    if final_screen("VITÓRIA", "Todos os bosses foram derrotados"):
        return run_game()

    


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    run_game()