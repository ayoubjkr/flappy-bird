import pygame
from constants import BIRD_IMG_PATHS

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for path in BIRD_IMG_PATHS:
            img = pygame.image.load(path)
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.space_pressed = False
        self.jump_strength = -7  
        self.gravity = 0.4

    def update(self, flying, game_over):
        if flying:
            # Apply gravity
            self.vel += self.gravity
            if self.vel > 7:  # Terminal velocity
                self.vel = 7
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Jump with mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = self.jump_strength
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
                
            # Jump with spacebar
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.space_pressed:
                self.space_pressed = True
                self.vel = self.jump_strength
            if not keys[pygame.K_SPACE]:
                self.space_pressed = False

            # Handle animation
            flap_cooldown = 5
            self.counter += 1
            
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1.5)
        else:
            # Point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)
