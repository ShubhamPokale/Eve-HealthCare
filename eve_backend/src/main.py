from fastapi import FastAPI

from src.bookings.router import router as bookings_router
from src.diagnostics.router import router as centres_router
from src.payments.router import router as payments_router

app = FastAPI(title="Eve Healthcare")
app.include_router(centres_router)
app.include_router(bookings_router)
app.include_router(payments_router)
