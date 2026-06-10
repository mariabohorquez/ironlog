---
globs:
  - "backend/**/*.py"
---

- All functions must have type hints on parameters and return values
- Max line length: 100 characters
- Max function length: 50 lines — split if longer
- Import order: stdlib → third-party → local (one blank line between groups)
- Use `|` union syntax for optionals (e.g. `str | None`) not `Optional[str]`
- Never use bare `except:` — always catch specific exceptions
- SQLAlchemy sessions: always use `Depends(get_db)`, never create sessions manually
