"""
utils.py — Audio, font helpers e assets partilhados.

Chame utils.init() UMA VEZ após pygame.init() e pygame.mixer.init()
para carregar sons, ícone da janela, toggle marker e música de fundo.
"""
import os

import pygame

import options_screen

# ---------------------------------------------------------------------------
# Objectos de áudio — populados por init()
# ---------------------------------------------------------------------------
som_salto   = None
som_morte   = None
som_ponto   = None
som_begining = None
som_ending  = None

TOGGLE_MARKER = None

musica_fundo_carregada = False
_musica_fundo_path = None


# ---------------------------------------------------------------------------
# Funções auxiliares (disponíveis antes de init())
# ---------------------------------------------------------------------------

def _carregar_som(nome_arquivo):
    caminho = os.path.join("assets", nome_arquivo)
    if os.path.exists(caminho):
        return pygame.mixer.Sound(caminho)
    return None


def tocar_som(som):
    if som is not None and options_screen.efeitos_ativos:
        som.play()


def asset_existe(nome_arquivo):
    return os.path.exists(os.path.join("assets", nome_arquivo))


def carregar_fonte_arcade(tamanho):
    """Tenta usar uma fonte estilo retro arcade disponível no sistema."""
    candidatos = [
        "Press Start 2P",
        "Arcade",
        "ArcadeClassic",
        "Pixeloid Sans",
        "VT323",
        "Courier New",
    ]
    for nome in candidatos:
        caminho = pygame.font.match_font(nome)
        if caminho:
            return pygame.font.Font(caminho, tamanho)
    return pygame.font.Font(None, tamanho)


def render_texto_pixel_bold(fonte, texto, cor_texto, cor_contorno=(28, 86, 145)):
    """Renderiza texto sem antialias com contorno — look retro/pixel bold."""
    base = fonte.render(texto, False, cor_texto)
    w, h = base.get_size()
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    contorno = fonte.render(texto, False, cor_contorno)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        out.blit(contorno, (1 + dx, 1 + dy))
    out.blit(base, (1, 1))
    return out


def iniciar_musica_fundo_se_ativo():
    """Inicia a música de fundo apenas se Som está activo e não está a tocar."""
    if not musica_fundo_carregada:
        return
    if not options_screen.som_ativo:
        return
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)


# ---------------------------------------------------------------------------
# init() — deve ser chamado após pygame.init() + pygame.mixer.init()
# ---------------------------------------------------------------------------

def init():
    """Carrega todos os assets que requerem pygame iniciado."""
    global som_salto, som_morte, som_ponto, som_begining, som_ending
    global TOGGLE_MARKER, musica_fundo_carregada, _musica_fundo_path

    # Sons
    som_salto    = _carregar_som("jump.wav")
    som_morte    = _carregar_som("die.wav")
    som_ponto    = _carregar_som("point.wav")
    som_begining = _carregar_som("begining.wav")
    som_ending   = _carregar_som("ending.wav")

    # Ícone da janela
    icon_path = os.path.join("assets", "toggle.png")
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))

    # Toggle marker (marcador da barra de progresso)
    toggle_path = os.path.join("assets", "toggle.png")
    if os.path.exists(toggle_path):
        raw = pygame.image.load(toggle_path).convert_alpha()
        _h = 42
        scale = _h / max(1, raw.get_height())
        TOGGLE_MARKER = pygame.transform.smoothscale(
            raw, (int(raw.get_width() * scale), _h)
        )

    # Música de fundo
    for ext in (".mp3", ".wav", ".ogg"):
        candidato = os.path.join("assets", f"background{ext}")
        if os.path.exists(candidato):
            _musica_fundo_path = candidato
            break
    if _musica_fundo_path is None:
        fallback = os.path.join("assets", "stranger_things_trilha.mp3")
        if os.path.exists(fallback):
            _musica_fundo_path = fallback
    if _musica_fundo_path is not None:
        pygame.mixer.music.load(_musica_fundo_path)
        pygame.mixer.music.set_volume(0.3)
        musica_fundo_carregada = True
