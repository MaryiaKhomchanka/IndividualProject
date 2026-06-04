import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from unittest.mock import MagicMock
from datetime import date
from main import app
from admin_controller import get_admin_service, get_current_admin
from models import User, UserRole, RoomType, Booking, BookingStatus
from schemas import RoomTypeUpdateRequest
from decimal import Decimal 
from services import AdminService

client = TestClient(app)

@pytest.fixture
def mock_admin_service():
    mock = MagicMock()
    return mock


@pytest.fixture
def setup_admin_override(mock_admin_service):
    app.dependency_overrides[get_admin_service] = lambda: mock_admin_service
    app.dependency_overrides[get_current_admin] = lambda: 999
    
    yield mock_admin_service
    
    app.dependency_overrides.clear()


def test_endpoint_should_deny_access_when_no_auth_header_is_provided():
    response = client.get("/api/admin/users")
    assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_401_UNAUTHORIZED]


def test_endpoint_should_return_403_forbidden_for_non_admin_roles():
    def mock_tourist_guard():
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied. Administrative privileges required.")
        
    app.dependency_overrides[get_current_admin] = mock_tourist_guard
    
    response = client.get("/api/admin/users", headers={"Authorization": "Bearer fake-tourist-token"})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Access denied. Administrative privileges required."
    app.dependency_overrides.clear()


def test_get_users_should_return_serialized_list_of_matching_profiles(setup_admin_override):
    mock_service = setup_admin_override
    
    fake_users = [
        User(id=1, name="John", lastName="Doe", username="johndoe", email="john@test.com", role=UserRole.TOURIST),
        User(id=2, name="Jane", lastName="Smith", username="janesmith", email="jane@test.com", role=UserRole.ADMIN)
    ]
    mock_service.searchUsers.return_value = fake_users


    response = client.get("/api/admin/users?search=john", headers={"Authorization": "Bearer mock-token"})


    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "johndoe"
    assert data[1]["role"] == "ADMIN"
    mock_service.searchUsers.assert_called_once_with("john")


def test_update_user_endpoint_should_pass_payload_and_return_updated_profile(setup_admin_override):
    mock_service = setup_admin_override
    
    updated_user = User(id=5, name="Alex", lastName="Jones", username="alexj", email="alex@test.com", role=UserRole.TOURIST)
    mock_service.updateUser.return_value = updated_user

    payload = {
        "name": "Alex",
        "lastName": "Jones",
        "username": "alexj",
        "email": "alex@test.com",
        "role": "TOURIST"
    }

    response = client.put("/api/admin/users/5", json=payload, headers={"Authorization": "Bearer mock-token"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "alex@test.com"


def test_update_room_type_price_should_modify_base_tariff_margins(setup_admin_override):
    mock_service = setup_admin_override
    
    updated_type = RoomType(id=2, name="Deluxe Premium Suite", price=299.99)
    mock_service.updateRoomType.return_value = updated_type

    payload = {
        "name": "Deluxe Premium Suite",
        "price": 299.99
    }

    response = client.put("/api/admin/room-types/2", json=payload, headers={"Authorization": "Bearer mock-token"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["price"] == "299.99"
    mock_service.updateRoomType.assert_called_once()


def test_get_bookings_should_return_consolidated_reservation_history(setup_admin_override):
    mock_service = setup_admin_override
    
    fake_bookings = [
        Booking(id=201, checkInDate=date(2026, 6, 1), checkOutDate=date(2026, 6, 5), totalPrice=400.00, 
                paymentMethod="CASH", bookingStatus=BookingStatus.ACTIVE, paidStatus=True, roomId=None)
    ]
    mock_service.searchBookings.return_value = fake_bookings

    response = client.get("/api/admin/bookings?search=ACTIVE", headers={"Authorization": "Bearer mock-token"})
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["bookingStatus"] == "ACTIVE"


def test_update_booking_endpoint_should_recalculate_parameters_successfully(setup_admin_override):
    mock_service = setup_admin_override
    
    modified_booking = Booking(id=201, checkInDate=date(2026, 6, 1), checkOutDate=date(2026, 6, 5), totalPrice=400.00, 
                               paymentMethod="CASH", bookingStatus=BookingStatus.INACTIVE, paidStatus=True, roomId=None)
    mock_service.updateBooking.return_value = modified_booking

    payload = {
        "checkInDate": "2026-06-01",
        "checkOutDate": "2026-06-05",
        "bookingStatus": "INACTIVE", 
        "paidStatus": True
    }

    response = client.put("/api/admin/bookings/201", json=payload, headers={"Authorization": "Bearer mock-token"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["bookingStatus"] == "INACTIVE"


def test_delete_booking_route_should_propagate_service_error_exceptions(setup_admin_override):
    mock_service = setup_admin_override
    
    from fastapi import HTTPException
    mock_service.deleteBooking.side_effect = HTTPException(
        status_code=400, 
        detail="Active bookings cannot be deleted. They must be set to inactive first."
    )

    response = client.delete("/api/admin/bookings/77", headers={"Authorization": "Bearer mock-token"})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Active bookings cannot be deleted" in response.json()["detail"]


def test_update_room_type_with_invalid_price_should_raise_http_exception():
    mock_user_repo = MagicMock()
    mock_booking_repo = MagicMock()
    mock_room_type_repo = MagicMock()

    admin_service = AdminService(
        userRepository=mock_user_repo,
        bookingRepository=mock_booking_repo,
        roomTypeRepository=mock_room_type_repo
    )

    fake_room_type = RoomType(id=1, name="Standard Room", price=Decimal("80.00"))
    mock_room_type_repo.findById.return_value = fake_room_type

    invalid_request = RoomTypeUpdateRequest(name="Standard Room", price=Decimal("-15.50"))

    with pytest.raises(HTTPException) as exc_info:
        admin_service.updateRoomType(room_type_id=1, request=invalid_request)

    assert exc_info.value.status_code == 400
    assert "Price validation failed" in exc_info.value.detail
    assert "must be a positive value" in exc_info.value.detail
    
    mock_room_type_repo.save.assert_not_called()