"""Configuration loading and management."""

import sys
from pathlib import Path

import tomllib


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


def get_temp_file_path(config: dict) -> Path:
    """Get temporary file path from config or use default.

    Args:
        config: Configuration dictionary

    Returns:
        Path to temporary file
    """
    default_temp_file = Path.cwd() / "clipboard_content.txt"
    return Path(config.get("clipboard_temp_file", default_temp_file))


def get_patterns(config: dict) -> list:
    """Get patterns list from config.

    Args:
        config: Configuration dictionary

    Returns:
        List of pattern dictionaries

    Raises:
        SystemExit: If no patterns are defined
    """
    patterns = config.get("patterns", [])
    if not patterns:
        print("エラー: 設定ファイルにpatternsが定義されていません")
        sys.exit(1)
    return patterns
