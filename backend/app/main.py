from fastapi import FastAPI
from app.database import Base, engine
from app import models  # noqa: F401  (registers the tables)

app = FastAPI(title="HomeEstatePH API")
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "HomeEstatePH API is running"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}