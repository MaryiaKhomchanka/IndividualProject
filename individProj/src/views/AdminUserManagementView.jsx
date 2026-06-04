import { useState, useEffect } from "react";
import { AdminApi } from "../api/AdminApi";
import "../styles/AdminDashboard.css"; 

function AdminUserManagementView() {
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);
  const [message, setMessage] = useState({ error: "", success: "" });

  useEffect(() => {
    handleSearch();
  }, []);

  async function handleSearch(e) {
    if (e) e.preventDefault();
    setMessage({ error: "", success: "" });
    try {
      const data = await AdminApi.searchUsers(searchQuery);
      setUsers(data);
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  async function handleSaveUserUpdate(e) {
    e.preventDefault();
    setMessage({ error: "", success: "" });
    try {
      const updated = await AdminApi.updateUser(selectedUser.id, selectedUser);
      setUsers(users.map((u) => (u.id === selectedUser.id ? updated : u)));
      setMessage((m) => ({ ...m, success: "User updated successfully!" }));
      setSelectedUser(null);
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  async function handleDeleteClick(userId) {
    setMessage({ error: "", success: "" });
    if (!window.confirm("Are you certain you want to remove this user profile record?")) return;

    try {
      const res = await AdminApi.deleteUser(userId);
      setUsers(users.filter((u) => u.id !== userId));
      setMessage((m) => ({ ...m, success: res.message }));
    } catch (err) {
      setMessage((m) => ({ ...m, error: err.message }));
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '20px', color: '#1e293b', marginBottom: '15px' }}> Account Management</h2>
      
      {message.error && <p className="error">{message.error}</p>}
      {message.success && <p className="success">{message.success}</p>}

  
      <form onSubmit={handleSearch} className="admin-search-wrapper">
        <input
          type="text"
          placeholder="Search by username or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="admin-search-field"
        />
        <button type="submit" className="admin-search-submit">Search</button>
      </form>

      {selectedUser && (
        <form onSubmit={handleSaveUserUpdate} className="card" style={{ marginBottom: "25px", background: "#f8fafc" }}>
          <h3>Edit User: {selectedUser.username}</h3>
          <label>First Name</label>
          <input
            type="text"
            value={selectedUser.name}
            onChange={(e) => setSelectedUser({ ...selectedUser, name: e.target.value })}
            required
          />
          <label>Last Name</label>
          <input
            type="text"
            value={selectedUser.lastName}
            onChange={(e) => setSelectedUser({ ...selectedUser, lastName: e.target.value })}
            required
          />
          <label>Email Address</label>
          <input
            type="email"
            value={selectedUser.email}
            onChange={(e) => setSelectedUser({ ...selectedUser, email: e.target.value })}
            required
          />
          <label>System Role</label>
          <select
            value={selectedUser.role}
            onChange={(e) => setSelectedUser({ ...selectedUser, role: e.target.value })}
          >
            <option value="TOURIST">Tourist</option>
            <option value="ADMIN">Administrator</option>
          </select>
          <div style={{ display: "flex", gap: "10px", marginTop: "15px" }}>
            <button type="submit">Save Changes</button>
            <button type="button" className="link-button" onClick={() => setSelectedUser(null)}>Cancel</button>
          </div>
        </form>
      )}


      <div className="admin-data-card">
        {users.length === 0 ? (
          <p>No user profiles match search criteria parameters.</p>
        ) : (
          <table className="admin-data-grid">
            <thead>
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.name} {u.lastName}</td>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td><strong>{u.role}</strong></td>
                  <td>
                    <div className="admin-grid-actions">
                      <button onClick={() => setSelectedUser(u)} className="admin-action-btn-edit">
                        Edit
                      </button>
                      <button onClick={() => handleDeleteClick(u.id)} className="admin-action-btn-delete">
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

export default AdminUserManagementView;