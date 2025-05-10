from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, favorites
import os

app = FastAPI(title="Orbitune API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])

@app.get("/")

def root():
    return {"message": "Orbitune backend is alive"}
