# TennisCourtBooking

A simple FastAPI application to manage tennis court reservations.

## Features
- View bookings by week or day
- Create and cancel bookings with basic validation
- Prevent overlapping reservations

## Running Locally
1. Copy `.env.example` to `.env` and set `DATABASE_URL`
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `uvicorn app.main:app --reload`
4. Access the interactive docs at `http://localhost:8000/docs`

