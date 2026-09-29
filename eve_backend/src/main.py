from fastapi import FastAPI

from src.diagnostics.router import router as centres_router

app = FastAPI(title="Eve Healthcare")
app.include_router(centres_router)
