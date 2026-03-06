from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, POSTGRES_URL, engine
from app.core.middleware import smart_cors_middleware
from app.endpoints import auth, leads, payments, projects, tracking, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(POSTGRES_URL)
    yield


app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)

app.middleware("http")(smart_cors_middleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(leads.router)
app.include_router(tracking.router)
app.include_router(payments.router)


@app.get("/health")
def health():
    return {"status": "ok"}
