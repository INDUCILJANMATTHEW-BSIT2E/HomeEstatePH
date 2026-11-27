from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.database import Base, engine
from app import models  # noqa: F401  (registers the tables)
from app.routers.engagement import router as engagement_router

app = FastAPI(title="HomeEstatePH API")
app.include_router(engagement_router)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.routers.auth import router as auth_router
app.include_router(auth_router)
from app.routers.properties import router as properties_router
app.include_router(properties_router)
Base.metadata.create_all(bind=engine)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def home():
    return {"message": "HomeEstatePH API is running"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}