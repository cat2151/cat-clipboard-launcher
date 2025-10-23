"""Clipboard operations module."""

import sys
from pathlib import Path

try:
    import pyperclip
except ImportError:
    print("エラー: pyperclipがインストールされていません")
    print("pip install pyperclip を実行してください")
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


def write_output_to_clipboard(output_file_path: Path) -> None:
    """Read output file and write its content to clipboard.

    Args:
        output_file_path: Path to output file
    """
    try:
        if not output_file_path.exists():
            print(f"警告: 出力ファイルが見つかりません ({output_file_path})")
            return

        with open(output_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        pyperclip.copy(content)
        print(f"出力をクリップボードに書き戻しました ({len(content)} 文字)")
    except Exception as e:
        print(f"警告: 出力ファイルの読み取りまたはクリップボードへの書き込みに失敗しました: {e}")
