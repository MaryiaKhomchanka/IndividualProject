from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import jwt
from pydantic import BaseModel
from database import get_db
from repositories import UserRepository, BookingRepository, RoomTypeRepository, RoomRepository
from schemas import (
    UserResponse, UserUpdateRequest, 
    RoomTypeResponse, RoomTypeUpdateRequest, 
    BookingResponse, BookingUpdateRequest
)
from services import AdminService, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/admin", tags=["Administrative Control Panels"])


class MessageResponse(BaseModel):
    message: str

def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(
        userRepository=UserRepository(db),
        bookingRepository=BookingRepository(db),
        roomTypeRepository=RoomTypeRepository(db),
        roomRepository=RoomRepository(db)
    )

def get_current_admin(authorization: str = Header(...)) -> int:
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("role") != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access denied. Administrative privileges required."
            )
        return payload.get("userId")
    except HTTPException as he:
        raise he
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Session Token Context")


@router.get("/users", response_model=list[UserResponse])
def get_users(
    search: str = "",
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    users = admin_service.searchUsers(search)
    return [UserResponse.model_validate(u) for u in users]


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UserUpdateRequest,
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    updated = admin_service.updateUser(user_id, request)
    return UserResponse.model_validate(updated)


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    admin_service.deleteUser(user_id)
    return MessageResponse(message="User profile successfully removed from database records.")


@router.put("/room-types/{room_type_id}", response_model=RoomTypeResponse)
def update_room_type(
    room_type_id: int,
    request: RoomTypeUpdateRequest,
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    updated = admin_service.updateRoomType(room_type_id, request)
    return RoomTypeResponse.model_validate(updated)


@router.get("/bookings", response_model=list[BookingResponse])
def get_bookings(
    search: str = "",
    db: Session = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    bookings = admin_service.searchBookings(search)
    response = []
    
    for b in bookings:
        room_num = None
        if b.roomId:
            room = RoomRepository(db).findById(b.roomId)
            room_num = room.roomNumber if room else None
            
        response.append(BookingResponse(
            id=b.id,
            checkInDate=b.checkInDate,
            checkOutDate=b.checkOutDate,
            totalPrice=b.totalPrice,
            paymentMethod=b.paymentMethod,
            bookingStatus=b.bookingStatus,
            paidStatus=b.paidStatus,
            roomNumber=room_num,
            userId=b.userId
        ))
    return response


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    request: BookingUpdateRequest,
    db: Session = Depends(get_db),
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    updated = admin_service.updateBooking(booking_id, request)
    room = RoomRepository(db).findById(updated.roomId) if updated.roomId else None
    return BookingResponse(
        id=updated.id,
        checkInDate=updated.checkInDate,
        checkOutDate=updated.checkOutDate,
        totalPrice=updated.totalPrice,
        paymentMethod=updated.paymentMethod,
        bookingStatus=updated.bookingStatus,
        paidStatus=updated.paidStatus,
        roomNumber=room.roomNumber if room else None,
        userId=updated.userId
    )


@router.delete("/bookings/{booking_id}", response_model=MessageResponse)
def delete_booking(
    booking_id: int,
    admin_service: AdminService = Depends(get_admin_service),
    admin_id: int = Depends(get_current_admin)
):
    admin_service.deleteBooking(booking_id)
    return MessageResponse(message="Booking stay record permanently removed.")