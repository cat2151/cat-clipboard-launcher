"""Clipboard launcher main script."""

import argparse
import sys
from pathlib import Path

from src.clipboard import get_clipboard_content, save_to_temp_file, write_output_to_clipboard
from src.command import execute_command, replace_placeholders
from src.config import load_config
from src.display import display_tui
from src.patterns import match_patterns
from src.user_input import get_user_choice


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
    # Default to clipboard_content.txt in current directory if not specified
    default_temp_file = Path.cwd() / "clipboard_content.txt"
    temp_file_path = Path(config.get("clipboard_temp_file", default_temp_file))

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

    # Handle output file if specified and write_output_to_clipboard is enabled
    write_to_clipboard = selected_pattern.get("write_output_to_clipboard", False)
    output_file_pattern = selected_pattern.get("output_file")

    if write_to_clipboard and output_file_pattern:
        output_file_path = Path(replace_placeholders(output_file_pattern, temp_file_path))
        write_output_to_clipboard(output_file_path)

    sys.exit(0)


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
