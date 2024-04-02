from dataclasses import dataclass
from enum import Enum, auto

import pygame


@dataclass
class FacesImages:
    idle: pygame.Surface
    pressed: pygame.Surface
    action: pygame.Surface
    won: pygame.Surface
    lost: pygame.Surface


class FacesStates(Enum):
    NEW_GAME = auto()
    IDLE = auto()
    PRESSED = auto()
    ACTION = auto()
    WON = auto()
    LOST = auto()


class Faces:
    def __init__(self, sprites: FacesImages):
        self.sprites = sprites
        self.image = sprites.idle
        self.rect = self.image.get_rect()
        self.pressed = False

        self.current_state = FacesStates.IDLE
        self.previous_state = FacesStates.IDLE

        self.action_collision_field = pygame.display.get_surface().get_rect(
            topleft=(0, 18)
        )

    def change_state(self, state: FacesStates):
        if state is not self.current_state:
            self.previous_state = self.current_state
            self.current_state = state

    def revert_state(self):
        if self.current_state is not self.previous_state:
            self.current_state = self.previous_state

    def dispatch_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
            elif (
                not self.rect.collidepoint(event.pos)
                and self.action_collision_field.collidepoint(event.pos)
                and self.current_state not in (FacesStates.LOST, FacesStates.WON)
            ):
                self.change_state(FacesStates.ACTION)

        elif event.type == pygame.MOUSEBUTTONUP:
            if (
                self.rect.collidepoint(event.pos)
                and self.current_state is FacesStates.PRESSED
            ):
                self.change_state(FacesStates.NEW_GAME)
            elif self.current_state not in (FacesStates.LOST, FacesStates.WON):
                self.revert_state()
            self.pressed = False

    def update(self):
        screen = pygame.display.get_surface()
        mouse_pos = pygame.mouse.get_pos()

        # Centering face
        self.rect.center = (screen.get_width() / 2, 48)

        # Defining action collision field
        self.action_collision_field = screen.get_rect(topleft=(0, 18))

        # Handling faces collision effects when pressd
        if self.pressed:
            if self.rect.collidepoint(mouse_pos):
                self.change_state(FacesStates.PRESSED)
            else:
                self.revert_state()

        # Seletcting appropriate image by the current state
        self.image = getattr(
            self.sprites, self.current_state.name.lower(), self.sprites.idle
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)
