from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class BuildingEnum(str, Enum):
    s1 = "1 Savoie"
    s3 = "3 Savoie"
    s5 = "5 Savoie"
    s7 = "7 Savoie"
    s9 = "9 Savoie"
    s11 = "11 Savoie"


class BookingBase(BaseModel):
    name: str
    building: BuildingEnum
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
