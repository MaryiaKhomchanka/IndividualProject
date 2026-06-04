import enum
from sqlalchemy import Column, Enum, Integer, String, Date, Numeric, ForeignKey, Boolean
from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TOURIST = "TOURIST"

class BookingStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CHECKED_IN = "CHECKED_IN"
    INACTIVE = "INACTIVE"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"

class RoomStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)
    lastName = Column(String, nullable = False)
    username = Column(String, unique = True, index = True, nullable = False)
    email = Column(String, unique = True, index = True, nullable = False)
    passwordHash = Column(String, nullable = False)
    role = Column(Enum(UserRole), default = UserRole.TOURIST, nullable = False)

class RoomType(Base):
    __tablename__ = "room_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Numeric(10, 2), nullable=False)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    roomNumber = Column(String, nullable=False, unique=True)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False)
    roomTypeId = Column(Integer, ForeignKey("room_types.id"), nullable=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    checkInDate = Column(Date, nullable=False)
    checkOutDate = Column(Date, nullable=False)
    totalPrice = Column(Numeric(10, 2), nullable=False)
    paymentMethod = Column(Enum(PaymentMethod), nullable=False)
    bookingStatus = Column(Enum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False)
    paidStatus = Column(Boolean, default=False, nullable=False)
    roomTypeId = Column(Integer, ForeignKey("room_types.id"), nullable=False)
    userId = Column(Integer, ForeignKey("users.id"), nullable=False)
    roomId = Column(Integer, ForeignKey("rooms.id"), nullable=True) # None until Checked In