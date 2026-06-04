from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from auth_controller import router as auth_router 
from booking_controller import router as booking_router 
from admin_controller import router as admin_router
from database import Base, engine, SessionLocal
from models import RoomType, Room, User, UserRole
from services import PasswordEncoder

Base.metadata.create_all(bind=engine) 


db = SessionLocal()
if db.query(RoomType).count() == 0:
    deluxe = RoomType(name="Deluxe Suite", price=150.00)
    standard = RoomType(name="Standard Room", price=80.00)
    db.add_all([deluxe, standard])
    db.commit()
    db.add_all([
        Room(roomNumber="101", roomTypeId=deluxe.id),
        Room(roomNumber="102", roomTypeId=deluxe.id),
        Room(roomNumber="201", roomTypeId=standard.id)
    ])
    db.commit()

if db.query(User).filter(User.role == UserRole.ADMIN).count() == 0:
    encoder = PasswordEncoder()
    admin_user = User(
        name="System",
        lastName="Administrator",
        username="admin",
        email="admin@hotel.com",
        passwordHash=encoder.encode("admin123"), 
        role=UserRole.ADMIN
    )
    db.add(admin_user)
    db.commit()
    print("Default admin profile seeded successfully.")
db.close()


app = FastAPI(title="Hotel Booking Core Engine API") 

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
) 

app.include_router(auth_router) 
app.include_router(booking_router) 
app.include_router(admin_router)


@app.get("/")
def root():
    return {"message": "System Architecture Core Layer Online"}