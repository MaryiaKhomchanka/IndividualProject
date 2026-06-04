from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import jwt
from database import get_db
from repositories import BookingRepository, RoomTypeRepository, RoomRepository
from schemas import BookingRequest, BookingResponse, RoomTypeResponse
from services import BookingService, RoomService, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api", tags=["Booking Operations"])

def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    room_repo = RoomRepository(db)
    room_service = RoomService(room_repo)
    return BookingService(
        bookingRepository=BookingRepository(db),
        roomTypeRepository=RoomTypeRepository(db),
        roomService=room_service
    )


def get_current_user_id(authorization: str = Header(...)) -> int:
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("userId")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Session Token Context")

@router.get("/room-types", response_model=list[RoomTypeResponse])
def get_room_types(db: Session = Depends(get_db)):
    return RoomTypeRepository(db).findAll()

@router.post("/bookings", response_model=BookingResponse)
def create_booking(
    request: BookingRequest,
    bookingService: BookingService = Depends(get_booking_service),
    userId: int = Depends(get_current_user_id)
):
    booking = bookingService.createBooking(request, userId)
    return booking

@router.get("/bookings/my", response_model=list[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    userId: int = Depends(get_current_user_id)
):
    repo = BookingRepository(db)
    bookings = repo.findByUserId(userId)
    

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
            roomNumber=room_num
        ))
    return response

@router.post("/bookings/{booking_id}/check-in", response_model=BookingResponse)
def check_in(
    booking_id: int,
    db: Session = Depends(get_db),
    bookingService: BookingService = Depends(get_booking_service),
    userId: int = Depends(get_current_user_id)
):
    updated = bookingService.checkIn(booking_id)
    room = RoomRepository(db).findById(updated.roomId) if updated.roomId else None
    return BookingResponse(
        id=updated.id,
        checkInDate=updated.checkInDate,
        checkOutDate=updated.checkOutDate,
        totalPrice=updated.totalPrice,
        paymentMethod=updated.paymentMethod,
        bookingStatus=updated.bookingStatus,
        paidStatus=updated.paidStatus,
        roomNumber=room.roomNumber if room else None
    )

@router.post("/bookings/{booking_id}/check-out", response_model=BookingResponse)
def check_out(
    booking_id: int,
    bookingService: BookingService = Depends(get_booking_service),
    userId: int = Depends(get_current_user_id)
):
    updated = bookingService.checkOut(booking_id)
    return BookingResponse(
        id=updated.id,
        checkInDate=updated.checkInDate,
        checkOutDate=updated.checkOutDate,
        totalPrice=updated.totalPrice,
        paymentMethod=updated.paymentMethod,
        bookingStatus=updated.bookingStatus,
        paidStatus=updated.paidStatus,
        roomNumber=None 
    )