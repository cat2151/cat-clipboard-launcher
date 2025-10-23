"""Command execution module."""

import subprocess
from pathlib import Path


def replace_placeholders(text: str, temp_file_path: Path) -> str:
    """Replace placeholders in text with actual values.

    Args:
        text: Text containing {CLIPBOARD_FILE} placeholder
        temp_file_path: Path to temporary file

    Returns:
        Text with placeholders replaced
    """
    full_path = str(temp_file_path.resolve())
    return text.replace("{CLIPBOARD_FILE}", full_path)


def execute_command(command: str, temp_file_path: Path) -> None:
    """Execute the selected command with placeholder replacement.

    Args:
        command: Command string with {CLIPBOARD_FILE} placeholder
        temp_file_path: Path to temporary file
    """
    # Replace placeholder with actual temp file path
    command_with_path = replace_placeholders(command, temp_file_path)

    try:
        # Use shell=True for Windows command execution
        subprocess.run(command_with_path, shell=True, check=False)
    except Exception as e:
        print(f"\nエラー: コマンドの実行に失敗しました: {e}")
