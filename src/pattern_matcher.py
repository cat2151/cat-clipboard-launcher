"""Pattern matching operations."""

import re


def match_patterns(content: str, patterns: list) -> list:
    """Match clipboard content against regex patterns.

    Args:
        content: Clipboard text content
        patterns: List of pattern dictionaries from config

    Returns:
        List of matched pattern dictionaries
    """
    matched = []

    for pattern in patterns:
        try:
            regex = pattern.get("regex", "")
            if re.search(regex, content):
                matched.append(pattern)
        except re.error as e:
            print(f"警告: 無効な正規表現をスキップしました ({pattern.get('name', 'unknown')}): {e}")
            continue

    return matched


def get_matched_line_numbers(content: str, patterns: list) -> list:
    """Get line numbers where patterns match.

    Args:
        content: Clipboard text content
        patterns: List of pattern dictionaries with regex fields

    Returns:
        Sorted list of unique line numbers (0-based) where matches occur
    """
    lines = content.split("\n")
    matched_line_numbers = set()

    for pattern in patterns:
        try:
            regex = pattern.get("regex", "")
            for line_num, line in enumerate(lines):
                if re.search(regex, line):
                    matched_line_numbers.add(line_num)
        except re.error:
            # Skip invalid regex patterns
            continue

    return sorted(matched_line_numbers)


def colorize_matched_text(text: str, patterns: list) -> str:
    """Colorize text based on regex pattern matches.

    Args:
        text: Text to colorize
        patterns: List of pattern dictionaries with regex fields

    Returns:
        Text with ANSI color codes for matched portions
    """
    # ANSI color codes
    COLOR_HIGHLIGHT = "\033[93m"  # Yellow for highlighting matches
    COLOR_RESET = "\033[0m"  # Reset to default color

    # Collect all match positions from all patterns
    matches = []
    for pattern in patterns:
        try:
            regex = pattern.get("regex", "")
            for match in re.finditer(regex, text):
                matches.append((match.start(), match.end()))
        except re.error:
            # Skip invalid regex patterns
            continue

    if not matches:
        return text

    # Sort matches by start position
    matches.sort()

    # Merge overlapping matches
    merged_matches = []
    for start, end in matches:
        if merged_matches and start <= merged_matches[-1][1]:
            # Overlapping or adjacent, merge them
            merged_matches[-1] = (merged_matches[-1][0], max(merged_matches[-1][1], end))
        else:
            merged_matches.append((start, end))

    # Build colorized text
    result = []
    last_pos = 0

    for start, end in merged_matches:
        # Add unmatched text (white/default)
        result.append(text[last_pos:start])
        # Add matched text (highlighted)
        result.append(f"{COLOR_HIGHLIGHT}{text[start:end]}{COLOR_RESET}")
        last_pos = end

    # Add remaining unmatched text
    result.append(text[last_pos:])

    return "".join(result)


def get_display_lines(content: str, matched_patterns: list) -> list:
    """Get lines to display based on matched patterns.

    Args:
        content: Clipboard text content
        matched_patterns: List of matched pattern dictionaries

    Returns:
        List of tuples (line_content, line_number) to display, max 3 lines
    """
    lines = content.split("\n")
    total_lines = len(lines)
    matched_line_numbers = get_matched_line_numbers(content, matched_patterns)

    if not matched_line_numbers:
        # Fallback to first 3 lines if no lines match
        return [(lines[i], i) for i in range(min(3, total_lines))]

    display_lines = []
    num_matches = len(matched_line_numbers)

    if num_matches == 1:
        # 1 match: Show line before, matched line, line after
        match_line = matched_line_numbers[0]

        # Add line before if exists
        if match_line > 0:
            display_lines.append((lines[match_line - 1], match_line - 1))
        else:
            display_lines.append(("(file先頭)", -1))

        # Add matched line
        display_lines.append((lines[match_line], match_line))

        # Add line after if exists
        if match_line < total_lines - 1:
            display_lines.append((lines[match_line + 1], match_line + 1))
        else:
            display_lines.append(("(file終端)", -1))

    elif num_matches == 2:
        # 2 matches: Show line before first match, first match, second match
        first_match = matched_line_numbers[0]
        second_match = matched_line_numbers[1]

        # Add line before first match if exists
        if first_match > 0:
            display_lines.append((lines[first_match - 1], first_match - 1))
        else:
            display_lines.append(("(file先頭)", -1))

        # Add first matched line
        display_lines.append((lines[first_match], first_match))

        # Add second matched line
        display_lines.append((lines[second_match], second_match))

    else:
        # 3+ matches: Show first 3 matched lines
        for i in range(min(3, num_matches)):
            line_num = matched_line_numbers[i]
            display_lines.append((lines[line_num], line_num))

    return display_lines
