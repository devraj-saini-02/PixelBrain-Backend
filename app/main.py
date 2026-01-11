from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, auth, image, search
from database import engine, Base
import models
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="PixelBrain API", version="0.1.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(image.router)
app.include_router(search.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "PixelBrain API is up", "version": app.version}

