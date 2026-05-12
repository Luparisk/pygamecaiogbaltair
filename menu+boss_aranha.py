"""
========================================================
  HALLOWEEN ADVENTURES
  Menu → História → Boss Aranha → Vitória / Game Over
========================================================
"""

import pygame, sys, os, math, random, traceback
from dataclasses import dataclass
from pathlib import Path

# ── Pasta base ────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"

# ══════════════════════════════════════════════════════
#   EDITAR — Janela
# ══════════════════════════════════════════════════════
TITULO_JANELA = "Halloween Adventures"
FPS           = 60
MENU_W, MENU_H = 900, 600
BOSS_W, BOSS_H = 1280, 720

# ══════════════════════════════════════════════════════
#   EDITAR — Imagens do Menu
# ══════════════════════════════════════════════════════
IMAGEM_LOGO  = "LOGO.png"
IMAGEM_BOTAO = "BOTAO.png"
IMAGEM_FUNDO = "castelo.jpg"   # None = gradiente

LOGO_W, LOGO_H   = 460, 460
BOTAO_W, BOTAO_H = 250, 115
LOGO_POS_Y  = 0.04
BOTAO_POS_Y = 0.84

TITULO_FALLBACK = "HALLOWEEN ADVENTURES"
BOTAO_FALLBACK  = "INICIAR"

# ══════════════════════════════════════════════════════
#   EDITAR — Cores
# ══════════════════════════════════════════════════════
COR_FUNDO_TOPO = (5,   0,   15)
COR_FUNDO_BASE = (20,  5,   40)
COR_TITULO_FB  = (255, 160,  20)
COR_BOTAO_FB   = (120,  50,  10)
COR_BOTAO_HV   = (200,  90,  20)
COR_BOTAO_TXT  = (255, 220,  80)
COR_PARTICULA  = (255, 120,  20)
COR_HISTORIA   = (255, 165,   0)

# ══════════════════════════════════════════════════════
#   EDITAR — Sons  (None = silêncio)
# ══════════════════════════════════════════════════════
MUSICA_MENU     = "fundo_inicio.mp3"
SOM_CLIQUE      = "clique.mp3"
MUSICA_HISTORIA = "historia.mp3"
MUSICA_BOSS     = "aranha.mp3"

# ══════════════════════════════════════════════════════
#   EDITAR — Historinha
# ══════════════════════════════════════════════════════
HISTORIA = [
    "Na noite mais sombria do ano...\numa criança desapareceu.",
    "A vila de Ravenmoor está em pânico.\nNinguém se atreve a entrar na floresta amaldiçoada.",
    "Mas você não é como os outros.\nVocê conhece os segredos das sombras.",
    "Enfrente bruxas, fantasmas e criaturas das trevas\npara resgatar o que foi perdido.",
    "A noite é longa.\nE o Halloween... mal começou.",
]
TEMPO_SLIDE = 3.5

# ══════════════════════════════════════════════════════
#   EDITAR — Boss Aranha
# ══════════════════════════════════════════════════════
PLAYER_SIZE          = (96, 96)
PLAYER_SPEED         = 360
PLAYER_MAX_HP        = 8
PLAYER_SHOT_CD       = 0.18
PLAYER_PROJ_SPEED    = 760
PLAYER_PROJ_DMG      = 1

SPIDER_MAX_HP        = 30
SPIDER_RADIUS_X      = 5000
SPIDER_RADIUS_Y      = 500
SPIDER_MOVE_SPD      = 0.75
SPIDER_ATK_CD        = (0.9, 1.6)
SPIDER_BALL_SPD      = 300
SPIDER_BALL_DMG      = 1
CIRCLE_CLOSE_DUR     = 1.6

BG_COLOR       = (19,  16,  31)
ARENA_FLOOR    = (70,  58,  52)
ARENA_WALL     = (39,  33,  45)
UI_TEXT        = (245, 235, 220)
P_BODY         = (92,  196, 255)
P_BODY_DK      = (45,  126, 181)
P_OUTLINE      = (17,   26,  40)
P_PROJ_COLOR   = (255, 232, 110)
SPIDER_WEB_CLR = (222, 222, 235)

# ══════════════════════════════════════════════════════
#  Inicialização
# ══════════════════════════════════════════════════════
pygame.init()
pygame.mixer.init()
tela    = pygame.display.set_mode((MENU_W, MENU_H))
pygame.display.set_caption(TITULO_JANELA)
relogio = pygame.time.Clock()

def fnt(tam, bold=False):
    try:    return pygame.font.SysFont("Arial Black", tam, bold=bold)
    except: return pygame.font.Font(None, tam)

f_titulo   = fnt(72, bold=True)
f_sub      = fnt(28)
f_botao    = fnt(30, bold=True)
f_historia = fnt(26)
f_pular    = fnt(18)

# ── Sons ─────────────────────────────────────────────
def load_sound(nome):
    if not nome: return None
    p = BASE_DIR / nome
    if not p.exists():
        print(f"[SOM] não encontrado: {p}")
        return None
    try:
        s = pygame.mixer.Sound(str(p))
        print(f"[SOM] carregado: {nome}")
        return s
    except Exception as e:
        print(f"[SOM] erro ao carregar {nome}: {e}")
        return None

def play_music(nome):
    if not nome: return
    p = BASE_DIR / nome
    if not p.exists():
        print(f"[MUSICA] não encontrada: {p}")
        return
    try:
        pygame.mixer.music.load(str(p))
        pygame.mixer.music.play(-1)
        print(f"[MUSICA] tocando: {nome}")
    except Exception as e:
        print(f"[MUSICA] erro: {e}")

def stop_music(fade_ms=300):
    try: pygame.mixer.music.fadeout(fade_ms)
    except: pass

som_clique = load_sound(SOM_CLIQUE)

# ── Imagens ───────────────────────────────────────────
def load_img(nome, w, h):
    if not nome: return None
    p = BASE_DIR / nome
    if not p.exists():
        print(f"[IMG] não encontrada: {p}")
        return None
    try:
        img = pygame.image.load(str(p)).convert_alpha()
        img = pygame.transform.smoothscale(img, (w, h))
        print(f"[IMG] carregada: {nome} ({w}x{h})")
        return img
    except Exception as e:
        print(f"[IMG] erro: {nome}: {e}")
        return None

def load_img_path(p, size=None):
    if not p or not Path(p).exists(): return None
    try:
        img = pygame.image.load(str(p)).convert_alpha()
        if size: img = pygame.transform.smoothscale(img, size)
        return img
    except: return None

def load_frames(folder, pattern, scale=None):
    frames, i = [], 1
    while True:
        p = folder / pattern.format(i)
        if not p.exists(): break
        try:
            img = pygame.image.load(str(p)).convert_alpha()
            if scale: img = pygame.transform.smoothscale(img, scale)
            frames.append(img)
        except: pass
        i += 1
    print(f"[FRAMES] {folder.name}: {len(frames)} carregados")
    return frames

img_logo  = load_img(IMAGEM_LOGO,  LOGO_W,  LOGO_H)
img_botao = load_img(IMAGEM_BOTAO, BOTAO_W, BOTAO_H)

img_botao_hv = None
if img_botao:
    img_botao_hv = img_botao.copy()
    brl = pygame.Surface((BOTAO_W, BOTAO_H), pygame.SRCALPHA)
    brl.fill((80, 40, 0, 55))
    img_botao_hv.blit(brl, (0, 0))

img_fundo = load_img(IMAGEM_FUNDO, MENU_W, MENU_H)

_grad = pygame.Surface((MENU_W, MENU_H))
for _y in range(MENU_H):
    _t = _y / MENU_H
    _c = tuple(int(COR_FUNDO_TOPO[i]+(COR_FUNDO_BASE[i]-COR_FUNDO_TOPO[i])*_t) for i in range(3))
    pygame.draw.line(_grad, _c, (0,_y), (MENU_W,_y))

def draw_bg():
    tela.blit(img_fundo if img_fundo else _grad, (0,0))

# ── Partículas ────────────────────────────────────────
class Particula:
    def __init__(self, rand=True):
        self.reset(rand)
    def reset(self, rand=False):
        self.x     = random.uniform(0, MENU_W)
        self.y     = random.uniform(0, MENU_H) if rand else MENU_H+4
        self.r     = random.uniform(1.0, 3.0)
        self.vel   = random.uniform(0.3, 1.0)
        self.alpha = random.randint(50, 170)
    def update(self):
        self.y -= self.vel
        if self.y < -5: self.reset()
    def draw(self, surf):
        s = pygame.Surface((int(self.r*2+2),int(self.r*2+2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*COR_PARTICULA,self.alpha),
                           (int(self.r)+1,int(self.r)+1), int(self.r))
        surf.blit(s, (int(self.x-self.r), int(self.y-self.r)))

particulas = [Particula(rand=True) for _ in range(90)]

# ── Fade ──────────────────────────────────────────────
class Fade:
    def __init__(self):
        self.frame = 0
        self.dur   = 60
        self.ativa = False
        self.modo  = "out"   # "out" escurece, "in" clareia
    def start(self, modo="out", dur=60):
        self.modo  = modo
        self.frame = 0
        self.dur   = dur
        self.ativa = True
    def update(self):
        if self.ativa:
            self.frame += 1
            if self.frame >= self.dur:
                self.ativa = False
    @property
    def done(self):
        return not self.ativa
    def draw(self, surf, w, h):
        if not self.ativa: return
        t     = self.frame / self.dur
        alpha = int(255*t) if self.modo=="out" else int(255*(1-t))
        s = pygame.Surface((w,h)); s.fill((0,0,0)); s.set_alpha(alpha)
        surf.blit(s,(0,0))

fade = Fade()

# ── Botão ─────────────────────────────────────────────
class Botao:
    def __init__(self):
        self.cx   = MENU_W//2
        self.cy   = int(MENU_H*BOTAO_POS_Y)
        self.w0   = BOTAO_W
        self.h0   = BOTAO_H
        self.rect = pygame.Rect(self.cx-self.w0//2, self.cy-self.h0//2, self.w0, self.h0)
        self.hover = False
        self.t     = 0.0
    def update(self, mpos):
        self.hover = self.rect.collidepoint(mpos)
        self.t += 0.07
    def clicado(self, ev):
        return (ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1
                and self.rect.collidepoint(ev.pos))
    def draw(self, surf):
        # Pulso suave quando ocioso; expansão no hover
        if self.hover:
            esc = 1.06 + 0.01*math.sin(self.t*3)
        else:
            esc = 1.0 + 0.03*math.sin(self.t)
        w=int(self.w0*esc); h=int(self.h0*esc)
        rx=self.cx-w//2;    ry=self.cy-h//2

        if img_botao:
            img = img_botao_hv if (self.hover and img_botao_hv) else img_botao
            sc  = pygame.transform.smoothscale(img,(w,h))

            # Sombra
            sh = pygame.Surface((w,h),pygame.SRCALPHA)
            sh.blit(sc,(0,0)); sh.set_alpha(70)
            surf.blit(sh,(rx+8,ry+10))

            # Brilho laranja pulsante ao redor no hover
            if self.hover:
                glow_alpha = int(80 + 60*math.sin(self.t*4))
                glow = pygame.Surface((w+20, h+20), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255,140,0,glow_alpha),
                                 (0,0,w+20,h+20), border_radius=18)
                surf.blit(glow, (rx-10, ry-10))

            surf.blit(sc,(rx,ry))

            # Partículas de estrelinhas no hover
            if self.hover and int(self.t*10)%3==0:
                for _ in range(2):
                    sx = rx + random.randint(0,w)
                    sy = ry + random.randint(0,h)
                    sr = random.randint(2,5)
                    sa = random.randint(120,220)
                    ps = pygame.Surface((sr*2,sr*2),pygame.SRCALPHA)
                    pygame.draw.circle(ps,(255,220,80,sa),(sr,sr),sr)
                    surf.blit(ps,(sx-sr,sy-sr))
        else:
            cor   = COR_BOTAO_HV if self.hover else COR_BOTAO_FB
            borda = (255,160,30) if self.hover else (180,100,20)
            pygame.draw.rect(surf,(0,0,0),(rx+4,ry+4,w,h),border_radius=14)
            pygame.draw.rect(surf,cor,(rx,ry,w,h),border_radius=14)
            pygame.draw.rect(surf,borda,(rx,ry,w,h),width=2,border_radius=14)
            txt=f_botao.render(BOTAO_FALLBACK,True,COR_BOTAO_TXT)
            surf.blit(txt,(rx+(w-txt.get_width())//2,ry+(h-txt.get_height())//2))

botao = Botao()

# ══════════════════════════════════════════════════════
#  Máquina de estados  (string simples, sem constante)
#  "menu" | "fade_menu_historia" | "historia" |
#  "fade_historia_boss" | "boss"
# ══════════════════════════════════════════════════════
estado = "menu"

slide_i=0; slide_t=0.0; slide_alpha=0; slide_fase="in"
tempo = 0.0

play_music(MUSICA_MENU)

# ── Render do menu ────────────────────────────────────
def render_menu():
    draw_bg()
    for p in particulas: p.update(); p.draw(tela)
    flutuacao = math.sin(tempo*1.35)*9
    logo_y    = int(MENU_H*LOGO_POS_Y+flutuacao)
    if img_logo:
        lx = MENU_W//2-LOGO_W//2
        sh = pygame.Surface((LOGO_W,LOGO_H),pygame.SRCALPHA)
        sh.blit(img_logo,(0,0)); sh.set_alpha(65)
        tela.blit(sh,(lx+6,logo_y+10))
        tela.blit(img_logo,(lx,logo_y))
    else:
        ts=f_titulo.render(TITULO_FALLBACK,True,COR_TITULO_FB)
        ss=f_titulo.render(TITULO_FALLBACK,True,(0,0,0))
        tela.blit(ss,(MENU_W//2-ss.get_width()//2+3,logo_y+3))
        tela.blit(ts,(MENU_W//2-ts.get_width()//2,  logo_y))
    botao.update(mouse)   # <- atualiza hover e timer de animação
    botao.draw(tela)

# ── História ──────────────────────────────────────────
def update_historia(dt):
    global slide_t,slide_alpha,slide_fase,estado,slide_i
    FADE=0.55; SHOW=TEMPO_SLIDE
    slide_t+=dt
    if slide_fase=="in":
        slide_alpha=min(255,int(255*slide_t/FADE))
        if slide_t>=FADE: slide_fase="show"; slide_t=0.0
    elif slide_fase=="show":
        slide_alpha=255
        if slide_t>=SHOW: slide_fase="out"; slide_t=0.0
    elif slide_fase=="out":
        slide_alpha=max(0,255-int(255*slide_t/FADE))
        if slide_t>=FADE:
            slide_i+=1
            if slide_i>=len(HISTORIA):
                estado="fade_historia_boss"
                fade.start("out",dur=80)
            else:
                slide_t=0.0; slide_fase="in"

def render_historia():
    draw_bg()
    for p in particulas: p.update(); p.draw(tela)
    if slide_i>=len(HISTORIA): return
    linhas  = HISTORIA[slide_i].split("\n")
    lh      = f_historia.get_height()+8
    total_h = len(linhas)*lh
    y0      = MENU_H//2-total_h//2
    s = pygame.Surface((MENU_W,MENU_H),pygame.SRCALPHA)
    for i,linha in enumerate(linhas):
        txt=f_historia.render(linha,True,COR_HISTORIA)
        s.blit(txt,(MENU_W//2-txt.get_width()//2, y0+i*lh))
    s.set_alpha(slide_alpha)
    tela.blit(s,(0,0))
    n=len(HISTORIA)
    for i in range(n):
        cor=(255,165,0) if i==slide_i else (60,45,20)
        pygame.draw.circle(tela,cor,(MENU_W//2-(n-1)*14+i*28,MENU_H-38),6)
    hint=f_pular.render("ESPACO ou ENTER para avançar",True,(130,100,60))
    tela.blit(hint,(MENU_W//2-hint.get_width()//2,MENU_H-20))

# ══════════════════════════════════════════════════════
#  Boss — helpers de fallback
# ══════════════════════════════════════════════════════
def clamp(v,lo,hi): return max(lo,min(hi,v))

def draw_text_boss(surf,text,size,color,x,y,center=True):
    font=pygame.font.SysFont("arial",size,bold=True)
    img=font.render(text,True,color)
    r=img.get_rect()
    if center: r.center=(x,y)
    else:      r.topleft=(x,y)
    surf.blit(img,r)

def make_player_surf(size):
    surf=pygame.Surface(size,pygame.SRCALPHA)
    w,h=size; cx,cy=w//2,h//2
    pygame.draw.ellipse(surf,P_OUTLINE,(18,20,w-36,h-20))
    pygame.draw.ellipse(surf,P_BODY,   (22,24,w-44,h-28))
    pygame.draw.ellipse(surf,P_BODY_DK,(34,36,w-68,h-60))
    pygame.draw.circle(surf,(245,245,245),(cx-14,cy-10),14)
    pygame.draw.circle(surf,(245,245,245),(cx+14,cy-10),14)
    pygame.draw.circle(surf,P_OUTLINE,(cx-10,cy-8),5)
    pygame.draw.circle(surf,P_OUTLINE,(cx+18,cy-8),5)
    pygame.draw.arc(surf,P_OUTLINE,(cx-18,cy+4,36,20),math.pi*0.1,math.pi*0.9,3)
    for ox in [28,w-28]:
        pygame.draw.line(surf,P_OUTLINE,(ox,60),(8 if ox<50 else w-8,36),8)
        pygame.draw.line(surf,P_BODY,   (ox,60),(12 if ox<50 else w-12,38),4)
    for ox in [42,w-42]:
        pygame.draw.line(surf,P_OUTLINE,(ox,h-32),(18 if ox<50 else w-18,h-10),8)
        pygame.draw.line(surf,P_BODY,   (ox,h-32),(20 if ox<50 else w-20,h-12),4)
    pygame.draw.rect(surf,(255,128,128),(cx-16,cy+10,32,18),border_radius=8)
    pygame.draw.rect(surf,P_OUTLINE,   (cx-16,cy+10,32,18),2,border_radius=8)
    return surf

def make_web_surf(size=96):
    surf=pygame.Surface((size,size),pygame.SRCALPHA)
    c=size//2; web=(245,245,250,255)
    for r,lw in [(34,3),(24,2),(14,2),(7,1)]:
        pygame.draw.circle(surf,web,(c,c),r,lw)
    for ang in range(0,360,30):
        rad=math.radians(ang)
        x=c+int(math.cos(rad)*36); y=c+int(math.sin(rad)*36)
        pygame.draw.line(surf,web,(c,c),(x,y),3)
        pygame.draw.line(surf,(90,90,110,255),(c,c),(x,y),1)
    for i in range(3):
        pygame.draw.line(surf,(200,200,215,120),(c-6-i*6,c+4+i*3),(c-26-i*6,c+16+i*3),2)
    return surf

# ── Classes do Boss ───────────────────────────────────
@dataclass
class Proj:
    x:float; y:float; vx:float; vy:float
    image:object; radius:int; damage:int; color:tuple
    from_player:bool=True
    def update(self,dt): self.x+=self.vx*dt; self.y+=self.vy*dt
    def getrect(self):
        if self.image:
            w,h=self.image.get_size()
            return pygame.Rect(int(self.x-w//2),int(self.y-h//2),w,h)
        return pygame.Rect(int(self.x-self.radius),int(self.y-self.radius),
                           self.radius*2,self.radius*2)
    def draw(self,surf):
        if self.image:
            surf.blit(self.image,self.image.get_rect(center=(int(self.x),int(self.y))))
        else:
            pygame.draw.circle(surf,self.color,(int(self.x),int(self.y)),self.radius)
            pygame.draw.circle(surf,(255,255,255),(int(self.x-3),int(self.y-3)),max(2,self.radius//3))

class Jogador:
    def __init__(self,x,y,img=None):
        self.x=x; self.y=y
        self.w,self.h=PLAYER_SIZE
        self.hp=PLAYER_MAX_HP; self.img=img
        self.shoot_t=0.0; self.invuln_t=0.0
        self.dead=False; self.facing=1
        self.rect=pygame.Rect(x,y,self.w,self.h)
    def update(self,dt,keys,projs):
        if self.dead: return
        mx=my=0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  mx-=1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: mx+=1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    my-=1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  my+=1
        if mx or my:
            ln=math.hypot(mx,my); mx/=ln; my/=ln
            self.x+=mx*PLAYER_SPEED*dt; self.y+=my*PLAYER_SPEED*dt
            if mx: self.facing=1 if mx>0 else -1
        self.x=clamp(self.x,40,BOSS_W-self.w-40)
        self.y=clamp(self.y,330,BOSS_H-self.h-40)
        if self.shoot_t>0:  self.shoot_t-=dt
        if self.invuln_t>0: self.invuln_t-=dt
        if keys[pygame.K_SPACE] and self.shoot_t<=0:
            self.shoot_t=PLAYER_SHOT_CD
            px=self.x+self.w*0.52+self.facing*34
            py=self.y+self.h*0.42
            projs.append(Proj(px,py,PLAYER_PROJ_SPEED*self.facing,0,
                               None,8,PLAYER_PROJ_DMG,P_PROJ_COLOR,True))
        self.rect.update(int(self.x),int(self.y),self.w,self.h)
    def hit(self,dmg):
        if self.invuln_t>0 or self.dead: return
        self.hp-=dmg; self.invuln_t=0.65
        if self.hp<=0: self.dead=True
    def draw(self,surf):
        if self.dead: return
        sp=self.img if self.img else make_player_surf(PLAYER_SIZE)
        if self.invuln_t>0 and int(self.invuln_t*20)%2==0:
            sp=sp.copy(); sp.fill((255,120,120,120),special_flags=pygame.BLEND_RGBA_ADD)
        if self.facing<0: sp=pygame.transform.flip(sp,True,False)
        surf.blit(sp,(int(self.x),int(self.y)))

class Aranha:
    def __init__(self,x,y,frames,web_img=None):
        self.bx=x; self.by=y; self.x=x; self.y=y
        self.frames=frames or []; self.web_img=web_img
        self.fi=0.0; self.fspd=6.0
        self.w,self.h=self.frames[0].get_size() if self.frames else (320,320)
        self.hp=SPIDER_MAX_HP; self.max_hp=SPIDER_MAX_HP
        self.atk_t=random.uniform(0.8,1.6)
        self.mv_t=0.0; self.flash_t=0.0; self.dead=False
        self.rect=pygame.Rect(x,y,self.w,self.h)
    def update(self,dt,jogador,projs):
        if self.dead: return
        self.mv_t+=dt*SPIDER_MOVE_SPD
        self.x=self.bx+math.sin(self.mv_t)*SPIDER_RADIUS_X
        self.y=self.by+math.sin(self.mv_t*1.7)*SPIDER_RADIUS_Y
        self.x=clamp(self.x,90,BOSS_W-self.w-50)
        self.y=clamp(self.y,20,BOSS_H-self.h-230)
        self.fi=(self.fi+dt*self.fspd)%max(1,len(self.frames))
        if self.atk_t>0:   self.atk_t-=dt
        if self.flash_t>0: self.flash_t-=dt
        if self.atk_t<=0:
            self.atk_t=random.uniform(*SPIDER_ATK_CD)
            self._shoot(jogador,projs)
        self.rect.update(int(self.x),int(self.y),self.w,self.h)
    def _shoot(self,jogador,projs):
        if jogador.dead: return
        sx=self.x+self.w*0.55; sy=self.y+self.h*0.65
        dx=(jogador.x+jogador.w*0.5)-sx; dy=(jogador.y+jogador.h*0.5)-sy
        dist=max(1.0,math.hypot(dx,dy))
        img=self.web_img.copy() if self.web_img else make_web_surf()
        projs.append(Proj(sx,sy,dx/dist*SPIDER_BALL_SPD,dy/dist*SPIDER_BALL_SPD,
                          img,16,SPIDER_BALL_DMG,SPIDER_WEB_CLR,False))
    def hit(self,dmg):
        if self.dead: return
        self.hp-=dmg; self.flash_t=0.15
        if self.hp<=0: self.dead=True
    def draw(self,surf):
        if self.frames:
            fr=self.frames[int(self.fi)%len(self.frames)]
            surf.blit(fr,(int(self.x),int(self.y)))
        else:
            pygame.draw.circle(surf,(20,20,20),(int(self.x+160),int(self.y+160)),100)
        bw,bh=420,18; bx=BOSS_W//2-bw//2; by=18
        pygame.draw.rect(surf,(20,20,20),(bx,by,bw,bh),border_radius=8)
        pygame.draw.rect(surf,(190,52,76),(bx,by,int(bw*max(0,self.hp)/self.max_hp),bh),border_radius=8)
        pygame.draw.rect(surf,(240,220,220),(bx,by,bw,bh),2,border_radius=8)
        draw_text_boss(surf,"ARANHA SOMBRIA",18,UI_TEXT,BOSS_W//2,by+9)

def draw_cave(surf,bg):
    if bg: surf.blit(bg,(0,0)); return
    surf.fill(BG_COLOR)
    pygame.draw.rect(surf,ARENA_WALL,(0,0,BOSS_W,120))
    pygame.draw.polygon(surf,ARENA_WALL,[(0,0),(170,140),(0,300)])
    pygame.draw.polygon(surf,ARENA_WALL,[(BOSS_W,0),(BOSS_W-170,140),(BOSS_W,300)])
    pygame.draw.rect(surf,ARENA_FLOOR,(0,470,BOSS_W,250))
    pygame.draw.ellipse(surf,(92,79,72),(250,520,780,220))
    for x in range(0,BOSS_W,90):
        y=470+int(8*math.sin(x*0.06))
        pygame.draw.circle(surf,(98,84,76),(x+18,y+20),8)
        pygame.draw.circle(surf,(80,70,64),(x+40,y+26),5)

def draw_circle_close(surf,prog):
    if prog<=0: return
    ov=pygame.Surface((BOSS_W,BOSS_H),pygame.SRCALPHA)
    ov.fill((0,0,0,220))
    r=int(max(BOSS_W,BOSS_H)*0.8*(1.0-prog))
    pygame.draw.circle(ov,(0,0,0,0),(BOSS_W//2,BOSS_H//2),r)
    surf.blit(ov,(0,0))

# ── Loop do boss ─────────────────────────────────────
def run_boss():
    global tela
    tela = pygame.display.set_mode((BOSS_W,BOSS_H))
    tela_b = tela

    bg_img   = load_img_path(ASSET_DIR/"backgrounds"/"cave_background.png",(BOSS_W,BOSS_H))
    p_img    = load_img_path(BASE_DIR/"player.png",PLAYER_SIZE)
    win_img  = load_img_path(BASE_DIR/"minha_imagem_final.png",(BOSS_W,BOSS_H))
    web_img  = load_img_path(ASSET_DIR/"projectiles"/"spider_web.png",(96,96))
    sp_frs   = load_frames(ASSET_DIR/"boss_spider","spider_idle_{}.png",(320,320))

    jogador  = Jogador(150,BOSS_H-210,img=p_img)
    aranha   = Aranha(BOSS_W-420,40,sp_frs,web_img=web_img)
    projs    = []
    bstate   = "fadein"
    close_p  = 0.0
    go_timer = 0.0       # timer do game over
    DURACAO_GO = 3.0
    bf       = Fade(); bf.start("in",dur=72)
    clock    = pygame.time.Clock()

    while True:
        dt=clock.tick(FPS)/1000.0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                tela = pygame.display.set_mode((MENU_W,MENU_H))
                return

        keys=pygame.key.get_pressed()

        if bstate=="fadein":
            bf.update()
            if bf.done: bstate="fight"

        elif bstate=="fight":
            jogador.update(dt,keys,projs)
            aranha.update(dt,jogador,projs)
            for pr in projs[:]:
                pr.update(dt)
                if pr.x<-200 or pr.x>BOSS_W+200 or pr.y<-200 or pr.y>BOSS_H+200:
                    projs.remove(pr); continue
                if pr.from_player and not aranha.dead and aranha.rect.colliderect(pr.getrect()):
                    aranha.hit(pr.damage)
                    if pr in projs: projs.remove(pr)
                    continue
                if not pr.from_player and not jogador.dead and jogador.rect.colliderect(pr.getrect()):
                    jogador.hit(pr.damage)
                    if pr in projs: projs.remove(pr)
                    continue
            # Dano por contato direto com a aranha
            if not aranha.dead and not jogador.dead:
                if aranha.rect.colliderect(jogador.rect):
                    jogador.hit(SPIDER_BALL_DMG)

            if aranha.dead:  bstate="transition"; close_p=0.0
            if jogador.dead: bstate="gameover"

        elif bstate=="transition":
            close_p+=dt/CIRCLE_CLOSE_DUR
            if close_p>=1.0: close_p=1.0; bstate="win"

        # render
        draw_cave(tela_b,bg_img)
        for pr in projs: pr.draw(tela_b)
        aranha.draw(tela_b)
        jogador.draw(tela_b)

        hw,hh=260,18; hx,hy=20,BOSS_H-30
        pygame.draw.rect(tela_b,(20,20,20),(hx,hy,hw,hh),border_radius=8)
        pygame.draw.rect(tela_b,(82,214,118),(hx,hy,int(hw*max(0,jogador.hp)/PLAYER_MAX_HP),hh),border_radius=8)
        pygame.draw.rect(tela_b,(240,220,220),(hx,hy,hw,hh),2,border_radius=8)
        draw_text_boss(tela_b,"JOGADOR",18,UI_TEXT,hx+hw+62,hy+9)
        draw_text_boss(tela_b,"WASD/SETAS mover  |  ESPACO atirar  |  ESC menu",
                       18,UI_TEXT,BOSS_W//2,BOSS_H-14)

        if bstate=="transition": draw_circle_close(tela_b,close_p)
        if bstate=="fadein":     bf.draw(tela_b,BOSS_W,BOSS_H)

        if bstate=="win":
            if win_img: tela_b.blit(win_img,(0,0))
            else:
                tela_b.fill((15,12,20))
                draw_text_boss(tela_b,"VITÓRIA!",72,(255,210,90),BOSS_W//2,BOSS_H//2-30)
            draw_text_boss(tela_b,"Pressione qualquer tecla",26,UI_TEXT,BOSS_W//2,BOSS_H-36)
            pygame.display.flip()
            aguarda=True
            while aguarda:
                for ev in pygame.event.get():
                    if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
                    if ev.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN): aguarda=False
                clock.tick(FPS)
            tela = pygame.display.set_mode((MENU_W,MENU_H))
            return

        if bstate=="gameover":
            go_timer += dt
            prog = min(go_timer / DURACAO_GO, 1.0)
            # Render arena congelada + overlay
            ov=pygame.Surface((BOSS_W,BOSS_H),pygame.SRCALPHA)
            ov.fill((0,0,0,170)); tela_b.blit(ov,(0,0))
            draw_text_boss(tela_b,"GAME OVER",72,(255,92,110),BOSS_W//2,BOSS_H//2-30)
            draw_text_boss(tela_b,"Voltando ao menu...",28,UI_TEXT,BOSS_W//2,BOSS_H//2+40)
            # Barra de progresso
            bw=400; bh=8; bx=BOSS_W//2-bw//2; by=BOSS_H//2+80
            pygame.draw.rect(tela_b,(60,20,20),(bx,by,bw,bh),border_radius=4)
            pygame.draw.rect(tela_b,(255,92,110),(bx,by,int(bw*prog),bh),border_radius=4)
            # Fade final
            fd=pygame.Surface((BOSS_W,BOSS_H)); fd.fill((0,0,0)); fd.set_alpha(int(200*prog))
            tela_b.blit(fd,(0,0))
            pygame.display.flip()
            clock.tick(FPS)
            if prog >= 1.0:
                tela = pygame.display.set_mode((MENU_W,MENU_H))
                return
            continue

        pygame.display.flip()

# ══════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ══════════════════════════════════════════════════════
t_ant = pygame.time.get_ticks()

while True:
    agora = pygame.time.get_ticks()
    dt    = (agora-t_ant)/1000.0
    t_ant = agora
    tempo += dt
    mouse = pygame.mouse.get_pos()

    # ── Eventos ─────────────────────────────────────
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        # Clique no botão só é lido no estado "menu"
        if estado=="menu" and not fade.ativa:
            if botao.clicado(ev):
                try:
                    if som_clique: som_clique.play()
                except: pass
                fade.start("out",dur=60)
                estado="fade_menu_historia"

        # Pular slide da história
        if estado=="historia":
            if ev.type==pygame.KEYDOWN and ev.key in (pygame.K_SPACE,pygame.K_RETURN):
                slide_i+=1
                if slide_i>=len(HISTORIA):
                    estado="fade_historia_boss"
                    fade.start("out",dur=80)
                else:
                    slide_t=0.0; slide_alpha=0; slide_fase="in"

    # ── Lógica por estado ───────────────────────────
    if estado=="fade_menu_historia":
        if fade.done:
            # Inicia a história
            estado="historia"
            slide_i=0; slide_t=0.0; slide_alpha=0; slide_fase="in"
            stop_music(400)
            play_music(MUSICA_HISTORIA)
            fade.start("in",dur=40)   # fade-in ao entrar na história

    elif estado=="historia":
        update_historia(dt)

    elif estado=="fade_historia_boss":
        if fade.done:
            estado="boss"

    # Atualiza qualquer fade ativo (inclusive quando voltar do boss)
    fade.update()

    # ── Render ──────────────────────────────────────
    if estado in ("menu","fade_menu_historia"):
        render_menu()
        fade.draw(tela,MENU_W,MENU_H)

    elif estado in ("historia","fade_historia_boss"):
        render_historia()
        fade.draw(tela,MENU_W,MENU_H)

    elif estado=="boss":
        stop_music(300)
        play_music(MUSICA_BOSS)
        run_boss()
        # Volta ao menu
        estado="menu"
        stop_music(300)
        play_music(MUSICA_MENU)
        fade.start("in",dur=60)

    pygame.display.flip()
    relogio.tick(FPS)
