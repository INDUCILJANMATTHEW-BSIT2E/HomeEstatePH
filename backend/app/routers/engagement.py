from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Property, Favorite, Inquiry, User
from app.security import get_current_user

router = APIRouter(prefix="/api/v1", tags=["favorites and inquiries"])

class InquiryIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

def approved_or_404(db: Session, property_id: int) -> Property:
    item = db.get(Property, property_id)
    if not item or item.status != "approved":
        raise HTTPException(404, "Property not found")
    return item

@router.post("/properties/{property_id}/favorite")
def add_favorite(property_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    approved_or_404(db, property_id)
    exists = db.query(Favorite).filter_by(user_id=user.id, property_id=property_id).first()
    if not exists:
        db.add(Favorite(user_id=user.id, property_id=property_id))
        db.commit()
    return {"favorited": True}

@router.delete("/properties/{property_id}/favorite")
def remove_favorite(property_id: int, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    db.query(Favorite).filter_by(user_id=user.id, property_id=property_id).delete()
    db.commit()
    return {"favorited": False}

@router.get("/me/favorites")
def my_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (db.query(Property)
              .join(Favorite, Favorite.property_id == Property.id)
              .filter(Favorite.user_id == user.id, Property.status == "approved")
              .all())

@router.post("/properties/{property_id}/inquiries")
def send_inquiry(property_id: int, data: InquiryIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    approved_or_404(db, property_id)
    message = data.message.strip()
    if not message:
        raise HTTPException(422, "Message cannot be empty")
    inquiry = Inquiry(property_id=property_id, customer_id=user.id, message=message)
    db.add(inquiry); db.commit(); db.refresh(inquiry)
    return inquiry

@router.get("/me/inquiries")
def my_inquiries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Inquiry).filter(Inquiry.customer_id == user.id).all()

@router.get("/me/received-inquiries")
def received_inquiries(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (db.query(Inquiry)
              .join(Property, Property.id == Inquiry.property_id)
              .filter(Property.owner_id == user.id)
              .all())