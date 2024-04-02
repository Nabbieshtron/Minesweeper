from dataclasses import dataclass, field
from enum import Enum, auto

import pygame

import widgets
from board import Board, BoardImages
from faces import Faces, FacesImages, FacesStates
from display_manager import DisplayManager
from constants import Colors
from sprite_slicer import slicer


@dataclass
class GameImages:
    spritesheet_tiles: pygame.Surface
    spritesheet_faces: pygame.Surface
    spritesheet_digits: pygame.Surface
    tiles: list[pygame.Surface] = field(init=False)
    faces: list[pygame.Surface] = field(init=False)
    digits: list[pygame.Surface] = field(init=False)

    def __post_init__(self):
        self.tiles = slicer(self.spritesheet_tiles, (16, 16), iter_num=8, rows=2)
        self.faces = slicer(self.spritesheet_faces, (24, 24), iter_num=5)
        self.digits = slicer(self.spritesheet_digits, (13, 23), iter_num=11)


class GameDifficulty(Enum):
    BEGINNER = auto()
    INTERMEDIATE = auto()
    EXPERT = auto()


class GameState(Enum):
    IDLE = auto()
    PLAYING = auto()
    LOST = auto()
    WON = auto()


class Game:
    def __init__(self, display_manager: DisplayManager, sprites: GameImages):
        self.sprites = sprites
        self.display_manager = display_manager
        self.game_state = GameState.IDLE

        # Dropboxes
        self.dbox_game_options = ("New game", "Beginner", "Intermediate", "Expert")
        self.dbox_game = widgets.DropBox(
            pygame.Rect(0, 0, 45, 18),
            "Game",
            pygame.font.SysFont("Arial", 12),
            self.dbox_game_options,
            (Colors.drop_box_idle, Colors.drop_box_select),
        )
        self.dbox_help_options = ("One", "Two", "Three", "Four")
        self.dbox_help = widgets.DropBox(
            pygame.Rect(45, 0, 40, 18),
            "Help",
            pygame.font.SysFont("Arial", 12),
            self.dbox_help_options,
            (Colors.drop_box_idle, Colors.drop_box_select),
        )

        self.wtimer = widgets.Timer(
            widgets.TimerCountImages(digits=self.sprites.digits[1:])
        )

        self.faces = Faces(FacesImages(*self.sprites.faces))

        self.board_images = BoardImages(
            minus=self.sprites.digits[0],
            digits=self.sprites.digits[1:],
            tiles=self.sprites.tiles,
            faces=self.sprites.faces,
        )

        self.board_difficulties = {
            GameDifficulty.BEGINNER: Board(
                rows=10, columns=10, mines_count=10, sprites=self.board_images
            ),
            GameDifficulty.INTERMEDIATE: Board(
                rows=16, columns=16, mines_count=40, sprites=self.board_images
            ),
            GameDifficulty.EXPERT: Board(
                rows=16, columns=30, mines_count=99, sprites=self.board_images
            ),
        }

        self.difficulty = GameDifficulty.BEGINNER
        self.board = self.board_difficulties[self.difficulty]

        self.display_manager.set_mode(
            16 * self.board.columns + 20, 16 * self.board.rows + 85
        )

        self.mine_counter = widgets.MineCounter(
            self.board.mines_count,
            widgets.MineCountImages(
                minus=self.sprites.digits[0], digits=self.sprites.digits[1:]
            ),
        )

    def new_game(self):
        self.game_state = GameState.IDLE
        self.faces.change_state(FacesStates.IDLE)
        self.board.reset()
        self.wtimer.reset()

    def change_dificulty(self):
        self.game_state = GameState.IDLE

        dificulty = self.dbox_game.get_current_option()
        self.difficulty = getattr(GameDifficulty, dificulty.upper())

        self.board = self.board_difficulties[self.difficulty]

        width, height = 16 * self.board.columns + 20, 16 * self.board.rows + 85
        self.display_manager.set_mode(width, height)

        self.new_game()

    def dispatch_events(self, event):
        if not self.dbox_game.draw_menu and not self.dbox_help.draw_menu:
            self.faces.dispatch_event(event)
            if self.game_state not in (GameState.WON, GameState.LOST):
                self.board.dispatch_events(event)

        # Dropbox events
        self.dbox_game.dispatch_event(event)
        self.dbox_help.dispatch_event(event)

    def update(self):
        # Dropbox
        self.dbox_game.update()
        self.dbox_help.update()

        # Count marked mines
        marked_count = sum(
            [True for square in self.board.squares if square.state.name == "FLAG"]
        )
        self.mine_counter.update(self.board.mines_count - marked_count)

        self.wtimer.update()

        if self.game_state is GameState.IDLE:
            # Starting timer on first pressed square/tile
            if not self.wtimer.timer.running and any(
                [True for square in self.board.squares if square.state.name == "REVEAL"]
            ):
                self.wtimer.start()
                self.game_state = GameState.PLAYING

        if not self.dbox_game.draw_menu and not self.dbox_help.draw_menu:
            self.faces.update()
            if self.game_state not in (GameState.WON, GameState.LOST):
                self.board.update()

        # Game logic
        dbox_current_option = self.dbox_game.get_current_option().upper()

        # Change dificulty
        if self.dbox_game.pressed and hasattr(GameDifficulty, dbox_current_option):
            if self.difficulty is not getattr(GameDifficulty, dbox_current_option):
                self.change_dificulty()

        # New game
        elif (
            self.dbox_game.pressed and self.dbox_game.get_current_option() == "New game"
        ):
            self.dbox_game.pressed = not self.dbox_game.pressed
            self.new_game()
        elif self.faces.current_state is FacesStates.NEW_GAME:
            self.new_game()

        if self.game_state != GameState.LOST:
            for square in self.board.squares:
                # Lost check
                if square.state.name == "REVEAL" and square.square_type == "x":
                    self.faces.change_state(FacesStates.LOST)
                    self.game_state = GameState.LOST
                    self.wtimer.end()
                    break

        # Won check
        if self.game_state != GameState.WON:
            revealed_squares = 0
            flaged_squares = 0
            for square in self.board.squares:
                if square.state.name == "REVEAL":
                    revealed_squares += 1
                elif square.state.name == "FLAG":
                    flaged_squares += 1

            if flaged_squares == self.board.mines_count:
                print("All flaged")
            if revealed_squares + flaged_squares == len(self.board.squares):
                print("You won")
                self.faces.change_state(FacesStates.WON)
                self.game_state = GameState.WON
                self.wtimer.end()

    def draw(self, screen):
        screen = self.display_manager.screen
        width, height = screen.get_size()

        # Dropbox background
        pygame.draw.rect(screen, Colors.white, (0, 0, width, 18))
        pygame.draw.line(screen, Colors.lighter_gray, (0, 18), (width, 18), 2)

        # Layout for UI
        pygame.draw.rect(screen, Colors.white, (0, 20, width + 5, height), 3)
        pygame.draw.rect(screen, Colors.light_gray, (3, 23, width - 3, 50), 6)
        pygame.draw.rect(screen, Colors.light_gray, (9, 29, width - 12, 39))

        # Top
        pygame.draw.line(screen, Colors.dark_gray, (9, 29), (width - 7, 29), 2)
        # Left
        pygame.draw.line(screen, Colors.dark_gray, (9, 29), (9, 65), 2)
        # Bottom
        pygame.draw.line(screen, Colors.white, (9, 65), (width - 7, 65), 2)
        # Right
        pygame.draw.line(screen, Colors.white, (width - 7, 29), (width - 7, 65), 2)

        # Layout for game board encasing
        pygame.draw.rect(screen, Colors.light_gray, (3, 67, width - 3, height - 67), 6)
        # Top
        pygame.draw.line(screen, Colors.dark_gray, (9, 74), (width - 7, 74), 3)
        # Left
        pygame.draw.line(screen, Colors.dark_gray, (10, 74), (10, height - 7), 3)
        # Bottom
        pygame.draw.line(
            screen, Colors.white, (9, height - 8), (width - 7, height - 8), 3
        )
        # Right
        pygame.draw.line(
            screen, Colors.white, (width - 7, 73), (width - 7, height - 7), 3
        )

        self.mine_counter.draw(screen)
        self.wtimer.draw(screen)
        self.faces.draw(screen)
        self.board.draw(screen)
        self.dbox_game.draw(screen)
        self.dbox_help.draw(screen)
