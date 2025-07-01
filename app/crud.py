from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from . import models, schemas

MAX_DURATION_HOURS_PER_DAY = 2
# Allow booking up to two weeks in advance
MAX_ADVANCE_DAYS = 14
TZ = timezone(timedelta(hours=2))


def auto_confirm_expired_requests(db: Session):
    """Confirm pending bookings older than 48 hours."""
    expire_time = datetime.now(TZ) - timedelta(hours=48)
    expired = db.query(models.booking.Booking).filter(
        and_(models.booking.Booking.booking_status == "pending",
             models.booking.Booking.created_at != None,
             models.booking.Booking.created_at <= expire_time)
    ).all()
    # if column existed without default, ensure new value
    missing = db.query(models.booking.Booking).filter(
        models.booking.Booking.created_at == None
    ).all()
    for book in missing:
        book.created_at = datetime.now(TZ)
    for book in expired:
        book.booking_status = "confirmed"
    if expired or missing:
        db.commit()


def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    auto_confirm_expired_requests(db)
    return db.query(models.booking.Booking).offset(skip).limit(limit).all()


def get_bookings_in_range(db: Session, start, end):
    return db.query(models.booking.Booking).filter(
        and_(models.booking.Booking.start >= start,
             models.booking.Booking.end <= end)
    ).all()


def create_booking(db: Session, booking: schemas.booking.BookingCreate):
    # Basic validations
    start = booking.start
    end = booking.end
    if start.tzinfo is None:
        start = start.replace(tzinfo=TZ)
    else:
        start = start.astimezone(TZ)
    if end.tzinfo is None:
        end = end.replace(tzinfo=TZ)
    else:
        end = end.astimezone(TZ)
    duration = end - start
    if duration.total_seconds() <= 0:
        raise ValueError("End time must be after start time")
    if duration > timedelta(hours=MAX_DURATION_HOURS_PER_DAY):
        raise ValueError("Booking exceeds maximum duration per day")

    # check if booking is too far in future
    if start.date() > (datetime.now(TZ).date() + timedelta(days=MAX_ADVANCE_DAYS)):
        raise ValueError("Booking too far in advance")

    # prevent overlaps
    overlapping = db.query(models.booking.Booking).filter(
        and_(models.booking.Booking.start < end.replace(tzinfo=None),
             models.booking.Booking.end > start.replace(tzinfo=None),
             models.booking.Booking.booking_status != "denied")
    ).first()
    if overlapping:
        raise ValueError("Time slot already booked")

    db_booking = models.booking.Booking(
        name=booking.name,
        building=booking.building.value if hasattr(booking.building, "value") else booking.building,
        start=start.replace(tzinfo=None),
        end=end.replace(tzinfo=None),
        booking_status="pending",
        created_at=datetime.now(TZ)
    )
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


def confirm_booking(db: Session, booking_id: int):
    booking = db.get(models.booking.Booking, booking_id)
    if not booking:
        return None
    booking.booking_status = "confirmed"
    db.commit()
    db.refresh(booking)
    return booking


def deny_booking(db: Session, booking_id: int):
    booking = db.get(models.booking.Booking, booking_id)
    if not booking:
        return None
    booking.booking_status = "denied"
    db.commit()
    db.refresh(booking)
    return booking
