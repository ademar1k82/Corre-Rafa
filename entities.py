"""
entities.py — Classes de jogo: Player, Obstaculo, Chuva.
"""
import os
import random

import pygame

from constants import LARGURA, ALTURA, CHAO_Y, GRAVIDADE
import utils


class Player:
    def __init__(self):
        self.frames_corrida = [
            pygame.image.load(os.path.join("assets", f"run{i}.png")).convert_alpha()
            for i in [1, 2, 3, 4, 5]
        ]
        self.frames_salto = [
            pygame.image.load(os.path.join("assets", f"jump_0{i}.png")).convert_alpha()
            for i in [1, 2, 3, 4, 5]
        ]
        self.frames_baixo = [
            pygame.image.load(os.path.join("assets", f"crawl_0{i}.png")).convert_alpha()
            for i in [1, 2, 3, 4]
        ]
        self.frames_hit = [
            pygame.image.load(os.path.join("assets", f"hit_0{i}.png")).convert_alpha()
            for i in [1, 2, 3, 4]
        ]
        self.frames_die = [
            pygame.image.load(os.path.join("assets", f"die_0{i}.png")).convert_alpha()
            for i in [1, 2, 3, 4, 5]
        ]
        self.frames_win = [
            pygame.image.load(os.path.join("assets", f"win_0{i}.png")).convert_alpha()
            for i in [1, 2, 3, 4, 5]
        ]
        caminho_morto = os.path.join("assets", "morto.png")
        if os.path.exists(caminho_morto):
            self.img_morto = pygame.image.load(caminho_morto).convert_alpha()
        else:
            self.img_morto = self.frames_die[-1].copy()

        self.tamanho_normal   = (110, 140)
        self.tamanho_salto    = (110, 150)
        self.tamanho_hit      = (124, 140)
        self.tamanho_die      = (150, 170)
        self.tamanho_baixo    = (170, 90)

        self.frames_corrida = [pygame.transform.smoothscale(img, self.tamanho_normal)   for img in self.frames_corrida]
        self.frames_salto   = [pygame.transform.smoothscale(img, self.tamanho_salto)    for img in self.frames_salto]
        self.frames_baixo   = [pygame.transform.smoothscale(img, self.tamanho_baixo)    for img in self.frames_baixo]
        self.frames_hit     = [pygame.transform.smoothscale(img, self.tamanho_hit)      for img in self.frames_hit]
        self.frames_die     = [pygame.transform.smoothscale(img, self.tamanho_die)      for img in self.frames_die]
        self.frames_win     = [pygame.transform.smoothscale(img, self.tamanho_normal)   for img in self.frames_win]
        self.img_morto      = pygame.transform.smoothscale(self.img_morto, (132, 110))

        self.image  = self.frames_corrida[0]
        self.rect   = self.image.get_rect(topleft=(50, CHAO_Y - self.tamanho_normal[1]))
        self.hitbox = self.rect.inflate(-44, -26)

        self.vel_y             = 0
        self.no_chao           = True
        self.baixo             = False
        self.step_index        = 0.0
        self.salto_step_index  = 0.0
        self.hit_step_index    = 0.0
        self.die_step_index    = 0.0
        self.win_step_index    = 0.0
        self.hit_anim_timer    = 0
        self.hit_cooldown_timer = 0

    def saltar(self):
        if self.no_chao and not self.baixo:
            self.vel_y = -18
            self.no_chao = False
            self.salto_step_index = 0.0
            utils.tocar_som(utils.som_salto)

    def cancelar_salto(self):
        if self.vel_y < -10:
            self.vel_y = -10

    def baixar(self, apertou):
        self.baixo = apertou

    def sofrer_hit(self):
        if self.hit_cooldown_timer > 0:
            return False
        self.hit_anim_timer     = 30
        self.hit_step_index     = 0.0
        self.hit_cooldown_timer = 75
        return True

    def atualizar(self, velocidade_atual, morto=False, venceu=False):
        if venceu:
            self.win_step_index = min(self.win_step_index + 0.10, len(self.frames_win) - 1)
            self.image = self.frames_win[int(self.win_step_index)]
            self.rect.height = self.tamanho_normal[1]
            self.rect.bottom = CHAO_Y
            self.hitbox = self.rect.inflate(-34, -18)
            return

        if morto:
            self.die_step_index = min(self.die_step_index + 0.15, len(self.frames_die) - 1)
            self.image = self.frames_die[int(self.die_step_index)]
            self.rect.width  = self.tamanho_die[0]
            self.rect.height = self.tamanho_die[1]
            self.rect.bottom = CHAO_Y
            self.hitbox = self.rect.inflate(-34, -18)
            return

        self.die_step_index = 0.0
        self.win_step_index = 0.0

        self.vel_y += GRAVIDADE
        self.rect.y += self.vel_y
        if self.rect.bottom >= CHAO_Y:
            self.rect.bottom, self.vel_y, self.no_chao = CHAO_Y, 0, True
            self.salto_step_index = 0.0

        if self.hit_anim_timer > 0:
            self.hit_anim_timer -= 1
        if self.hit_cooldown_timer > 0:
            self.hit_cooldown_timer -= 1

        self.step_index += velocidade_atual * 0.015

        if self.hit_anim_timer > 0:
            self.hit_step_index = min(self.hit_step_index + 0.14, len(self.frames_hit) - 1)
            self.image = self.frames_hit[int(self.hit_step_index)]
            self.rect.height = self.tamanho_hit[1]
            self.rect.bottom = CHAO_Y
            self.hitbox = self.rect.inflate(-34, -18)
        elif not self.no_chao:
            self.salto_step_index = min(self.salto_step_index + 0.35, len(self.frames_salto) - 1)
            self.image = self.frames_salto[int(self.salto_step_index)]
            self.rect.height = self.tamanho_salto[1]
            self.hitbox = self.rect.inflate(-30, -20)
        elif self.baixo:
            indice = int(self.step_index) % len(self.frames_baixo)
            self.image = self.frames_baixo[indice]
            self.rect.height = self.tamanho_baixo[1]
            self.rect.bottom = CHAO_Y
            self.hitbox = self.rect.inflate(-20, -10)
        else:
            indice = int(self.step_index) % len(self.frames_corrida)
            self.image = self.frames_corrida[indice]
            self.rect.height = self.tamanho_normal[1]
            self.rect.bottom = CHAO_Y
            self.hitbox = self.rect.inflate(-40, -20)

    def desenhar(self, surface):
        surface.blit(self.image, self.rect)


class Obstaculo:
    def __init__(self, tipo):
        self.tipo = tipo
        self.step_index = 0

        if tipo == "dog":
            self.image = pygame.image.load(os.path.join("assets", "dog.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (78, 72))
            self.rect = self.image.get_rect(midbottom=(LARGURA + 100, CHAO_Y))
            self.hitbox_offset = (-25, -20)
            self.vel_propria = 0
        elif tipo == "box":
            self.image = pygame.image.load(os.path.join("assets", "box.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (90, 90))
            self.rect = self.image.get_rect(midbottom=(LARGURA + 100, CHAO_Y))
            self.hitbox_offset = (-10, -10)
            self.vel_propria = 0
        elif tipo in ("granny-left", "granny-right"):
            self.frames = [
                pygame.image.load(os.path.join("assets", f"{tipo}_0{i}.png")).convert_alpha()
                for i in [1, 2, 3, 4]
            ]
            self.frames = [pygame.transform.scale(img, (85, 105)) for img in self.frames]
            self.image = self.frames[0]
            self.rect = self.image.get_rect(midbottom=(LARGURA + 100, CHAO_Y))
            self.hitbox_offset = (-20, -15)
            self.vel_propria = 0
        elif tipo == "pidgeon":
            self.frames = [
                pygame.image.load(os.path.join("assets", f"pidgeon_0{i}.png")).convert_alpha()
                for i in [1, 2, 3]
            ]
            self.frames = [pygame.transform.scale(img, (90, 90)) for img in self.frames]
            self.image = self.frames[0]
            self.rect = self.image.get_rect(midbottom=(LARGURA + 100, CHAO_Y - 100))
            self.hitbox_offset = (-35, -45)
            self.vel_propria = 3
        elif tipo == "girl":
            self.frames = [
                pygame.image.load(os.path.join("assets", f"girl_0{i}.png")).convert_alpha()
                for i in [1, 2, 3, 4, 5]
            ]
            self.frames = [pygame.transform.scale(img, (85, 108)) for img in self.frames]
            self.image = self.frames[0]
            self.rect = self.image.get_rect(midbottom=(LARGURA + 100, CHAO_Y))
            self.hitbox_offset = (-18, -18)
            self.vel_propria = 0.7

        self.hitbox = self.rect.inflate(*self.hitbox_offset)

    def mover(self, vel):
        if self.tipo in ("dog", "box", "granny-left", "granny-right"):
            self.rect.x -= vel * 0.4
        else:
            self.rect.x -= (vel + self.vel_propria)

        if self.tipo == "pidgeon":
            self.step_index += 0.08
            if self.step_index >= len(self.frames):
                self.step_index = 0
            self.image = self.frames[int(self.step_index)]
        elif self.tipo == "girl":
            self.step_index += 0.08
            if self.step_index >= len(self.frames):
                self.step_index = 0
            self.image = self.frames[int(self.step_index)]
        elif self.tipo in ("granny-left", "granny-right"):
            self.step_index += 0.06
            if self.step_index >= len(self.frames):
                self.step_index = 0
            self.image = self.frames[int(self.step_index)]

        self.hitbox = self.rect.inflate(*self.hitbox_offset)

    def desenhar(self, surface):
        surface.blit(self.image, self.rect)


class Chuva:
    def __init__(self, tempestade=False):
        self.tempestade = tempestade
        self.reiniciar()

    def reiniciar(self):
        self.x = random.randint(0, LARGURA)
        self.y = random.randint(-ALTURA, 0)
        if self.tempestade:
            self.vel_x  = random.uniform(-1.8, 1.0)
            self.vel_y  = random.uniform(10.0, 18.0)
            self.tamanho = random.randint(10, 20)
        else:
            self.vel_x  = random.uniform(-1.0, 0.8)
            self.vel_y  = random.uniform(7.0, 13.0)
            self.tamanho = random.randint(8, 16)

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y > ALTURA + self.tamanho or self.x < -20 or self.x > LARGURA + 20:
            self.reiniciar()
            self.y = random.randint(-120, -10)

    def desenhar(self, surface):
        inicio = (int(self.x), int(self.y))
        fim    = (int(self.x + self.vel_x * 2), int(self.y + self.tamanho))
        cor       = (190, 225, 245) if self.tempestade else (173, 216, 230)
        espessura = 3               if self.tempestade else 2
        pygame.draw.line(surface, cor, inicio, fim, espessura)
