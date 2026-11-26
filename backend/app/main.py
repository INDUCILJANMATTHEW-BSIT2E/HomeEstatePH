from fastapi import FastAPI

app = FastAPI(title="HomeEstatePH API")

@app.get("/")
def home():
    return {"message": "HomeEstatePH API is running"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}