from sqlalchemy.orm import Session
from models import User, RoomType, Room, Booking, RoomStatus

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def findByUsername(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def findByEmail(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def findByUsernameOrEmail(self, username: str, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def existsByUsername(self, username: str) -> bool:
        return self.findByUsername(username) is not None

    def existsByEmail(self, email: str) -> bool:
        return self.findByEmail(email) is not None
    
    #3 iter
    def searchUsers(self, query: str) -> list[User]:
        return (
            self.db.query(User)
            .filter((User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%")))
            .all()
        )

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()


#Iter 2

class RoomTypeRepository:
    def __init__(self, db: Session):
        self.db = db
    def findAll(self) -> list[RoomType]:
        return self.db.query(RoomType).all()
    def findById(self, room_type_id: int) -> RoomType | None:
        return self.db.query(RoomType).filter(RoomType.id == room_type_id).first()
    
    #Iter 3
    def save(self, room_type: RoomType) -> RoomType:
        self.db.add(room_type)
        self.db.commit()
        self.db.refresh(room_type)
        return room_type

class RoomRepository:
    def __init__(self, db: Session):
        self.db = db
    def findAvailableByRoomType(self, room_type_id: int) -> Room | None:
        return self.db.query(Room).filter(
            Room.roomTypeId == room_type_id,
            Room.status == RoomStatus.AVAILABLE
        ).first()
    def findById(self, room_id: int) -> Room | None:
        return self.db.query(Room).filter(Room.id == room_id).first()
    def save(self, room: Room) -> Room:
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

class BookingRepository:
    def __init__(self, db: Session):
        self.db = db
    def save(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    def findById(self, booking_id: int) -> Booking | None:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()
    def findByUserId(self, user_id: int) -> list[Booking]:
        return self.db.query(Booking).filter(Booking.userId == user_id).all()
    
    #Iter 3
    
    def searchBookings(self, query: str) -> list[Booking]:
        # Looks up matching entries via status codes or basic identifier matching
        return (
            self.db.query(Booking)
            .filter(Booking.bookingStatus.ilike(f"%{query}%") | Booking.paymentMethod.ilike(f"%{query}%"))
            .all()
        )

    def delete(self, booking: Booking) -> None:
        self.db.delete(booking)
        self.db.commit()


