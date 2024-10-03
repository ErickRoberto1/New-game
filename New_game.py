import pygame
from pygame.locals import *
from sys import exit
import random

pygame.init()

# Cores
GREEN_GRASS = (34, 139, 34)  # Cor de fundo verde, semelhante à grama
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
player_y = height // 2
speed_player = 5
arara_image = pygame.image.load('assets/arara.png')
arara_image = pygame.transform.scale(arara_image, (player_width, player_height))

# Criar máscara para o jogador
player_mask = pygame.mask.from_surface(arara_image)

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

# Paredes ao redor das bordas da tela (todas brancas)
walls = [
    (0, 0, width, 20),
    (0, height - 20, width, 20),
    (0, 0, 20, height),
    (width - 20, 0, 20, height)
]

# Carrega e redimensiona a imagem da árvore
tree_image = pygame.image.load('assets/tree.png')
tree_image = pygame.transform.scale(tree_image, (60, 80))  # Ajusta o tamanho da árvore

# Criar máscara para a árvore
tree_mask = pygame.mask.from_surface(tree_image)

# Função para verificar se uma posição está longe o suficiente de outras árvores e do centro
def is_position_valid(x, y, positions, min_distance):
    # Distância mínima entre árvores (ajustada para o tamanho do jogador + 20 pixels)
    for pos in positions:
        if abs(x - pos[0]) < min_distance and abs(y - pos[1]) < min_distance:
            return False

    # Distância mínima do centro (para evitar sobreposição com o jogador)
    center_x, center_y = width // 2, height // 2
    distance_from_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
    if distance_from_center < 100:  # Raio seguro de 100 pixels ao redor do centro
        return False

    return True

# Cria várias árvores em posições aleatórias para formar uma floresta, garantindo distância mínima
tree_positions = []
max_attempts = 1000
min_distance_between_trees = player_height + 20

while len(tree_positions) < 15:
    attempts = 0
    while attempts < max_attempts:
        x = random.randint(20, width - 80)
        y = random.randint(20, height - 100)
        if is_position_valid(x, y, tree_positions, min_distance=min_distance_between_trees):
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
    pygame.draw.rect(tela, WHITE, (aim_x, aim_y, aim_width, aim_height))

# Desenha os inimigos
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(tela, WHITE, (enemy[0], enemy[1], enemy_size, enemy_size))

# Desenha as paredes ao redor da tela
def draw_walls():
    for wall in walls:
        pygame.draw.rect(tela, WHITE, wall)

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
    new_player_x = player_x
    new_player_y = player_y
    if keys[pygame.K_LEFT]:
        new_player_x -= speed_player
        facing_right = False
    if keys[pygame.K_RIGHT]:
        new_player_x += speed_player
        facing_right = True
    if keys[pygame.K_UP]:
        new_player_y -= speed_player
    if keys[pygame.K_DOWN]:
        new_player_y += speed_player

    # Limites do jogador para evitar sair da tela
    new_player_x = max(20, min(width - player_width - 20, new_player_x))
    new_player_y = max(20, min(height - player_height - 20, new_player_y))

    # Atualiza a mira
    aim_x = new_player_x + (player_width // 2) - (aim_width // 2)
    aim_y = new_player_y - aim_height

    # Verifica colisões com as árvores antes de atualizar a posição do jogador
    new_player_rect = pygame.Rect(new_player_x, new_player_y, player_width, player_height)
    collision = False

    for pos in tree_positions:
        tree_rect = pygame.Rect(pos[0], pos[1], 60, 80)

        # Calcular a posição relativa entre a árvore e o jogador
        offset_x = new_player_rect.left - tree_rect.left
        offset_y = new_player_rect.top - tree_rect.top

        # Verificar a colisão com máscaras
        if tree_mask.overlap(player_mask, (offset_x, offset_y)):
            collision = True
            break

    # Atualiza a posição do jogador apenas se não houver colisão
    if not collision:
        player_x = new_player_x
        player_y = new_player_y

    # Limpa a tela com um tom de verde para representar grama
    tela.fill(GREEN_GRASS)

    # Desenha o cenário
    draw_forest()
    draw_walls()
    draw_enemies()
    draw_player()
    update_bullets()
    for bullet in bullets:
        draw_bullet(bullet)

    # Disparar as balas
    if keys[pygame.K_SPACE] and clicks <= 0:
        # Adiciona uma nova bala na posição da mira
        bullets.append([aim_x + aim_width // 2, aim_y])  # Posição da bala
        clicks += 1

    pygame.display.update()
