from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app import models, schemas
from app.core.config import get_settings

settings = get_settings()
TZ = settings.local_timezone
MAX_DURATION_HOURS_PER_DAY = 2
MAX_ADVANCE_DAYS = 14


def _localize(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


def _strip_timezone(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None)


def auto_confirm_expired_requests(db: Session):
    """Confirm pending bookings older than the configured window."""
    expire_threshold = datetime.now(TZ) - timedelta(hours=settings.auto_confirm_hours)
    expire_threshold_naive = _strip_timezone(expire_threshold)

    expired = db.query(models.booking.Booking).filter(
        and_(
            models.booking.Booking.booking_status == "pending",
            models.booking.Booking.created_at != None,
            models.booking.Booking.created_at <= expire_threshold_naive,
        )
    ).all()

    missing = db.query(models.booking.Booking).filter(
        models.booking.Booking.created_at == None
    ).all()

    now_naive = _strip_timezone(datetime.now(TZ))
    for booking in missing:
        booking.created_at = now_naive
    for booking in expired:
        booking.booking_status = "confirmed"
    if expired or missing:
        db.commit()


def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.booking.Booking).offset(skip).limit(limit).all()


def get_bookings_in_range(db: Session, start, end):
    return db.query(models.booking.Booking).filter(
        and_(
            models.booking.Booking.start >= start,
            models.booking.Booking.end <= end,
        )
    ).all()


def create_booking(db: Session, booking: schemas.booking.BookingCreate):
    start_local = _localize(booking.start)
    end_local = _localize(booking.end)

    duration = end_local - start_local
    if duration.total_seconds() <= 0:
        raise ValueError("End time must be after start time")
    if duration > timedelta(hours=MAX_DURATION_HOURS_PER_DAY):
        raise ValueError("Booking exceeds maximum duration per day")

    if start_local.date() > (datetime.now(TZ).date() + timedelta(days=MAX_ADVANCE_DAYS)):
        raise ValueError("Booking too far in advance")

    start_naive = _strip_timezone(start_local)
    end_naive = _strip_timezone(end_local)

    overlapping = db.query(models.booking.Booking).filter(
        and_(
            models.booking.Booking.start < end_naive,
            models.booking.Booking.end > start_naive,
            models.booking.Booking.booking_status != "denied",
        )
    ).first()
    if overlapping:
        raise ValueError("Time slot already booked")

    db_booking = models.booking.Booking(
        name=booking.name,
        building=booking.building.value if hasattr(booking.building, "value") else booking.building,
        start=start_naive,
        end=end_naive,
        booking_status="pending",
        created_at=_strip_timezone(datetime.now(TZ)),
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
