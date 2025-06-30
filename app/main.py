from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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

app = FastAPI(title="Tennis Court Booking")
templates = Jinja2Templates(directory="app/templates")

app.include_router(bookings.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
