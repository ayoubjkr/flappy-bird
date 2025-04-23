import pygame
from pygame.locals import *
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, FONT, SMALL_FONT,
    MAIN_MENU, NAME_INPUT, GAME, HIGH_SCORES
)
from button import Button
from game import Game
from database import setup_database, get_highest_score, get_all_scores

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Set up clock
clock = pygame.time.Clock()

def main():
    # Setup database
    setup_database()
    highest_score = get_highest_score()
    
    # Create game instance
    game = Game(screen)
    game.highest_score = highest_score
    
    # Create buttons
    restart_button = Button(SCREEN_WIDTH // 2 - 100, 420, None, "Restart", 200, 50)
    menu_button = Button(SCREEN_WIDTH // 2 - 100, 500, None, "MENU", 200, 50)
    play_button = Button(SCREEN_WIDTH // 2 - 250 // 2, 200, None, "NEW GAME", 250, 50)
    scores_button = Button(SCREEN_WIDTH // 2 - 250 // 2, 270, None, "HIGH SCORES", 250, 50)
    quit_button = Button(SCREEN_WIDTH // 2 - 250 // 2, 340, None, "QUIT", 250, 50)
    back_button = Button(SCREEN_WIDTH // 2 - 100, 500, None, "BACK", 200, 50)
    submit_button = Button(SCREEN_WIDTH // 2 - 100, 350, None, "PLAY", 200, 50)
    
    # Game loop variables
    run = True
    menu_state = MAIN_MENU
    player_name = ""
    input_active = False
    
    # Game loop
    while run:
        clock.tick(FPS)
        
        # Draw background (handled in each state)
        screen.blit(game.bg_img, (0, 0))
        
        if menu_state == MAIN_MENU:
            # Main menu
            game.draw_text("FLAPPY BIRD", FONT, WHITE, SCREEN_WIDTH // 2 - 140, 100)
            
            if play_button.draw(screen):
                menu_state = NAME_INPUT
                player_name = ""
                input_active = True
            
            if scores_button.draw(screen):
                menu_state = HIGH_SCORES
            
            if quit_button.draw(screen):
                run = False
        
        elif menu_state == NAME_INPUT:
            # Name input screen
            game.draw_text("ENTER YOUR NAME:", SMALL_FONT, WHITE, SCREEN_WIDTH // 2 - 150, 200)
            
            # Draw input box
            input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 250, 300, 50)
            pygame.draw.rect(screen, WHITE, input_box, 2)
            
            # Display current input
            name_surface = SMALL_FONT.render(player_name, True, WHITE)
            screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))
            
            if submit_button.draw(screen) and player_name.strip():
                menu_state = GAME
                game.reset_game()
        
        elif menu_state == HIGH_SCORES:
            # High scores screen
            game.draw_text("HIGH SCORES", FONT, WHITE, SCREEN_WIDTH // 2 - 180, 50)
            
            scores = get_all_scores()
            y_offset = 150
            for i, (name, player_score) in enumerate(scores):
                game.draw_text(f"{i+1}. {name}: {player_score}", SMALL_FONT, WHITE, SCREEN_WIDTH // 2 - 150, y_offset)
                y_offset += 40
            
            if back_button.draw(screen):
                menu_state = MAIN_MENU
        
        elif menu_state == GAME:
            # Game screen
            game.update()
            
            # Check for game over
            if game.game_over:
                game.display_game_over(player_name)
                
                if restart_button.draw(screen):
                    game.reset_game()
                
                if menu_button.draw(screen):
                    menu_state = MAIN_MENU
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if menu_state == GAME:
                if (event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[K_SPACE]) and not game.flying and not game.game_over:
                    game.flying = True
            
            if menu_state == NAME_INPUT:
                if event.type == pygame.KEYDOWN:
                    if input_active:
                        if event.key == pygame.K_BACKSPACE:
                            player_name = player_name[:-1]
                        elif event.key == pygame.K_RETURN and player_name.strip():
                            menu_state = GAME
                            game.reset_game()
                        else:
                            # Limit name length to 15 characters
                            if len(player_name) < 15:
                                player_name += event.unicode
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()