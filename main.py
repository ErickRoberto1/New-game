import os
import pygame
from pygame.locals import *
from sys import exit
import random
import math

pygame.init()
pygame.mixer.init()

# Cores
GREEN_GRASS = (34, 139, 34)  # Cor de fundo verde, semelhante à grama
WHITE = (255, 255, 255)
BLUE_LIGHT = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Tela
width = 1200
height = 875
hud_height = 100
tela = pygame.display.set_mode((width, height))
pygame.display.set_caption("Retro Game with Arara Player")
clock = pygame.time.Clock()

# Music and soundeffects
sounds = 'assets/sounds'
pygame.mixer.music.load(os.path.join(sounds, 'backsoundtrackB.mp3'))
pygame.mixer.music.play(-1)
fire = pygame.mixer.Sound(os.path.join(sounds, 'fire_sound.wav'))

# Player (arara)
player_width = 40
player_height = 60
player_x = width // 2
player_y = height // 2
speed_player = 5
player_health = 20
arara_image = pygame.image.load('assets/images/arara.png')
arara_image = pygame.transform.scale(arara_image, (player_width, player_height))
player_mask = pygame.mask.from_surface(arara_image)
facing_right = False

# Ghost State
hit = False
blink_timer = 0
blink_interval = 100


# Background
background_image = pygame.image.load('assets/images/background.png')
background_image = pygame.transform.scale(background_image, (width, height))


# Mira
aim_width = 5
aim_height = 15
aim_x = player_x + (player_width // 2) - (aim_width // 2)
aim_y = player_y - aim_height
aim_direction = K_UP

# Bala do jogador (gota)
drop_image = pygame.image.load('assets/images/drop.png')
drop_image = pygame.transform.scale(drop_image, (20, 20))
bullet_speed = 10
clicks = 0
bullets = []


# Paredes ao redor das bordas da tela (todas brancas)
walls = [
    (0, 0, width, 20),
    (0, height - 20, width, 20),
    (0, 0, 20, height),
    (width - 20, 0, 20, height)
]

fire_frames = [
    pygame.transform.scale(pygame.image.load('assets/images/fire_1.png'), (60,60)),
    pygame.transform.scale(pygame.image.load('assets/images/fire_2.png'), (60,60)),
    pygame.transform.scale(pygame.image.load('assets/images/fire_3.png'), (60,60))
]
current_fire_frame = 0
frame_delay = 5
frame_counter = 0

tree_image = pygame.image.load('assets/images/tree.png')
tree_image = pygame.transform.scale(tree_image, (60, 80))
tree_mask = pygame.mask.from_surface(tree_image)
tree_bullets = []
tree_shoot_timer = 0

fireball_image = pygame.image.load('assets/images/fireball.png')
fireball_image = pygame.transform.scale(fireball_image, (20, 20))

#Variáveis do jogo
start_time = pygame.time.get_ticks()
current_phase = 1


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

# Carrega o background
def load_background():
    tela.blit(background_image, (0, 0))


def draw_hud(elapsed_time, player_health, current_phase):
    # Desenhar o fundo do HUD
    pygame.draw.rect(tela, BLACK, (0, 0, width, hud_height))

    # Fonte para o HUD
    font = pygame.font.Font(None, 36)

    # Texto do tempo de jogo
    time_text = font.render(f"Time: {elapsed_time // 1000}s", True, WHITE)
    tela.blit(time_text, (20, 10))

    # Texto da fase atual
    phase_text = font.render(f"Phase: {current_phase}", True, WHITE)
    tela.blit(phase_text, (width // 2 - 50, 10))

    # Texto da barra de vida
    health_bar_text = font.render(f"Health:", True, WHITE)
    tela.blit(health_bar_text, (20, 50))

    # Desenhar a barra de vida
    bar_width = 200
    bar_height = 20
    health_ratio = player_health / 10
    current_bar_width = bar_width * health_ratio

    pygame.draw.rect(tela, RED, (120, 55, bar_width, bar_height))
    pygame.draw.rect(tela, BLUE_LIGHT, (120, 55, current_bar_width, bar_height))

# Desenha o jogador (arara) usando imagem
def draw_player():
    global aim
    if not hit:
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

# Desenha as balas do jogador com a imagem da gota (sem ajuste de ângulo)
def draw_bullet(bullet):
    rect = drop_image.get_rect(center=(bullet[0], bullet[1]))
    tela.blit(drop_image, rect.topleft)

# Desenha as balas das árvores com a imagem da fireball e rotação ajustada
def draw_tree_bullet(tree_bullet):
    angle = math.degrees(math.atan2(-tree_bullet[3], tree_bullet[2])) + 180
    rotated_fireball = pygame.transform.rotate(fireball_image, angle)
    rect = rotated_fireball.get_rect(center=(tree_bullet[0], tree_bullet[1]))
    tela.blit(rotated_fireball, rect.topleft)

# Desenha as árvores e o fogo sobrepondo o topo de cada árvore
def draw_forest_with_fire():
    for i, pos in enumerate(tree_positions):
        # Desenhar a árvore
        tela.blit(tree_image, pos)
        if trees_on_fire[i]:
            fire_x = pos[0]
            fire_y = pos[1] - 20  # Ajuste para posicionar o fogo sobre a árvore
            tela.blit(fire_frames[current_fire_frame], (fire_x, fire_y))


# Desenha a barra de vida do jogador
def draw_health_bar():
    bar_width = 200
    bar_height = 20
    health_ratio = player_health / 10
    current_bar_width = bar_width * health_ratio

    pygame.draw.rect(tela, RED, (20, 20, bar_width, bar_height))
    pygame.draw.rect(tela, BLUE_LIGHT, (20, 20, current_bar_width, bar_height))


# Atualiza a posição das balas do jogador
def update_bullets():
    for bullet in bullets[:]:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        bullet_rect = pygame.Rect(bullet[0] - 10, bullet[1] - 10, 20, 20)

        # Verifica colisão da bala com árvores
        for i, pos in enumerate(tree_positions):
            tree_rect = pygame.Rect(pos[0], pos[1], 60, 80)

            if bullet_rect.colliderect(tree_rect):
                if trees_on_fire[i]:  # Se a árvore estiver pegando fogo
                    trees_on_fire[i] = False
                    bullets.remove(bullet)
                else:  # Se a árvore não estiver pegando fogo
                    # Refletir a bala
                    if bullet[2] != 0:  # Refletir horizontalmente
                        bullet[2] = -bullet[2]
                    if bullet[3] != 0:  # Refletir verticalmente
                        bullet[3] = -bullet[3]
                break  # Saia do loop após uma colisão

        if bullet[1] < 0 or bullet[1] > height or bullet[0] < 0 or bullet[0] > width:
            bullets.remove(bullet)

# Atualiza a posição das balas das árvores
def update_tree_bullets():
    global player_health, player_x, player_y, hit
    for tree_bullet in tree_bullets[:]:
        tree_bullet[0] += tree_bullet[2]
        tree_bullet[1] += tree_bullet[3]
        tree_bullet_rect = pygame.Rect(tree_bullet[0] - 10, tree_bullet[1] - 10, 20, 20)

        # Verificar colisão da bala com o jogador
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        if tree_bullet_rect.colliderect(player_rect) and not hit:
            hit = True
            tree_bullets.remove(tree_bullet)
            pygame.mixer.Sound.play(fire)
            pygame.mixer.Sound.fadeout(fire,2000)
            if hit:
                player_health -= 1
            if player_health <= 0:
                # Reiniciar o jogo quando a vida do jogador for 0
                player_x = width // 2
                player_y = height // 2
                player_health = 10
                bullets.clear()
                tree_bullets.clear()
                trees_on_fire[:] = [True] * len(trees_on_fire)
                break

        if tree_bullet[0] < 0 or tree_bullet[0] > width or tree_bullet[1] < 0 or tree_bullet[1] > height:
            tree_bullets.remove(tree_bullet)


# Loop principal do jogo
while True:
    clock.tick(60)
    elapsed_time = pygame.time.get_ticks() - start_time
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

    frame_counter += 1
    if frame_counter >= frame_delay:
        frame_counter = 0
        current_fire_frame = (current_fire_frame + 1) % len(fire_frames)

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
        offset_x = new_player_rect.left - tree_rect.left
        offset_y = new_player_rect.top - tree_rect.top
        if tree_mask.overlap(player_mask, (offset_x, offset_y)):
            collision = True
            break


    if not collision:
        player_x = new_player_x
        player_y = new_player_y

    tree_shoot_timer += clock.get_time()
    if tree_shoot_timer >= 4000:
        tree_shoot_timer = 0
        for i, pos in enumerate(tree_positions):
            if trees_on_fire[i]:
                direction_x = player_x - pos[0]
                direction_y = player_y - pos[1]
                distance = math.hypot(direction_x, direction_y)
                if distance != 0:
                    direction_x /= distance
                    direction_y /= distance
                bullet_speed = 4
                direction_x *= bullet_speed
                direction_y *= bullet_speed
                tree_bullets.append([pos[0] + 30, pos[1] + 40, direction_x, direction_y])

    tela.fill(GREEN_GRASS)
    load_background()
    draw_forest_with_fire()
    draw_walls()
    draw_player()
    draw_health_bar()
    draw_hud(elapsed_time, player_health, current_phase)
    update_bullets()
    for bullet in bullets:
        draw_bullet(bullet)
    update_tree_bullets()
    for tree_bullet in tree_bullets:
        draw_tree_bullet(tree_bullet)

    if keys[pygame.K_SPACE] and clicks <= 0:
        direction_x, direction_y = 0, 0
        if aim_direction == K_RIGHT:
            direction_x = bullet_speed
        elif aim_direction == K_LEFT:
            direction_x = -bullet_speed
        elif aim_direction == K_UP:
            direction_y = -bullet_speed
        elif aim_direction == K_DOWN:
            direction_y = bullet_speed
        bullets.append([aim.x,aim.y, direction_x, direction_y])
        clicks += 1

    blink_timer += clock.get_time()
    if blink_timer >= blink_interval:
        hit = False
        blink_timer = 0
    pygame.display.update()
