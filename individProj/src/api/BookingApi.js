const API_BASE_URL = "http://localhost:8000/api";

function getHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
}

async function handleResponse(response) {
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Transaction Process Error");
  return data;
}

export const BookingApi = {
  async getRoomTypes() {
    const response = await fetch(`${API_BASE_URL}/room-types`, { headers: getHeaders() });
    return handleResponse(response);
  },

  async createBooking(request) {
    const response = await fetch(`${API_BASE_URL}/bookings`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async getMyBookings() {
    const response = await fetch(`${API_BASE_URL}/bookings/my`, { headers: getHeaders() });
    return handleResponse(response);
  },

  async checkIn(bookingId) {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/check-in`, {
      method: "POST",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },

  async checkOut(bookingId) {
    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/check-out`, {
      method: "POST",
      headers: getHeaders(),
    });
    return handleResponse(response);
  },
};