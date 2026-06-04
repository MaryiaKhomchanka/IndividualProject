import { useState } from "react";
import AdminUserManagementView from "./AdminUserManagementView";
import AdminPriceManagementView from "./AdminPriceManagementView";
import AdminBookingManagementView from "./AdminBookingManagementView";
import "../styles/AdminDashboard.css"; 

function AdminDashboardView({ handleLogout }) {
  const [currentTab, setCurrentTab] = useState("users");

  return (

    <div className="admin-scope">
      

      <div className="admin-main-banner">
        <div className="admin-banner-titles">
          <h1>Admin Dashboard</h1>
          <p>System configuration panel layout context active.</p>
        </div>
        <button onClick={handleLogout} className="admin-logout-btn">
          Logout
        </button>
      </div>


      <div className="admin-tab-row">
        <button 
          onClick={() => setCurrentTab("users")} 
          className={`admin-tab-trigger ${currentTab === "users" ? "active" : "inactive"}`}
        >
          User Profiles
        </button>
        <button 
          onClick={() => setCurrentTab("prices")} 
          className={`admin-tab-trigger ${currentTab === "prices" ? "active" : "inactive"}`}
        >
          Room prices
        </button>
        <button 
          onClick={() => setCurrentTab("bookings")} 
          className={`admin-tab-trigger ${currentTab === "bookings" ? "active" : "inactive"}`}
        >
          Bookings
        </button>
      </div>


      <div>
        {currentTab === "users" && <AdminUserManagementView />}
        {currentTab === "prices" && <AdminPriceManagementView />}
        {currentTab === "bookings" && <AdminBookingManagementView />}
      </div>
      
    </div>
  );
}

export default AdminDashboardView;