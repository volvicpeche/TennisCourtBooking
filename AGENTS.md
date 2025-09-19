# Agents

This document tracks automated agents, background jobs, and third-party integrations used in the TennisCourtBooking project.

## Maintainers

- florian (GitHub: `volvicpeche`): primary contact for automation changes and release approvals

## Agent Inventory

### Built-in automation
- Schema safety check (`app/main.py:9`): on application startup we validate the `bookings` table and add missing `created_at` and `building` columns. Treat this as a lightweight migration helper; review the SQL before deploying to production databases.
- Pending booking auto-confirm (`app/crud.py:14`): `auto_confirm_expired_requests` promotes bookings older than 48 hours from `pending` to `confirmed` every time `get_bookings` runs. It also backfills missing `created_at` values so reporting stays consistent.

### External services
- None configured yet. When introducing a new API integration or automated agent, document its purpose, trigger, credentials, and failure handling here.

## Onboarding Notes

- Python 3.10+ recommended; create a virtual environment and run `pip install -r requirements.txt`.
- Copy `.env.example` to `.env` and set `DATABASE_URL` (SQLite path is fine for local work). FastAPI loads this via `python-dotenv`.
- Optional admin credentials come from `ADMIN_USERNAME` and `ADMIN_PASSWORD`; defaults are `admin` / `secret` and should be overridden outside local development.
- Run `uvicorn app.main:app --reload` for local testing and `pytest` to validate automation behaviour (`tests/test_booking.py`, `tests/test_admin_auth.py`).

## Credentials & Storage

- Store secrets in environment variables or your team-approved secret manager; never commit them. Local `.env` files stay git-ignored (`.gitignore`).
- Production deployments should inject `DATABASE_URL` and admin credentials through the hosting platform (container env vars, CI secrets, etc.).

## Usage Guidelines

- Review the auto-confirm behaviour whenever you change booking lifecycles or status values; adjust the 48-hour window in `app/crud.py` if business rules change.
- If you introduce real background jobs (e.g., using APScheduler), ensure they start within FastAPI's lifespan events and add coverage here plus regression tests.
- When adding or modifying agents, capture owner, environments enabled, alerting or monitoring strategy, and rollback steps. Update this file as part of the same change.
