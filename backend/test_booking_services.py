from datetime import date, timedelta
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from models import Booking, BookingStatus, PaymentMethod, Room, RoomStatus, RoomType
from schemas import BookingRequest
from services import BookingService


def test_create_booking_with_card_should_be_automatically_marked_as_paid():
    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()
    mock_room_service = MagicMock()

    fake_room_type = RoomType(id=1, name="Deluxe Suite", price=150.00)
    mock_room_type_repo.findById.return_value = fake_room_type

    mock_booking_repo.save.side_effect = lambda b: b

    booking_service = BookingService(
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo,
        roomService=mock_room_service
    )

    request_dto = BookingRequest(
        checkInDate=date.today(),
        checkOutDate=date.today() + timedelta(days=2),
        roomTypeId=1,
        paymentMethod=PaymentMethod.CARD
    )

    result = booking_service.createBooking(request_dto, user_id=42)

    assert result.totalPrice == 300.00 #150 * 2 
    assert result.paidStatus is True #Card pays automatically
    assert result.bookingStatus == BookingStatus.ACTIVE
    assert result.userId == 42


def test_create_booking_with_cash_should_default_to_unpaid():

    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()
    mock_room_service = MagicMock()

    fake_room_type = RoomType(id=1, name="Standard Room", price=80.00)
    mock_room_type_repo.findById.return_value = fake_room_type
    mock_booking_repo.save.side_effect = lambda b: b

    booking_service = BookingService(
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo,
        roomService=mock_room_service
    )


    request_dto = BookingRequest(
        checkInDate=date.today(),
        checkOutDate=date.today() + timedelta(days=1),
        roomTypeId=1,
        paymentMethod=PaymentMethod.CASH
    )

    result = booking_service.createBooking(request_dto, user_id=42)

    assert result.totalPrice == 80.00
    assert result.paidStatus is False #Cash stays unpaid until Admin updates it
    assert result.bookingStatus == BookingStatus.ACTIVE


def test_check_in_should_successfully_assign_room_and_change_status():
    # 1. ARRANGE
    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()
    mock_room_service = MagicMock()

    # FIX: Explicitly add paidStatus=True here so it clears our new security gate
    existing_booking = Booking(
        id=10,
        checkInDate=date.today(),
        checkOutDate=date.today() + timedelta(days=1),
        bookingStatus=BookingStatus.ACTIVE,
        paidStatus=True, # Added
        roomTypeId=1,
        roomId=None
    )
    mock_booking_repo.findById.return_value = existing_booking
    
    fake_assigned_room = Room(id=99, roomNumber="101", status=RoomStatus.OCCUPIED)
    mock_room_service.assignRoomToBooking.return_value = fake_assigned_room
    mock_booking_repo.save.side_effect = lambda b: b

    booking_service = BookingService(
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo,
        roomService=mock_room_service
    )

  
    result = booking_service.checkIn(bookingId=10)


    assert result.bookingStatus == BookingStatus.CHECKED_IN
    assert result.roomId == 99
    mock_room_service.assignRoomToBooking.assert_called_once_with(1)

def test_create_booking_in_the_past_should_raise_http_exception():
   
    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()
    mock_room_service = MagicMock()

    fake_room_type = RoomType(id=1, name="Deluxe Suite", price=150.00)
    mock_room_type_repo.findById.return_value = fake_room_type

    booking_service = BookingService(
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo,
        roomService=mock_room_service
    )


    request_dto = BookingRequest(
        checkInDate=date.today() - timedelta(days=5),
        checkOutDate=date.today() + timedelta(days=2),
        roomTypeId=1,
        paymentMethod=PaymentMethod.CARD
    )

   
    with pytest.raises(HTTPException) as exc_info:
        booking_service.createBooking(request_dto, user_id=42)

    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Check-in date cannot be in the past."
    
  
    mock_booking_repo.save.assert_not_called()

def test_check_in_unpaid_booking_should_raise_http_exception():
    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()
    mock_room_service = MagicMock()

    unpaid_booking = Booking(
        id=11,
        checkInDate=date.today(),
        checkOutDate=date.today() + timedelta(days=1),
        bookingStatus=BookingStatus.ACTIVE,
        paidStatus=False, #Unpaid
        roomTypeId=1,
        roomId=None
    )
    mock_booking_repo.findById.return_value = unpaid_booking

    booking_service = BookingService(
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo,
        roomService=mock_room_service
    )


    with pytest.raises(HTTPException) as exc_info:
        booking_service.checkIn(bookingId=11)

  
    assert exc_info.value.status_code == 400
    assert "Cannot check-in to an unpaid booking" in exc_info.value.detail
    
    mock_room_service.assignRoomToBooking.assert_not_called()
    mock_booking_repo.save.assert_not_called()

def test_create_booking_when_sold_out_should_raise_http_exception():

    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()
    mock_room_service = MagicMock()


    fake_room_type = RoomType(id=1, name="Standard Room", price=80.00)
    mock_room_type_repo.findById.return_value = fake_room_type

   
    mock_db = MagicMock()
    mock_booking_repo.db = mock_db
    

    mock_db.query.return_value.filter.return_value.count.side_effect = [1, 1]

    booking_service = BookingService(
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo,
        roomService=mock_room_service
    )

  
    request_dto = BookingRequest(
        checkInDate=date.today(),
        checkOutDate=date.today() + timedelta(days=2),
        roomTypeId=1,
        paymentMethod=PaymentMethod.CARD
    )

  
    with pytest.raises(HTTPException) as exc_info:
        booking_service.createBooking(request_dto, user_id=42)

    
    assert exc_info.value.status_code == 400
    assert "Sold Out!" in exc_info.value.detail
    assert "No vacant units remaining" in exc_info.value.detail
    
    
    mock_booking_repo.save.assert_not_called()