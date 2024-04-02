import pygame


class DisplayManager:
    def __init__(self):
        self.SIZE = (180, 245)
        self.screen = pygame.display.set_mode(self.SIZE)
        self.logo = pygame.image.load("assets/images/logo.png").convert_alpha()

    def set_mode(self, width, height):
        pygame.display.quit()

        self.screen = pygame.display.set_mode((width, height))

        pygame.display.set_caption("Minesweeper")
        pygame.display.set_icon(self.logo)

    def draw(self):
        self.screen.fill("Red")
