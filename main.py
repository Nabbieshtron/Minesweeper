import pygame

from game import Game, GameImages
from display_manager import DisplayManager

pygame.init()

display_manager = DisplayManager()

# Sprites
spritesheet_tiles = pygame.image.load("assets/images/tiles.png").convert_alpha()
spritesheet_faces = pygame.image.load("assets/images/faces.png").convert_alpha()
spritesheet_digits = pygame.image.load("assets/images/digits.png").convert_alpha()

game_imgs = GameImages(spritesheet_tiles, spritesheet_faces, spritesheet_digits)
game = Game(display_manager, game_imgs)


running = True
while running:
    for event in pygame.event.get():
        game.dispatch_events(event)
        if event.type == pygame.QUIT:
            running = False

    display_manager.draw()
    game.update()

    game.draw(display_manager.screen)
    pygame.display.flip()
