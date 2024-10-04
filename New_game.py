import pygame
from pygame.locals import *
from sys import exit
import random
import math

pygame.init()

# Cores
GREEN_GRASS = (34, 139, 34)  # Cor de fundo verde, semelhante à grama
WHITE = (255, 255, 255)
BLUE_LIGHT = (0, 0, 255)

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
aim_direction = K_UP

# Bala do jogador (gota)
bullet_speed = 10
clicks = 0  # Controla a taxa de tiro
bullets = []

# Carrega e redimensiona a imagem da gota
drop_image = pygame.image.load('assets/drop.png')
drop_image = pygame.transform.scale(drop_image, (20, 20))  # Ajusta o tamanho da gota

# Balas das árvores
tree_bullets = []

# Timer para disparos das arvores
tree_shoot_timer = 0

# Paredes ao redor das bordas da tela (todas brancas)
walls = [
    (0, 0, width, 20),
    (0, height - 20, width, 20),
    (0, 0, 20, height),
    (width - 20, 0, 20, height)
]

# Carrega e redimensiona a imagem do fogo
fire_image = pygame.image.load('assets/fire.png')
fire_image = pygame.transform.scale(fire_image, (60, 60))  # Ajusta o tamanho do fogo

# Carrega e redimensiona a imagem da árvore
tree_image = pygame.image.load('assets/tree.png')
tree_image = pygame.transform.scale(tree_image, (60, 80))  # Ajusta o tamanho da árvore

# Carrega e redimensiona a imagem do lago
lake_image = pygame.image.load('assets/lake.png')
lake_image = pygame.transform.scale(lake_image, (100, 100))  # Ajusta o tamanho do lago

# Carrega e redimensiona a imagem da fireball
fireball_image = pygame.image.load('assets/fireball.png')
fireball_image = pygame.transform.scale(fireball_image, (20, 20))  # Ajusta o tamanho da fireball

# Criar máscara para a árvore e o lago
tree_mask = pygame.mask.from_surface(tree_image)
lake_mask = pygame.mask.from_surface(lake_image)

# Função para verificar se uma posição está longe o suficiente de outras árvores e do centro
def is_position_valid(x, y, positions, min_distance):
    for pos in positions:
        if abs(x - pos[0]) < min_distance and abs(y - pos[1]) < min_distance:
            return False

    center_x, center_y = width // 2, height // 2
    distance_from_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
    if distance_from_center < 100:
        return False

    return True

# Cria várias árvores em posições aleatórias para formar uma floresta, garantindo distância mínima
tree_positions = []
trees_on_fire = []  # Lista que indica quais árvores estão pegando fogo
max_attempts = 1000
min_distance_between_trees = player_height + 20

while len(tree_positions) < 19:
    attempts = 0
    while attempts < max_attempts:
        x = random.randint(100, width - 140)
        y = random.randint(100, height - 160)
        if is_position_valid(x, y, tree_positions, min_distance=min_distance_between_trees):
            tree_positions.append((x, y))
            trees_on_fire.append(True)  # Todas as árvores começam pegando fogo
            break
        attempts += 1

# Cria lagos em posições aleatórias garantindo que não colidam com árvores
lake_positions = []
while len(lake_positions) < 3:
    attempts = 0
    while attempts < max_attempts:
        x = random.randint(20, width - 120)
        y = random.randint(20, height - 120)
        # Garantir que os lagos não estejam na mesma posição das árvores
        if is_position_valid(x, y, tree_positions, min_distance=150) and is_position_valid(x, y, lake_positions, min_distance=150):
            lake_positions.append((x, y))
            break
        attempts += 1

# Desenha o jogador (arara) usando imagem
def draw_player():
    global aim
    if facing_right:
        arara = pygame.transform.flip(arara_image, True, False)
    else:
        arara = arara_image
    tela.blit(arara, (player_x, player_y))
    # Mira do jogador
    if aim_direction == K_RIGHT:
        aim = pygame.draw.rect(tela, WHITE, (player_x + 35, player_y + 20, aim_height, aim_width))
    elif aim_direction == K_LEFT:
        aim = pygame.draw.rect(tela, WHITE, (player_x - 15, player_y + 20, aim_height, aim_width))
    elif aim_direction == K_UP:
        aim = pygame.draw.rect(tela, WHITE, (aim_x, aim_y, aim_width, aim_height))
    elif aim_direction == K_DOWN:
        aim = pygame.draw.rect(tela, WHITE, (aim_x, aim_y + player_height, aim_width, aim_height))

# Desenha as paredes ao redor da tela
def draw_walls():
    for wall in walls:
        pygame.draw.rect(tela, WHITE, wall)

# Desenha as balas do jogador com a imagem da gota e rotação ajustada
def draw_bullet(bullet):
    # Calcula o ângulo da direção do movimento para rotacionar a gota
    angle = math.degrees(math.atan2(-bullet[3], bullet[2]))
    # Ajusta a rotação da gota em 180 graus para que a ponta esteja sempre apontando para a direção correta
    angle += 180
    rotated_drop = pygame.transform.rotate(drop_image, angle)
    rect = rotated_drop.get_rect(center=(bullet[0], bullet[1]))
    tela.blit(rotated_drop, rect.topleft)

# Desenha as balas das árvores com a imagem da fireball e rotação ajustada
def draw_tree_bullet(tree_bullet):
    # Calcula o ângulo da direção do movimento para rotacionar a fireball
    angle = math.degrees(math.atan2(-tree_bullet[3], tree_bullet[2])) + 180  # O sinal negativo é para ajustar o eixo Y invertido do Pygame, e +180 para inverter
    rotated_fireball = pygame.transform.rotate(fireball_image, angle)
    rect = rotated_fireball.get_rect(center=(tree_bullet[0], tree_bullet[1]))
    tela.blit(rotated_fireball, rect.topleft)

# Desenha as árvores e o fogo sobrepondo o topo de cada árvore
def draw_forest_with_fire():
    for i, pos in enumerate(tree_positions):
        tela.blit(tree_image, pos)  # Desenha a árvore
        if trees_on_fire[i]:
            fire_x = pos[0]
            fire_y = pos[1] - 20  # Posiciona o fogo para sobrepor o topo da árvore
            tela.blit(fire_image, (fire_x, fire_y))  # Desenha o fogo sobre as folhas da árvore

# Desenha os lagos
def draw_lakes():
    for pos in lake_positions:
        tela.blit(lake_image, pos)

# Atualiza a posição das balas do jogador
def update_bullets():
    for bullet in bullets[:]:
        bullet[0] += bullet[2]  # Atualiza posição x com a direção x
        bullet[1] += bullet[3]  # Atualiza posição y com a direção y

        bullet_rect = pygame.Rect(bullet[0] - 10, bullet[1] - 10, 20, 20)  # Tamanho da gota

        # Verifica colisão da bala com árvores
        for i, pos in enumerate(tree_positions):
            tree_rect = pygame.Rect(pos[0], pos[1], 60, 80)

            if bullet_rect.colliderect(tree_rect) and trees_on_fire[i]:
                # Se houver colisão e a árvore estiver pegando fogo, apagar o fogo
                trees_on_fire[i] = False
                bullets.remove(bullet)
                break

        # Remove a bala se sair da tela
        if bullet[1] < 0 or bullet[1] > height or bullet[0] < 0 or bullet[0] > width:  # Remove a bala se sair da tela
            bullets.remove(bullet)

# Atualiza a posição das balas das árvores
def update_tree_bullets():
    for tree_bullet in tree_bullets[:]:
        tree_bullet[0] += tree_bullet[2]  # Atualiza posição x com a direção x
        tree_bullet[1] += tree_bullet[3]  # Atualiza posição y com a direção y
        # Remove a bala se sair da tela
        if tree_bullet[0] < 0 or tree_bullet[0] > width or tree_bullet[1] < 0 or tree_bullet[1] > height:
            tree_bullets.remove(tree_bullet)

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
            if event.key in [K_DOWN, K_UP, K_RIGHT, K_LEFT]:
                aim_direction = event.key

    # Movimento do player
    keys = pygame.key.get_pressed()
    new_player_x = player_x
    new_player_y = player_y
    if keys[pygame.K_a]:
        new_player_x -= speed_player
        facing_right = False
    if keys[pygame.K_d]:
        new_player_x += speed_player
        facing_right = True
    if keys[pygame.K_w]:
        new_player_y -= speed_player
    if keys[pygame.K_s]:
        new_player_y += speed_player

    # Limites do jogador para evitar sair da tela
    new_player_x = max(20, min(width - player_width - 20, new_player_x))
    new_player_y = max(20, min(height - player_height - 20, new_player_y))

    # Atualiza a mira
    aim_x = new_player_x + (player_width // 2) - (aim_width // 2)
    aim_y = new_player_y - aim_height

    # Verifica colisões com as árvores e lagos antes de atualizar a posição do jogador
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

    for pos in lake_positions:
        lake_rect = pygame.Rect(pos[0], pos[1], 100, 100)
        # Calcular a posição relativa entre o lago e o jogador
        offset_x = new_player_rect.left - lake_rect.left
        offset_y = new_player_rect.top - lake_rect.top
        # Verificar a colisão com máscaras
        if lake_mask.overlap(player_mask, (offset_x, offset_y)):
            collision = True
            break

    # Atualiza a posição do jogador apenas se não houver colisão
    if not collision:
        player_x = new_player_x
        player_y = new_player_y

    # Atualiza o timer de disparo das árvores
    tree_shoot_timer += clock.get_time()
    if tree_shoot_timer >= 4000:  # 4 segundos
        tree_shoot_timer = 0
        for i, pos in enumerate(tree_positions):
            if trees_on_fire[i]:  # Só árvores em chamas disparam
                # Calcular a direção do tiro
                direction_x = player_x - pos[0]
                direction_y = player_y - pos[1]
                distance = math.hypot(direction_x, direction_y)
                if distance != 0:
                    direction_x /= distance
                    direction_y /= distance

                # Multiplicar pela velocidade da bala
                bullet_speed = 4
                direction_x *= bullet_speed
                direction_y *= bullet_speed

                # Adicionar bala das árvores
                tree_bullets.append([pos[0] + 30, pos[1] + 40, direction_x, direction_y])

    # Limpa a tela com um tom de verde para representar grama
    tela.fill(GREEN_GRASS)

    # Desenha o cenário
    draw_forest_with_fire()  # Desenha as árvores com fogo sobrepondo o topo, se ainda estiverem pegando fogo
    draw_lakes()  # Desenha os lagos
    draw_walls()  # Desenha as paredes brancas ao redor do cenário
    draw_player()  # Desenha o jogador
    update_bullets()  # Atualiza e desenha as balas do jogador
    for bullet in bullets:
        draw_bullet(bullet)
    update_tree_bullets()  # Atualiza e desenha as balas das árvores
    for tree_bullet in tree_bullets:
        draw_tree_bullet(tree_bullet)

    # Disparar as balas do jogador
    if keys[pygame.K_SPACE] and clicks <= 0:
        # Determinar a direção do disparo
        direction_x, direction_y = 0, 0
        if aim_direction == K_RIGHT:
            direction_x = bullet_speed
        elif aim_direction == K_LEFT:
            direction_x = -bullet_speed
        elif aim_direction == K_UP:
            direction_y = -bullet_speed
        elif aim_direction == K_DOWN:
            direction_y = bullet_speed

        bullets.append([aim.x, aim.y, direction_x, direction_y])  # Adiciona uma nova bala com direção
        clicks += 1

    pygame.display.update()
