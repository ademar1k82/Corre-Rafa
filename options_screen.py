import asyncio
import os
import unicodedata

import pygame

# ---------------------------------------------------------------------------
# Estado global das opções — importado por game_logic.py
# ---------------------------------------------------------------------------
som_ativo = True      # música de fundo
efeitos_ativos = True  # sons de efeitos sfx


def _normalize_char(char):
    # Remove acentos para permitir texto como "OPCOES" a partir de "OPÇÕES".
    base = unicodedata.normalize("NFD", char)
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    return base.upper()


def _stem_to_char(stem):
    stem_up = stem.upper()
    if len(stem_up) == 1:
        return stem_up
    if stem_up.startswith("CHAR_") and len(stem_up) == 6:
        return stem_up[-1]
    special = {
        "SPACE": " ",
        "DOT": ".",
        "COMMA": ",",
        "HYPHEN": "-",
        "PLUS": "+",
        "EXCLAMATION": "!",
        "QUESTION": "?",
        "COLON": ":",
    }
    return special.get(stem_up)


class ImageAlphabet:
    def __init__(self, glyphs):
        self.glyphs = glyphs
        self._cache = {}

    @classmethod
    def from_folder(cls, folder_path):
        glyphs = {}
        if not os.path.isdir(folder_path):
            return cls(glyphs)

        for name in os.listdir(folder_path):
            if not name.lower().endswith(".png"):
                continue
            stem = os.path.splitext(name)[0]
            char = _stem_to_char(stem)
            if not char:
                continue
            path = os.path.join(folder_path, name)
            glyphs[char] = pygame.image.load(path).convert_alpha()
        return cls(glyphs)

    def has_glyphs(self):
        return bool(self.glyphs)

    def _scaled_glyph(self, char, target_height):
        key = (char, target_height)
        if key in self._cache:
            return self._cache[key]

        glyph = self.glyphs.get(char)
        if glyph is None:
            return None

        if target_height is None:
            self._cache[key] = glyph
            return glyph

        h = max(1, glyph.get_height())
        scale = target_height / h
        width = max(1, int(glyph.get_width() * scale))
        height = max(1, int(glyph.get_height() * scale))
        scaled = pygame.transform.smoothscale(glyph, (width, height))
        self._cache[key] = scaled
        return scaled

    def render(self, text, target_height=48, letter_spacing=3, line_spacing=14):
        lines = text.split("\n")
        rendered_lines = []
        max_width = 0
        total_height = 0

        for line in lines:
            glyphs = []
            line_width = 0
            line_height = 0

            for raw_char in line:
                # Tenta o carácter original primeiro (ex: Ç), depois a versão normalizada (C)
                char_original = raw_char.upper()
                char_normalizado = _normalize_char(raw_char)
                char = char_original if char_original in self.glyphs else char_normalizado

                if char == " ":
                    space_width = max(10, (target_height or 40) // 2)
                    glyphs.append((None, space_width, target_height or 40))
                    line_width += space_width + letter_spacing
                    line_height = max(line_height, target_height or 40)
                    continue

                glyph = self._scaled_glyph(char, target_height)
                if glyph is None:
                    # Se faltar caractere, ignora silenciosamente.
                    continue
                glyphs.append((glyph, glyph.get_width(), glyph.get_height()))
                line_width += glyph.get_width() + letter_spacing
                line_height = max(line_height, glyph.get_height())

            if line_width > 0:
                line_width -= letter_spacing
            max_width = max(max_width, line_width)
            total_height += line_height
            rendered_lines.append((glyphs, line_width, line_height))

        if rendered_lines:
            total_height += line_spacing * (len(rendered_lines) - 1)

        if max_width <= 0 or total_height <= 0:
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        y = 0

        for glyphs, line_width, line_height in rendered_lines:
            x = 0
            for glyph, glyph_w, _ in glyphs:
                if glyph is not None:
                    surface.blit(glyph, (x, y + (line_height - glyph.get_height()) // 2))
                x += glyph_w + letter_spacing
            y += line_height + line_spacing

        return surface


# ---------------------------------------------------------------------------
# Toggle visual
# ---------------------------------------------------------------------------

TOGGLE_W = 110
TOGGLE_H = 50
# Cores inspiradas no estilo das letras do alfabeto
_COR_ON    = (194, 52, 52)    # vermelho das letras
_COR_OFF   = (60,  60, 60)    # cinzento escuro
_COR_BORDA = (40,  80, 140)   # azul do contorno das letras
_COR_CIRCULO_ON  = (240, 200, 60)   # amarelo/dourado (destaque activo)
_COR_CIRCULO_OFF = (160, 160, 160)  # cinzento (inactivo)


def _draw_toggle(surface, x, y, active):
    """Pill toggle: vermelho+círculo dourado = ON; cinzento+círculo cinzento = OFF."""
    cor = _COR_ON if active else _COR_OFF
    r = TOGGLE_H // 2
    rect = pygame.Rect(x, y, TOGGLE_W, TOGGLE_H)
    pygame.draw.rect(surface, cor, rect, border_radius=r)
    pygame.draw.rect(surface, _COR_BORDA, rect, 3, border_radius=r)

    circle_r = r - 5
    if active:
        cx = x + TOGGLE_W - r
    else:
        cx = x + r
    cy = y + r
    cor_circulo = _COR_CIRCULO_ON if active else _COR_CIRCULO_OFF
    pygame.draw.circle(surface, cor_circulo, (cx, cy), circle_r)
    pygame.draw.circle(surface, _COR_BORDA, (cx, cy), circle_r, 2)


def _toggle_rect(cx, y):
    """pygame.Rect do toggle centrado em cx."""
    return pygame.Rect(cx - TOGGLE_W // 2, y, TOGGLE_W, TOGGLE_H)


# ---------------------------------------------------------------------------
# Ecrã de Opções
# ---------------------------------------------------------------------------

async def show_options_screen(tela, clock, largura, altura, branco, cinza, preto):
    """Ecrã de Opções com toggles Som e Efeitos."""
    global som_ativo, efeitos_ativos

    alphabet_dir = os.path.join("assets", "alfabeto")
    image_font = ImageAlphabet.from_folder(alphabet_dir)

    fonte_titulo = pygame.font.SysFont("Arial", 44, bold=True)
    fonte_label  = pygame.font.SysFont("Arial", 30, bold=True)
    fonte_hint   = pygame.font.SysFont("Arial", 20)

    # Posições das linhas de opções  (centro horizontal)
    cx = largura // 2
    TITULO_Y  = 100
    ROW1_Y    = 230   # Som
    ROW2_Y    = 340   # Efeitos
    HINT_Y    = 480

    # Os toggles ficam à direita do label; labels à esquerda centrados a ~200px do centro
    LABEL_RIGHT_X = cx - 40   # borda direita do label
    TOGGLE_LEFT_X = cx + 40   # borda esquerda do toggle
    TOGGLE_CX     = TOGGLE_LEFT_X + TOGGLE_W // 2

    toggle_som_rect      = _toggle_rect(TOGGLE_CX, ROW1_Y)
    toggle_efeitos_rect  = _toggle_rect(TOGGLE_CX, ROW2_Y)

    def _render_label(text):
        if image_font.has_glyphs():
            return image_font.render(text, target_height=40, letter_spacing=-1)
        return fonte_label.render(text, True, branco)

    # Título: imagem botao-opcoes.png, escalada para altura máx de 80px
    titulo_path = os.path.join("assets", "botao-opcoes.png")
    if os.path.exists(titulo_path):
        _t_raw = pygame.image.load(titulo_path).convert_alpha()
        _t_max_h = 80
        _t_scale = _t_max_h / _t_raw.get_height()
        surf_titulo = pygame.transform.smoothscale(
            _t_raw,
            (int(_t_raw.get_width() * _t_scale), _t_max_h),
        )
    elif image_font.has_glyphs():
        surf_titulo = image_font.render("OPCOES", target_height=60, letter_spacing=4)
    else:
        surf_titulo = fonte_titulo.render("OPCOES", True, branco)

    surf_som      = _render_label("SOM")
    surf_efeitos  = _render_label("EFEITOS")
    surf_hint     = fonte_hint.render("ESC para voltar", True, cinza)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "back"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if toggle_som_rect.collidepoint(mouse_pos):
                    som_ativo = not som_ativo
                    if som_ativo:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                elif toggle_efeitos_rect.collidepoint(mouse_pos):
                    efeitos_ativos = not efeitos_ativos

        # --- Desenho ---
        tela.fill(preto)

        # Painel central
        panel = pygame.Rect(largura // 2 - 320, 70, 640, altura - 140)
        pygame.draw.rect(tela, (12, 12, 12), panel, border_radius=16)
        pygame.draw.rect(tela, (45, 45, 45), panel, 2, border_radius=16)

        # Título
        tela.blit(surf_titulo, (cx - surf_titulo.get_width() // 2, TITULO_Y))

        # Linha Som
        tela.blit(
            surf_som,
            (LABEL_RIGHT_X - surf_som.get_width(), ROW1_Y + (TOGGLE_H - surf_som.get_height()) // 2),
        )
        _draw_toggle(tela, toggle_som_rect.x, toggle_som_rect.y, som_ativo)

        # Linha Efeitos
        tela.blit(
            surf_efeitos,
            (LABEL_RIGHT_X - surf_efeitos.get_width(), ROW2_Y + (TOGGLE_H - surf_efeitos.get_height()) // 2),
        )
        _draw_toggle(tela, toggle_efeitos_rect.x, toggle_efeitos_rect.y, efeitos_ativos)

        # Hint
        tela.blit(surf_hint, (cx - surf_hint.get_width() // 2, HINT_Y))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
