"""
========================================================
  PYGAME - TELA INICIAL COMPLETA  (Halloween Adventures)
  Editável, com imagens, som, transição e historinha
========================================================
  Personalize tudo nas seções marcadas com  EDITAR
========================================================
"""

import pygame
import sys
import os
import math
import random
from dataclasses import dataclass
from pathlib import Path

# Pasta onde este script está — imagens/sons devem ficar aqui também
PASTA = os.path.dirname(os.path.abspath(__file__))

def caminho(arquivo):
    if arquivo is None:
        return None
    return os.path.join(PASTA, arquivo)

# ══════════════════════════════════════════════════════
#   EDITAR — Configurações Gerais
# ══════════════════════════════════════════════════════
TITULO_JANELA        = "Halloween Adventures"
LARGURA              = 900
ALTURA               = 600
FPS                  = 60

# ══════════════════════════════════════════════════════
#   EDITAR — Imagens
#   Todos os arquivos devem estar na MESMA PASTA que main.py
# ══════════════════════════════════════════════════════
IMAGEM_LOGO          = "LOGO.png"       # Logo/título  |  None = usa texto
IMAGEM_BOTAO         = "BOTAO.png"      # Botão start  |  None = usa botão desenhado
IMAGEM_FUNDO         = "castelo.jpg"             # Fundo        |  None = usa gradiente

LOGO_LARGURA         = 460             # Largura da logo em pixels
LOGO_ALTURA          = 460             # Altura  da logo em pixels
BOTAO_LARGURA        = 250             # Largura do botão em pixels
BOTAO_ALTURA         = 115             # Altura  do botão em pixels

# Posição vertical (fração da tela: 0.0 = topo, 1.0 = base)
LOGO_POS_Y           = 0.04            # Logo começa a 4% do topo
BOTAO_POS_Y          = 0.84            # Botão centralizado em 76% da altura

# ══════════════════════════════════════════════════════
#   EDITAR — Textos de fallback (se imagens não existirem)
# ══════════════════════════════════════════════════════
TITULO_FALLBACK      = "HALLOWEEN ADVENTURES"
BOTAO_FALLBACK       = "INICIAR"

# ══════════════════════════════════════════════════════
#   EDITAR — Cores (R, G, B)
# ══════════════════════════════════════════════════════
COR_FUNDO_TOPO       = (5,   0,   15)
COR_FUNDO_BASE       = (20,  5,   40)
COR_TITULO_FALLBACK  = (255, 160, 20)
COR_BOTAO_FALLBACK   = (120, 50,  10)
COR_BOTAO_HOVER_FB   = (200, 90,  20)
COR_BOTAO_TEXT_FB    = (255, 220, 80)
COR_PARTICULA        = (255, 120, 20)
COR_HISTORIA         = (255, 165, 0)

# ══════════════════════════════════════════════════════
#   EDITAR — Sons (.mp3 / .ogg / .wav  na mesma pasta)
# ══════════════════════════════════════════════════════
MUSICA_MENU          = "fundo_inicio.mp3"             # ex: "menu.mp3"
SOM_CLIQUE           = "clique.mp3"           # ex: "click.wav"
MUSICA_HISTORIA      = "historia.mp3"           # ex: "story.mp3"
MUSICA_ARANHA        = "aranha.mp3"
# ══════════════════════════════════════════════════════
#   EDITAR — Historinha  (cada string = 1 slide)
#   Use  \n  para quebrar linha dentro do mesmo slide.
# ══════════════════════════════════════════════════════
HISTORIA = [
    "Na noite mais sombria do ano...\numa criança desapareceu.",
    "A vila de Ravenmoor está em pânico.\nNinguém se atreve a entrar na floresta amaldiçoada.",
    "Mas você não é como os outros.\nVocê conhece os segredos das sombras.",
    "Enfrente bruxas, fantasmas e criaturas das trevas\npara resgatar o que foi perdido.",
    "A noite é longa.\nE o Halloween... mal começou.",
]

TEMPO_SLIDE_HISTORIA = 3.5   # segundos por slide

# ══════════════════════════════════════════════════════
#  Inicialização  — não precisa editar abaixo daqui
# ══════════════════════════════════════════════════════

pygame.init()
pygame.mixer.init()

tela    = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption(TITULO_JANELA)
relogio = pygame.time.Clock()

# ── Fontes ──────────────────────────────────────────
def fonte(tam, bold=False):
    try:
        return pygame.font.SysFont("Arial Black", tam, bold=bold)
    except:
        return pygame.font.Font(None, tam)

f_titulo   = fonte(72, bold=True)
f_sub      = fonte(28)
f_botao    = fonte(30, bold=True)
f_historia = fonte(26)
f_pular    = fonte(18)

# ── Sons ────────────────────────────────────────────
def carregar_som(arq):
    p = caminho(arq)
    if p and os.path.exists(p):
        return pygame.mixer.Sound(p)
    return None

def tocar_musica(arq, loop=-1):
    p = caminho(arq)
    if p and os.path.exists(p):
        pygame.mixer.music.load(p)
        pygame.mixer.music.play(loop)

som_clique = carregar_som(SOM_CLIQUE)

# ── Imagens ─────────────────────────────────────────
def carregar_img(arq, w, h):
    p = caminho(arq)
    if p and os.path.exists(p):
        try:
            img = pygame.image.load(p).convert_alpha()
            img = pygame.transform.smoothscale(img, (w, h))
            print(f"[OK] Imagem carregada: {arq}  ({w}x{h})")
            return img
        except Exception as e:
            print(f"[ERRO] Nao foi possivel carregar {arq}: {e}")
    else:
        print(f"[AVISO] Arquivo nao encontrado: {p}")
    return None

img_logo  = carregar_img(IMAGEM_LOGO,  LOGO_LARGURA,  LOGO_ALTURA)
img_botao = carregar_img(IMAGEM_BOTAO, BOTAO_LARGURA, BOTAO_ALTURA)

# Variante hover do botão (levemente mais clara)
img_botao_hover = None
if img_botao:
    img_botao_hover = img_botao.copy()
    brilho = pygame.Surface((BOTAO_LARGURA, BOTAO_ALTURA), pygame.SRCALPHA)
    brilho.fill((80, 40, 0, 55))
    img_botao_hover.blit(brilho, (0, 0))

# Fundo opcional
img_fundo = None
p_fundo   = caminho(IMAGEM_FUNDO)
if p_fundo and os.path.exists(p_fundo):
    img_fundo = pygame.transform.scale(pygame.image.load(p_fundo), (LARGURA, ALTURA))

# ── Gradiente pré-computado ─────────────────────────
_grad = pygame.Surface((LARGURA, ALTURA))
for _y in range(ALTURA):
    _t = _y / ALTURA
    _c = tuple(int(COR_FUNDO_TOPO[i] + (COR_FUNDO_BASE[i] - COR_FUNDO_TOPO[i]) * _t) for i in range(3))
    pygame.draw.line(_grad, _c, (0, _y), (LARGURA, _y))

def desenhar_fundo():
    tela.blit(img_fundo if img_fundo else _grad, (0, 0))

# ── Partículas ──────────────────────────────────────
class Particula:
    def __init__(self, aleatorio=True):
        self.reset(aleatorio)
    def reset(self, aleatorio=False):
        self.x     = random.uniform(0, LARGURA)
        self.y     = random.uniform(0, ALTURA) if aleatorio else ALTURA + 4
        self.r     = random.uniform(1.0, 3.0)
        self.vel   = random.uniform(0.3, 1.0)
        self.alpha = random.randint(50, 170)
    def update(self):
        self.y -= self.vel
        if self.y < -5:
            self.reset()
    def draw(self, surf):
        s = pygame.Surface((int(self.r*2+2), int(self.r*2+2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*COR_PARTICULA, self.alpha),
                           (int(self.r)+1, int(self.r)+1), int(self.r))
        surf.blit(s, (int(self.x - self.r), int(self.y - self.r)))

particulas = [Particula(aleatorio=True) for _ in range(90)]

# ── Transição fade ──────────────────────────────────
class Transicao:
    def __init__(self, dur=70):
        self.dur   = dur
        self.frame = 0
        self.ativa = False
        self.modo  = "fade_out"
        self.cb    = None
    def iniciar(self, modo="fade_out", cb=None):
        self.modo  = modo
        self.frame = 0
        self.ativa = True
        self.cb    = cb
    def update(self):
        if not self.ativa:
            return
        self.frame += 1
        if self.frame >= self.dur:
            self.ativa = False
            if self.cb:
                self.cb()
    def draw(self, surf):
        if not self.ativa:
            return
        t     = self.frame / self.dur
        alpha = int(255 * t) if self.modo == "fade_out" else int(255 * (1 - t))
        s = pygame.Surface((LARGURA, ALTURA))
        s.fill((0, 0, 0))
        s.set_alpha(alpha)
        surf.blit(s, (0, 0))

fade = Transicao()

# ── Botão ────────────────────────────────────────────
class Botao:
    def __init__(self):
        self.cx    = LARGURA // 2
        self.cy    = int(ALTURA * BOTAO_POS_Y)
        self.w0    = BOTAO_LARGURA
        self.h0    = BOTAO_ALTURA
        self.rect  = pygame.Rect(self.cx - self.w0//2, self.cy - self.h0//2,
                                 self.w0, self.h0)
        self.hover = False
        self.t     = 0.0

    def update(self, mpos):
        self.hover = self.rect.collidepoint(mpos)
        self.t    += 0.07

    def clicado(self, ev):
        return (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1
                and self.rect.collidepoint(ev.pos))

    def draw(self, surf):
        escala = 1.0 + (0.025 * math.sin(self.t) if not self.hover else 0.04)
        w = int(self.w0 * escala)
        h = int(self.h0 * escala)
        rx = self.cx - w // 2
        ry = self.cy - h // 2

        if img_botao:
            img = img_botao_hover if (self.hover and img_botao_hover) else img_botao
            scaled = pygame.transform.smoothscale(img, (w, h))
            sh = pygame.Surface((w, h), pygame.SRCALPHA)
            sh.blit(scaled, (0, 0))
            sh.set_alpha(70)
            surf.blit(sh, (rx + 7, ry + 9))
            surf.blit(scaled, (rx, ry))
        else:
            cor   = COR_BOTAO_HOVER_FB if self.hover else COR_BOTAO_FALLBACK
            borda = (255, 160, 30)     if self.hover else (180, 100, 20)
            pygame.draw.rect(surf, (0,0,0), (rx+4, ry+4, w, h), border_radius=14)
            pygame.draw.rect(surf, cor,     (rx, ry, w, h),     border_radius=14)
            pygame.draw.rect(surf, borda,   (rx, ry, w, h), width=2, border_radius=14)
            txt = f_botao.render(BOTAO_FALLBACK, True, COR_BOTAO_TEXT_FB)
            surf.blit(txt, (rx + (w - txt.get_width())//2,
                            ry + (h - txt.get_height())//2))

botao = Botao()

# ── Estados ─────────────────────────────────────────
ST_MENU     = "menu"
ST_HISTORIA = "historia"
ST_JOGO     = "jogo"
estado      = ST_MENU

slide_i     = 0
slide_t     = 0.0
slide_alpha = 0
slide_fase  = "in"

tocar_musica(MUSICA_MENU)
tempo = 0.0

# ── Placeholder do jogo ──────────────────────────────
def tela_jogo():
    """ EDITAR — substitua pelo loop do seu jogo real! """
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return
        tela.fill((15, 25, 15))
        pygame.display.flip()
        relogio.tick(FPS)
        
        

# ── História ─────────────────────────────────────────
def comecar_historia():
    global estado, slide_i, slide_t, slide_alpha, slide_fase
    estado      = ST_HISTORIA
    slide_i     = 0
    slide_t     = 0.0
    slide_alpha = 0
    slide_fase  = "in"
    pygame.mixer.music.fadeout(400)
    tocar_musica(MUSICA_HISTORIA)

def pular_slide():
    global slide_i, slide_t, slide_alpha, slide_fase, estado
    slide_i += 1
    if slide_i >= len(HISTORIA):
        estado = ST_JOGO
    else:
        slide_t     = 0.0
        slide_alpha = 0
        slide_fase  = "in"

def update_historia(dt):
    global slide_t, slide_alpha, slide_fase, estado, slide_i
    FADE = 0.55
    SHOW = TEMPO_SLIDE_HISTORIA
    slide_t += dt
    if slide_fase == "in":
        slide_alpha = min(255, int(255 * slide_t / FADE))
        if slide_t >= FADE:
            slide_fase = "show"
            slide_t    = 0.0
    elif slide_fase == "show":
        slide_alpha = 255
        if slide_t >= SHOW:
            slide_fase = "out"
            slide_t    = 0.0
    elif slide_fase == "out":
        slide_alpha = max(0, 255 - int(255 * slide_t / FADE))
        if slide_t >= FADE:
            slide_i += 1
            if slide_i >= len(HISTORIA):
                estado = ST_JOGO
            else:
                slide_t    = 0.0
                slide_fase = "in"

def draw_historia():
    desenhar_fundo()
    for p in particulas:
        p.update(); p.draw(tela)

    if estado != ST_HISTORIA:
        return

    linhas  = HISTORIA[slide_i].split("\n")
    lh      = f_historia.get_height() + 8
    total_h = len(linhas) * lh
    y0      = ALTURA // 2 - total_h // 2

    s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    for i, linha in enumerate(linhas):
        txt = f_historia.render(linha, True, COR_HISTORIA)
        s.blit(txt, (LARGURA//2 - txt.get_width()//2, y0 + i * lh))
    s.set_alpha(slide_alpha)
    tela.blit(s, (0, 0))

    n = len(HISTORIA)
    for i in range(n):
        cor = (255, 165, 0) if i == slide_i else (60, 45, 20)
        pygame.draw.circle(tela, cor, (LARGURA//2 - (n-1)*14 + i*28, ALTURA - 38), 6)

    hint = f_pular.render("ESPACO ou ENTER para avancar", True, (130, 100, 60))
    tela.blit(hint, (LARGURA//2 - hint.get_width()//2, ALTURA - 20))

# ══════════════════════════════════════════════════════
#  Loop Principal
# ══════════════════════════════════════════════════════
t_ant = pygame.time.get_ticks()

while True:
    agora = pygame.time.get_ticks()
    dt    = (agora - t_ant) / 1000.0
    t_ant = agora
    tempo += dt
    mouse = pygame.mouse.get_pos()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if estado == ST_MENU:
            if botao.clicado(ev) and not fade.ativa:
                if som_clique:
                    som_clique.play()
                fade.iniciar("fade_out", cb=comecar_historia)

        elif estado == ST_HISTORIA:
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                pular_slide()

    if estado == ST_HISTORIA:
        update_historia(dt)

    # ── Render ──────────────────────────────────────
    if estado == ST_MENU:
        desenhar_fundo()

        for p in particulas:
            p.update(); p.draw(tela)

        # Logo flutuante
        flutuacao = math.sin(tempo * 1.35) * 9
        logo_y    = int(ALTURA * LOGO_POS_Y + flutuacao)

        if img_logo:
            lx = LARGURA//2 - LOGO_LARGURA//2
            sh = pygame.Surface((LOGO_LARGURA, LOGO_ALTURA), pygame.SRCALPHA)
            sh.blit(img_logo, (0, 0))
            sh.set_alpha(65)
            tela.blit(sh,       (lx + 6, logo_y + 10))
            tela.blit(img_logo, (lx,     logo_y))
        else:
            ts = f_titulo.render(TITULO_FALLBACK, True, COR_TITULO_FALLBACK)
            ss = f_titulo.render(TITULO_FALLBACK, True, (0, 0, 0))
            tela.blit(ss, (LARGURA//2 - ss.get_width()//2 + 3, logo_y + 3))
            tela.blit(ts, (LARGURA//2 - ts.get_width()//2,     logo_y))

        botao.update(mouse)
        botao.draw(tela)

        hint = f_pular.render(" ", True, (120, 80, 40))
        tela.blit(hint, (LARGURA//2 - hint.get_width()//2, ALTURA - 26))

        fade.update(); fade.draw(tela)

    elif estado == ST_HISTORIA:
        draw_historia()
        fade.update(); fade.draw(tela)

    elif estado == ST_JOGO:
        pygame.mixer.music.fadeout(500)
        tela_jogo()
        estado = ST_MENU
        tocar_musica(MUSICA_MENU)
        fade.iniciar("fade_in")

    pygame.display.flip()
    relogio.tick(FPS)
    
