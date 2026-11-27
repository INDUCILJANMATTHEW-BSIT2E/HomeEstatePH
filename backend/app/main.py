from fastapi import FastAPI
from app.database import Base, engine
from app import models  # noqa: F401  (registers the tables)

app = FastAPI(title="HomeEstatePH API")
from app.routers.auth import router as auth_router
app.include_router(auth_router)
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "HomeEstatePH API is running"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}