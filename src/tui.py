"""TUI (Text User Interface) display operations."""

import re

from .pattern_matcher import colorize_matched_text, get_display_lines

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_WHITE = "\033[97m"  # Bright white for headers and prompts
COLOR_BRIGHT_RED = "\033[91m"  # Bright red for pattern options
GRAY = "\033[90m"
RESET = "\033[0m"


def display_tui(content: str, matched_patterns: list) -> None:
    """Display TUI with clipboard content and matched patterns.

    Args:
        content: Clipboard text content
        matched_patterns: List of matched pattern dictionaries
    """
    # Display clipboard content (matched lines with context)
    print(f"{GRAY}クリップボード内容:{RESET}")
    print(f"{GRAY}{'-' * 40}{RESET}")

    display_lines = get_display_lines(content, matched_patterns)

    for line_content, line_num in display_lines:
        # Special markers don't get colorized
        if line_num == -1:
            print(f"{GRAY}{line_content}{RESET}")
        else:
            # Colorize the line before truncating
            colorized_line = colorize_matched_text(line_content, matched_patterns)

            # Handle truncation - need to be careful with ANSI codes
            # Calculate visible length (excluding ANSI codes)
            visible_length = len(re.sub(r"\033\[[0-9;]+m", "", colorized_line))

            if visible_length > 80:
                # Truncate to 80 visible characters
                # This is complex with ANSI codes, so we'll truncate the original and re-colorize
                truncated_line = line_content[:80]
                colorized_line = colorize_matched_text(truncated_line, matched_patterns)
                print(colorized_line + "...")
            else:
                print(colorized_line)

    print(f"{GRAY}{'-' * 40}{RESET}")
    print()

    # Display matched patterns
    print(f"{GRAY}マッチしたパターン:{RESET}")
    for i, pattern in enumerate(matched_patterns):
        letter = chr(ord("a") + i)
        name = pattern.get("name", "unknown")
        print(f"{COLOR_BRIGHT_RED}{letter}: {name}{COLOR_RESET}")

    print()

    # Show prompt
    last_letter = chr(ord("a") + len(matched_patterns) - 1)
    print(f"{COLOR_WHITE}選択してください (a-{last_letter}, ESC: 終了): {COLOR_RESET}", end="", flush=True)


def display_no_match_tui(content: str) -> None:
    """Display TUI when no patterns match.

    Args:
        content: Clipboard text content
    """
    # Display clipboard content (first 3 lines)
    print(f"{GRAY}クリップボード内容:{RESET}")
    print(f"{GRAY}{'-' * 40}{RESET}")

    lines = content.split("\n")
    for i in range(min(3, len(lines))):
        line = lines[i]
        # Truncate if too long
        if len(line) > 80:
            print(line[:80] + "...")
        else:
            print(line)

    print(f"{GRAY}{'-' * 40}{RESET}")
    print()

    # Display no match message
    print(f"{GRAY}マッチする候補がありませんでした{RESET}")
    print()

    # Show prompt
    print(f"{COLOR_WHITE}任意のキーを押して終了: {COLOR_RESET}", end="", flush=True)
