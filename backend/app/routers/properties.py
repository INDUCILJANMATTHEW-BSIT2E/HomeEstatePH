from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Property, User
from app.schemas import PropertyCreate, PropertyUpdate
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])

def can_manage(user: User, item: Property) -> bool:
    return user.role == "admin" or item.owner_id == user.id

@router.get("")
def list_properties(db: Session = Depends(get_db)):
    return db.query(Property).filter(Property.status == "approved").all()

@router.post("")
def create_property(data: PropertyCreate, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    if user.role not in ("agent", "owner", "admin"):
        raise HTTPException(403, "Agents/owners only")
    item = Property(**data.model_dump(), owner_id=user.id, status="pending")
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/mine")
def my_properties(db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    return db.query(Property).filter(Property.owner_id == user.id).all()

@router.get("/{property_id}")
def get_property(property_id: int, db: Session = Depends(get_db)):
    item = db.get(Property, property_id)
    if not item or item.status != "approved":
        raise HTTPException(404, "Property not found")
    return item

@router.patch("/{property_id}")
def update_property(property_id: int, data: PropertyUpdate,
                    db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    item = db.get(Property, property_id)
    if not item:
        raise HTTPException(404, "Property not found")
    if not can_manage(user, item):
        raise HTTPException(403, "Not allowed")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit(); db.refresh(item)
    return item

@router.delete("/{property_id}")
def delete_property(property_id: int, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    item = db.get(Property, property_id)
    if not item:
        raise HTTPException(404, "Property not found")
    if not can_manage(user, item):
        raise HTTPException(403, "Not allowed")
    db.delete(item); db.commit()
    return {"deleted": True}