from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os
from .core.database import Base, engine
from sqlalchemy import inspect, text
from .api import bookings

Base.metadata.create_all(bind=engine)
insp = inspect(engine)
if 'bookings' in insp.get_table_names():
    cols = [c['name'] for c in insp.get_columns('bookings')]
    if 'created_at' not in cols:
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE bookings ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP'))
            conn.commit()
    if 'building' not in cols:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE bookings ADD COLUMN building TEXT DEFAULT '1 Savoie'"))
            conn.commit()

app = FastAPI(title="Tennis Court Booking")
templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username,
        os.getenv("ADMIN_USERNAME", "admin"),
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        os.getenv("ADMIN_PASSWORD", "secret"),
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

app.include_router(bookings.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, user: str = Depends(verify_admin)):
    return templates.TemplateResponse("admin.html", {"request": request})
