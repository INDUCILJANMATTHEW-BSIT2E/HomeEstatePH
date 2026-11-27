from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Property, User
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admins only")
    return user

def set_status(db: Session, property_id: int, status: str) -> Property:
    item = db.get(Property, property_id)
    if not item:
        raise HTTPException(404, "Property not found")
    item.status = status
    db.commit(); db.refresh(item)
    return item

@router.get("/properties/pending")
def pending(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(Property).filter(Property.status == "pending").all()

@router.patch("/properties/{property_id}/approve")
def approve(property_id: int, db: Session = Depends(get_db),
            admin: User = Depends(require_admin)):
    return set_status(db, property_id, "approved")

@router.patch("/properties/{property_id}/reject")
def reject(property_id: int, db: Session = Depends(get_db),
           admin: User = Depends(require_admin)):
    return set_status(db, property_id, "rejected")