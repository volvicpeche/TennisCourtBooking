# TennisCourtBooking

A simple FastAPI application to manage tennis court reservations.

## Features
- View bookings by week or day
- Create and cancel bookings with basic validation
- Prevent overlapping reservations

## Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `uvicorn app.main:app --reload`
3. Access the interactive docs at `http://localhost:8000/docs`
4. Access the admin panel at `/admin` (HTTP Basic auth, default credentials `admin`/`secret`)

