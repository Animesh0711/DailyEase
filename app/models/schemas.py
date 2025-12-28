from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str
    address: str
    city: str
    pincode: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    address: str
    city: str
    pincode: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class NewspaperResponse(BaseModel):
    id: int
    name: str
    language: str
    genre: str
    price_daily: float
    price_weekly: float
    price_monthly: float
    description: str

    class Config:
        from_attributes = True

class MilkPackageResponse(BaseModel):
    id: int
    name: str
    quantity_ml: int
    price_daily: float
    price_weekly: float
    price_monthly: float
    description: str

    class Config:
        from_attributes = True

class MagazineResponse(BaseModel):
    id: int
    name: str
    language: str
    genre: str
    is_complementary: bool
    price: float

    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    newspaper_id: Optional[int]
    milk_package_id: Optional[int]
    frequency: str
    is_paused: bool
    total_cost: float
    paused_from: Optional[datetime]
    paused_until: Optional[datetime]

    class Config:
        from_attributes = True

class DeliveryResponse(BaseModel):
    id: int
    subscription_id: int
    scheduled_date: datetime
    status: str
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: int
    amount: float
    status: str
    stripe_payment_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
