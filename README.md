HomeEstatePH

Real estate listing prototype: FastAPI, PostgreSQL/PostGIS and Leaflet.

1. Create a database named homeestateph and run: CREATE EXTENSION postgis;
2. In backend/, create .env with DATABASE_URL and JWT_SECRET (not included in this repo).
3. python -m venv .venv, activate it, then pip install -r requirements.txt
4.    uvicorn app.main:app --reload
5.    Open http://127.0.0.1:8000/docs