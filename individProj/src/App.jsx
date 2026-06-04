import { useState, useEffect } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginView from "./views/LoginView";
import RegisterView from "./views/RegisterView";
import TouristPage from "./views/TouristPage";
import CreateBookingView from "./views/CreateBookingView";
import ServicesView from "./views/ServicesView";
import AdminDashboardView from "./views/AdminDashboardView";

function AppContent() {

  const { isAuthenticated, user, logout } = useAuth();
  const [page, setPage] = useState("login");

  useEffect(() => {
    if (isAuthenticated() && user) {
      if (user.role === "ADMIN") {
        setPage("admin");
      } else {
        setPage("tourist");
      }
    } else {
      setPage("login");
    }
  }, [user, isAuthenticated]);

  function openLoginPage() {
    setPage("login");
  }

  function openRegisterPage() {
    setPage("register");
  }

  function openTouristPage() {
    if (user?.role === "ADMIN") {
      setPage("admin");
    } else {
      setPage("tourist");
    }
  }

  function openBookingPage() {
    setPage("booking");
  }

  function openServicesPage() {
    setPage("services");
  }

  function handleAdminLogout() {
    logout();
    setPage("login");
  }

  if (page === "register") {
    return <RegisterView openLoginPage={openLoginPage} />;
  }

  if (page === "booking") {
    return <CreateBookingView openTouristPage={openTouristPage} />;
  }

  if (page === "services") {
    return <ServicesView openTouristPage={openTouristPage} />;
  }

  if (page === "admin") {
    return <AdminDashboardView handleLogout={handleAdminLogout} />;
  }

  if (page === "tourist") {
    return (
      <TouristPage 
        openLoginPage={openLoginPage} 
        openBookingPage={openBookingPage} 
        openServicesPage={openServicesPage} 
      />
    );
  }

  return (
    <LoginView
      openRegisterPage={openRegisterPage}
      openTouristPage={openTouristPage}
    />
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;