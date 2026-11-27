from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="customer")

class PropertyType(Base):
    __tablename__ = "property_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    type_id: Mapped[int] = mapped_column(ForeignKey("property_types.id"))
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float)
    city: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")

class PropertyImage(Base):
    __tablename__ = "property_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    file_path: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())