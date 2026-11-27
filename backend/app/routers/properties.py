import uuid
from pathlib import Path
from fastapi import UploadFile, File
from app.models import PropertyImage

UPLOAD_DIR = Path("uploads")
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
SIGNATURES = {".jpg": b"\xff\xd8\xff", ".png": b"\x89PNG\r\n\x1a\n", ".webp": b"RIFF"}
MAX_BYTES = 5 * 1024 * 1024
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

@router.post("/{property_id}/images")
async def upload_image(property_id: int, file: UploadFile = File(...),
                       db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    item = db.get(Property, property_id)
    if not item:
        raise HTTPException(404, "Property not found")
    if not can_manage(user, item):
        raise HTTPException(403, "Not allowed")
    ext = ALLOWED.get(file.content_type)
    if not ext:
        raise HTTPException(415, "Only JPEG, PNG or WebP images")
    UPLOAD_DIR.mkdir(exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / name
    size, first = 0, True
    try:
        with open(dest, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                if first and not chunk.startswith(SIGNATURES[ext]):
                    raise HTTPException(415, "File content does not match its type")
                first = False
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "File too large (max 5 MB)")
                out.write(chunk)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise
    db.add(PropertyImage(property_id=item.id, file_path=name))
    db.commit()
    return {"url": f"/uploads/{name}"}