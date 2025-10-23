"""Configuration loading module."""

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
