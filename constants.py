import pygame

# Initialize pygame
pygame.init()

# Display settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 630
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game settings
GROUND_Y = 568
SCROLL_SPEED = 4
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Fonts
FONT = pygame.font.SysFont('Bauhaus 93', 60)
SMALL_FONT = pygame.font.SysFont('Bauhaus 93', 30)
MENU_FONT = pygame.font.SysFont('Bauhaus 93', 40)

# File paths
BG_IMG_PATH = 'img/bg.png'
GROUND_IMG_PATH = 'img/ground.png'
BIRD_IMG_PATHS = ['img/bird1.png', 'img/bird2.png', 'img/bird3.png']
PIPE_IMG_PATH = 'img/pipe.png'
DATABASE_PATH = 'flappy_scores.db'

# Menu states
MAIN_MENU = 'main'
NAME_INPUT = 'name_input'
GAME = 'game'
HIGH_SCORES = 'high_scores'
