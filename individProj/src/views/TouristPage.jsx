import { useState, useEffect } from "react"; 
import { useAuth } from "../context/AuthContext";
import { BookingApi } from "../api/BookingApi"; 
import "../styles/TouristPage.css";

function TouristPage({ openLoginPage, openBookingPage, openServicesPage }) {
  const { user, logout } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      BookingApi.getMyBookings()
        .then(setBookings)
        .catch((err) => setError(err.message));
    }
  }, [user]);

  function handleLogout() {
    logout();
    openLoginPage();
  }

  async function handleCheckIn(id) {
    try {
      const updatedBooking = await BookingApi.checkIn(id);
      setBookings(bookings.map((b) => (b.id === id ? updatedBooking : b)));
    } catch (err) {
      alert(err.message);
    }
  }

  async function handleCheckOut(id) {
    try {
      const updatedBooking = await BookingApi.checkOut(id);
      setBookings(bookings.map((b) => (b.id === id ? updatedBooking : b)));
    } catch (err) {
      alert(err.message);
    }
  }

  if (!user) {
    return (
      <div className="tourist-page" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="profile-card" style={{ textAlign: "center", maxWidth: "400px" }}>
          <h1>You are not logged in</h1>
          <button onClick={openLoginPage} className="tourist-btn btn-primary">Go to Login</button>
        </div>
      </div>
    );
  }

  return (
    <div className="tourist-page">
      <div className="tourist-layout">
        
        <div className="profile-card">
          <h1>Welcome, {user.name}!</h1>
          <p style={{ color: "#94a3b8" }}>You are logged in as a tourist.</p>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Role:</strong> {user.role}</p>

          <div className="tourist-nav-actions">
            <button onClick={openBookingPage} className="tourist-btn btn-primary">Book New Stay</button>
            <button onClick={openServicesPage} className="tourist-btn btn-secondary">Browse Facilities</button>
            <button onClick={handleLogout} className="tourist-btn btn-danger">Logout</button>
          </div>
        </div>

        <h3 className="section-heading">Your Stay Records</h3>
        {error && <p className="error">{error}</p>}
        
        {bookings.length === 0 ? (
          <p style={{ color: "#94a3b8" }}>No reservation parameters populated.</p>
        ) : (
          bookings.map((b) => (
            <div key={b.id} className="booking-record-card">
              <p><strong>Stay Interval:</strong> {b.checkInDate} to {b.checkOutDate}</p>
              <p>
                <strong>Billing Settlement:</strong> ${b.totalPrice} ({b.paymentMethod}) - 
                <span style={{ color: b.paidStatus ? "#4ade80" : "#fb923c", fontWeight: "bold" }}>
                  {b.paidStatus ? " PAID" : " UNPAID"}
                </span>
              </p>
              <p><strong>Status state:</strong> <span className="status-tag">{b.bookingStatus}</span></p>
              
              {b.roomNumber && (
                <h3 className="room-alert-banner">
                  Assigned Room Number: {b.roomNumber}
                </h3>
              )}

              {b.bookingStatus === "ACTIVE" && (
                <button onClick={() => handleCheckIn(b.id)} className="booking-action-btn btn-checkin">
                  Check In
                </button>
              )}
              {b.bookingStatus === "CHECKED_IN" && (
                <button onClick={() => handleCheckOut(b.id)} className="booking-action-btn btn-checkout">
                  Check Out
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default TouristPage;