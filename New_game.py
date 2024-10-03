import pygame
from pygame.locals import *
from sys import exit
import random

pygame.init()

# Cores
GREEN_GRASS = (34, 139, 34)
BLUE_LIGHT = (0, 102, 204)
YELLOW = (255, 221, 51)
WHITE = (255, 255, 255)

# Tela
width = 1200
height = 875
tela = pygame.display.set_mode((width, height))
pygame.display.set_caption("Retro Game with Arara Player")
clock = pygame.time.Clock()

# Player (arara)
player_width = 40
player_height = 60
player_x = width // 2
player_y = height - player_height * 2
speed_player = 5
arara_image = pygame.image.load('assets/arara.png')
arara_image = pygame.transform.scale(arara_image, (player_width, player_height))

# Direção do jogador
facing_right = False  # A arara começa virada para a esquerda

# Mira
aim_width = 5
aim_height = 15
aim_x = player_x + (player_width // 2) - (aim_width // 2)
aim_y = player_y - aim_height

# Bala
bullet_size = 5
clicks = 0  # Controla a taxa de tiro
bullets = []

# Inimigos
enemy_size = 20
enemies = [[200, 150], [250, 150], [300, 100]]

# Paredes
walls = [
    (100, 100, 600, 20),  # Parede superior
    (100, 400, 600, 20),  # Parede inferior
    (100, 100, 20, 320),  # Parede esquerda
    (680, 100, 20, 320),  # Parede direita
]

# Carrega e redimensiona a imagem da árvore
tree_image = pygame.image.load('assets/tree.png')
tree_image = pygame.transform.scale(tree_image, (60, 80))  # Ajusta o tamanho da árvore

# Função para verificar se uma posição está longe o suficiente de outras árvores
def is_position_valid(x, y, positions, min_distance=80):
    for pos in positions:
        distance = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
        if distance < min_distance:
            return False
    return True

# Cria várias árvores em posições aleatórias para formar uma floresta, garantindo distância mínima
tree_positions = []
max_attempts = 1000  # Número máximo de tentativas para encontrar uma posição válida
while len(tree_positions) < 20:  # Queremos 20 árvores
    attempts = 0
    while attempts < max_attempts:
        x = random.randint(0, width - 60)
        y = random.randint(0, height - 80)
        if is_position_valid(x, y, tree_positions, min_distance=80):
            tree_positions.append((x, y))
            break
        attempts += 1

# Desenha o jogador (arara) usando imagem
def draw_player():
    if facing_right:
        arara = pygame.transform.flip(arara_image, True, False)
    else:
        arara = arara_image
    tela.blit(arara, (player_x, player_y))
    # Mira do jogador
    pygame.draw.rect(tela, YELLOW, (aim_x, aim_y, aim_width, aim_height))

# Desenha os inimigos
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(tela, YELLOW, (enemy[0], enemy[1], enemy_size, enemy_size))

# Desenha as paredes
def draw_walls():
    for wall in walls:
        pygame.draw.rect(tela, BLUE_LIGHT, wall)

# Desenha as balas
def draw_bullet(bullet):
    pygame.draw.circle(tela, WHITE, (bullet[0], bullet[1]), bullet_size)

# Desenha as árvores para formar a floresta
def draw_forest():
    for pos in tree_positions:
        tela.blit(tree_image, pos)

# Atualiza a posição das balas
def update_bullets():
    for bullet in bullets[:]:
        bullet[1] -= 10  # Move a bala para cima
        if bullet[1] < 0:  # Remove a bala se sair da tela
            bullets.remove(bullet)

# Loop principal do jogo
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                clicks = 0

    # Movimento do player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= speed_player
        facing_right = False
    if keys[pygame.K_RIGHT]:
        player_x += speed_player
        facing_right = True
    if keys[pygame.K_UP]:
        player_y -= speed_player
    if keys[pygame.K_DOWN]:
        player_y += speed_player
    if keys[pygame.K_SPACE]:
        if clicks <= 0:
            # Adiciona uma nova bala na posição da mira
            bullets.append([aim_x + aim_width // 2, aim_y])  # Posição da bala
            clicks += 1

    # Limites do jogador
    player_x = max(0, min(width - player_width, player_x))
    player_y = max(0, min(height - player_height, player_y))

    # Atualiza a mira
    aim_x = player_x + (player_width // 2) - (aim_width // 2)
    aim_y = player_y - aim_height

    # Limpa a tela com um tom de verde para representar grama
    tela.fill(GREEN_GRASS)

    # Desenha o cenário
    draw_forest()  # Desenha a floresta de fundo
    draw_walls()
    draw_enemies()
    draw_player()
    update_bullets()
    for bullet in bullets:
        draw_bullet(bullet)

    pygame.display.update()
