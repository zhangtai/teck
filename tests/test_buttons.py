from Teck.utils.buttons import get_pressed_buttons_states


def test_pressed_button_match_states():
    pressed_buttons = [[1, 1], [1, 5]]
    expected_states = [
        True,
        False,
        False,
        False,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    assert get_pressed_buttons_states(pressed_buttons) == expected_states
