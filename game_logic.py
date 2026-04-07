"""
game_logic.py — Núcleo do jogo: loop principal e orquestração da campanha.

Módulos de suporte:
  constants.py   — constantes partilhadas
  utils.py       — audio, fonts e helpers (inicializado aqui após pygame.init)
    entities.py    — Player, Obstaculo, Chuva
  screens.py     — ecrãs de UI (banner, menu, fim de campanha)
  level_boards   — boards entre níveis
  storyboard     — cenas de narrativa
  options_screen — ecrã de opções + estado de áudio
"""
import asyncio
import os
import random
import sys

import pygame

from constants import (
    LARGURA, ALTURA, BRANCO, PRETO, CINZA, VERMELHO,
    DURACAO_JOGO, PENALIDADE_COLISAO, PENALIDADE_DURACAO_FRAMES,
    LEVELS,
)
import utils
from entities import Player, Obstaculo, Chuva
from screens import (
    show_banner_screen,
    show_main_menu,
    show_placeholder_screen,
    show_campaign_end_screen,
)
from info_screen import show_info_screen
from level_boards import show_level_board
from storyboard import show_story_scene
from highscores import process_final_score
import options_screen
from options_screen import show_options_screen

# Garante paths relativos consistentes em .py, .exe one-folder e .exe one-file.
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)
elif getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Inicialização pygame
# ---------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()
tela  = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Corre, Rafa!")
clock = pygame.time.Clock()

utils.init()   # carrega sons, ícone, toggle marker e música


# ---------------------------------------------------------------------------
# Helpers de nível
# ---------------------------------------------------------------------------

def carregar_backgrounds(bg_file, sky_file):
    sky_image = pygame.image.load(os.path.join("assets", sky_file)).convert_alpha()
    sky_image = pygame.transform.scale(sky_image, (LARGURA, ALTURA))
    sky_width = sky_image.get_width()

    bg_image  = pygame.image.load(os.path.join("assets", bg_file)).convert_alpha()
    bg_image  = pygame.transform.scale(bg_image, (LARGURA, ALTURA))
    bg_width  = bg_image.get_width()
    return sky_image, sky_width, bg_image, bg_width


def resetar_jogo(initial_score=0):
    return Player(), [], [], 0, 6, initial_score, False, 0


# ---------------------------------------------------------------------------
# Loop principal de um nível
# ---------------------------------------------------------------------------

async def run_game(
    level_name,
    bg_file,
    sky_file,
    distance_target,
    spawn_range,
    starting_score=0,
    auto_advance_on_win=False,
    win_transition_text="A iniciar o proximo nivel...",
    quit_on_exit=True,
):
    pygame.display.set_caption(f"Corre, Rafa! | {level_name}")
    sky_image, sky_width, bg_image, bg_width = carregar_backgrounds(bg_file, sky_file)

    level_start_score = starting_score
    player, obstaculos, cinzas, timer_spawn, vel_jogo, pontos, game_over, penalidade_frames = (
        resetar_jogo(level_start_score)
    )
    distancia = 0.0

    chuva_ativa      = level_name in ("Level 2", "Level 3")
    tempestade_ativa = level_name == "Level 3"
    qtd_gotas        = 130 if tempestade_ativa else 85
    gotas_chuva      = [Chuva(tempestade=tempestade_ativa) for _ in range(qtd_gotas)] if chuva_ativa else []

    fonte        = pygame.font.SysFont("Arial", 22, bold=True)
    fonte_bonus  = pygame.font.SysFont("Arial", 26, bold=True)
    fonte_ui     = utils.carregar_fonte_arcade(24)
    fonte_grande = pygame.font.SysFont("Arial", 55, bold=True)

    alfabeto_dir = os.path.join("assets", "Alfabeto")
    if not os.path.isdir(alfabeto_dir):
        alfabeto_dir = os.path.join("assets", "alfabeto")
    fonte_png_vitoria = options_screen.ImageAlphabet.from_folder(alfabeto_dir)

    bg_x  = 0
    sky_x = 0

    start_time               = pygame.time.get_ticks()
    time_up                  = False
    won                      = False
    final_score              = 0
    bonus_tempo              = 0
    transicao_vitoria_inicio = None
    transicao_derrota_inicio = None
    flash_tempestade         = 0

    rodando = True
    while rodando:
        # 1. Parallax background
        tela.blit(sky_image, (sky_x, 0))
        tela.blit(sky_image, (sky_width + sky_x, 0))
        tela.blit(bg_image,  (bg_x, 0))
        tela.blit(bg_image,  (bg_width + bg_x, 0))

        if chuva_ativa:
            for gota in gotas_chuva:
                gota.atualizar()
                gota.desenhar(tela)

        if tempestade_ativa and flash_tempestade == 0 and random.random() < 0.004:
            flash_tempestade = random.randint(2, 4)

        if not game_over:
            sky_x -= vel_jogo * 0.2
            if sky_x <= -sky_width:
                sky_x = 0
            bg_x -= vel_jogo * 0.4
            if bg_x <= -bg_width:
                bg_x = 0

        # 2. Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                continue
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_SPACE, pygame.K_UP]:
                    if game_over:
                        if not (won and auto_advance_on_win):
                            player, obstaculos, cinzas, timer_spawn, vel_jogo, pontos, game_over, penalidade_frames = resetar_jogo(level_start_score)
                            distancia = 0.0
                            bg_x = sky_x = 0
                            start_time = pygame.time.get_ticks()
                            time_up = won = False
                            final_score = 0
                            bonus_tempo = 0
                            transicao_vitoria_inicio = None
                    else:
                        player.saltar()
                if evento.key == pygame.K_r and game_over and not (won and auto_advance_on_win):
                    player, obstaculos, cinzas, timer_spawn, vel_jogo, pontos, game_over, penalidade_frames = resetar_jogo(level_start_score)
                    distancia = 0.0
                    bg_x = sky_x = 0
                    start_time = pygame.time.get_ticks()
                    time_up = won = False
                    final_score = 0
                    bonus_tempo = 0
                    transicao_vitoria_inicio = None
            if evento.type == pygame.KEYUP:
                if evento.key in [pygame.K_SPACE, pygame.K_UP]:
                    player.cancelar_salto()

        # Verificar tempo / vitória
        elapsed   = (pygame.time.get_ticks() - start_time) / 1000
        remaining = max(0, DURACAO_JOGO - elapsed)
        if remaining <= 0 and not game_over:
            game_over = True
            time_up   = True
        if distancia >= distance_target and not game_over:
            game_over   = True
            won         = True
            bonus_tempo = int(remaining * 20)
            pontos     += bonus_tempo
            final_score = int(pontos)
            utils.tocar_som(utils.som_ending)

        # 3. Lógica de jogo
        if not game_over:
            teclas = pygame.key.get_pressed()
            player.baixar(teclas[pygame.K_DOWN])
            if teclas[pygame.K_RIGHT]:
                vel_jogo = min(15, vel_jogo + 0.2)
            elif teclas[pygame.K_LEFT]:
                vel_jogo = max(3, vel_jogo - 0.3)
            else:
                vel_jogo = max(5, vel_jogo - 0.1)

            if penalidade_frames > 0:
                penalidade_frames -= 1
                vel_jogo = max(3, vel_jogo - 0.15)

            player.atualizar(vel_jogo)

            ganho_movimento = vel_jogo * 0.12
            distancia += ganho_movimento
            pontos    += ganho_movimento

            timer_spawn += 1
            if timer_spawn > random.randint(spawn_range[0], spawn_range[1]):
                tipos_spawn = []
                if utils.asset_existe("dog.png"):           tipos_spawn.append("dog")
                if utils.asset_existe("box.png"):           tipos_spawn.append("box")
                if utils.asset_existe("granny-left_01.png"):  tipos_spawn.append("granny-left")
                if utils.asset_existe("granny-right_01.png"): tipos_spawn.append("granny-right")
                if utils.asset_existe("pidgeon_01.png"):    tipos_spawn.append("pidgeon")
                if utils.asset_existe("girl_01.png"):       tipos_spawn.append("girl")
                if tipos_spawn:
                    obstaculos.append(Obstaculo(random.choice(tipos_spawn)))
                timer_spawn = 0

            for obs in obstaculos[:]:
                obs.mover(vel_jogo)
                if player.hitbox.colliderect(obs.hitbox):
                    if player.sofrer_hit():
                        vel_jogo          = max(3, vel_jogo - PENALIDADE_COLISAO)
                        penalidade_frames = max(penalidade_frames, PENALIDADE_DURACAO_FRAMES)
                        pontos            = max(0, pontos - 20)
                        utils.tocar_som(utils.som_morte)
                        if obs in obstaculos:
                            obstaculos.remove(obs)
                        continue
                if obs.rect.right < 0:
                    obstaculos.remove(obs)
                    pontos += 20
                    utils.tocar_som(utils.som_ponto)
        else:
            player.atualizar(vel_jogo, morto=time_up, venceu=won)

        # 4. Desenho
        player.desenhar(tela)
        for obs in obstaculos:
            obs.desenhar(tela)

        if tempestade_ativa:
            sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            sombra.fill((18, 22, 34, 65))
            tela.blit(sombra, (0, 0))
            if flash_tempestade > 0:
                flash = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                flash.fill((220, 230, 255, 70))
                tela.blit(flash, (0, 0))
                flash_tempestade -= 1

        # Barra de progresso
        progresso = min(distancia / distance_target, 1.0)
        barra_w   = 620
        barra_h   = 24
        barra_x   = LARGURA // 2 - barra_w // 2
        barra_y   = 16
        raio      = barra_h // 2

        trilho_rect = pygame.Rect(barra_x, barra_y, barra_w, barra_h)
        pygame.draw.rect(tela, (34, 16, 16),  trilho_rect, border_radius=raio)
        pygame.draw.rect(tela, (110, 45, 45), trilho_rect, 2, border_radius=raio)

        fill_w = max(0, int((barra_w - 4) * progresso))
        if fill_w > 0:
            fill_rect = pygame.Rect(barra_x + 2, barra_y + 2, fill_w, barra_h - 4)
            fill_raio = max(2, (barra_h - 4) // 2)
            pygame.draw.rect(tela, (198, 56, 56), fill_rect, border_radius=fill_raio)

        if utils.TOGGLE_MARKER is not None:
            marcador_min_x = barra_x + 2
            marcador_max_x = barra_x + barra_w - 2
            marcador_cx    = int(marcador_min_x + (marcador_max_x - marcador_min_x) * progresso)
            marcador_x     = marcador_cx - utils.TOGGLE_MARKER.get_width() // 2
            marcador_y     = barra_y + barra_h // 2 - utils.TOGGLE_MARKER.get_height() // 2
            tela.blit(utils.TOGGLE_MARKER, (marcador_x, marcador_y))

        # HUD — Score e Time Remaining
        if tempestade_ativa:
            ui_cor_texto    = (255, 245, 170)
            ui_cor_contorno = (8,   12,  20)
        else:
            ui_cor_texto    = (255, 232, 120)
            ui_cor_contorno = (18,  32,  58)

        txt_score = utils.render_texto_pixel_bold(
            fonte_ui, f"SCORE: {int(pontos)}", ui_cor_texto, ui_cor_contorno,
        )
        txt_tempo = utils.render_texto_pixel_bold(
            fonte_ui, f"TIME REMAINING: {int(remaining)}", ui_cor_texto, ui_cor_contorno,
        )
        tela.blit(txt_score, (20, 18))
        tela.blit(txt_tempo, (LARGURA - txt_tempo.get_width() - 20, 18))

        # Mensagens de game over
        if game_over:
            if won:
                msg = fonte_grande.render(f"VENCEU! SCORE: {final_score}", True, (0, 255, 0))
                msg_bonus = fonte_bonus.render(f"Bonus de tempo: +{bonus_tempo}", True, (255, 235, 120))
                if auto_advance_on_win:
                    if transicao_vitoria_inicio is None:
                        transicao_vitoria_inicio = pygame.time.get_ticks()
                    msg_r = fonte.render(win_transition_text, True, BRANCO)
                    if pygame.time.get_ticks() - transicao_vitoria_inicio >= 1800:
                        if quit_on_exit:
                            pygame.quit()
                        return "won", pontos
                else:
                    msg_r = fonte.render("Pressione ESPAÇO ou R para Reiniciar", True, BRANCO)
            elif time_up:
                msg = fonte_grande.render("TEMPO ESGOTADO!", True, VERMELHO)
                if auto_advance_on_win:
                    if transicao_derrota_inicio is None:
                        transicao_derrota_inicio = pygame.time.get_ticks()
                    msg_r = fonte.render("A regressar ao menu...", True, BRANCO)
                    if pygame.time.get_ticks() - transicao_derrota_inicio >= 1500:
                        if quit_on_exit:
                            pygame.quit()
                        return "lost", pontos
                else:
                    msg_r = fonte.render("Pressione ESPAÇO ou R para Reiniciar", True, BRANCO)
            else:
                msg = fonte_grande.render("PERDEU!", True, VERMELHO)
                if auto_advance_on_win:
                    if transicao_derrota_inicio is None:
                        transicao_derrota_inicio = pygame.time.get_ticks()
                    msg_r = fonte.render("A regressar ao menu...", True, BRANCO)
                    if pygame.time.get_ticks() - transicao_derrota_inicio >= 1500:
                        if quit_on_exit:
                            pygame.quit()
                        return "lost", pontos
                else:
                    msg_r = fonte.render("Pressione ESPAÇO ou R para Reiniciar", True, BRANCO)
            tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, ALTURA // 2 - 72))
            if won:
                tela.blit(msg_bonus, (LARGURA // 2 - msg_bonus.get_width() // 2, ALTURA // 2 - 20))
                tela.blit(msg_r, (LARGURA // 2 - msg_r.get_width() // 2, ALTURA // 2 + 24))
            else:
                tela.blit(msg_r, (LARGURA // 2 - msg_r.get_width() // 2, ALTURA // 2 + 20))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    if quit_on_exit:
        pygame.quit()
    return "quit", pontos


# ---------------------------------------------------------------------------
# Campanha
# ---------------------------------------------------------------------------

async def run_campaign():
    await show_banner_screen(tela, clock)

    while True:
        action = await show_main_menu(tela, clock)
        if action == "quit":
            break

        elif action == "start":
            quit_requested = False
            campaign_score = 0

            utils.iniciar_musica_fundo_se_ativo()

            for idx, level in enumerate(LEVELS, start=1):
                scene_result = await show_story_scene(tela, clock, LARGURA, ALTURA, f"scene-{idx}.png")
                if scene_result == "quit":
                    quit_requested = True
                    break

                board_result = await show_level_board(tela, clock, LARGURA, ALTURA, idx)
                if board_result == "quit":
                    quit_requested = True
                    break

                utils.tocar_som(utils.som_begining)

                resultado, campaign_score = await run_game(
                    level["name"],
                    level["background"],
                    level["sky"],
                    level["distance_target"],
                    level["spawn_range"],
                    starting_score=campaign_score,
                    auto_advance_on_win=True,
                    win_transition_text=(
                        "A iniciar o proximo nivel..."
                        if idx < len(LEVELS)
                        else "Campanha concluida!"
                    ),
                    quit_on_exit=False,
                )
                if resultado == "quit":
                    quit_requested = True
                    break
                if resultado == "lost":
                    await show_story_scene(tela, clock, LARGURA, ALTURA, "scene-gameover.png")
                    quit_requested = True
                    break
            if quit_requested:
                break

            await show_story_scene(tela, clock, LARGURA, ALTURA, "scene-4.png")
            await show_campaign_end_screen(tela, clock)
            await process_final_score(tela, clock, LARGURA, ALTURA, int(campaign_score))

        elif action == "options":
            if await show_options_screen(tela, clock, LARGURA, ALTURA, BRANCO, CINZA, PRETO) == "quit":
                break

        elif action == "info":
            if await show_info_screen(tela, clock, LARGURA, ALTURA) == "quit":
                break

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(run_campaign())
