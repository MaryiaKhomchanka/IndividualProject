import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_booking_endpoint_should_fail_when_payment_mode_is_invalid():
  
    invalid_payload = {
        "checkInDate": "2026-06-01",
        "checkOutDate": "2026-06-05",
        "roomTypeId": 1,
        "paymentMethod": "BITCOIN"  
    }

   
    response = client.post("/api/bookings", json=invalid_payload)


    assert response.status_code == 422  
    

    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "paymentMethod" for err in errors)