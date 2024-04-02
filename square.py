from __future__ import annotations

from dataclasses import dataclass
from typing import Union
from enum import Enum, auto

import pygame


@dataclass
class SquareImages:
    hide: pygame.Surface
    reveal: pygame.Surface
    hover: pygame.Surface
    flag: pygame.Surface

    @classmethod
    def create_instance(cls, square_type: Union[str, int], sprites) -> SquareImages:
        if isinstance(square_type, int):
            image = sprites[square_type + 7] if square_type > 0 else sprites[1]
        else:
            image = sprites[5]

        return cls(
            sprites[0],
            image,
            sprites[1],
            sprites[2],
        )


class SquareState(Enum):
    HIDE = auto()
    REVEAL = auto()
    HOVER = auto()
    FLAG = auto()


class Square(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: pygame.Vector2,
        pos_grid: pygame.Vector2,
        square_type: Union[int, str],
        sprites: SquareImages,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.pos_grid = pos_grid
        self.square_type = square_type
        self.sprites = sprites
        self.state = SquareState.HIDE
        self.pressed = False
        self.image = getattr(self.sprites, self.state.name.lower(), self.sprites.hide)
        self.rect = self.image.get_rect(topleft=self.pos)

    def dispatch_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                if event.button == 1 and self.state is not SquareState.FLAG:
                    self.state = SquareState.REVEAL
                if event.button == 3 and self.state is not SquareState.REVEAL:
                    if self.state is not SquareState.FLAG:
                        self.state = SquareState.FLAG
                    else:
                        self.state = SquareState.HIDE

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.state not in (SquareState.REVEAL, SquareState.FLAG):
            if mouse_pressed[0] and self.rect.collidepoint(mouse_pos):
                self.state = SquareState.HOVER
            else:
                self.state = SquareState.HIDE

        self.image = getattr(self.sprites, self.state.name.lower(), self.sprites.hide)
