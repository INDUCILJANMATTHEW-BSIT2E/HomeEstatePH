from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RegisterIn, LoginIn
from app.security import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")
    user = User(full_name=data.full_name, email=email,
                password_hash=hash_password(data.password), role="customer")
    db.add(user); db.commit(); db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_token(user.id, user.role),
            "token_type": "bearer"}