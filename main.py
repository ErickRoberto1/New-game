import os
import pygame
from pygame.locals import *
from sys import exit
import random
import math


pygame.init()
pygame.mixer.init()

# Cores
GREEN_GRASS = (34, 139, 34)
WHITE = (255, 255, 255)
BLUE_LIGHT = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# Tela
width = 1200
height = 875
hud_height = 100
tela = pygame.display.set_mode((width, height))
pygame.display.set_caption("Retro Game with Arara Player")
clock = pygame.time.Clock()

# Music and sound effects
sounds = 'assets/sounds'


# função com o som do jogo
def sound_game() :
    pygame.mixer.music.load(os.path.join(sounds, 'backsoundtrackB.mp3'))
    pygame.mixer.music.play(-1, 0.0, 3000)

pygame.mixer.music.set_volume(0.7)
fire = pygame.mixer.Sound(os.path.join(sounds, 'fire_sound.wav'))
bullet_sound = pygame.mixer.Sound(os.path.join(sounds, 'bullet_sound.mp3'))
fire_extinguish = pygame.mixer.Sound(os.path.join(sounds, 'fire_extinguish.mp3'))

# Player (arara)
player_width = 40
player_height = 60
player_x = width // 2
player_y = height // 2
speed_player = 5
player_health = 15
arara_image = pygame.image.load('assets/images/arara.png')
arara_image = pygame.transform.scale(arara_image, (player_width, player_height))
player_mask = pygame.mask.from_surface(arara_image)
facing_right = False

# Ghost State
hit = False
blink_timer = 0
blink_interval = 100

# Fontes
title_font_path = os.path.join('assets/fonts', 'Gorditas-Regular.ttf')
title_size = 74
title_font = pygame.font.Font(title_font_path, title_size)

secondary_font_path = os.path.join('assets/fonts', 'PressStart2P-Regular.ttf')
secondary_size = 26
secondary_font = pygame.font.Font(secondary_font_path, secondary_size)

# Background
background_image = pygame.image.load('assets/images/background.png')
background_image = pygame.transform.scale(background_image, (width, height))

heart_image = pygame.image.load('assets/images/heart.png')
heart_image = pygame.transform.scale(heart_image, (40, 40))

# Mira
aim_width = 2
aim_height = 15
aim_x = player_x + (player_width // 2) - (aim_width // 2)
aim_y = player_y - aim_height
aim_direction = K_UP

# Bala do jogador (gota)
drop_image = pygame.image.load('assets/images/drop.png')
drop_image = pygame.transform.scale(drop_image, (20, 20))
bullet_speed = 5
clicks = 0
bullets = []

# Mira do jogador
aim_image = pygame.image.load('assets/images/water_gun.png')
aim_image = pygame.transform.scale(aim_image, (50, 50))

# Paredes ao redor das bordas da tela (todas brancas)
walls = [
    (0, 0, width, 20),
    (0, height - 20, width, 20),
    (0, 0, 20, height),
    (width - 20, 0, 20, height)
]

fire_frames = [
    pygame.transform.scale(pygame.image.load('assets/images/fire_1.png'), (60, 60)),
    pygame.transform.scale(pygame.image.load('assets/images/fire_2.png'), (60, 60)),
    pygame.transform.scale(pygame.image.load('assets/images/fire_3.png'), (60, 60))
]
current_fire_frame = 0
frame_delay = 5
frame_counter = 0

tree_image = pygame.image.load('assets/images/tree.png')
tree_image = pygame.transform.scale(tree_image, (60, 80))
tree_mask = pygame.mask.from_surface(tree_image)
tree_bullets = []
tree_shoot_timer = 0
tree_bullet_speed = 0

fireball_image = pygame.image.load('assets/images/fireball.png')
fireball_image = pygame.transform.scale(fireball_image, (20, 20))

# Variáveis do jogo
start_time = pygame.time.get_ticks()
current_phase = 1
tree_quantity = 5
shoot_timer = 5000
score = 0
points = 5
tries = 3
stop = False
elapsed_time = 0

# Função para verificar se uma posição está longe o suficiente de outras árvores e do centro
def is_position_valid(x, y, positions, min_distance) :
    for pos in positions :
        if abs(x - pos[0]) < min_distance and abs(y - pos[1]) < min_distance :
            return False

    center_x, center_y = width // 2, height // 2
    distance_from_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
    if distance_from_center < 100 :
        return False

    return True


# Cria várias árvores em posições aleatórias para formar uma floresta, garantindo distância mínima
tree_positions = []
trees_on_fire = []
max_attempts = 1000
min_distance_between_trees = player_height + 20


# função que cria as árvores
def create_trees() :
    global tree_positions, trees_on_fire, tree_quantity, shoot_timer, stop
    if current_phase == 1 or stop:
        tree_positions = []
        trees_on_fire = []
        tree_quantity = 5
    elif current_phase > current_phase - 1 and not stop:
        tree_quantity += 2
        shoot_timer -= 300

    while len(tree_positions) < tree_quantity :
        attempts = 0
        while attempts < max_attempts :
            x = random.randint(100, width - 140)
            y = random.randint(100, height - 160)
            if is_position_valid(x, y, tree_positions, min_distance=min_distance_between_trees) :
                tree_positions.append((x, y))
                trees_on_fire.append(True)
                break
            attempts += 1


# reinicia o estado das árvores para a próxima fase
def reset_trees() :
    global trees_on_fire, tree_positions
    trees_on_fire = []
    trees_on_fire[:] = [True] * len(trees_on_fire)
    tree_positions = []
    create_trees()


# Carrega o background
def load_background() :
    tela.blit(background_image, (0, 0))


def draw_hud(elapsed_time, player_health, current_phase) :
    global stop
    pygame.draw.rect(tela, BLACK, (0, 0, width, hud_height))
    font = pygame.font.Font(None, 36)

    time_text = font.render(f"TIME: {elapsed_time // 100}s", True, WHITE)
    tela.blit(time_text, (20, 10))

    phase_text = font.render(f"LEVEL: {current_phase}", True, WHITE)
    tela.blit(phase_text, (width // 2 - 50, 10))

    tries_text = font.render(f"TRIES: {tries}", True, WHITE)
    tela.blit(tries_text, (width // 2 - 50, 50))

    score_text = font.render(f"SCORE: {score}", True, WHITE)
    tela.blit(score_text, (width - 200, 10))

    tela.blit(heart_image, (20, 50))

    # Desenhar a barra de vida
    bar_x = 70
    bar_y = 60
    bar_width = 200
    bar_height = 20
    pixel_size = 4
    health_ratio = player_health / 15
    current_bar_width = bar_width * health_ratio

    if health_ratio > 0.6 :
        bar_color = GREEN
    elif health_ratio > 0.3 :
        bar_color = ORANGE
    else :
        bar_color = RED

    pygame.draw.rect(tela, WHITE, (bar_x, bar_y, bar_width, bar_height))

    for i in range(0, bar_height // 2, pixel_size) :
        pygame.draw.rect(tela, WHITE, (bar_x - i, bar_y + i, pixel_size, pixel_size))
        pygame.draw.rect(tela, WHITE, (bar_x + bar_width - pixel_size + i, bar_y + i, pixel_size, pixel_size))
        pygame.draw.rect(tela, WHITE, (bar_x - i, bar_y + bar_height - pixel_size - i, pixel_size, pixel_size))
        pygame.draw.rect(tela, WHITE, (
            bar_x + bar_width - pixel_size + i, bar_y + bar_height - pixel_size - i, pixel_size, pixel_size))

        # Desenhar a barra de vida atual com aparência pixelada
    if current_bar_width > 0 :
        pygame.draw.rect(tela, bar_color, (bar_x, bar_y, current_bar_width, bar_height))

        # Bordas arredondadas pixeladas da barra de vida atual
        for i in range(0, bar_height // 2, pixel_size) :
            if current_bar_width > i :
                pygame.draw.rect(tela, bar_color, (bar_x - i, bar_y + i, pixel_size, pixel_size))
                pygame.draw.rect(tela, bar_color, (
                    bar_x + min(current_bar_width, bar_width) - pixel_size + i, bar_y + i, pixel_size, pixel_size))
                pygame.draw.rect(tela, bar_color,
                                 (bar_x - i, bar_y + bar_height - pixel_size - i, pixel_size, pixel_size))
                pygame.draw.rect(tela, bar_color, (
                    bar_x + min(current_bar_width, bar_width) - pixel_size + i, bar_y + bar_height - pixel_size - i,
                    pixel_size, pixel_size))


# Desenha o jogador (arara) usando imagem
def draw_player() :
    global aim, player_rect
    if not hit :
        if facing_right :
            arara = pygame.transform.flip(arara_image, True, False)
        else :
            arara = arara_image
        tela.blit(arara, (player_x, player_y))

    # Obtém o retângulo delimitador da máscara do jogador (arara)
    player_rect = player_mask.get_bounding_rects()[0]

    # Atualiza a posição da mira do jogador com base na posição do jogador e distância padronizada
    if aim_direction == K_RIGHT :
        aim_pos = (player_x + player_width + 10,
                   player_y + player_height // 4)
        rotated_aim = pygame.transform.rotate(aim_image, 0)  # Sem rotação
        aim = pygame.draw.rect(tela, WHITE, (player_x + 84, player_y + 42, aim_height, aim_width))
    elif aim_direction == K_LEFT :
        aim_pos = (player_x - aim_image.get_width() - 10, player_y + player_height // 4)
        rotated_aim = pygame.transform.flip(aim_image, True, False)
        aim = pygame.draw.rect(tela, WHITE, (player_x - 58, player_y + 42, aim_height, aim_width))
    elif aim_direction == K_UP :
        aim_pos = (
            player_x + player_width // 2 - aim_image.get_width() // 2, player_y - aim_image.get_height() - 10)
        rotated_aim = pygame.transform.rotate(aim_image, 90)
        aim = pygame.draw.rect(tela, WHITE, (aim_x + 3, aim_y - 45, aim_width, aim_height))
    elif aim_direction == K_DOWN :
        aim_pos = (
            player_x + player_width // 2 - aim_image.get_width() // 2, player_y + player_height + 10)
        rotated_aim = pygame.transform.rotate(aim_image, -90)
        aim = pygame.draw.rect(tela, WHITE, (aim_x - 3, aim_y + player_height + 58, aim_width, aim_height))

    # Desenha a mira (arma) na tela
    tela.blit(rotated_aim, aim_pos)


# Desenha as paredes ao redor da tela
def draw_walls() :
    for wall in walls :
        pygame.draw.rect(tela, BLACK, wall)


# Desenha as balas do jogador com a imagem da gota (sem ajuste de ângulo)
def draw_bullet(bullet) :
    rect = drop_image.get_rect(center=(bullet[0], bullet[1]))
    tela.blit(drop_image, rect.topleft)


# Desenha as balas das árvores com a imagem da fireball e rotação ajustada
def draw_tree_bullet(tree_bullet) :
    angle = math.degrees(math.atan2(-tree_bullet[3], tree_bullet[2])) + 180
    rotated_fireball = pygame.transform.rotate(fireball_image, angle)
    rect = rotated_fireball.get_rect(center=(tree_bullet[0], tree_bullet[1]))
    tela.blit(rotated_fireball, rect.topleft)


# Desenha as árvores e o fogo sobrepondo o topo de cada árvore
def draw_forest_with_fire() :
    for i, pos in enumerate(tree_positions) :
        # Desenhar a árvore
        tela.blit(tree_image, pos)
        if trees_on_fire[i] :
            fire_x = pos[0]
            fire_y = pos[1] - 20
            tela.blit(fire_frames[current_fire_frame], (fire_x, fire_y))


# Desenha a barra de vida do jogador
def draw_health_bar() :
    bar_width = 200
    bar_height = 20
    health_ratio = player_health / 10
    current_bar_width = bar_width * health_ratio

    pygame.draw.rect(tela, RED, (20, 20, bar_width, bar_height))
    pygame.draw.rect(tela, BLUE_LIGHT, (20, 20, current_bar_width, bar_height))


def update_bullets() :
    global score, points
    for bullet in bullets[:] :
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]
        bullet_rect = pygame.Rect(bullet[0] - 10, bullet[1] - 10, 20, 20)

        # Verifica colisão da bala com árvores
        for i, pos in enumerate(tree_positions) :
            tree_rect = pygame.Rect(pos[0], pos[1], 60, 80)

            if bullet_rect.colliderect(tree_rect) :
                if trees_on_fire[i] :
                    trees_on_fire[i] = False
                    pygame.mixer.Sound.play(fire_extinguish)
                    pygame.mixer.Sound.fadeout(fire_extinguish, 2000)
                    bullets.remove(bullet)
                    score += points
                    break
                else :
                    if not bullet[4] :
                        bullet[2] = -bullet[2]
                        bullet[3] = -bullet[3]
                        bullet[4] = True
                    else :
                        bullets.remove(bullet)
                    break

        # Remove a bala se sair da tela
        if bullet[1] < 0 or bullet[1] > height or bullet[0] < 0 or bullet[0] > width :
            bullets.remove(bullet)


# Atualiza a posição das balas das árvores
def update_tree_bullets() :
    global player_health, player_x, player_y, hit, tries
    for tree_bullet in tree_bullets[:] :
        tree_bullet[0] += tree_bullet[2]
        tree_bullet[1] += tree_bullet[3]
        tree_bullet_rect = pygame.Rect(tree_bullet[0] - 10, tree_bullet[1] - 10, 20, 20)

        # Verificar colisão da bala com o jogador
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        if tree_bullet_rect.colliderect(player_rect) and not hit :
            hit = True
            tree_bullets.remove(tree_bullet)
            pygame.mixer.Sound.play(fire)
            pygame.mixer.Sound.fadeout(fire, 2000)
            if hit :
                player_health -= 1
            if player_health <= 0 :
                # Reiniciar o jogo quando a vida do jogador for 0
                player_x = width // 2
                player_y = height // 2
                player_health = 15
                tries -= 1
                bullets.clear()
                tree_bullets.clear()
                trees_on_fire[:] = [True] * len(trees_on_fire)
                break

        if tree_bullet[0] < 0 or tree_bullet[0] > width or tree_bullet[1] < 0 or tree_bullet[1] > height :
            tree_bullets.remove(tree_bullet)


# Função para o menu inicial
def show_menu() :
    while True :
        load_background()
        title_text = title_font.render("SUPER MACAW", True, WHITE)
        start_text = secondary_font.render("Press ENTER to start", True, WHITE)
        exit_text = secondary_font.render("Press ESC to leave", True, WHITE)

        tela.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 2 - 140))
        tela.blit(start_text, (width // 2 - start_text.get_width() // 2, height // 2))
        tela.blit(exit_text, (width // 2 - exit_text.get_width() // 2, height // 2 + 60))

        for event in pygame.event.get() :
            if event.type == QUIT :
                pygame.quit()
                exit()
            if event.type == KEYDOWN :
                print("me culo")
                if event.key == K_RETURN :
                    return
                if event.key == K_ESCAPE :
                    pygame.quit()
                    exit()

        pygame.display.update()


show_menu()
sound_game()

# cria as árvores no início do jogo
create_trees()

phase_message = ""
show_phase_message = False
message_start_time = 0


# função que desenha em cada nível
def draw_phase_message(message) :
    if show_phase_message :
        font = pygame.font.Font(None, 74)
        text = font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(width // 2, height // 2))
        tela.blit(text, text_rect)


# Loop principal do jogo
while True :
    clock.tick(60)
    for event in pygame.event.get() :
        if event.type == QUIT :
            pygame.quit()
            exit()
        if event.type == KEYDOWN :
            if event.key == K_ESCAPE :
                pygame.quit()
                exit()
            if event.key == K_SPACE :
                clicks = 0
            if event.key == K_BACKSPACE and stop:
                current_phase = 1
                tree_quantity = 5
                shoot_timer = 5000
                score = 0
                points = 5
                tries = 3
                elapsed_time = 0
                create_trees()
                stop = False
                sound_game()
            if event.key in [K_DOWN, K_UP, K_RIGHT, K_LEFT] :
                aim_direction = event.key

    # Movimento do player
    keys = pygame.key.get_pressed()
    new_player_x = player_x
    new_player_y = player_y

    if keys[pygame.K_a] :
        new_player_x -= speed_player
        facing_right = False
    if keys[pygame.K_d] :
        new_player_x += speed_player
        facing_right = True
    if keys[pygame.K_w] :
        new_player_y -= speed_player
    if keys[pygame.K_s] :
        new_player_y += speed_player

    # Limites do jogador para evitar sair da tela
    new_player_x = max(20, min(width - player_width - 20, new_player_x))
    new_player_y = max(hud_height, min(height - player_height - 20, new_player_y))

    frame_counter += 1
    if frame_counter >= frame_delay :
        frame_counter = 0
        current_fire_frame = (current_fire_frame + 1) % len(fire_frames)

    # Atualiza a mira
    aim_x = new_player_x + (player_width // 2) - (aim_width // 2)
    aim_y = new_player_y - aim_height

    # Verifica colisões com as árvores e lagos antes de atualizar a posição do jogador
    new_player_rect = pygame.Rect(new_player_x, new_player_y, player_width, player_height)
    collision = False

    for pos in tree_positions :
        tree_rect = pygame.Rect(pos[0], pos[1], 60, 80)
        offset_x = new_player_rect.left - tree_rect.left
        offset_y = new_player_rect.top - tree_rect.top
        if tree_mask.overlap(player_mask, (offset_x, offset_y)) :
            collision = True
            break

    if not collision :
        player_x = new_player_x
        player_y = new_player_y

    tree_shoot_timer += clock.get_time()
    if tree_shoot_timer >= shoot_timer :
        tree_shoot_timer = 0
        for i, pos in enumerate(tree_positions) :
            if trees_on_fire[i] :
                direction_x = player_x - pos[0]
                direction_y = player_y - pos[1]
                distance = math.hypot(direction_x, direction_y)
                if distance != 0 :
                    direction_x /= distance
                    direction_y /= distance
                if current_phase == 1 :
                    tree_bullet_speed = 4
                elif current_phase > current_phase - 1 :
                    tree_bullet_speed += 0.03
                direction_x *= tree_bullet_speed
                direction_y *= tree_bullet_speed
                tree_bullets.append([pos[0] + 30, pos[1] + 40, direction_x, direction_y])

    if not stop:
        elapsed_time += 1
        tela.fill(GREEN_GRASS)
        load_background()
        draw_forest_with_fire()
        draw_walls()
        draw_player()
        draw_health_bar()
        draw_hud(elapsed_time, player_health, current_phase)
        update_bullets()
        for bullet in bullets :
            draw_bullet(bullet)
        update_tree_bullets()
        for tree_bullet in tree_bullets :
            draw_tree_bullet(tree_bullet)

        # Disparar as balas do jogador
        if keys[pygame.K_SPACE] and clicks <= 0 :
            direction_x, direction_y = 0, 0
            pygame.mixer.Sound.play(bullet_sound)
            bullet_x, bullet_y = player_x, player_y

            if aim_direction == K_RIGHT :
                direction_x = bullet_speed
                bullet_x = player_x + 35
                bullet_y = player_y + 20
            elif aim_direction == K_LEFT :
                direction_x = -bullet_speed
                bullet_x = player_x - 15
                bullet_y = player_y + 20
            elif aim_direction == K_UP :
                direction_y = -bullet_speed
                bullet_x = aim_x
                bullet_y = aim_y
            elif aim_direction == K_DOWN :
                direction_y = bullet_speed
                bullet_x = aim_x
                bullet_y = aim_y + player_height

            bullets.append([aim.x, aim.y, direction_x, direction_y, False])
            clicks += 1


    else :
        pygame.mixer.music.unload()
        tela.fill(BLACK)
        title_text = title_font.render("VOCÊ FOI TORRADO", True, WHITE)
        tela.blit(title_text, (width // 2 - title_text.get_width() // 2, height // 2 - 140))
        try_again_text = secondary_font.render("Continuar..? Aperte Backspace", True, WHITE)
        tela.blit(try_again_text, (width // 2 - try_again_text.get_width() // 2, height // 2))
        score_text = secondary_font.render(f"SCORE FINAL: {score}", True, WHITE)
        tela.blit(score_text, (width // 2 - score_text.get_width() // 2, height // 4))
        






    # verifica se todas as árvores estão apagadas
    count_trees_fire = 0
    for fire_tree in trees_on_fire :
        if not fire_tree :
            count_trees_fire += 1
        if count_trees_fire == len(trees_on_fire) :
            reset_trees()
            current_phase += 1

            # reseta a vida em cada fase
            player_health = 15

            if current_phase > current_phase - 2 :
                points += 5

            phase_message = f"LEVEL {current_phase}"
            show_phase_message = True
            message_start_time = pygame.time.get_ticks()

    # Update phase message display
    if show_phase_message :
        current_time = pygame.time.get_ticks()
        if current_time - message_start_time < 2000 :  # mostra por 3 segundos
            draw_phase_message(phase_message)
        else :
            show_phase_message = False  # esconde depois de 3 segundos

    blink_timer += clock.get_time()
    if blink_timer >= blink_interval :
        hit = False
        blink_timer = 0

    if tries <=0:
        stop = True

    pygame.display.update()
