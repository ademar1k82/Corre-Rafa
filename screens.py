"""
screens.py — Ecrãs de UI: banner, menu principal, placeholders, fim de campanha.

Todas as funções recebem `tela` e `clock` como parâmetros,
seguindo o mesmo padrão de level_boards.py e storyboard.py.
"""
import asyncio
import os

import pygame

from constants import LARGURA, ALTURA, PRETO, BRANCO, CINZA


async def show_banner_screen(tela, clock):
    """Ecrã inicial: banner.png com fade-in / hold / fade-out sobre fundo preto."""
    banner_path = os.path.join("assets", "banner.png")
    if not os.path.exists(banner_path):
        return

    banner_raw = pygame.image.load(banner_path).convert_alpha()
    bw, bh = banner_raw.get_size()
    max_w = int(LARGURA * 0.5)
    max_h = int(ALTURA * 0.5)
    scale = min(max_w / bw, max_h / bh)
    banner = pygame.transform.smoothscale(banner_raw, (int(bw * scale), int(bh * scale)))
    bx = (LARGURA - banner.get_width()) // 2
    by = (ALTURA - banner.get_height()) // 2

    FADE_IN  = 90   # ~1.5 s a 60 fps
    HOLD     = 60   # ~1 s
    FADE_OUT = 90   # ~1.5 s

    for frame in range(FADE_IN + HOLD + FADE_OUT):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return  # saltar animação

        if frame < FADE_IN:
            alpha = int(255 * frame / FADE_IN)
        elif frame < FADE_IN + HOLD:
            alpha = 255
        else:
            alpha = int(255 * (1.0 - (frame - FADE_IN - HOLD) / FADE_OUT))

        tela.fill(PRETO)
        banner_copia = banner.copy()
        banner_copia.set_alpha(alpha)
        tela.blit(banner_copia, (bx, by))
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


async def show_main_menu(tela, clock):
    """Menu principal com logo e botões Iniciar / Opções / Info.
    Retorna: 'start' | 'options' | 'info' | 'quit'
    """
    logo_path = os.path.join("assets", "Main_logo.png")
    if os.path.exists(logo_path):
        logo_raw = pygame.image.load(logo_path).convert_alpha()
        lw, lh = logo_raw.get_size()
        max_w = LARGURA - 80
        max_h = int(ALTURA * 0.54)
        scale = min(max_w / lw, max_h / lh)
        logo = pygame.transform.smoothscale(logo_raw, (int(lw * scale), int(lh * scale)))
    else:
        logo = None

    botoes = [
        {
            "action": "start",
            "image_path": os.path.join("assets", "botao-iniciar.png"),
            "base_scale": 0.84,
        },
        {
            "action": "options",
            "image_path": os.path.join("assets", "botao-opcoes.png"),
            "base_scale": 1.1,
        },
        {
            "action": "info",
            "image_path": os.path.join("assets", "botao-info.png"),
            "base_scale": 0.84,
        },
    ]

    btn_row_gap  = 44
    btn_pair_gap = 130
    fallback_font = pygame.font.SysFont("Arial", 26, bold=True)

    for btn in botoes:
        if os.path.exists(btn["image_path"]):
            img = pygame.image.load(btn["image_path"]).convert_alpha()
            iw, ih = img.get_size()
            max_w = int(LARGURA * 0.26)
            max_h = 64
            scale = min(max_w / iw, max_h / ih) * btn.get("base_scale", 1.0)
            btn["image"] = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
            btn["hover_image"] = pygame.transform.smoothscale(
                btn["image"],
                (
                    int(btn["image"].get_width() * 1.14),
                    int(btn["image"].get_height() * 1.14),
                ),
            )
        else:
            label = btn["action"].upper()
            btn["image"] = fallback_font.render(label, True, BRANCO)
            btn["hover_image"] = pygame.transform.smoothscale(
                btn["image"],
                (
                    int(btn["image"].get_width() * 1.14),
                    int(btn["image"].get_height() * 1.14),
                ),
            )

    btn_by_action = {btn["action"]: btn for btn in botoes}
    start_btn   = btn_by_action["start"]
    options_btn = btn_by_action["options"]
    info_btn    = btn_by_action["info"]

    logo_bottom = 18 + logo.get_height() if logo else int(ALTURA * 0.32)

    start_x = LARGURA // 2 - start_btn["image"].get_width() // 2
    start_y = logo_bottom + 18
    start_btn["rect"] = start_btn["image"].get_rect(topleft=(start_x, start_y))

    pair_y      = start_btn["rect"].bottom + btn_row_gap
    pair_row_h  = max(options_btn["image"].get_height(), info_btn["image"].get_height())
    pair_total_w = options_btn["image"].get_width() + btn_pair_gap + info_btn["image"].get_width()
    pair_left_x  = LARGURA // 2 - pair_total_w // 2
    options_offset_x = -36

    options_y = pair_y + (pair_row_h - options_btn["image"].get_height()) // 2
    info_y    = pair_y + (pair_row_h - info_btn["image"].get_height()) // 2
    options_btn["rect"] = options_btn["image"].get_rect(
        topleft=(pair_left_x + options_offset_x, options_y)
    )
    info_btn["rect"] = info_btn["image"].get_rect(
        topleft=(pair_left_x + options_btn["image"].get_width() + btn_pair_gap, info_y)
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "start"
                if evento.key == pygame.K_ESCAPE:
                    return "quit"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for btn in botoes:
                    if btn["rect"].collidepoint(mouse_pos):
                        return btn["action"]

        tela.fill(PRETO)
        if logo:
            lx = (LARGURA - logo.get_width()) // 2
            tela.blit(logo, (lx, 18))

        for btn in botoes:
            hover = btn["rect"].collidepoint(mouse_pos)
            base_img = btn["hover_image"] if hover else btn["image"]
            if hover:
                pos = (
                    btn["rect"].centerx - base_img.get_width() // 2,
                    btn["rect"].centery - base_img.get_height() // 2,
                )
                tela.blit(base_img, pos)
            else:
                tela.blit(base_img, btn["rect"].topleft)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


async def show_placeholder_screen(tela, clock, titulo):
    """Ecrã placeholder para Info (em breve)."""
    fonte     = pygame.font.SysFont("Arial", 36, bold=True)
    fonte_sub = pygame.font.SysFont("Arial", 20)
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "back"
        tela.fill(PRETO)
        msg = fonte.render(titulo, True, BRANCO)
        sub = fonte_sub.render("Em breve  |  pressione qualquer tecla para voltar", True, CINZA)
        tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, ALTURA // 2 - 40))
        tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, ALTURA // 2 + 20))
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


async def show_campaign_end_screen(tela, clock):
    """Ecrã de fim de campanha."""
    fonte = pygame.font.SysFont("Arial", 34, bold=True)
    fonte_sub = pygame.font.SysFont("Arial", 22, bold=True)

    epgaia_path = os.path.join("assets", "EPGaia.png")
    epgaia_img = None
    if os.path.exists(epgaia_path):
        raw = pygame.image.load(epgaia_path).convert_alpha()
        rw, rh = raw.get_size()
        max_w = int(LARGURA * 0.56)
        max_h = int(ALTURA * 0.46)
        scale = min(max_w / max(1, rw), max_h / max(1, rh), 1.0)
        epgaia_img = pygame.transform.smoothscale(raw, (int(rw * scale), int(rh * scale)))

    inicio = pygame.time.get_ticks()
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN:
                return
        tela.fill((18, 24, 30))

        msg = fonte.render("O Rafa chegou a tempo e teve uma nota incrível!", True, (0, 255, 120))
        sub = fonte_sub.render("Obrigado por ajudares", True, BRANCO)
        tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, 58))
        tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 106))

        if epgaia_img is not None:
            tela.blit(
                epgaia_img,
                (
                    LARGURA // 2 - epgaia_img.get_width() // 2,
                    160,
                ),
            )

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
        if pygame.time.get_ticks() - inicio >= 2600:
            return
