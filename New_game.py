import pygame
from pygame.locals import *
from sys import exit

pygame.init()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Tela
width = 1280
height = 720
tela = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("New Game")
clock = pygame.time.Clock()

# Player
player_x = width // 2
player_y = height // 2
radius = 30
speed_player = 10

# Mira
aim_width = 15
aim_height = 50
aim_x = player_x - (aim_width // 2)
aim_y = player_y - aim_height 

# Bala
bullet_size = 5
bullets = []

def draw_player():
    pygame.draw.circle(tela, BLACK, (player_x, player_y), radius)
    pygame.draw.rect(tela, BLACK, (aim_x, aim_y, aim_width, aim_height))

def draw_bullet(bullet):
    pygame.draw.circle(tela, BLACK, (bullet[0], bullet[1]), bullet_size)

# Atualiza a posição das balas
def update_bullets():
    for bullet in bullets[:]:
        bullet[1] -= 10  # Move a bala para cima
        if bullet[1] < 0:  # Remove a bala se sair da tela
            bullets.remove(bullet)

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    # Movimento do player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= speed_player
    if keys[pygame.K_RIGHT]:
        player_x += speed_player
    if keys[pygame.K_UP]:
        player_y -= speed_player
    if keys[pygame.K_DOWN]:
        player_y += speed_player
    if keys[pygame.K_SPACE]:
        # Adiciona uma nova bala na posição da mira
        bullets.append([aim_x + aim_width // 2, aim_y])  # Posição da bala

    # Limites do jogador
    player_x = max(radius, min(width - radius, player_x))
    player_y = max(radius, min(height - radius, player_y))
    
    # Atualiza a mira
    aim_x = player_x - (aim_width // 2)
    aim_y = player_y - aim_height 

    # Limpa a tela
    tela.fill(WHITE)
    # Desenha o jogador e a mira
    draw_player()
    # Atualiza e desenha as balas
    update_bullets()
    for bullet in bullets:
        draw_bullet(bullet)

    pygame.display.update()
