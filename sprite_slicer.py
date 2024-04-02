from pygame import Surface


def slicer(
    image: Surface,
    stop_pos: tuple[int, int],
    start_pos: tuple[int, int] = (0, 0),
    iter_num: int = 1,
    rows: int = 1,
) -> list[Surface]:
    output = []
    x, y = start_pos
    w, h = stop_pos
    for _ in range(rows):
        for _ in range(iter_num):
            img = image.subsurface(x, y, w, h)
            output.append(img)
            x += stop_pos[0]

        # Next row
        x, y = start_pos
        y += stop_pos[1]
    return output
