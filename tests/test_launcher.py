"""Tests for clipboard launcher."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.clipboard import get_clipboard_content, save_to_temp_file, write_output_to_clipboard
from src.config import load_config
from src.executor import execute_command, replace_placeholders
from src.input_handler import get_user_choice
from src.launcher import main
from src.pattern_matcher import (
    colorize_matched_text,
    get_display_lines,
    get_matched_line_numbers,
    match_patterns,
)
from src.tui import display_tui


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid TOML config file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
clipboard_temp_file = "C:/temp/test.txt"

[[patterns]]
name = "Test Pattern"
regex = "test"
command = "echo test"
"""
        )

        config = load_config(config_file)
        assert config["clipboard_temp_file"] == "C:/temp/test.txt"
        assert len(config["patterns"]) == 1
        assert config["patterns"][0]["name"] == "Test Pattern"

    def test_load_nonexistent_config(self, tmp_path, capsys):
        """Test loading a non-existent config file."""
        config_file = tmp_path / "nonexistent.toml"

        with pytest.raises(SystemExit):
            load_config(config_file)

        captured = capsys.readouterr()
        assert "エラー: 設定ファイルが見つかりません" in captured.out

    def test_load_invalid_toml(self, tmp_path, capsys):
        """Test loading an invalid TOML file."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text("invalid toml content [[[")

        with pytest.raises(SystemExit):
            load_config(config_file)

        captured = capsys.readouterr()
        assert "エラー: TOML設定ファイルの構文エラー" in captured.out


class TestGetClipboardContent:
    """Tests for get_clipboard_content function."""

    @patch("src.clipboard.pyperclip.paste")
    def test_get_valid_content(self, mock_paste):
        """Test getting valid clipboard content."""
        mock_paste.return_value = "test content"
        content = get_clipboard_content()
        assert content == "test content"

    @patch("src.clipboard.pyperclip.paste")
    def test_get_empty_clipboard(self, mock_paste, capsys):
        """Test getting empty clipboard."""
        mock_paste.return_value = ""

        with pytest.raises(SystemExit):
            get_clipboard_content()

        captured = capsys.readouterr()
        assert "テキストが取得できません" in captured.out

    @patch("src.clipboard.pyperclip.paste")
    def test_get_clipboard_exception(self, mock_paste, capsys):
        """Test clipboard read exception."""
        mock_paste.side_effect = Exception("Clipboard error")

        with pytest.raises(SystemExit):
            get_clipboard_content()

        captured = capsys.readouterr()
        assert "エラー: クリップボードの読み取りに失敗しました" in captured.out


class TestSaveToTempFile:
    """Tests for save_to_temp_file function."""

    def test_save_content(self, tmp_path):
        """Test saving content to temp file."""
        temp_file = tmp_path / "test.txt"
        content = "test content\nline 2"

        save_to_temp_file(content, temp_file)

        assert temp_file.exists()
        assert temp_file.read_text(encoding="utf-8") == content

    def test_save_creates_directory(self, tmp_path):
        """Test that parent directories are created."""
        temp_file = tmp_path / "subdir" / "test.txt"
        content = "test content"

        save_to_temp_file(content, temp_file)

        assert temp_file.exists()
        assert temp_file.read_text(encoding="utf-8") == content

    def test_save_utf8_without_bom(self, tmp_path):
        """Test that file is saved as UTF-8 without BOM."""
        temp_file = tmp_path / "test.txt"
        content = "日本語テスト"

        save_to_temp_file(content, temp_file)

        # Read raw bytes to check for BOM
        raw_bytes = temp_file.read_bytes()
        # UTF-8 BOM is EF BB BF
        assert not raw_bytes.startswith(b"\xef\xbb\xbf")
        # Content should be readable as UTF-8
        assert temp_file.read_text(encoding="utf-8") == content


class TestMatchPatterns:
    """Tests for match_patterns function."""

    def test_single_match(self):
        """Test matching a single pattern."""
        content = "https://example.com"
        patterns = [
            {"name": "URL", "regex": r"^https?://.*", "command": "start chrome"},
            {"name": "Email", "regex": r"^\w+@\w+\.\w+$", "command": "start outlook"},
        ]

        matched = match_patterns(content, patterns)
        assert len(matched) == 1
        assert matched[0]["name"] == "URL"

    def test_multiple_matches(self):
        """Test matching multiple patterns."""
        content = "#123 is a GitHub issue"
        patterns = [
            {"name": "GitHub Issue", "regex": r"#\d+", "command": "notepad"},
            {"name": "Contains text", "regex": r"GitHub", "command": "notepad"},
        ]

        matched = match_patterns(content, patterns)
        assert len(matched) == 2

    def test_no_matches(self):
        """Test when no patterns match."""
        content = "random text"
        patterns = [
            {"name": "URL", "regex": r"^https?://.*", "command": "start chrome"},
        ]

        matched = match_patterns(content, patterns)
        assert len(matched) == 0

    def test_invalid_regex(self, capsys):
        """Test handling of invalid regex patterns."""
        content = "test"
        patterns = [
            {"name": "Invalid", "regex": r"[invalid(regex", "command": "notepad"},
            {"name": "Valid", "regex": r"test", "command": "notepad"},
        ]

        matched = match_patterns(content, patterns)
        captured = capsys.readouterr()

        # Should warn about invalid regex
        assert "警告: 無効な正規表現をスキップしました" in captured.out
        # Should still match the valid pattern
        assert len(matched) == 1
        assert matched[0]["name"] == "Valid"


class TestColorizeMatchedText:
    """Tests for colorize_matched_text function."""

    def test_single_match_colorization(self):
        """Test colorizing a single match."""
        text = "https://example.com"
        patterns = [{"regex": r"https?://\S+"}]

        result = colorize_matched_text(text, patterns)

        # Should contain color codes
        assert "\033[93m" in result  # Yellow color
        assert "\033[0m" in result  # Reset code
        # Should contain the original text
        assert "https://example.com" in result.replace("\033[93m", "").replace("\033[0m", "")

    def test_multiple_matches_colorization(self):
        """Test colorizing multiple matches."""
        text = "#123 and #456 are issues"
        patterns = [{"regex": r"#\d+"}]

        result = colorize_matched_text(text, patterns)

        # Should have multiple color sections
        assert result.count("\033[93m") == 2  # Two yellow starts
        assert result.count("\033[0m") == 2  # Two resets

    def test_overlapping_matches_merged(self):
        """Test that overlapping matches are merged."""
        text = "test testing"
        patterns = [{"regex": r"test"}, {"regex": r"testing"}]

        result = colorize_matched_text(text, patterns)

        # "test" and "testing" overlap, should be merged
        # First "test" is standalone, second "testing" contains "test"
        # Should have 2 highlighted regions: "test" and "testing"
        assert result.count("\033[93m") == 2

    def test_no_match_no_colorization(self):
        """Test that text without matches is not colorized."""
        text = "plain text"
        patterns = [{"regex": r"https?://"}]

        result = colorize_matched_text(text, patterns)

        # Should not contain any color codes
        assert "\033[93m" not in result
        assert "\033[0m" not in result
        # Should be unchanged
        assert result == text

    def test_empty_patterns_list(self):
        """Test with empty patterns list."""
        text = "some text"
        patterns = []

        result = colorize_matched_text(text, patterns)

        # Should return unchanged text
        assert result == text

    def test_invalid_regex_in_patterns(self):
        """Test that invalid regex patterns are skipped."""
        text = "test text"
        patterns = [{"regex": r"[invalid(regex"}, {"regex": r"test"}]

        result = colorize_matched_text(text, patterns)

        # Should still colorize valid pattern
        assert "\033[93m" in result
        assert "test" in result

    def test_adjacent_matches_merged(self):
        """Test that adjacent matches are merged."""
        text = "abc def"
        patterns = [{"regex": r"abc"}, {"regex": r"def"}]

        result = colorize_matched_text(text, patterns)

        # Should have 2 separate color regions since there's a space between them
        assert result.count("\033[93m") == 2

    def test_partial_line_match(self):
        """Test matching part of a line."""
        text = "before https://example.com after"
        patterns = [{"regex": r"https?://\S+"}]

        result = colorize_matched_text(text, patterns)

        # Check that "before" and "after" are not colored
        assert result.startswith("before ")
        assert result.endswith(" after")
        # Check that the URL is colored
        assert "\033[93mhttps://example.com\033[0m" in result


class TestGetMatchedLineNumbers:
    """Tests for get_matched_line_numbers function."""

    def test_single_line_match(self):
        """Test finding a single matched line."""
        content = "line1\nmatched line\nline3"
        patterns = [{"regex": "matched"}]

        result = get_matched_line_numbers(content, patterns)
        assert result == [1]

    def test_multiple_line_matches(self):
        """Test finding multiple matched lines."""
        content = "match1\nline2\nmatch3\nline4\nmatch5"
        patterns = [{"regex": "match"}]

        result = get_matched_line_numbers(content, patterns)
        assert result == [0, 2, 4]

    def test_multiple_patterns_same_line(self):
        """Test multiple patterns matching the same line."""
        content = "test matched line\nother line"
        patterns = [{"regex": "test"}, {"regex": "matched"}]

        result = get_matched_line_numbers(content, patterns)
        assert result == [0]  # Both patterns match line 0, should appear once

    def test_no_matches(self):
        """Test when no lines match."""
        content = "line1\nline2\nline3"
        patterns = [{"regex": "notfound"}]

        result = get_matched_line_numbers(content, patterns)
        assert result == []

    def test_invalid_regex_skipped(self):
        """Test that invalid regex patterns are skipped."""
        content = "test line\nother line"
        patterns = [{"regex": "[invalid(regex"}, {"regex": "test"}]

        result = get_matched_line_numbers(content, patterns)
        assert result == [0]  # Only valid pattern should match


class TestGetDisplayLines:
    """Tests for get_display_lines function."""

    def test_single_match_with_context(self):
        """Test displaying single matched line with context."""
        content = "line0\nline1\nmatched line\nline3\nline4"
        patterns = [{"regex": "matched"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("line1", 1)  # Line before
        assert result[1] == ("matched line", 2)  # Matched line
        assert result[2] == ("line3", 3)  # Line after

    def test_single_match_at_start(self):
        """Test single match at file start shows marker."""
        content = "matched line\nline1\nline2"
        patterns = [{"regex": "matched"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("(file先頭)", -1)  # File start marker
        assert result[1] == ("matched line", 0)  # Matched line
        assert result[2] == ("line1", 1)  # Line after

    def test_single_match_at_end(self):
        """Test single match at file end shows marker."""
        content = "line0\nline1\nmatched line"
        patterns = [{"regex": "matched"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("line1", 1)  # Line before
        assert result[1] == ("matched line", 2)  # Matched line
        assert result[2] == ("(file終端)", -1)  # File end marker

    def test_single_match_single_line_file(self):
        """Test single match in a single-line file."""
        content = "matched line"
        patterns = [{"regex": "matched"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("(file先頭)", -1)  # File start marker
        assert result[1] == ("matched line", 0)  # Matched line
        assert result[2] == ("(file終端)", -1)  # File end marker

    def test_two_matches(self):
        """Test displaying two matched lines."""
        content = "line0\nmatch1\nline2\nmatch2\nline4"
        patterns = [{"regex": "match"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("line0", 0)  # Line before first match
        assert result[1] == ("match1", 1)  # First matched line
        assert result[2] == ("match2", 3)  # Second matched line

    def test_two_matches_at_start(self):
        """Test two matches starting at file start."""
        content = "match1\nmatch2\nline2"
        patterns = [{"regex": "match"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("(file先頭)", -1)  # File start marker
        assert result[1] == ("match1", 0)  # First matched line
        assert result[2] == ("match2", 1)  # Second matched line

    def test_three_or_more_matches(self):
        """Test displaying first 3 of many matched lines."""
        content = "match0\nmatch1\nmatch2\nmatch3\nmatch4"
        patterns = [{"regex": "match"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("match0", 0)
        assert result[1] == ("match1", 1)
        assert result[2] == ("match2", 2)

    def test_no_matches_fallback(self):
        """Test fallback to first 3 lines when no matches."""
        content = "line0\nline1\nline2\nline3"
        patterns = [{"regex": "notfound"}]

        result = get_display_lines(content, patterns)

        assert len(result) == 3
        assert result[0] == ("line0", 0)
        assert result[1] == ("line1", 1)
        assert result[2] == ("line2", 2)

    def test_empty_content(self):
        """Test with empty content."""
        content = ""
        patterns = [{"regex": "test"}]

        result = get_display_lines(content, patterns)

        # Empty content results in one empty line
        assert len(result) == 1
        assert result[0] == ("", 0)


class TestDisplayTUI:
    """Tests for display_tui function."""

    def test_display_short_content(self, capsys):
        """Test displaying short clipboard content."""
        content = "Short line"
        patterns = [
            {"name": "Pattern 1", "regex": "Short", "command": "cmd1"},
            {"name": "Pattern 2", "regex": "line", "command": "cmd2"},
        ]

        display_tui(content, patterns)
        captured = capsys.readouterr()

        assert "クリップボード内容:" in captured.out
        # Should show file start marker, matched line, file end marker
        assert "(file先頭)" in captured.out
        assert "(file終端)" in captured.out
        assert "a: Pattern 1" in captured.out
        assert "b: Pattern 2" in captured.out
        assert "選択してください (a-b, ESC: 終了):" in captured.out

    def test_display_with_colorization(self, capsys):
        """Test that matches are colorized in display."""
        content = "line0\nhttps://example.com\nline2"
        patterns = [{"name": "URL", "regex": r"https?://\S+", "command": "cmd"}]

        display_tui(content, patterns)
        captured = capsys.readouterr()

        # Should contain ANSI color codes
        assert "\033[93m" in captured.out  # Yellow color for match
        assert "\033[0m" in captured.out  # Reset code

    def test_display_truncates_long_lines(self, capsys):
        """Test that long lines are truncated to 80 characters."""
        content = "line0\n" + "a" * 100 + "\nline2"
        patterns = [{"name": "Pattern 1", "regex": "a+", "command": "cmd1"}]

        display_tui(content, patterns)
        captured = capsys.readouterr()

        # Should show 80 chars plus "..."
        # Remove ANSI codes for checking visible length
        output_lines = captured.out.split("\n")
        # Find the content line (between dashes)
        for line in output_lines:
            if "a" * 50 in line.replace("\033[93m", "").replace("\033[0m", ""):
                # Check it contains ellipsis
                assert "..." in line
                break

    def test_display_shows_matched_lines(self, capsys):
        """Test that matched lines are shown instead of first 3 lines."""
        content = "line1\nline2\nline3\nmatched line\nline5"
        patterns = [{"name": "Pattern 1", "regex": "matched", "command": "cmd1"}]

        display_tui(content, patterns)
        captured = capsys.readouterr()

        # Remove ANSI codes for checking
        clean_output = captured.out.replace("\033[93m", "").replace("\033[0m", "").replace("\033[90m", "")

        # Should show line3 (before), matched line, line5 (after)
        assert "line3" in clean_output
        assert "matched line" in clean_output
        assert "line5" in clean_output
        # Should NOT show line1 and line2
        assert "line1" not in clean_output
        assert "line2" not in clean_output

    def test_display_file_start_marker(self, capsys):
        """Test file start marker is displayed correctly."""
        content = "matched line\nline2\nline3"
        patterns = [{"name": "Pattern 1", "regex": "matched", "command": "cmd1"}]

        display_tui(content, patterns)
        captured = capsys.readouterr()

        clean_output = captured.out.replace("\033[90m", "").replace("\033[0m", "")
        assert "(file先頭)" in clean_output

    def test_display_file_end_marker(self, capsys):
        """Test file end marker is displayed correctly."""
        content = "line1\nline2\nmatched line"
        patterns = [{"name": "Pattern 1", "regex": "matched", "command": "cmd1"}]

        display_tui(content, patterns)
        captured = capsys.readouterr()

        clean_output = captured.out.replace("\033[90m", "").replace("\033[0m", "")
        assert "(file終端)" in clean_output


class TestExecuteCommand:
    """Tests for execute_command function."""

    @patch("src.executor.subprocess.run")
    def test_execute_with_placeholder(self, mock_run, tmp_path):
        """Test executing command with placeholder replacement."""
        temp_file = tmp_path / "test.txt"
        temp_file.write_text("content")

        command = "notepad.exe {CLIPBOARD_FILE}"
        execute_command(command, temp_file)

        expected_command = f"notepad.exe {temp_file.resolve()}"
        mock_run.assert_called_once_with(expected_command, shell=True, check=False)

    @patch("src.executor.subprocess.run")
    def test_execute_without_placeholder(self, mock_run, tmp_path):
        """Test executing command without placeholder."""
        temp_file = tmp_path / "test.txt"
        command = "echo hello"

        execute_command(command, temp_file)

        mock_run.assert_called_once_with("echo hello", shell=True, check=False)

    @patch("src.executor.subprocess.run")
    def test_execute_multiple_placeholders(self, mock_run, tmp_path):
        """Test executing command with multiple placeholders."""
        temp_file = tmp_path / "test.txt"
        temp_file.write_text("content")

        command = "python.exe script.py --input {CLIPBOARD_FILE} --output {CLIPBOARD_FILE}.result"
        execute_command(command, temp_file)

        expected_path = str(temp_file.resolve())
        expected_command = f"python.exe script.py --input {expected_path} --output {expected_path}.result"
        mock_run.assert_called_once_with(expected_command, shell=True, check=False)

    @patch("src.executor.subprocess.run")
    def test_execute_command_exception(self, mock_run, tmp_path, capsys):
        """Test handling of command execution exception."""
        temp_file = tmp_path / "test.txt"
        mock_run.side_effect = Exception("Command failed")

        command = "invalid_command {CLIPBOARD_FILE}"
        execute_command(command, temp_file)

        captured = capsys.readouterr()
        assert "エラー: コマンドの実行に失敗しました" in captured.out


class TestGetUserChoice:
    """Tests for get_user_choice function."""

    @patch("src.input_handler.msvcrt")
    def test_select_first_option(self, mock_msvcrt):
        """Test selecting first option with 'a' key."""
        mock_msvcrt.getch.return_value = b"a"

        choice = get_user_choice(3)
        assert choice == 0

    @patch("src.input_handler.msvcrt")
    def test_select_middle_option(self, mock_msvcrt):
        """Test selecting middle option with 'b' key."""
        mock_msvcrt.getch.return_value = b"b"

        choice = get_user_choice(3)
        assert choice == 1

    @patch("src.input_handler.msvcrt")
    def test_esc_returns_none(self, mock_msvcrt):
        """Test that ESC key returns None."""
        mock_msvcrt.getch.return_value = b"\x1b"

        choice = get_user_choice(3)
        assert choice is None

    @patch("src.input_handler.msvcrt")
    def test_invalid_key_retry(self, mock_msvcrt):
        """Test that invalid keys are ignored and retry occurs."""
        # First invalid key '1', then valid 'a'
        mock_msvcrt.getch.side_effect = [b"1", b"a"]

        choice = get_user_choice(3)
        assert choice == 0
        assert mock_msvcrt.getch.call_count == 2

    @patch("src.input_handler.msvcrt")
    def test_out_of_range_retry(self, mock_msvcrt):
        """Test that out-of-range keys are ignored."""
        # 'd' is index 3, but we only have 2 patterns (0-1)
        mock_msvcrt.getch.side_effect = [b"d", b"a"]

        choice = get_user_choice(2)
        assert choice == 0
        assert mock_msvcrt.getch.call_count == 2


class TestWaitForAnyKey:
    """Tests for wait_for_any_key function."""

    @patch("src.input_handler.msvcrt")
    def test_wait_for_any_key(self, mock_msvcrt):
        """Test that wait_for_any_key waits for a key press."""
        from src.input_handler import wait_for_any_key

        mock_msvcrt.getch.return_value = b"a"

        wait_for_any_key()

        mock_msvcrt.getch.assert_called_once()


class TestDisplayNoMatchTUI:
    """Tests for display_no_match_tui function."""

    def test_display_short_content(self, capsys):
        """Test displaying short clipboard content with no matches."""
        from src.tui import display_no_match_tui

        content = "Short line"

        display_no_match_tui(content)
        captured = capsys.readouterr()

        assert "クリップボード内容:" in captured.out
        assert "Short line" in captured.out
        assert "マッチする候補がありませんでした" in captured.out
        assert "任意のキーを押して終了:" in captured.out

    def test_display_multiline_content(self, capsys):
        """Test displaying multiline clipboard content with no matches."""
        from src.tui import display_no_match_tui

        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        display_no_match_tui(content)
        captured = capsys.readouterr()

        # Should show first 3 lines
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out
        # Should not show lines beyond 3
        assert "Line 4" not in captured.out
        assert "Line 5" not in captured.out

    def test_display_long_line_truncated(self, capsys):
        """Test that long lines are truncated to 80 characters."""
        from src.tui import display_no_match_tui

        content = "a" * 100

        display_no_match_tui(content)
        captured = capsys.readouterr()

        # Should contain ellipsis for truncation
        assert "..." in captured.out


class TestNoMatchIntegration:
    """Integration tests for no-match scenario."""

    @patch("src.clipboard.pyperclip.paste")
    @patch("src.launcher.wait_for_any_key")
    def test_main_with_no_matches(self, mock_wait, mock_paste, tmp_path, capsys):
        """Test main() when no patterns match."""
        from src.launcher import main

        # Create config file
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            f"""
clipboard_temp_file = "{tmp_path / "clipboard.txt"}"

[[patterns]]
name = "URL Pattern"
regex = "^https?://.*"
command = "echo test"
"""
        )

        # Mock clipboard to have non-matching content
        mock_paste.return_value = "just some text"

        # Mock wait_for_any_key to return immediately
        mock_wait.return_value = None

        # Call main - should exit with 0
        with pytest.raises(SystemExit) as exc_info:
            main(config_file)

        assert exc_info.value.code == 0

        # Check that the no-match UI was displayed
        captured = capsys.readouterr()
        assert "クリップボード内容:" in captured.out
        assert "just some text" in captured.out
        assert "マッチする候補がありませんでした" in captured.out
        assert "任意のキーを押して終了:" in captured.out
        assert "終了しました" in captured.out

        # Verify wait_for_any_key was called
        mock_wait.assert_called_once()


class TestIntegration:
    """Integration tests for the launcher."""

    def test_full_workflow_with_match(self, tmp_path):
        """Test complete workflow with successful pattern match."""
        # Create config file
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            f"""
clipboard_temp_file = "{tmp_path / "clipboard.txt"}"

[[patterns]]
name = "Test Pattern"
regex = "test.*content"
command = "echo {{CLIPBOARD_FILE}}"
"""
        )

        # Load config
        config = load_config(config_file)
        assert config["clipboard_temp_file"] == str(tmp_path / "clipboard.txt")

        # Simulate clipboard content
        content = "test clipboard content"

        # Save to temp file
        temp_file = Path(config["clipboard_temp_file"])
        save_to_temp_file(content, temp_file)
        assert temp_file.exists()

        # Match patterns
        matched = match_patterns(content, config["patterns"])
        assert len(matched) == 1
        assert matched[0]["name"] == "Test Pattern"

    def test_no_match_workflow(self, tmp_path):
        """Test workflow when no patterns match."""
        # Create config file
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            f"""
clipboard_temp_file = "{tmp_path / "clipboard.txt"}"

[[patterns]]
name = "URL Pattern"
regex = "^https?://.*"
command = "echo {{CLIPBOARD_FILE}}"
"""
        )

        config = load_config(config_file)
        content = "just some text"

        matched = match_patterns(content, config["patterns"])
        assert len(matched) == 0


class TestArgumentParsing:
    """Tests for command-line argument parsing."""

    def test_main_requires_config_path(self, tmp_path, capsys):
        """Test that main() requires a config_path argument."""
        # Create a minimal valid config
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            f"""
clipboard_temp_file = "{tmp_path / "clipboard.txt"}"

[[patterns]]
name = "Test"
regex = "test"
command = "echo test"
"""
        )

        # Mock clipboard to have content
        with patch("src.clipboard.pyperclip.paste") as mock_paste:
            mock_paste.return_value = "test content"

            # Mock get_user_choice to return None (ESC key) to avoid hanging
            with patch("src.launcher.get_user_choice") as mock_choice:
                mock_choice.return_value = None

                # Call main with config_path - should not raise an error
                with pytest.raises(SystemExit) as exc_info:
                    main(config_file)

                # Should exit with 0 (ESC was pressed)
                assert exc_info.value.code == 0

    def test_main_function_signature(self):
        """Test that main() function signature requires config_path."""
        import inspect

        sig = inspect.signature(main)
        params = sig.parameters

        # Should have exactly one parameter: config_path
        assert len(params) == 1
        assert "config_path" in params

        # config_path should not have a default value
        assert params["config_path"].default == inspect.Parameter.empty


class TestReplacePlaceholders:
    """Tests for replace_placeholders function."""

    def test_replace_single_placeholder(self, tmp_path):
        """Test replacing single placeholder."""
        temp_file = tmp_path / "test.txt"
        text = "command {CLIPBOARD_FILE}"

        result = replace_placeholders(text, temp_file)
        assert result == f"command {temp_file.resolve()}"

    def test_replace_multiple_placeholders(self, tmp_path):
        """Test replacing multiple placeholders."""
        temp_file = tmp_path / "test.txt"
        text = "command --input {CLIPBOARD_FILE} --output {CLIPBOARD_FILE}.result"

        result = replace_placeholders(text, temp_file)
        expected = f"command --input {temp_file.resolve()} --output {temp_file.resolve()}.result"
        assert result == expected

    def test_replace_no_placeholder(self, tmp_path):
        """Test when there's no placeholder to replace."""
        temp_file = tmp_path / "test.txt"
        text = "command without placeholder"

        result = replace_placeholders(text, temp_file)
        assert result == "command without placeholder"


class TestWriteOutputToClipboard:
    """Tests for write_output_to_clipboard function."""

    @patch("src.clipboard.pyperclip.copy")
    def test_write_existing_file(self, mock_copy, tmp_path, capsys):
        """Test writing existing output file to clipboard."""
        output_file = tmp_path / "output.txt"
        output_content = "This is the output content"
        output_file.write_text(output_content, encoding="utf-8")

        write_output_to_clipboard(output_file)

        mock_copy.assert_called_once_with(output_content)
        captured = capsys.readouterr()
        assert "出力をクリップボードに書き戻しました" in captured.out
        assert "26 文字" in captured.out

    def test_write_nonexistent_file(self, tmp_path, capsys):
        """Test handling of non-existent output file."""
        output_file = tmp_path / "nonexistent.txt"

        write_output_to_clipboard(output_file)

        captured = capsys.readouterr()
        assert "警告: 出力ファイルが見つかりません" in captured.out

    @patch("src.clipboard.pyperclip.copy")
    def test_write_empty_file(self, mock_copy, tmp_path, capsys):
        """Test writing empty output file to clipboard."""
        output_file = tmp_path / "empty.txt"
        output_file.write_text("", encoding="utf-8")

        write_output_to_clipboard(output_file)

        mock_copy.assert_called_once_with("")
        captured = capsys.readouterr()
        assert "出力をクリップボードに書き戻しました" in captured.out
        assert "0 文字" in captured.out

    @patch("src.clipboard.pyperclip.copy")
    def test_write_multiline_file(self, mock_copy, tmp_path, capsys):
        """Test writing multiline output file to clipboard."""
        output_file = tmp_path / "multiline.txt"
        output_content = "Line 1\nLine 2\nLine 3"
        output_file.write_text(output_content, encoding="utf-8")

        write_output_to_clipboard(output_file)

        mock_copy.assert_called_once_with(output_content)
        captured = capsys.readouterr()
        assert "出力をクリップボードに書き戻しました" in captured.out


class TestOutputFileIntegration:
    """Integration tests for output_file functionality."""

    @patch("src.executor.subprocess.run")
    @patch("src.clipboard.pyperclip.paste")
    @patch("src.clipboard.pyperclip.copy")
    @patch("src.launcher.get_user_choice")
    def test_output_file_written_to_clipboard_when_enabled(
        self, mock_choice, mock_copy, mock_paste, mock_run, tmp_path
    ):
        """Test that output file is written to clipboard when enabled."""
        # Create config with write_output_to_clipboard enabled at pattern level
        config_file = tmp_path / "config.toml"
        clipboard_temp = tmp_path / "clipboard.txt"

        config_file.write_text(
            f"""
clipboard_temp_file = "{clipboard_temp}"

[[patterns]]
name = "Test Pattern"
regex = "test"
command = "echo test > {{CLIPBOARD_FILE}}.output"
output_file = "{{CLIPBOARD_FILE}}.output"
write_output_to_clipboard = true
"""
        )

        # Mock clipboard content
        mock_paste.return_value = "test content"

        # Mock user selecting first pattern
        mock_choice.return_value = 0

        # Create the output file that would be created by the command
        actual_output_file = Path(str(clipboard_temp.resolve()) + ".output")
        actual_output_file.write_text("Output from command", encoding="utf-8")

        # Run main
        with pytest.raises(SystemExit):
            main(config_file)

        # Verify clipboard was updated with output content
        mock_copy.assert_called_once_with("Output from command")

    @patch("src.executor.subprocess.run")
    @patch("src.clipboard.pyperclip.paste")
    @patch("src.clipboard.pyperclip.copy")
    @patch("src.launcher.get_user_choice")
    def test_output_file_not_written_when_disabled(self, mock_choice, mock_copy, mock_paste, mock_run, tmp_path):
        """Test that output file is not written to clipboard when disabled."""
        # Create config with write_output_to_clipboard disabled at pattern level
        config_file = tmp_path / "config.toml"
        clipboard_temp = tmp_path / "clipboard.txt"

        config_file.write_text(
            f"""
clipboard_temp_file = "{clipboard_temp}"

[[patterns]]
name = "Test Pattern"
regex = "test"
command = "echo test"
output_file = "{{CLIPBOARD_FILE}}.output"
write_output_to_clipboard = false
"""
        )

        # Mock clipboard content
        mock_paste.return_value = "test content"

        # Mock user selecting first pattern
        mock_choice.return_value = 0

        # Run main
        with pytest.raises(SystemExit):
            main(config_file)

        # Verify clipboard was NOT updated
        mock_copy.assert_not_called()

    @patch("src.executor.subprocess.run")
    @patch("src.clipboard.pyperclip.paste")
    @patch("src.clipboard.pyperclip.copy")
    @patch("src.launcher.get_user_choice")
    def test_no_output_file_specified(self, mock_choice, mock_copy, mock_paste, mock_run, tmp_path):
        """Test that clipboard is not updated when no output_file is specified."""
        # Create config without output_file
        config_file = tmp_path / "config.toml"
        clipboard_temp = tmp_path / "clipboard.txt"

        config_file.write_text(
            f"""
clipboard_temp_file = "{clipboard_temp}"

[[patterns]]
name = "Test Pattern"
regex = "test"
command = "echo test"
"""
        )

        # Mock clipboard content
        mock_paste.return_value = "test content"

        # Mock user selecting first pattern
        mock_choice.return_value = 0

        # Run main
        with pytest.raises(SystemExit):
            main(config_file)

        # Verify clipboard was NOT updated (no output_file specified)
        mock_copy.assert_not_called()

    @patch("src.executor.subprocess.run")
    @patch("src.clipboard.pyperclip.paste")
    @patch("src.clipboard.pyperclip.copy")
    @patch("src.launcher.get_user_choice")
    def test_default_write_output_to_clipboard_is_false(
        self, mock_choice, mock_copy, mock_paste, mock_run, tmp_path, capsys
    ):
        """Test that write_output_to_clipboard defaults to false when not specified."""
        # Create config WITHOUT write_output_to_clipboard setting
        config_file = tmp_path / "config.toml"
        clipboard_temp = tmp_path / "clipboard.txt"

        config_file.write_text(
            f"""
clipboard_temp_file = "{clipboard_temp}"

[[patterns]]
name = "Test Pattern"
regex = "test"
command = "echo test"
output_file = "{{CLIPBOARD_FILE}}.output"
"""
        )

        # Mock clipboard content
        mock_paste.return_value = "test content"

        # Mock user selecting first pattern
        mock_choice.return_value = 0

        # Create the output file
        actual_output_file = Path(str(clipboard_temp.resolve()) + ".output")
        actual_output_file.write_text("Output from command", encoding="utf-8")

        # Run main
        with pytest.raises(SystemExit):
            main(config_file)

        # Should NOT write to clipboard (default is false)
        captured = capsys.readouterr()
        assert "出力をクリップボードに書き戻しました" not in captured.out
        # Verify the copy was NOT called
        mock_copy.assert_not_called()


class TestDefaultClipboardTempFile:
    """Tests for default clipboard_temp_file behavior."""

    def test_default_clipboard_temp_file(self, tmp_path):
        """Test that clipboard_temp_file defaults to clipboard_content.txt in current directory."""
        # Create a config file without clipboard_temp_file
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[[patterns]]
name = "Test"
regex = "test"
command = "echo test"
"""
        )

        # Mock clipboard to have content
        with patch("src.clipboard.pyperclip.paste") as mock_paste:
            mock_paste.return_value = "test content"

            # Mock get_user_choice to return None (ESC key) to avoid hanging
            with patch("src.launcher.get_user_choice") as mock_choice:
                mock_choice.return_value = None

                # Call main with config_path - should not raise an error
                with pytest.raises(SystemExit) as exc_info:
                    main(config_file)

                # Should exit with 0 (ESC was pressed)
                assert exc_info.value.code == 0

                # Check that the default temp file was created
                default_temp_file = Path.cwd() / "clipboard_content.txt"
                assert default_temp_file.exists()
                assert default_temp_file.read_text(encoding="utf-8") == "test content"

                # Clean up
                default_temp_file.unlink()
