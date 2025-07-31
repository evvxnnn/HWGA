# Security Ops Logger – Optimized

This repository contains an optimized version of the original **HWGA** project, which serves as a security workflow optimizer for real‑world operations centers. The refactor preserves all existing functionality and UI entry fields while improving performance, clarity and maintainability.

## Key Improvements

- **Centralized logging** – A new `logger.py` module provides a consistent logging configuration that writes logs to `logs/app.log`. All modules obtain a logger via `get_logger()` to record informational messages and errors.
- **Robust database layer** – `database.py` now uses context managers (`with sqlite3.connect(...)`) for all database interactions, ensuring connections are closed correctly and reducing boilerplate. Comprehensive docstrings and error handling have been added alongside detailed logging of failures.
- **Typed and documented functions** – Type hints and explanatory comments were introduced across `database.py` and `logic/event_handler.py` to clarify expected inputs and outputs.
- **Improved event handling** – `logic/event_handler.py` has been refactored to use context-managed database queries, added logging for operations such as loading logs, creating chains and linking logs, and returns empty lists on failure rather than raising unhandled exceptions.
- **Better settings persistence** – `app_settings.py` now logs issues encountered when reading from or writing to the `user_preferences.json` file instead of silently failing, making debugging easier.
- **Application lifecycle logging** – `main.py` logs application start‑up and shutdown events and uses the logger instead of `print()` for exit messages.
- **Automatic directory creation** – The application now ensures both the `data` directory (for the SQLite database) and the `logs` directory exist before writing to them.
- **General cleanup** – Unused imports were removed and comments were improved throughout the codebase for clarity.

These changes collectively enhance reliability, debuggability and maintainability without altering the user interface or the workflow expected by operators.