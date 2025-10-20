"""Clipboard launcher main script."""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import tomllib

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"  # Bright green for clipboard content
COLOR_WHITE = "\033[97m"  # Bright white for clipboard content headers
COLOR_BRIGHT_RED = "\033[91m"  # Bright red for pattern options

# Windows-specific import
try:
    import msvcrt
except ImportError:
    # For testing on non-Windows platforms
    msvcrt = None

try:
    import pyperclip
except ImportError:
    print("エラー: pyperclipがインストールされていません")
    print("pip install pyperclip を実行してください")
    sys.exit(1)


def load_config(config_path: Path) -> dict:
    """Load TOML configuration file.

    Args:
        config_path: Path to config.toml file

    Returns:
        Dictionary containing config data

    Raises:
        SystemExit: If config file is not found or has syntax errors
    """
    if not config_path.exists():
        print(f"エラー: 設定ファイルが見つかりません ({config_path})")
        sys.exit(1)

    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"エラー: TOML設定ファイルの構文エラー: {e}")
        sys.exit(1)


def get_clipboard_content() -> str:
    """Get text content from clipboard.

    Returns:
        Clipboard text content

    Raises:
        SystemExit: If clipboard is empty or not text
    """
    try:
        content = pyperclip.paste()
        if not content:
            print("テキストが取得できません")
            sys.exit(0)
        return content
    except Exception as e:
        print(f"エラー: クリップボードの読み取りに失敗しました: {e}")
        sys.exit(1)


def save_to_temp_file(content: str, temp_file_path: Path) -> None:
    """Save clipboard content to temporary file.

    Args:
        content: Text content to save
        temp_file_path: Path to temporary file

    Raises:
        SystemExit: If file write fails
    """
    try:
        # Ensure parent directory exists
        temp_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"エラー: クリップボード内容の保存に失敗しました: {e}")
        sys.exit(1)


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


def display_tui(content: str, matched_patterns: list) -> None:
    """Display TUI with clipboard content and matched patterns.

    Args:
        content: Clipboard text content
        matched_patterns: List of matched pattern dictionaries
    """
    # Display clipboard content (first 3 lines, max 80 chars each)
    # Using white for headers and green for content
    print(f"{COLOR_WHITE}クリップボード内容:{COLOR_RESET}")
    print(f"{COLOR_WHITE}{'-' * 40}{COLOR_RESET}")

    lines = content.split("\n")
    for i, line in enumerate(lines[:3]):
        if len(line) > 80:
            print(f"{COLOR_GREEN}{line[:80]}...{COLOR_RESET}")
        else:
            print(f"{COLOR_GREEN}{line}{COLOR_RESET}")

    print(f"{COLOR_WHITE}{'-' * 40}{COLOR_RESET}")
    print()

    # Display matched patterns
    # Using bright red for pattern options
    print(f"{COLOR_WHITE}マッチしたパターン:{COLOR_RESET}")
    for i, pattern in enumerate(matched_patterns):
        letter = chr(ord("a") + i)
        name = pattern.get("name", "unknown")
        print(f"{COLOR_BRIGHT_RED}{letter}: {name}{COLOR_RESET}")

    print()

    # Show prompt
    last_letter = chr(ord("a") + len(matched_patterns) - 1)
    print(f"{COLOR_WHITE}選択してください (a-{last_letter}, ESC: 終了): {COLOR_RESET}", end="", flush=True)


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


def execute_command(command: str, temp_file_path: Path) -> None:
    """Execute the selected command with placeholder replacement.

    Args:
        command: Command string with {CLIPBOARD_FILE} placeholder
        temp_file_path: Path to temporary file
    """
    # Replace placeholder with actual temp file path
    full_path = str(temp_file_path.resolve())
    command_with_path = command.replace("{CLIPBOARD_FILE}", full_path)

    try:
        # Use shell=True for Windows command execution
        subprocess.run(command_with_path, shell=True, check=False)
    except Exception as e:
        print(f"\nエラー: コマンドの実行に失敗しました: {e}")


def main(config_path: Path) -> None:
    """Main entry point for clipboard launcher.

    Args:
        config_path: Path to config file (required)
    """

    # Load configuration
    config = load_config(config_path)

    # Get clipboard content
    content = get_clipboard_content()

    # Save to temporary file
    temp_file_path = Path(config.get("clipboard_temp_file", ""))
    if not temp_file_path:
        print("エラー: 設定ファイルにclipboard_temp_fileが定義されていません")
        sys.exit(1)

    save_to_temp_file(content, temp_file_path)

    # Match patterns
    patterns = config.get("patterns", [])
    if not patterns:
        print("エラー: 設定ファイルにpatternsが定義されていません")
        sys.exit(1)

    matched_patterns = match_patterns(content, patterns)

    # Check if any patterns matched
    if not matched_patterns:
        print("マッチするパターンがありません")
        sys.exit(0)

    # Warn if too many patterns matched
    if len(matched_patterns) > 26:
        print(f"警告: マッチしたパターンが26個を超えています ({len(matched_patterns)}個)")
        matched_patterns = matched_patterns[:26]

    # Display TUI
    display_tui(content, matched_patterns)

    # Get user choice
    choice_index = get_user_choice(len(matched_patterns))

    if choice_index is None:
        # ESC pressed, exit without doing anything
        print("\n終了しました")
        sys.exit(0)

    # Execute selected command
    selected_pattern = matched_patterns[choice_index]
    command = selected_pattern.get("command", "")

    if not command:
        print("\nエラー: 選択されたパターンにコマンドが定義されていません")
        sys.exit(1)

    print(f"\n実行中: {selected_pattern.get('name', 'unknown')}")
    execute_command(command, temp_file_path)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Clipboard launcher - Launch applications based on clipboard content")
    parser.add_argument(
        "--config-filename",
        type=Path,
        required=True,
        help="Path to the TOML configuration file (required)",
    )
    args = parser.parse_args()

    main(args.config_filename)
