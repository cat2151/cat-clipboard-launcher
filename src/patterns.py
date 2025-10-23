"""Pattern matching module."""

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
