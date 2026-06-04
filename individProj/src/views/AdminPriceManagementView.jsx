import { useState, useEffect } from "react";
import { BookingApi } from "../api/BookingApi";
import { AdminApi } from "../api/AdminApi";
import "../styles/AdminDashboard.css";

function AdminPriceManagementView() {
  const [roomTypes, setRoomTypes] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({ name: "", price: "" });
  const [message, setMessage] = useState({ error: "", success: "" });

  useEffect(() => {
    loadRoomTypes();
  }, []);

  async function loadRoomTypes() {
    try {
      const data = await BookingApi.getRoomTypes();
      setRoomTypes(data);
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  function startEdit(type) {
    setEditingId(type.id);
    setEditForm({ name: type.name, price: type.price });
  }

  async function handlePriceUpdateSubmit(e) {
    e.preventDefault();
    setMessage({ error: "", success: "" });
    try {
      const updated = await AdminApi.updateRoomType(editingId, {
        name: editForm.name,
        price: parseFloat(editForm.price),
      });
      setRoomTypes(roomTypes.map((t) => (t.id === editingId ? updated : t)));
      setEditingId(null);
      setMessage((m) => ({ ...m, success: "Room type pricing modified successfully!" }));
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '20px', color: '#1e293b', marginBottom: '15px' }}>Price management</h2>
      
      {message.error && <p className="error">{message.error}</p>}
      {message.success && <p className="success">{message.success}</p>}


      {editingId && (
        <form onSubmit={handlePriceUpdateSubmit} className="card" style={{ marginBottom: "25px", background: "#f8fafc" }}>
          <h3>Modify Category parameters</h3>
          <label>Category Label Name</label>
          <input type="text" value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} required />
          <label>Base Nightly Rate ($)</label>
          <input type="number" step="0.01" value={editForm.price} onChange={(e) => setEditForm({ ...editForm, price: e.target.value })} required />
          <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
            <button type="submit">Update Parameters</button>
            <button type="button" className="link-button" onClick={() => setEditingId(null)}>Cancel</button>
          </div>
        </form>
      )}

      <div className="admin-data-card">
        <table className="admin-data-grid">
          <thead>
            <tr>
              <th>ID</th>
              <th>Room type name</th>
              <th>Price per night</th>
              <th>Controls</th>
            </tr>
          </thead>
          <tbody>
            {roomTypes.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>{t.name}</td>
                <td><strong>${t.price}</strong></td>
                <td>
                  <button onClick={() => startEdit(t)} className="admin-action-btn-edit">
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminPriceManagementView;