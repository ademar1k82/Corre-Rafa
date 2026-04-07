import asyncio
import os

import pygame

from options_screen import ImageAlphabet


INFO_TEXT = {
    "HISTORIA": (
        "A ideia surge no contexto do evento EPG Open - Uma escola\n"
        "de valores.\n\n"
        "A história principal nasce de uma brincadeira com um dos\n"
        "alunos, foi recebida com entusiasmo e mostra um dos\n"
        "principais valores notados na sala de aula: o\n"
        "companheirismo.\n\n"
        "A partir daí, o crescimento e desenvolvimento do projeto\n"
        "teve a participação e ideias de todos.\n\n"
        "Em termos de desenvolvimento técnico, o projeto servirá\n"
        "como base para análise e construção de vários conteúdos\n"
        "presentes no módulo, como bibliotecas em Python, classes\n"
        "e programação orientada a objetos."
    ),
    "COMANDOS": (
        "Seta CIMA / ESPACO: Saltar\n"
        "Seta BAIXO: Baixar\n"
        "Seta DIREITA: Acelerar\n"
        "Seta ESQUERDA: Travar\n\n"
        "ESC: Voltar ao menu\n"
        "R: Reiniciar (quando perde)"
    ),
    "CREDITOS": (
        "Desenvolvimento: 11º ano - Técnico de Gestão de Equipamentos\n"
        "Informáticos (2026).\n\n"
        "Inspiração: adaptado do jogo Dino-Run-Vecna, disponível em:\n"
        "github.com/elen-c-sales/dino-run-vecna-edition\n\n"
        "Arte e Design: criada com Nano Banana.\n"
        "Som e música: Sonic the Hedgehog.\n\n"
        "Obrigado por jogares!"
    ),
}


def _load_image_alphabet():
    pasta = os.path.join("assets", "Alfabeto")
    if not os.path.isdir(pasta):
        pasta = os.path.join("assets", "alfabeto")
    return ImageAlphabet.from_folder(pasta)


def _render_menu_label(image_font, fallback_font, text, selected=False):
    if image_font.has_glyphs():
        surf = image_font.render(text, target_height=44, letter_spacing=2)
    else:
        color = (255, 255, 255)
        surf = fallback_font.render(text, True, color)

    if not selected:
        return surf

    # Hover estilo menu principal: sem fundo, apenas aumento ligeiro.
    return pygame.transform.smoothscale(
        surf,
        (
            int(surf.get_width() * 1.12),
            int(surf.get_height() * 1.12),
        ),
    )


def _wrap_lines(font, text, max_width):
    result = []
    for block in text.split("\n"):
        if not block.strip():
            result.append("")
            continue
        words = block.split()
        cur = words[0]
        for w in words[1:]:
            candidate = f"{cur} {w}"
            if font.size(candidate)[0] <= max_width:
                cur = candidate
            else:
                result.append(cur)
                cur = w
        result.append(cur)
    return result


async def _show_text_page(tela, clock, largura, altura, image_font, title, text):
    body_font = pygame.font.SysFont("Arial", 28)
    hint_font = pygame.font.SysFont("Arial", 20)

    if image_font.has_glyphs():
        title_surf = image_font.render(title, target_height=54, letter_spacing=3)
    else:
        title_surf = pygame.font.SysFont("Arial", 42, bold=True).render(title, True, (255, 235, 120))

    max_text_w = largura - 160
    lines = _wrap_lines(body_font, text, max_text_w)

    text_top = 170
    text_bottom = altura - 78
    text_area_h = max(80, text_bottom - text_top)

    line_h = body_font.get_height() + 8
    spacer_h = line_h // 2

    rendered_items = []
    total_h = 0
    for line in lines:
        if not line:
            rendered_items.append((None, spacer_h))
            total_h += spacer_h
            continue
        surf = body_font.render(line, True, (230, 230, 230))
        rendered_items.append((surf, line_h))
        total_h += line_h

    scroll_px = 0
    max_scroll = max(0, total_h - text_area_h)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN):
                    return "back"
                if evento.key == pygame.K_UP:
                    scroll_px = max(0, scroll_px - 28)
                if evento.key == pygame.K_DOWN:
                    scroll_px = min(max_scroll, scroll_px + 28)
                if evento.key == pygame.K_PAGEUP:
                    scroll_px = max(0, scroll_px - text_area_h)
                if evento.key == pygame.K_PAGEDOWN:
                    scroll_px = min(max_scroll, scroll_px + text_area_h)
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 4:
                    scroll_px = max(0, scroll_px - 36)
                if evento.button == 5:
                    scroll_px = min(max_scroll, scroll_px + 36)

        tela.fill((0, 0, 0))
        tela.blit(title_surf, (largura // 2 - title_surf.get_width() // 2, 70))

        y = text_top - scroll_px
        for surf, h in rendered_items:
            if y + h >= text_top and y <= text_bottom:
                if surf is not None:
                    tela.blit(surf, (largura // 2 - surf.get_width() // 2, y))
            y += h

        if max_scroll > 0:
            hint_text = "ENTER/ESC para voltar | CIMA/BAIXO ou roda para scroll"
        else:
            hint_text = "ENTER/ESC para voltar"
        hint = hint_font.render(hint_text, True, (160, 160, 160))
        tela.blit(hint, (largura // 2 - hint.get_width() // 2, altura - 48))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


async def show_info_screen(tela, clock, largura, altura):
    image_font = _load_image_alphabet()
    fallback_font = pygame.font.SysFont("Arial", 32, bold=True)
    hint_font = pygame.font.SysFont("Arial", 20)

    options = ["HISTORIA", "COMANDOS", "CREDITOS"]
    selected = 0

    if image_font.has_glyphs():
        title_surf = image_font.render("INFO", target_height=64, letter_spacing=4)
    else:
        title_surf = pygame.font.SysFont("Arial", 48, bold=True).render("INFO", True, (255, 235, 120))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        item_rects = []

        y0 = 230
        gap = 72
        for i, item in enumerate(options):
            surf = _render_menu_label(image_font, fallback_font, item, selected=(i == selected))
            rect = surf.get_rect(center=(largura // 2, y0 + i * gap))
            item_rects.append((rect, item, surf))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "back"
                if evento.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if evento.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chosen = options[selected]
                    page_result = await _show_text_page(
                        tela,
                        clock,
                        largura,
                        altura,
                        image_font,
                        chosen,
                        INFO_TEXT[chosen],
                    )
                    if page_result == "quit":
                        return "quit"
            if evento.type == pygame.MOUSEMOTION:
                for i, (rect, _, _) in enumerate(item_rects):
                    if rect.collidepoint(mouse_pos):
                        selected = i
                        break
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for i, (rect, item, _) in enumerate(item_rects):
                    if rect.collidepoint(mouse_pos):
                        selected = i
                        page_result = await _show_text_page(
                            tela,
                            clock,
                            largura,
                            altura,
                            image_font,
                            item,
                            INFO_TEXT[item],
                        )
                        if page_result == "quit":
                            return "quit"
                        break

        tela.fill((0, 0, 0))
        tela.blit(title_surf, (largura // 2 - title_surf.get_width() // 2, 70))

        for rect, _, surf in item_rects:
            tela.blit(surf, rect.topleft)

        hint = hint_font.render("Setas + Enter para continuar | ESC para voltar", True, (160, 160, 160))
        tela.blit(hint, (largura // 2 - hint.get_width() // 2, altura - 44))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
