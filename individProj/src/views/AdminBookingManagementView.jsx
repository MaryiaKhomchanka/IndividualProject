import { useState, useEffect } from "react";
import { AdminApi } from "../api/AdminApi";
import "../styles/AdminDashboard.css"; 

function AdminBookingManagementView() {
  const [bookings, setBookings] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [message, setMessage] = useState({ error: "", success: "" });

  useEffect(() => {
    handleSearch();
  }, []);

  async function handleSearch(e) {
    if (e) e.preventDefault();
    setMessage({ error: "", success: "" });
    try {
      const data = await AdminApi.searchBookings(searchQuery);
      setBookings(data);
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  async function handleSaveBookingUpdate(e) {
    e.preventDefault();
    setMessage({ error: "", success: "" });
    try {
      const updated = await AdminApi.updateBooking(selectedBooking.id, selectedBooking);
      setBookings(bookings.map((b) => (b.id === selectedBooking.id ? updated : b)));
      setMessage((m) => ({ ...m, success: "Stay details shifted and modified." }));
      setSelectedBooking(null);
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  async function handleDeleteClick(bookingId) {
    setMessage({ error: "", success: "" });
    if (!window.confirm("Delete this transaction entry permanently?")) return;

    try {
      const res = await AdminApi.deleteBooking(bookingId);
      setBookings(bookings.filter((b) => b.id !== bookingId));
      setMessage((m) => ({ ...m, success: res.message }));
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '20px', color: '#1e293b', marginBottom: '15px' }}>Booking Management</h2>
      
      {message.error && <p className="error">{message.error}</p>}
      {message.success && <p className="success">{message.success}</p>}

  
      <form onSubmit={handleSearch} className="admin-search-wrapper">
        <input
          type="text"
          placeholder="Filter by context status (e.g., ACTIVE, CHECKED_IN)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="admin-search-field"
        />
        <button type="submit" className="admin-search-submit">Search</button>
      </form>

 
      {selectedBooking && (
        <form onSubmit={handleSaveBookingUpdate} className="card" style={{ marginBottom: "25px", background: "#f8fafc" }}>
          <h3>Edit Booking Record #{selectedBooking.id}</h3>
          <label>Arrival Check-In Date</label>
          <input type="date" value={selectedBooking.checkInDate} onChange={(e) => setSelectedBooking({ ...selectedBooking, checkInDate: e.target.value })} required />
          <label>Departure Checkout Date</label>
          <input type="date" value={selectedBooking.checkOutDate} onChange={(e) => setSelectedBooking({ ...selectedBooking, checkOutDate: e.target.value })} required />
          <label>Status</label>
          <select value={selectedBooking.bookingStatus} onChange={(e) => setSelectedBooking({ ...selectedBooking, bookingStatus: e.target.value })}>
            <option value="ACTIVE">ACTIVE</option>
            <option value="CHECKED_IN">CHECKED_IN</option>
            <option value="INACTIVE">INACTIVE</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
          <label>Payment status</label>
          <select value={selectedBooking.paidStatus ? "true" : "false"} onChange={(e) => setSelectedBooking({ ...selectedBooking, paidStatus: e.target.value === "true" })}>
            <option value="true">PAID Settled Transaction</option>
            <option value="false">UNPAID Pending Counter Balance</option>
          </select>
          <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
            <button type="submit">Push Modifications</button>
            <button type="button" className="link-button" onClick={() => setSelectedBooking(null)}>Cancel</button>
          </div>
        </form>
      )}


      <div className="admin-data-card">
        {bookings.length === 0 ? (
          <p>No recorded stays present matching target criteria logs.</p>
        ) : (
          <table className="admin-data-grid">
            <thead>
              <tr>
                <th>ID</th>
                <th>User ID</th>
                <th>Interval Dates</th>
                <th>Total Bill</th>
                <th>Payment type</th>
                <th>State</th>
                <th>Payment status</th>
                <th>Room</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => (
                <tr key={b.id}>
                  <td>#{b.id}</td>
                  <td><strong>User #{b.userId}</strong></td>
                  <td>{b.checkInDate} to {b.checkOutDate}</td>
                  <td>${b.totalPrice}</td>
                  <td>{b.paymentMethod}</td>
                  <td><strong>{b.bookingStatus}</strong></td>
                  <td style={{ color: b.paidStatus ? "green" : "orange", fontWeight: "bold" }}>
                    {b.paidStatus ? "PAID" : "UNPAID"}
                  </td>
                  <td>{b.roomNumber || "Unassigned"}</td>
                  <td>
                    <div className="admin-grid-actions">
                      <button onClick={() => setSelectedBooking(b)} className="admin-action-btn-edit">
                        Edit
                      </button>
                      <button onClick={() => handleDeleteClick(b.id)} className="admin-action-btn-delete">
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default AdminBookingManagementView;