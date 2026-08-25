from fastapi import FastAPI
from app.core.config import settings
from app.database.connection import engine
from app.routes.users import router as users_router
from app.routes.portfolios import router as portfolio_router
from app.routes.holdings import router as holdings_router
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.services.scheduler_service import (
    start_scheduler,
    stop_scheduler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background scheduler
    start_scheduler()

    yield

    # Stop scheduler cleanly
    stop_scheduler()

app = FastAPI(
    title="StockSense API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(portfolio_router)
app.include_router(holdings_router)

@app.get("/")
def home():
    return {
        "message": "StockSense Backend Running 🚀",
        "database": settings.DB_NAME
    }