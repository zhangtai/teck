def position_to_index(
    position: tuple[int, int], layout: tuple[int, int] = (3, 5)
) -> int:
    return (position[0] - 1) * layout[1] + position[1] - 1


def get_pressed_buttons_states(
    pressed_buttons: list[tuple[int, int]], layout: tuple[int, int] = (3, 5)
) -> list[bool]:
    stats = [False] * layout[0] * layout[1]
    for i in range(layout[0] * layout[1]):
        for button in pressed_buttons:
            if position_to_index(button) == i:
                stats[i] = True
    return stats
