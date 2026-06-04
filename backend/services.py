from datetime import datetime, timedelta, timezone, date
from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from models import User, UserRole, Booking, Room, RoomStatus, RoomType, BookingStatus, PaymentMethod
from repositories import UserRepository, BookingRepository, RoomRepository, RoomTypeRepository
from schemas import RegisterRequest, LoginRequest, AuthResponse, UserResponse, UserUpdateRequest, RoomTypeUpdateRequest, BookingUpdateRequest


SECRET_KEY = "change-this-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class PasswordEncoder:
    def __init__(self):
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def encode(self, password: str) -> str:
        return self.context.hash(password)

    def matches(self, rawPassword: str, encodedPassword: str) -> bool:
        return self.context.verify(rawPassword, encodedPassword)


class TokenService:
    def generateToken(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": user.username,
            "userId": user.id,
            "role": user.role.value,
            "exp": expire,
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def validateToken(self, token: str) -> bool:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except Exception:
            return False


class AuthService:
    def __init__(
        self,
        userRepository: UserRepository,
        passwordEncoder: PasswordEncoder,
        tokenService: TokenService,
    ):
        self.userRepository = userRepository
        self.passwordEncoder = passwordEncoder
        self.tokenService = tokenService

    def register(self, request: RegisterRequest) -> UserResponse:
        if self.userRepository.existsByUsername(request.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        if self.userRepository.existsByEmail(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        user = User(
            name=request.name,
            lastName=request.lastName,
            username=request.username,
            email=request.email,
            passwordHash=self.passwordEncoder.encode(request.password),
            role=UserRole.TOURIST,
        )

        saved_user = self.userRepository.save(user)

        return UserResponse.model_validate(saved_user)
        

    def login(self, request: LoginRequest) -> AuthResponse:
        user = self.userRepository.findByUsernameOrEmail(
            request.usernameOrEmail,
            request.usernameOrEmail,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
            )

        if not self.passwordEncoder.matches(request.password, user.passwordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
            )

        token = self.tokenService.generateToken(user)

        return AuthResponse(
            token=token,
            user=UserResponse.model_validate(user),
        )
    
class RoomService:
    def __init__(self, roomRepository: RoomRepository):
        self.roomRepository = roomRepository

    def assignRoomToBooking(self, roomTypeId: int) -> Room:
        room = self.roomRepository.findAvailableByRoomType(roomTypeId)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available physical rooms for this requested type selection."
            )
        room.status = RoomStatus.OCCUPIED
        return self.roomRepository.save(room)

    def releaseRoom(self, roomId: int) -> None:
        room = self.roomRepository.findById(roomId)
        if room:
            room.status = RoomStatus.AVAILABLE
            self.roomRepository.save(room)


class BookingService:
    def __init__(
        self,
        bookingRepository: BookingRepository,
        roomTypeRepository: RoomTypeRepository,
        roomService: RoomService
    ):
        self.bookingRepository = bookingRepository
        self.roomTypeRepository = roomTypeRepository
        self.roomService = roomService
    def createBooking(self, request: any, user_id: int) -> Booking:
        room_type = self.roomTypeRepository.findById(request.roomTypeId)
        if not room_type:
            raise HTTPException(status_code=404, detail="Selected Room Type not found.")
        
        if request.checkInDate < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Check-in date cannot be in the past."
            )
        days = (request.checkOutDate - request.checkInDate).days
        if days <= 0:
            raise HTTPException(status_code=400, detail="Checkout date must be after Check-in date.")

        total_physical_rooms = self.bookingRepository.db.query(Room).filter(
            Room.roomTypeId == request.roomTypeId
        ).count()

        overlapping_active_reservations = self.bookingRepository.db.query(Booking).filter(
            Booking.roomTypeId == request.roomTypeId,
            Booking.bookingStatus.in_([BookingStatus.ACTIVE, BookingStatus.CHECKED_IN]),
            Booking.checkInDate < request.checkOutDate,  
            Booking.checkOutDate > request.checkInDate   
        ).count()

        if overlapping_active_reservations >= total_physical_rooms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sold Out! No vacant units remaining for '{room_type.name}' within this chosen date window."
            )

        total_price = room_type.price * days
        is_paid = True if request.paymentMethod == PaymentMethod.CARD else False

        booking = Booking(
            checkInDate=request.checkInDate,
            checkOutDate=request.checkOutDate,
            totalPrice=total_price,
            paymentMethod=request.paymentMethod,
            bookingStatus=BookingStatus.ACTIVE,
            paidStatus=is_paid,
            roomTypeId=request.roomTypeId,
            userId=user_id,
            roomId=None
        )
        return self.bookingRepository.save(booking)

    def checkIn(self, bookingId: int) -> Booking:
        booking = self.bookingRepository.findById(bookingId)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking records not found.")
        
        if booking.bookingStatus != BookingStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Booking is not in a valid active status state.")
        
        if not booking.paidStatus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot check-in to an unpaid booking. Payment must be settled first."
            )
        
        today = date.today()
        if today < booking.checkInDate or today > booking.checkOutDate:
            raise HTTPException(status_code=400, detail="You can only check-in during your reserved stay dates.")

        assigned_room = self.roomService.assignRoomToBooking(booking.roomTypeId)
        booking.roomId = assigned_room.id
        booking.bookingStatus = BookingStatus.CHECKED_IN
        return self.bookingRepository.save(booking)

    def checkOut(self, bookingId: int) -> Booking:
        booking = self.bookingRepository.findById(bookingId)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking details not found.")
        
        if booking.bookingStatus != BookingStatus.CHECKED_IN:
            raise HTTPException(status_code=400, detail="You must be checked-in to perform a check-out.")

        if date.today() < booking.checkOutDate:
            raise HTTPException(status_code=400, detail="You can only check out on the scheduled day of leave.")

        if booking.roomId:
            self.roomService.releaseRoom(booking.roomId)

        booking.bookingStatus = BookingStatus.INACTIVE
        return self.bookingRepository.save(booking)

#3 iter
class AdminService:
    def __init__(
        self,
        userRepository: UserRepository,
        bookingRepository: BookingRepository,
        roomTypeRepository: RoomTypeRepository
    ):
        self.userRepository = userRepository
        self.bookingRepository = bookingRepository
        self.roomTypeRepository = roomTypeRepository


    def searchUsers(self, query: str) -> list[User]:
        return self.userRepository.searchUsers(query)

    def updateUser(self, user_id: int, request: UserUpdateRequest) -> User:
        user = self.userRepository.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Target user profile not found.")
        
        user.name = request.name
        user.lastName = request.lastName
        user.username = request.username
        user.email = request.email
        user.role = request.role
        
        return self.userRepository.save(user)

    def deleteUser(self, user_id: int) -> None:
        user = self.userRepository.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Target user profile not found.")
        
        user_bookings = self.bookingRepository.findByUserId(user_id)
        for booking in user_bookings:
            if booking.bookingStatus in [BookingStatus.ACTIVE, BookingStatus.CHECKED_IN]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Users with active or checked-in bookings cannot be deleted."
                )
        self.userRepository.delete(user)
 

    def updateRoomType(self, room_type_id: int, request: RoomTypeUpdateRequest) -> RoomType:
        room_type = self.roomTypeRepository.findById(room_type_id)
        if not room_type:
            raise HTTPException(status_code=404, detail="Target Room Type category not found.")
        
        if request.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price validation failed. Room price must be a positive value."
            )
        
        room_type.name = request.name
        room_type.price = request.price
        
        return self.roomTypeRepository.save(room_type)


    def searchBookings(self, query: str) -> list[Booking]:
        return self.bookingRepository.searchBookings(query)

    def updateBooking(self, id: int, request: BookingUpdateRequest) -> Booking:
        booking = self.bookingRepository.findById(id)
        if not booking:
            raise HTTPException(status_code=404, detail="Target booking records not found.")
        
       
        days = (request.checkOutDate - request.checkInDate).days
        if days <= 0:
            raise HTTPException(status_code=400, detail="Checkout date must be after Check-in date.")
            
  
        room_type = self.roomTypeRepository.findById(booking.roomTypeId)
        if room_type:
            booking.totalPrice = room_type.price * days
            
        booking.checkInDate = request.checkInDate
        booking.checkOutDate = request.checkOutDate
        booking.bookingStatus = request.bookingStatus
        booking.paidStatus = request.paidStatus
        
        return self.bookingRepository.save(booking)

    def deleteBooking(self, booking_id: int) -> None:
        booking = self.bookingRepository.findById(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Target booking records not found.")
        

        if booking.bookingStatus in [BookingStatus.ACTIVE, BookingStatus.CHECKED_IN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active bookings cannot be deleted. They must be set to inactive first."
            )
            
        self.bookingRepository.delete(booking)