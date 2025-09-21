from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=List[schemas.Booking])
def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_bookings(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Booking)
def create_new_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_booking(db, booking)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@router.delete("/{booking_id}")
def delete_existing_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = crud.delete_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"ok": True}


@router.post("/{booking_id}/confirm", response_model=schemas.Booking)
def confirm_existing_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = crud.confirm_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/{booking_id}/deny", response_model=schemas.Booking)
def deny_existing_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = crud.deny_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
