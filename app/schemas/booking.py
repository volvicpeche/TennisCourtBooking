from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict
from enum import Enum

from app.core.config import get_settings

settings = get_settings()
TZ = settings.local_timezone


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

    @field_validator("start", "end", mode="before")
    @classmethod
    def ensure_timezone(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=TZ)
        return value.astimezone(TZ)


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int
    booking_status: str
    created_at: Optional[datetime]

    @field_validator("created_at", mode="before")
    @classmethod
    def ensure_created_timezone(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=TZ)
        return value.astimezone(TZ)

    model_config = ConfigDict(from_attributes=True)
