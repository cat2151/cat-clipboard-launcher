# GitHub Copilot Instructions for cat-clipboard-launcher

## Code Formatting and Quality

**IMPORTANT: Before committing any code changes, you MUST run the following commands:**

```bash
# Format the code with ruff
ruff format src/ tests/

# Check for linting issues
ruff check src/ tests/

# Fix auto-fixable linting issues
ruff check --fix src/ tests/
```

**Why this is critical:**
- GitHub Actions workflows for automated ruff formatting have been removed for security reasons (PWN Request vulnerability)
- All code must be properly formatted before creating a PR
- Linting issues must be fixed before committing

## Project Structure

This is a Python-based clipboard launcher project. Expected structure:
- `src/` - Main source code
- `tests/` - Test files using pytest
- Configuration files for development tools (ruff, pytest, VSCode)

## Development Standards

### Code Style
- Maximum line length: 120 characters
- Use double quotes for strings
- Use spaces for indentation (4 spaces for Python)
- Follow PEP 8 guidelines (enforced by ruff)
- Organize imports with isort (integrated in ruff)

### Testing
- Use pytest for all tests
- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Run tests before committing: `pytest`

### VSCode Extensions
If working in VSCode, install these recommended extensions:
1. Python (ms-python.python)
2. Pylance (ms-python.vscode-pylance)
3. Ruff (charliermarsh.ruff)
4. EditorConfig for VS Code (editorconfig.editorconfig)

## Best Practices

1. **Always format and lint before committing:**
   ```bash
   ruff format . && ruff check --fix .
   ```

2. **Run tests to ensure nothing breaks:**
   ```bash
   pytest
   ```

3. **Keep commits focused and atomic**
   - One logical change per commit
   - Write clear, descriptive commit messages

4. **Follow the existing code patterns**
   - Match the style of surrounding code
   - Maintain consistency across the codebase

## Security Considerations

- Never commit sensitive data (API keys, passwords, tokens)
- Never commit secrets into source code
- Use environment variables for configuration
- Follow the principle of least privilege

## Common Commands

```bash
# Install development dependencies
pip install ruff pytest

# Format all Python files
ruff format .

# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Run tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_example.py
```

## Workflow

1. Make code changes
2. Format code: `ruff format .`
3. Check and fix linting: `ruff check --fix .`
4. Run tests: `pytest`
5. Commit changes with descriptive message
6. Create PR when ready

## Notes

- The `.vscode/settings.json` file is configured to auto-format on save if you're using VSCode
- The `.editorconfig` file ensures consistent formatting across different editors
- The `ruff.toml` file contains project-specific linting and formatting rules
- The `pytest.ini` file configures pytest behavior
