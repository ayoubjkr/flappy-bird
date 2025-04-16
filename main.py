import pygame
from pygame.locals import *
import random
import sqlite3
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 630

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# define fonts
font = pygame.font.SysFont('Bauhaus 93', 60)
small_font = pygame.font.SysFont('Bauhaus 93', 30)
menu_font = pygame.font.SysFont('Bauhaus 93', 40)

# define colours
white = (255, 255, 255)
black = (0, 0, 0)

# define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
menu_state = 'main'  # States: main, name_input, game, high_scores
player_name = ""
highest_score = 0

# load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')

# Setup database
def setup_database():
    if not os.path.exists('flappy_scores.db'):
        conn = sqlite3.connect('flappy_scores.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE scores
                    (name TEXT, score INTEGER)''')
        conn.commit()
        conn.close()

def get_highest_score():
    conn = sqlite3.connect('flappy_scores.db')
    c = conn.cursor()
    c.execute("SELECT MAX(score) FROM scores")
    result = c.fetchone()[0]
    conn.close()
    if result is None:
        return 0
    return result

def update_player_score(name, new_score):
    conn = sqlite3.connect('flappy_scores.db')
    c = conn.cursor()
    # Check if player exists
    c.execute("SELECT score FROM scores WHERE name = ?", (name,))
    result = c.fetchone()
    
    if result is None:
        # Player doesn't exist, create new record
        c.execute("INSERT INTO scores VALUES (?, ?)", (name, new_score))
    else:
        # Player exists, update if new score is higher
        if new_score > result[0]:
            c.execute("UPDATE scores SET score = ? WHERE name = ?", (new_score, name))
    
    conn.commit()
    conn.close()

def get_all_scores():
    conn = sqlite3.connect('flappy_scores.db')
    c = conn.cursor()
    c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
    result = c.fetchall()
    conn.close()
    return result

# function for outputting text into the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.space_pressed = False
        self.jump_strength = -7  
        self.gravity = 0.4       

    def update(self):
        if flying == True:
            # apply gentler gravity
            self.vel += self.gravity
            if self.vel > 7:  # Lower terminal velocity from 8 to 6
                self.vel = 7
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump with mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = self.jump_strength
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
                
            # jump with spacebar
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.space_pressed:
                self.space_pressed = True
                self.vel = self.jump_strength
            if not keys[pygame.K_SPACE]:
                self.space_pressed = False

            # handle the animation
            flap_cooldown = 5
            self.counter += 1
            
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate the bird (less extreme rotation)
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1.5)
        else:
            # point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        # position variable determines if the pipe is coming from the bottom or top
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image=None, text=None, width=None, height=None):
        if image:
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)
            self.text = None
        else:
            self.text = text
            self.rect = pygame.Rect(x, y, width, height)
            self.image = None

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        if self.image:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, (70, 70, 70), self.rect)
            pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
            if self.text:
                text_img = menu_font.render(self.text, True, white)
                text_rect = text_img.get_rect(center=self.rect.center)
                screen.blit(text_img, text_rect)

        return action

# Setup database
setup_database()
highest_score = get_highest_score()

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# create buttons
restart_button = Button(screen_width // 2 - 100, 420, None, "Restart", 200, 50)
menu_button = Button(screen_width // 2 - 100, 500, None, "MENU", 200, 50)
play_button = Button(screen_width // 2 - 100, 200, None, "NEW GAME", 250, 50)
scores_button = Button(screen_width // 2 - 100, 270, None, "HIGH SCORES", 250, 50)
quit_button = Button(screen_width // 2 - 100, 340, None, "QUIT", 250, 50)
back_button = Button(screen_width // 2 - 100, 500, None, "BACK", 200, 50)
submit_button = Button(screen_width // 2 - 100, 350, None, "PLAY", 200, 50)

run = True
input_active = False
while run:
    clock.tick(fps)

    # draw background
    screen.blit(bg, (0, 0))

    if menu_state == 'main':
        # Main menu
        draw_text("FLAPPY BIRD", font, white, screen_width // 2 - 140, 100)
        
        if play_button.draw():
            menu_state = 'name_input'
            player_name = ""
            input_active = True
        
        if scores_button.draw():
            menu_state = 'high_scores'
        
        if quit_button.draw():
            run = False
    
    elif menu_state == 'name_input':
        # Name input screen
        draw_text("ENTER YOUR NAME:", small_font, white, screen_width // 2 - 150, 200)
        
        # Draw input box
        input_box = pygame.Rect(screen_width // 2 - 150, 250, 300, 50)
        pygame.draw.rect(screen, white, input_box, 2)
        
        # Display current input
        name_surface = small_font.render(player_name, True, white)
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))
        
        if submit_button.draw() and player_name.strip():
            menu_state = 'game'
            game_over = False
            flying = False
            score = reset_game()
    
    elif menu_state == 'high_scores':
        # High scores screen
        draw_text("HIGH SCORES", font, white, screen_width // 2 - 180, 50)
        
        scores = get_all_scores()
        y_offset = 150
        for i, (name, player_score) in enumerate(scores):
            draw_text(f"{i+1}. {name}: {player_score}", small_font, white, screen_width // 2 - 150, y_offset)
            y_offset += 40
        
        if back_button.draw():
            menu_state = 'main'
    
    elif menu_state == 'game':
        # Game screen
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()

        # draw and scroll the ground
        screen.blit(ground_img, (ground_scroll, 568))

        # check the score
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False
        
        draw_text(f"SCORE:{str(score)}", small_font, white, 20, 20)

        # look for collision
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        # once the bird has hit the ground it's game over and no longer flying
        if flappy.rect.bottom >= 568:
            game_over = True
            flying = False

        if flying == True and game_over == False:
            # generate new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            pipe_group.update()

            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

        # check for game over and reset
        if game_over == True:
            # Update player score in database
            if score > 0:
                update_player_score(player_name, score)
                highest_score = max(highest_score, score)
            
            # Display game over screen
            draw_text("GAME OVER!", font, white, screen_width // 2 - 180, 100)
            
            draw_text(f"BEST: {highest_score}", small_font, white, screen_width // 2 - 70, 240)
            
            if restart_button.draw():
                game_over = False
                score = reset_game()
            
            if menu_button.draw():
                menu_state = 'main'
                game_over = False

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if menu_state == 'game':
            if (event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[K_SPACE]) and flying == False and game_over == False:
                flying = True
        
        if menu_state == 'name_input':
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_RETURN and player_name.strip():
                        menu_state = 'game'
                        game_over = False
                        flying = False
                        score = reset_game()
                    else:
                        # Limit name length to 15 characters
                        if len(player_name) < 15:
                            player_name += event.unicode

    pygame.display.update()

pygame.quit()