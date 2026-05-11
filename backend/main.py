from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database
from routers.generate import router as generate_router
from routers.history import router as history_router
from routers.responses import router as responses_router
from routers.results import router as results_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(responses_router)
app.include_router(results_router)
app.include_router(history_router)
