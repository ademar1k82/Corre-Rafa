import asyncio
import os

import pygame


def _load_scene(path, largura, altura):
    if not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    iw, ih = img.get_size()
    max_w = int(largura * 0.90)
    max_h = int(altura * 0.72)
    scale = min(max_w / max(1, iw), max_h / max(1, ih), 1.0)
    if scale != 1.0:
        img = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
    return img


def _wrap_text_lines(fonte, text, max_width):
    """Quebra texto por palavras para caber na largura indicada."""
    lines = []
    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        if paragraph == "":
            # Quebra dupla (\n\n) mantém uma linha em branco explícita.
            lines.append("")
            continue

        words = paragraph.split(" ")
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"
            if fonte.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                    current = word
                else:
                    # Palavra isolada maior que max_width: mantém como linha única.
                    lines.append(word)

        if current:
            lines.append(current)

    return lines if lines else [""]


def _render_typewriter_text(
    fonte,
    text,
    visible_chars,
    max_width,
    cor=(240, 235, 210),
    sombra=(20, 20, 20),
    line_gap=6,
):
    shown = text[: max(0, visible_chars)]
    lines = _wrap_text_lines(fonte, shown, max_width)

    rendered = [fonte.render(line, True, cor) for line in lines]
    rendered_shadow = [fonte.render(line, True, sombra) for line in lines]

    width = max((surf.get_width() for surf in rendered), default=1)
    line_h = max((surf.get_height() for surf in rendered), default=1)
    height = len(rendered) * line_h + max(0, len(rendered) - 1) * line_gap

    out = pygame.Surface((width + 2, height + 2), pygame.SRCALPHA)
    y = 0
    for sh, fg in zip(rendered_shadow, rendered):
        out.blit(sh, (2, y + 2))
        out.blit(fg, (0, y))
        y += line_h + line_gap

    return out


SCENE_CAPTIONS = {
    "scene-1.png": "Nãooo!!! Adormeci!Não posso faltar mais!\nTenho de me despachar!!!",
    "scene-2.png": "Agora vai começar a chover... mas não posso esperar, tenho de continuar!!!",
    "scene-3.png": "Nuno: - Stôr, o Rafa vai chegar atrasado...\nProfessor: - Outra vez!?!? Já chega! Diz-lhe que vai ter falta!",
    "scene-4.png": "Ganda Rafa!!! SIX-SEVEN!!!",
    "scene-gameover.png": "Já não consigo...o Stôr vai-me matar!"
}

async def show_story_scene(tela, clock, largura, altura, scene_file):
    """Mostra uma única cena do storyboard com texto animado (typewriter)."""
    caption = SCENE_CAPTIONS.get(scene_file, "")

    fonte = pygame.font.SysFont("Courier New", 28, bold=True)
    fonte_hint = pygame.font.SysFont("Courier New", 19, bold=True)
    fundo = (0, 0, 0)

    scene_path = os.path.join("assets", scene_file)
    scene_img = _load_scene(scene_path, largura, altura)

    if scene_img is not None:
        scene_rect = scene_img.get_rect(center=(largura // 2, int(altura * 0.42)))
    else:
        scene_rect = pygame.Rect(largura // 2 - 360, 70, 720, 360)

    # Ajuste da animação do texto (esquerda para direita)
    ms_por_char = 35
    hold_after_full_ms = 900
    scene_start = pygame.time.get_ticks()

    done = False
    while not done:
        now = pygame.time.get_ticks()
        elapsed = now - scene_start
        chars = min(len(caption), elapsed // ms_por_char)
        completed = chars >= len(caption)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "quit"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "quit"
                done = True
            if evento.type == pygame.MOUSEBUTTONDOWN:
                done = True

        tela.fill(fundo)

        if scene_img is not None:
            tela.blit(scene_img, scene_rect.topleft)
        else:
            pygame.draw.rect(tela, (20, 20, 20), scene_rect, border_radius=12)
            pygame.draw.rect(tela, (80, 80, 80), scene_rect, 2, border_radius=12)

        text_max_w = int(largura * 0.86)
        text_surf = _render_typewriter_text(fonte, caption, chars, text_max_w)
        text_x = largura // 2 - text_surf.get_width() // 2

        skip_tip = fonte_hint.render("Clique ou tecla para continuar", True, (120, 120, 120))
        skip_y = altura - 46

        # Reserva espaço para a linha da dica para evitar sobreposição.
        text_bottom_limit = skip_y - 14
        preferred_text_y = scene_rect.bottom + 26
        text_y = min(preferred_text_y, text_bottom_limit - text_surf.get_height())
        tela.blit(text_surf, (text_x, text_y))

        tela.blit(skip_tip, (largura // 2 - skip_tip.get_width() // 2, skip_y))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

        if completed and elapsed >= len(caption) * ms_por_char + hold_after_full_ms:
            done = True

    return "next"
