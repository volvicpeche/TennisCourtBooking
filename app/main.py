from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .core.database import Base, engine
from .api import bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tennis Court Booking")
templates = Jinja2Templates(directory="app/templates")

app.include_router(bookings.router)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
