from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from . import models, schemas

MAX_DURATION_HOURS_PER_DAY = 2
MAX_ADVANCE_DAYS = 7


def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.booking.Booking).offset(skip).limit(limit).all()


def get_bookings_in_range(db: Session, start, end):
    return db.query(models.booking.Booking).filter(
        and_(models.booking.Booking.start >= start,
             models.booking.Booking.end <= end)
    ).all()


def create_booking(db: Session, booking: schemas.booking.BookingCreate):
    # Basic validations
    duration = booking.end - booking.start
    if duration.total_seconds() <= 0:
        raise ValueError("End time must be after start time")
    if duration > timedelta(hours=MAX_DURATION_HOURS_PER_DAY):
        raise ValueError("Booking exceeds maximum duration per day")

    # check if booking is too far in future
    if booking.start.date() > (datetime.utcnow().date() + timedelta(days=MAX_ADVANCE_DAYS)):
        raise ValueError("Booking too far in advance")

    # prevent overlaps
    overlapping = db.query(models.booking.Booking).filter(
        and_(models.booking.Booking.start < booking.end,
             models.booking.Booking.end > booking.start)
    ).first()
    if overlapping:
        raise ValueError("Time slot already booked")

    db_booking = models.booking.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def delete_booking(db: Session, booking_id: int):
    booking = db.get(models.booking.Booking, booking_id)
    if booking:
        db.delete(booking)
        db.commit()
    return booking
