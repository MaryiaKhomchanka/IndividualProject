const API_BASE_URL = "http://localhost:8000/api/admin";

function getHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
}

async function handleResponse(response) {
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Administrative Request Failed");
  return data;
}

export const AdminApi = {

  async searchUsers(searchQuery = "") {
    const response = await fetch(`${API_BASE_URL}/users?search=${encodeURIComponent(searchQuery)}`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async updateUser(userId, request) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async deleteUser(userId) {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async updateRoomType(roomTypeId, request) {
    const response = await fetch(`${API_BASE_URL}/room-types/${roomTypeId}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async searchBookings(searchQuery = "") {
    const response = await fetch(`${API_BASE_URL}/bookings?search=${encodeURIComponent(searchQuery)}`, {
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async updateBooking(bookingId, request) {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async deleteBooking(bookingId) {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}`, {
      method: "DELETE",
      headers: getHeaders(),
    }); 
    return handleResponse(response);
  },
};