import { useState, useEffect } from "react";
import { BookingApi } from "../api/BookingApi";
import "../styles/CreateBookingView.css";

function CreateBookingView({ openTouristPage }) {
  const [roomTypes, setRoomTypes] = useState([]);
  const [formData, setFormData] = useState({
    checkInDate: "",
    checkOutDate: "",
    roomTypeId: "",
    paymentMethod: "CARD",
  });
  const [message, setMessage] = useState({ error: "", success: "" });

  useEffect(() => {
    BookingApi.getRoomTypes()
      .then((data) => {
        setRoomTypes(data);
        if (data.length > 0) setFormData((f) => ({ ...f, roomTypeId: data[0].id }));
      })
      .catch((err) => setMessage((m) => ({ ...m, error: err.message })));
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage({ error: "", success: "" });
    try {
      await BookingApi.createBooking(formData);
      setMessage((m) => ({ ...m, success: "Room Booked Successfully!" }));
      setTimeout(() => openTouristPage(), 1000);
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  return (
    <div className="booking-page-container">
      <form className="booking-form-card" onSubmit={handleSubmit}>
        <h1>Book a Room</h1>
        {message.error && <p className="error">{message.error}</p>}
        {message.success && <p className="success">{message.success}</p>}

        <label>Check In Date</label>
        <input type="date" required onChange={(e) => setFormData({ ...formData, checkInDate: e.target.value })} />

        <label>Check Out Date</label>
        <input type="date" required onChange={(e) => setFormData({ ...formData, checkOutDate: e.target.value })} />

        <label>Room Category</label>
        <select value={formData.roomTypeId} onChange={(e) => setFormData({ ...formData, roomTypeId: parseInt(e.target.value) })}>
          {roomTypes.map((t) => (
            <option key={t.id} value={t.id}>{t.name} (${t.price}/night)</option>
          ))}
        </select>

        <label>Payment Mode Selection</label>
        <select value={formData.paymentMethod} onChange={(e) => setFormData({ ...formData, paymentMethod: e.target.value })}>
          <option value="CARD">Credit/Debit Card (Automatic Billing)</option>
          <option value="CASH">Pay at Desk on Arrival (Cash)</option>
        </select>

        <button type="submit" className="booking-confirm-btn">Confirm Booking</button>
        <button type="button" className="booking-cancel-btn" onClick={openTouristPage}>Cancel</button>
      </form>
    </div>
  );
}
export default CreateBookingView;