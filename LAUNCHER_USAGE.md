# Launcher Usage Guide

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create or edit `config.toml` in the same directory as the launcher script:

```toml
# Path where clipboard content will be saved temporarily
clipboard_temp_file = "C:/temp/clipboard_content.txt"

# Pattern definitions
[[patterns]]
name = "URL"
regex = "^https?://.*"
command = "start chrome.exe {CLIPBOARD_FILE}"

[[patterns]]
name = "GitHub Issue"
regex = "#\\d+"
command = "notepad.exe {CLIPBOARD_FILE}"
```

### Configuration Fields

- `clipboard_temp_file`: Full path to temporary file for clipboard content
- `patterns`: Array of pattern definitions
  - `name`: Display name for the pattern
  - `regex`: Regular expression to match clipboard content
  - `command`: Command to execute (use `{CLIPBOARD_FILE}` as placeholder)

## Running the Launcher

```bash
# Use default config.toml in script directory
python src/launcher.py

# Use custom config file
python src/launcher.py path/to/config.toml
```

## Usage Flow

1. Copy text to clipboard
2. Run the launcher
3. The launcher will:
   - Display first 3 lines of clipboard content (80 chars max per line)
   - Show matched patterns (a-z)
   - Wait for your choice
4. Press a-z to select a pattern, or ESC to exit
5. Selected command will be executed

## Example Workflow

1. Copy `https://github.com/example/repo` to clipboard
2. Run launcher
3. See "URL" pattern matched
4. Press 'a' to open in browser
5. Chrome opens with the clipboard content

## Testing

Run tests with:

```bash
pytest tests/test_launcher.py -v
```

## Development

Format and lint code:

```bash
# Format code
ruff format src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```
