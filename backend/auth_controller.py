from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session 

from database import get_db 
from repositories import UserRepository 
from schemas import RegisterRequest, LoginRequest, AuthResponse, UserResponse
from services import AuthService, PasswordEncoder, TokenService

router = APIRouter(prefix="/api/auth", tags=["Authentication"]) 


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    userRepository = UserRepository(db) 
    passwordEncoder = PasswordEncoder()
    tokenService = TokenService() 

    return AuthService(
        userRepository=userRepository,
        passwordEncoder=passwordEncoder,
        tokenService=tokenService,
    )


@router.post("/register", response_model = UserResponse)
def register(request: RegisterRequest, authService: AuthService = Depends(get_auth_service)):
    return authService.register(request) 


@router.post("/login", response_model = AuthResponse)
def login(request: LoginRequest, authService: AuthService = Depends(get_auth_service)):
    return authService.login(request)