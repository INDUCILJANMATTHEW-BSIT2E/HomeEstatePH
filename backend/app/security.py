from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()
pwd = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def hash_password(value):
    return pwd.hash(value)

def verify_password(value, stored):
    return pwd.verify(value, stored)

def create_token(user_id, role):
    payload = {"sub": str(user_id), "role": role,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

oauth = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(token: str = Depends(oauth), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user