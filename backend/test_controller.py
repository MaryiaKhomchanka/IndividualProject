import pytest
from fastapi.testclient import TestClient 
from main import app

client = TestClient(app) 

def test_register_should_fail_when_email_has_incorrect_format():

    invalid_email = {
        "name": "Jane",
        "lastName": "Doe",
        "username": "janedoe",
        "email": "Jane",  #Invalid Email Format
        "password": "JaneDoe123"
    }

    
    response = client.post("/api/auth/register", json=invalid_email)

   
    assert response.status_code == 422  #Unprocessable entity validation error
    

    errors = response.json()["detail"]
    assert any(err["loc"][-1] == "email" for err in errors)