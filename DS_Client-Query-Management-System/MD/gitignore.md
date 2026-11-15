# .gitignore

## Purpose

The project's `.gitignore` tells Git which local or generated files not to track.

## Ignored entries

- `__pycache__/`, `*.py[cod]`, and `*$py.class`: Python cache and compiled files.
- `.venv/`, `venv/`, and `ENV/`: common local Python environment folders.
- `.env`: local environment configuration, which may contain secrets.
- `.idea/` and `.vscode/`: editor settings.
- `.DS_Store`: a macOS Finder metadata file.

These rules do not delete files; they only affect what Git normally considers for tracking.
