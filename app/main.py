from fastapi import FastAPI
from .core.database import Base, engine
from .api import bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tennis Court Booking")

app.include_router(bookings.router)
