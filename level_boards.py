import asyncio
import os

import pygame

from options_screen import ImageAlphabet


_ROMAN_BY_INDEX = {1: "I", 2: "II", 3: "III"}


def _load_scaled(image_path, max_w, max_h):
    if not os.path.exists(image_path):
        return None
    raw = pygame.image.load(image_path).convert_alpha()
    iw, ih = raw.get_size()
    scale = min(max_w / max(1, iw), max_h / max(1, ih))
    scale = min(scale, 1.0)
    if scale != 1.0:
        raw = pygame.transform.smoothscale(raw, (int(iw * scale), int(ih * scale)))
    return raw


async def show_level_board(tela, clock, largura, altura, level_index):
    """Board entre níveis com título, mapa e marcador do nível a piscar."""
    roman = _ROMAN_BY_INDEX.get(level_index, str(level_index))

    image_font = ImageAlphabet.from_folder(os.path.join("assets", "Alfabeto"))
    fallback_title_font = pygame.font.SysFont("Arial", 58, bold=True)

    map_path = os.path.join("assets", "lvl-map.jpg")
    marker_path = os.path.join("assets", f"lvl-{level_index}.png")

    map_img = _load_scaled(map_path, largura * 0.94, altura * 0.72)
    marker_raw = pygame.image.load(marker_path).convert_alpha() if os.path.exists(marker_path) else None

    if image_font.has_glyphs():
        title_surf = image_font.render(f"NIVEL {roman}", target_height=58, letter_spacing=0)
    else:
        title_surf = fallback_title_font.render(f"NIVEL {roman}", True, (235, 70, 70))

    if map_img is not None:
        map_rect = map_img.get_rect(center=(largura // 2, int(altura * 0.60)))
    else:
        map_rect = pygame.Rect(largura // 2 - 250, int(altura * 0.40), 500, 220)

    marker_img = None
    if marker_raw is not None:
        if map_img is not None:
            base_map_w, base_map_h = map_img.get_size()
            raw_map = pygame.image.load(map_path)
            raw_map_w, raw_map_h = raw_map.get_size()
            scale = base_map_w / max(1, raw_map_w)
            marker_img = pygame.transform.smoothscale(
                marker_raw,
                (max(1, int(marker_raw.get_width() * scale)), max(1, int(marker_raw.get_height() * scale))),
            )
        else:
            marker_img = marker_raw

    start = pygame.time.get_ticks()
    DURATION_MS = 3600
    BLINK_MS = 420

    while True:
        now = pygame.time.get_ticks()
        if now - start >= DURATION_MS:
            return "next"

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "next"

        tela.fill((0, 0, 0))

        title_x = largura // 2 - title_surf.get_width() // 2
        tela.blit(title_surf, (title_x, 70))

        if map_img is not None:
            tela.blit(map_img, map_rect.topleft)
        else:
            pygame.draw.rect(tela, (18, 18, 18), map_rect, border_radius=14)
            pygame.draw.rect(tela, (80, 80, 80), map_rect, 2, border_radius=14)

        # Pisca o marcador do nível sobre o mapa.
        if marker_img is not None and ((now - start) // BLINK_MS) % 2 == 0:
            if map_img is not None and marker_img.get_size() == map_img.get_size():
                marker_rect = marker_img.get_rect(topleft=map_rect.topleft)
            else:
                marker_rect = marker_img.get_rect(center=map_rect.center)
            tela.blit(marker_img, marker_rect.topleft)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
