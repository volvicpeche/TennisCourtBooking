from contextlib import closing
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
import secrets

from app import crud
from app.api import bookings
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine

settings = get_settings()
app = FastAPI(title="Tennis Court Booking")
templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()
_scheduler: BackgroundScheduler | None = None


def _ensure_schema() -> None:
    """Create tables and backfill missing columns for legacy databases."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "bookings" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("bookings")}
    with closing(engine.connect()) as connection:
        try:
            if "created_at" not in columns:
                connection.execute(
                    text("ALTER TABLE bookings ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                )
            if "building" not in columns:
                connection.execute(
                    text("ALTER TABLE bookings ADD COLUMN building TEXT DEFAULT '1 Savoie'")
                )
            connection.commit()
        except SQLAlchemyError:
            connection.rollback()
            raise


def _start_scheduler() -> None:
    """Boot the background scheduler that handles automation jobs."""
    global _scheduler
    if not settings.scheduler_enabled:
        return
    if _scheduler and _scheduler.running:
        return
    _scheduler = BackgroundScheduler(timezone=settings.local_timezone)
    _scheduler.add_job(
        _auto_confirm_job,
        trigger=IntervalTrigger(hours=1, timezone=settings.local_timezone),
        id="auto_confirm_bookings",
        max_instances=1,
        replace_existing=True,
    )
    _scheduler.start()


def _shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None


def _auto_confirm_job() -> None:
    with SessionLocal() as db:
        crud.auto_confirm_expired_requests(db)


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, settings.admin_username)
    correct_password = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.on_event("startup")
def on_startup() -> None:
    _ensure_schema()
    _start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    _shutdown_scheduler()


app.include_router(bookings.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, user: str = Depends(verify_admin)):
    return templates.TemplateResponse("admin.html", {"request": request, "user": user})
