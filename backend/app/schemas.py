from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class PropertyCreate(BaseModel):
    type_id: int
    title: str = Field(min_length=3, max_length=180)
    description: str = ""
    price: float = Field(gt=0)
    city: str
    address: str
    latitude: float | None = None
    longitude: float | None = None