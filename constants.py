LARGURA, ALTURA = 1200, 600
GRAVIDADE = 0.8
CHAO_Y = ALTURA - 100

DURACAO_JOGO = 60          # segundos para time trial
DISTANCIA_OBJETIVO = 3000  # distância base (substituída por LEVELS)
PENALIDADE_COLISAO = 4.5
PENALIDADE_DURACAO_FRAMES = 180

BRANCO  = (255, 255, 255)
PRETO   = (0,   0,   0)
CINZA   = (127, 140, 141)
VERMELHO = (231, 76,  60)

LEVELS = [
    {
        "name": "Level 1",
        "background": "background-stage1.png",
        "sky": "sky.png",
        "distance_target": 3000,
        "spawn_range": (80, 140),
    },
    {
        "name": "Level 2",
        "background": "background-stage2.png",
        "sky": "sky-2.png",
        "distance_target": 4500,
        "spawn_range": (65, 120),
    },
    {
        "name": "Level 3",
        "background": "background-stage3.png",
        "sky": "sky-3.png",
        "distance_target": 6000,
        "spawn_range": (60, 110),
    },
]
