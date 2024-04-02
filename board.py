from typing import Union
from dataclasses import dataclass

import pygame
from random import randint

from square import Square, SquareImages, SquareState


@dataclass
class BoardImages:
    minus: pygame.Surface
    digits: list[pygame.Surface]
    tiles: list[pygame.Surface]
    faces: list[pygame.Surface]


class Board:
    def __init__(self, rows, columns, mines_count, sprites):
        self.rows = rows
        self.columns = columns
        self.mines_count = mines_count
        self.sprites = sprites
        self.board_vector = pygame.math.Vector2(12, 76)
        self.mines_locations = self.get_random_coordinates(
            (self.columns, self.rows), iterations=self.mines_count
        )

        self.squares = pygame.sprite.Group(
            [[value for value in row] for row in self.generate_grid()]
        )

    def generate_grid(self):
        grid = [[0] * self.columns for _ in range(self.rows)]

        # Placing mines
        for x, y in self.mines_locations:
            grid[x][y] = "x"

        # Placing digits around the mines
        for x, y in self.mines_locations:
            neighbors = [
                (x - 1, y),
                (x + 1, y),
                (x - 1, y - 1),
                (x + 1, y + 1),
                (x - 1, y + 1),
                (x + 1, y - 1),
                (x, y - 1),
                (x, y + 1),
            ]

            for x, y in neighbors:
                try:
                    if type(grid[x][y]) is int:
                        grid[x][y] += 1
                except IndexError:
                    continue

        output = []
        tile_x, tile_y = self.sprites.tiles[0].get_size()
        pos_x, pos_y = self.board_vector.xy
        for row_num, row_iter in enumerate(grid):
            new_row = []
            pos_x = self.board_vector.x
            for column_num, value in enumerate(row_iter):
                new_row.append(
                    Square(
                        pygame.math.Vector2(pos_x, pos_y),
                        pygame.math.Vector2(row_num, column_num),
                        value,
                        SquareImages.create_instance(value, self.sprites.tiles),
                    )
                )
                pos_x += tile_x
            output.append(new_row)
            pos_y += tile_y

        return output

    def get_random_coordinates(
        self,
        end: tuple[int, int],
        start: tuple[int, int] = (0, 0),
        exclude: Union[list[tuple[int, int]], None] = None,
        iterations: int = 1,
        duplicate: bool = False,
    ) -> list[tuple[int, int]]:
        """
        Generates random coordinates,
        end - tuple[x,y] with end positions,
        start - tuple[x,y] with start positions, by default its (0,0),
        exclude - a list of coordinates tuple[x,y] to be excluded,
        iterations - a number of coordinates sets,
        duplicate - by default its False,
        returns a list[tuple[int,int]] of generated coordinates"""

        row = randint(start[0], end[1] - 1)
        collumn = randint(start[1], end[0] - 1)

        if exclude is None:
            exclude = []

        if duplicate or (row, collumn) not in exclude:
            exclude.append((row, collumn))
        else:
            return self.get_random_coordinates(
                end, start, exclude, iterations, duplicate
            )

        iterations -= 1
        if iterations > 0:
            return self.get_random_coordinates(
                end, start, exclude, iterations, duplicate
            )
        else:
            return exclude

    def reset(self):
        self.mines_locations = self.get_random_coordinates(
            (self.columns, self.rows), iterations=self.mines_count
        )
        self.squares = pygame.sprite.Group(
            [[value for value in row] for row in self.generate_grid()]
        )

    def flood_fill(self, square: Square):
        queue = [square.pos_grid.xy]

        while queue:
            square_pos = queue.pop()

            x = int(square_pos[0])
            y = int(square_pos[1])

            neighbours = [
                (x - 1, y),
                (x + 1, y),
                (x - 1, y - 1),
                (x + 1, y + 1),
                (x - 1, y + 1),
                (x + 1, y - 1),
                (x, y - 1),
                (x, y + 1),
            ]
            for neighbour in neighbours:
                for square in self.squares:
                    pos_x = int(square.pos_grid.x)
                    pos_y = int(square.pos_grid.y)

                    if neighbour[0] == pos_x and neighbour[1] == pos_y:
                        if (
                            square.square_type == 0
                            and square.state != SquareState.REVEAL
                        ):
                            square.state = SquareState.REVEAL
                            queue.append(neighbour)
                        else:
                            square.state = SquareState.REVEAL

    def dispatch_events(self, event):
        for square in self.squares:
            square.dispatch_event(event)

    def update(self):
        self.squares.update()

        for square in self.squares:
            if square.state.name == "REVEAL" and square.square_type == 0:
                self.flood_fill(square)

    def draw(self, screen):
        self.squares.draw(screen)
