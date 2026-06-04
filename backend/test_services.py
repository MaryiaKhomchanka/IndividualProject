from unittest.mock import MagicMock
from models import User, UserRole
from schemas import RegisterRequest
from services import AuthService

def test_should_successfully_register_a_new_user():

    mock_repo = MagicMock()  
    mock_encoder = MagicMock() 
    mock_token_service = MagicMock() 

    mock_repo.existsByUsername.return_value = False 
    mock_repo.existsByEmail.return_value = False
    

    mock_user = User(
        id=1, 
        name="John", 
        lastName="Doe", 
        username="johndoe", 
        email="john@example.com", 
        role=UserRole.TOURIST
    )
    mock_repo.save.return_value = mock_user 
    mock_encoder.encode.return_value = "encoded_secure_password" 

    auth_service = AuthService(
        userRepository=mock_repo,
        passwordEncoder=mock_encoder,
        tokenService=mock_token_service
    )

    request_dto = RegisterRequest(
        name="John",
        lastName="Doe",
        username="johndoe",
        email="john@example.com",
        password="password123"
    )

    response = auth_service.register(request_dto)

    assert response.id == 1
    assert response.name == "John"
    assert response.lastName == "Doe"
    assert response.username == "johndoe"
    assert response.email == "john@example.com"
    assert response.role == UserRole.TOURIST
  
    mock_repo.existsByUsername.assert_called_once_with("johndoe")
    mock_repo.existsByEmail.assert_called_once_with("john@example.com")
    mock_encoder.encode.assert_called_once_with("password123")
    mock_repo.save.assert_called_once()