# TennisCourtBooking

A simple FastAPI application to manage tennis court reservations.

Users must specify their building when booking. Admins can confirm or deny requests.

## Features
- View bookings by week or day
- Create and cancel bookings with basic validation
- Prevent overlapping reservations
- Specify your building when booking
- Admins can confirm or deny reservations

## Prerequisites
- Python 3.10+
- A Supabase project (PostgreSQL) connection string with `sslmode=require`

## Running Locally
1. Copy `.env.example` to `.env` and paste your Supabase Postgres connection string into `DATABASE_URL` (e.g. `postgresql+psycopg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres?sslmode=require`).
2. Install dependencies: `pip install -r requirements.txt`.
3. Start the server: `uvicorn app.main:app --reload` (or `python -m uvicorn app.main:app --reload`).
4. Access the interactive docs at `http://localhost:8000/docs`.
5. Access the admin panel at `/admin` (HTTP Basic auth, default credentials `admin`/`secret`).

## Docker
1. Build the image: `docker build -t tennis-booking .`
2. Run the container, providing your Supabase connection string:
   ```bash
   docker run -p 8000:8000 -e DATABASE_URL="postgresql+psycopg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres?sslmode=require" tennis-booking
   ```
   The API will be available at `http://localhost:8000`.

## Docker Compose
`docker-compose.yml` loads environment variables from `.env` and forwards port 8000:
```bash
docker compose up
```
Ensure `.env` contains a valid Supabase `DATABASE_URL` before starting the stack.

## Testing
Point `DATABASE_URL` at a disposable Supabase (PostgreSQL) database, then run `pytest`.
The suite skips automatically if `DATABASE_URL` is not a Postgres URL to prevent accidental runs against SQLite.
