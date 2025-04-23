import pygame
from constants import WHITE, MENU_FONT

class Button:
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

    def draw(self, screen):
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # Draw button
        if self.image:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, (70, 70, 70), self.rect)
            pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
            if self.text:
                text_img = MENU_FONT.render(self.text, True, WHITE)
                text_rect = text_img.get_rect(center=self.rect.center)
                screen.blit(text_img, text_rect)

        return action
