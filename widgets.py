import pygame
from dataclasses import dataclass

import timer
from constants import Colors


@dataclass
class TimerCountImages:
    digits: list[pygame.Surface]


class Timer:
    def __init__(self, sprites: TimerCountImages):
        self.sprites = sprites
        self.timer = timer.Timer()

    def start(self):
        self.timer.start()

    def end(self):
        self.timer.end()

    def reset(self):
        self.end()
        self.timer.reset()

    def update(self):
        self.timer.update()

    def draw(self, screen):
        width = screen.get_width()
        x = 0
        for n, index in enumerate(str(self.timer.counting).zfill(3)):
            try:
                surf = self.sprites.digits[int(index)]
            except ValueError:
                surf = self.sprites.minus
            rect_obj = surf.get_rect(topleft=(width - 65, 36))
            rect_obj.left += 12 + x
            screen.blit(surf, rect_obj)
            x += 13


class DropBox:
    def __init__(
        self,
        rect: pygame.Rect,
        main: str,
        font: pygame.Font,
        options,
        colors: tuple[tuple[int, int, int]],
    ):
        self.rect = rect
        self.main = main
        self.font = font
        self.colors = colors
        self.options = options
        self.options_rects = self.get_options_rects()
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.pressed = False

    def get_options_rects(self) -> dict[str : pygame.Rect]:
        output = {}
        for n, option in enumerate(self.options):
            rect = self.rect.copy()
            rect.w = self.rect.w * 2
            rect.y += (n + 1) * self.rect.height
            output[option] = rect
        return output

    def get_current_option(self) -> str:
        return self.options[self.active_option]

    def dispatch_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_active:
                self.draw_menu = not self.draw_menu
                self.pressed = False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.draw_menu and self.active_option >= 0:
                self.draw_menu = not self.draw_menu
                self.pressed = not self.pressed

    def update(self):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        # Highlight effect
        if self.draw_menu:
            self.active_option = -1
            for n, rect in enumerate(self.options_rects.values()):
                if rect.collidepoint(mpos):
                    self.active_option = n
                    break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.colors[self.menu_active], self.rect, 0)
        text = self.font.render(self.main, True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=self.rect.center))

        if self.draw_menu:
            for n, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.w = self.rect.w * 2
                rect.y += (n + 1) * self.rect.height
                pygame.draw.rect(
                    screen, self.colors[1 if n == self.active_option else 0], rect, 0
                )
                text = self.font.render(text, True, (0, 0, 0))
                screen.blit(text, text.get_rect(center=rect.center))


@dataclass
class MineCountImages:
    minus: pygame.Surface
    digits: list[pygame.Surface]


class MineCounter:
    def __init__(self, mine_count: int, sprites: MineCountImages):
        self.original_count = mine_count
        self.mine_count = mine_count
        self.sprites = sprites

    def reset(self):
        self.mine_count = self.original_count

    def update(self, marked_count):
        self.mine_count = marked_count

    def draw(self, screen):
        x = 0
        for index in str(self.mine_count).zfill(3):
            try:
                surf = self.sprites.digits[int(index)]
            except ValueError:
                surf = self.sprites.minus

            rect_obj = surf.get_rect(topleft=(10, 36))
            rect_obj.left += 7 + x
            screen.blit(surf, rect_obj)
            x += 13
