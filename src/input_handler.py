"""User input handling."""

# Windows-specific import
try:
    import msvcrt
except ImportError:
    # For testing on non-Windows platforms
    msvcrt = None


def get_user_choice(num_patterns: int) -> int | None:
    """Get user's choice from keyboard input.

    Args:
        num_patterns: Number of available patterns

    Returns:
        Index of selected pattern (0-based), or None if ESC pressed
    """
    if msvcrt is None:
        raise RuntimeError("msvcrt is not available (Windows only)")

    while True:
        key = msvcrt.getch()

        # Check for ESC key
        if key == b"\x1b":
            return None

        # Check for a-z selection
        if b"a" <= key <= b"z":
            index = ord(key) - ord(b"a")
            if index < num_patterns:
                return index

        # Invalid input, continue waiting
