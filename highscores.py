import asyncio
import os
import sys

import pygame
import utils


if getattr(sys, "frozen", False):
    HIGHSCORE_FILE = os.path.join(os.path.dirname(sys.executable), "highscore.txt")
else:
    HIGHSCORE_FILE = "highscore.txt"
MAX_ENTRIES = 5


def _load_scores(path=HIGHSCORE_FILE):
    entries = []
    if not os.path.exists(path):
        return entries

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # Formato novo: nome,score
            if "," in line:
                parts = line.rsplit(",", 1)
                name = parts[0].strip() or "Jogador"
                try:
                    score = int(parts[1].strip())
                except ValueError:
                    continue
                entries.append({"name": name, "score": score})
                continue

            # Compatibilidade com formato antigo: só número
            try:
                score = int(line)
                entries.append({"name": "Jogador", "score": score})
            except ValueError:
                continue

    entries.sort(key=lambda e: e["score"], reverse=True)
    return entries[:MAX_ENTRIES]


def _save_scores(entries, path=HIGHSCORE_FILE):
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries[:MAX_ENTRIES]:
            f.write(f"{entry['name']},{int(entry['score'])}\n")


def _qualifies(score, entries):
    if len(entries) < MAX_ENTRIES:
        return True
    lowest = entries[-1]["score"]
    return score >= lowest


async def _ask_player_name(tela, clock, largura, altura, score):
    nome = ""
    fonte_titulo = utils.carregar_fonte_arcade(34)
    fonte = utils.carregar_fonte_arcade(28)
    fonte_hint = utils.carregar_fonte_arcade(20)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "Jogador"
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return nome.strip() or "Jogador"
                if evento.key == pygame.K_ESCAPE:
                    return "Jogador"
                if evento.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                else:
                    ch = evento.unicode
                    if ch and ch.isprintable() and len(nome) < 14:
                        nome += ch

        tela.fill((0, 0, 0))

        titulo = fonte_titulo.render("TOP 5 - NOVA PONTUACAO", True, (255, 235, 120))
        subtitulo = fonte.render(f"Pontuacao: {int(score)}", True, (220, 220, 220))
        prompt = fonte.render("Escreve o teu nome:", True, (255, 255, 255))
        entrada = fonte.render(nome or "_", True, (0, 255, 180))
        hint = fonte_hint.render("ENTER para confirmar", True, (170, 170, 170))

        tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, 90))
        tela.blit(subtitulo, (largura // 2 - subtitulo.get_width() // 2, 150))
        tela.blit(prompt, (largura // 2 - prompt.get_width() // 2, 230))
        tela.blit(entrada, (largura // 2 - entrada.get_width() // 2, 280))
        tela.blit(hint, (largura // 2 - hint.get_width() // 2, 345))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


async def _show_scoreboard(tela, clock, largura, altura, entries, destaque=None):
    fonte_titulo = utils.carregar_fonte_arcade(44)
    fonte_header = utils.carregar_fonte_arcade(32)
    fonte_linha = utils.carregar_fonte_arcade(26)
    fonte_hint = utils.carregar_fonte_arcade(20)

    col_gap = 320
    col_nome_cx = largura // 2 - col_gap // 2
    col_score_cx = largura // 2 + col_gap // 2
    y0 = 230
    row_h = 42

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return

        tela.fill((0, 0, 0))

        titulo = fonte_titulo.render("HALL OF FAME", True, (255, 235, 120))
        titulo_sombra = fonte_titulo.render("HALL OF FAME", True, (22, 26, 36))
        h_nome = fonte_header.render("Nome", True, (255, 255, 255))
        h_nome_sombra = fonte_header.render("Nome", True, (18, 22, 30))
        h_score = fonte_header.render("Pontuacao", True, (255, 255, 255))
        h_score_sombra = fonte_header.render("Pontuacao", True, (18, 22, 30))
        hint = fonte_hint.render("Pressiona qualquer tecla para continuar", True, (170, 170, 170))

        titulo_x = largura // 2 - titulo.get_width() // 2
        tela.blit(titulo_sombra, (titulo_x + 3, 94))
        tela.blit(titulo, (titulo_x, 90))

        nome_x = col_nome_cx - h_nome.get_width() // 2
        score_x = col_score_cx - h_score.get_width() // 2
        header_y = y0 - 52
        tela.blit(h_nome_sombra, (nome_x + 2, header_y + 2))
        tela.blit(h_nome, (nome_x, header_y))
        tela.blit(h_score_sombra, (score_x + 2, header_y + 2))
        tela.blit(h_score, (score_x, header_y))

        for i in range(MAX_ENTRIES):
            y = y0 + i * row_h
            if i < len(entries):
                nome = entries[i]["name"]
                score = str(int(entries[i]["score"]))
                cor = (0, 255, 180) if destaque == (entries[i]["name"], entries[i]["score"]) else (235, 235, 235)
            else:
                nome = "---"
                score = "---"
                cor = (110, 110, 110)

            n_txt = fonte_linha.render(nome, True, cor)
            s_txt = fonte_linha.render(score, True, cor)
            tela.blit(n_txt, (col_nome_cx - n_txt.get_width() // 2, y))
            tela.blit(s_txt, (col_score_cx - s_txt.get_width() // 2, y))

        tela.blit(hint, (largura // 2 - hint.get_width() // 2, altura - 55))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


async def process_final_score(tela, clock, largura, altura, final_score):
    score = int(final_score)
    entries = _load_scores()

    destaque = None
    if _qualifies(score, entries):
        nome = await _ask_player_name(tela, clock, largura, altura, score)
        entries.append({"name": nome, "score": score})
        entries.sort(key=lambda e: e["score"], reverse=True)
        entries = entries[:MAX_ENTRIES]
        _save_scores(entries)
        destaque = (nome, score)

    await _show_scoreboard(tela, clock, largura, altura, entries, destaque=destaque)
