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


## Docker
1. Build the image: `docker build -t tennis-booking .`
2. Run the container:
   ```bash
   docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./booking.db tennis-booking
   ```
   The API will be available at `http://localhost:8000`.

## Docker Compose
A `docker-compose.yml` is provided to persist the SQLite database in a volume:
```bash
docker compose up
```
This starts the application on port 8000 and stores `booking.db` in a named volume.
