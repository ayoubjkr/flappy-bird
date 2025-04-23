import pygame
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y, PIPE_FREQUENCY, 
    PIPE_GAP, SCROLL_SPEED, WHITE, FONT, SMALL_FONT
)
from bird import Bird
from pipe import Pipe
from database import update_player_score

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.ground_img = pygame.image.load('img/ground.png')
        self.bg_img = pygame.image.load('img/bg.png')
        self.ground_scroll = 0
        self.flying = False
        self.game_over = False
        self.score = 0
        self.pass_pipe = False
        self.last_pipe = pygame.time.get_ticks() - PIPE_FREQUENCY
        self.highest_score = 0
        
        # Create sprite groups
        self.pipe_group = pygame.sprite.Group()
        self.bird_group = pygame.sprite.Group()
        
        # Create bird
        self.flappy = Bird(100, int(SCREEN_HEIGHT / 2))
        self.bird_group.add(self.flappy)
    
    def reset_game(self):
        """Reset game state for a new game"""
        self.pipe_group.empty()
        self.flappy.rect.x = 100
        self.flappy.rect.y = int(SCREEN_HEIGHT / 2)
        self.score = 0
        self.game_over = False
        self.flying = False
        return self.score
        
    def draw_text(self, text, font, text_col, x, y):
        """Render text on screen"""
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))
    
    def update(self):
        """Update game state"""
        # Draw background
        self.screen.blit(self.bg_img, (0, 0))
        
        # Draw and update pipes
        self.pipe_group.draw(self.screen)
        
        # Draw and update bird
        self.bird_group.draw(self.screen)
        self.flappy.update(self.flying, self.game_over)
        
        # Draw ground
        self.screen.blit(self.ground_img, (self.ground_scroll, GROUND_Y))
        
        # Check score
        if len(self.pipe_group) > 0:
            if (self.flappy.rect.left > self.pipe_group.sprites()[0].rect.left
                    and self.flappy.rect.right < self.pipe_group.sprites()[0].rect.right
                    and not self.pass_pipe):
                self.pass_pipe = True
            if self.pass_pipe:
                if self.flappy.rect.left > self.pipe_group.sprites()[0].rect.right:
                    self.score += 1
                    self.pass_pipe = False
        
        # Display score
        self.draw_text(f"SCORE:{str(self.score)}", SMALL_FONT, WHITE, 20, 20)
        
        # Check for collision
        if (pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False) 
                or self.flappy.rect.top < 0 or self.flappy.rect.bottom >= GROUND_Y):
            self.game_over = True
            if self.flappy.rect.bottom >= GROUND_Y:
                self.flying = False
        
        # Generate new pipes
        if self.flying and not self.game_over:
            time_now = pygame.time.get_ticks()
            if time_now - self.last_pipe > PIPE_FREQUENCY:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, -1)
                top_pipe = Pipe(SCREEN_WIDTH, int(SCREEN_HEIGHT / 2) + pipe_height, 1)
                self.pipe_group.add(btm_pipe)
                self.pipe_group.add(top_pipe)
                self.last_pipe = time_now
            
            # Update pipes
            self.pipe_group.update()
            
            # Scroll ground
            self.ground_scroll -= SCROLL_SPEED
            if abs(self.ground_scroll) > 35:
                self.ground_scroll = 0
    
    def display_game_over(self, player_name):
        """Handle game over state"""
        # Update player score in database
        if self.score > 0:
            update_player_score(player_name, self.score)
            self.highest_score = max(self.highest_score, self.score)
        
        # Display game over text
        self.draw_text("GAME OVER!", FONT, WHITE, SCREEN_WIDTH // 2 - 120, 100)
        self.draw_text(f"BEST: {self.highest_score}", SMALL_FONT, WHITE, SCREEN_WIDTH // 2 - 70, 240)
