from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:
    text_color: tuple[int, int, int] = (0, 0, 0)
    white: tuple[int, int, int] = (255, 255, 255)
    lighter_gray: tuple[int, int, int] = (241, 241, 241)
    light_gray: tuple[int, int, int] = (192, 192, 192)
    dark_gray: tuple[int, int, int] = (128, 128, 128)
    drop_box_idle: tuple[int, int, int] = (255, 255, 255)
    drop_box_select: tuple[int, int, int] = (241, 241, 241)
