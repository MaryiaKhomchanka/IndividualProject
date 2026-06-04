from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from models import UserRole, BookingStatus, PaymentMethod


class RegisterRequest(BaseModel):
    name: str
    lastName: str
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    usernameOrEmail: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    lastName: str
    username: str
    email: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    token: str
    user: UserResponse

#Iter 2

class RoomTypeResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    class Config:
        from_attributes = True

class BookingRequest(BaseModel):
    checkInDate: date
    checkOutDate: date
    roomTypeId: int
    paymentMethod: PaymentMethod

class BookingResponse(BaseModel):
    id: int
    checkInDate: date
    checkOutDate: date
    totalPrice: Decimal
    paymentMethod: PaymentMethod
    bookingStatus: BookingStatus
    paidStatus: bool
    roomNumber: Optional[str] = None 

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    name: str
    lastName: str
    username: str
    email: str
    role: UserRole


class RoomTypeUpdateRequest(BaseModel):
    name: str
    price: Decimal


class BookingUpdateRequest(BaseModel):
    checkInDate: date
    checkOutDate: date
    bookingStatus: BookingStatus
    paidStatus: bool
