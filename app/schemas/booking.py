from datetime import datetime
from pydantic import BaseModel


class BookingBase(BaseModel):
    name: str
    start: datetime
    end: datetime


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int
    booking_status: str
    created_at: datetime

    class Config:
        orm_mode = True
