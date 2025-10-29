## Quick context

This repository is the backend for "PIC - Plataforma Interativa pelo Clima". It's a small FastAPI + SQLAlchemy project that currently stores data in a local SQLite database.

Key files:
- `database.py` — SQLAlchemy engine, `SessionLocal`, and `Base` (declarative base).
- `models.py` — SQLAlchemy ORM models (currently defines `User`).
- `app.py` — (currently empty) intended to hold the FastAPI application and route wiring.
- `requirements.txt` — lists `fastapi`, `uvicorn`, `sqlalchemy`.

## High-level architecture notes for the agent

- Persistence: SQLAlchemy ORM with a SQLite database (file `./pic_plataforma.db`). The DB engine and session factory live in `database.py`. Models import `Base` from that file.
- Service boundary: this repo is just the backend API. Keep all HTTP/API concerns in `app.py` (or in a `routers/` module you add) and keep raw DB logic inside functions that use `SessionLocal` as dependency.
- Why this layout: keeping `engine`, `SessionLocal`, and `Base` in `database.py` makes it easy to share the DB session across endpoints and tests.

## Project-specific conventions and patterns

- Use `SessionLocal` from `database.py` when you need a DB session. Prefer a short-lived session per request and close it afterward. Example pattern (when adding endpoints):

  - Acquire session: `db = SessionLocal()`
  - Use it for queries/commits.
  - Ensure `db.close()` runs (or implement FastAPI dependency to handle lifecycle).

- Models use `DateTime` timestamps with `default=datetime.utcnow` and `onupdate=datetime.utcnow` for `updated_at`.
- `User.phone_number` is declared `unique=True` and `nullable=False` — treat it as an alternate unique identifier.

## Running & debugging (what worked/what to expect)

- Dependencies: install via `pip install -r requirements.txt`.
- Typical development run (once a FastAPI `app` is created in `app.py`):

  uvicorn app:app --reload

- Database initialization: there are no migrations in the repo. Create tables with SQLAlchemy if needed (for example add a small script or call `Base.metadata.create_all(engine)` from `database.py` or a startup event). The agent should not assume an existing DB file unless it is created at runtime.

## Integration points & external dependencies

- External libs: `fastapi`, `uvicorn`, `sqlalchemy` (pins are not provided in this repo).
- Persistence: local SQLite file `pic_plataforma.db` via SQLAlchemy engine in `database.py`.

## What to do when adding endpoints or features (practical rules)

1. Create or reuse a router module (e.g., `routers/users.py`) and register it in `app.py`.
2. Use a DB session dependency (short-lived) rather than global sessions.
3. Keep model changes in `models.py`; use explicit migrations only if you also add Alembic (not present yet).
4. When adding new tests or scripts that touch the DB, prefer an in-memory SQLite (`sqlite:///:memory:`) or a separate test DB file to avoid clobbering local dev data.

## Examples (referencing this codebase)

- To access the `User` model: `from models import User` (models import Base from `database.py`).
- To get a DB session: `from database import SessionLocal` and then `db = SessionLocal()`.

## When to ask the repo owner

- Confirm if you want migrations (Alembic) added for schema evolution.
- Confirm intended path for the FastAPI application (should it be `app.py` or a `src/` layout?). Right now `app.py` is empty.

## Editing / PR guidance for AI agents

- Keep changes minimal and localized (create `routers/` when adding endpoints). Show the patch and tests that exercise new behavior. If you modify `models.py`, include a short migration plan or create-only a `Base.metadata.create_all()` helper and note that migrations are needed for production.

If you see missing behavior (empty `app.py`), propose a small scaffolding PR that:
- creates a `FastAPI()` instance in `app.py`,
- a `/health` route,
- a `startup` event that ensures DB tables exist (calls `Base.metadata.create_all(engine)`),
- and documents the run command in `README.md`.

---
If this file already exists, merge by keeping any custom wording and preserving explicit owner preferences. Ask for clarification if you need to choose between structural directions (e.g., add migrations vs. keep simple create_all).

Please review — tell me what extra conventions, dev commands, or integration details you want included and I'll iterate.
