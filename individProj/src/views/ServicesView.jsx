import "../styles/ServicesView.css";

function ServicesView({ openTouristPage }) {
  return (
    <div className="services-page-wrapper">
      <div className="services-main-card">
        <h1>Hotel Facilities & Premium Offerings</h1>
        <p className="services-sub-text">Explore our premium guest amenities.</p>
        
        <div className="facility-item">
          <h3>Pool & Spa</h3>
          <p>Open daily 07:00 - 20:00.</p>
        </div>

        <div className="facility-item">
          <h3>Restaurant</h3>
          <p>Open daily 06:00 - 23:00.</p>
        </div>

        <div className="facility-item">
          <h3>GYM</h3>
          <p>Open 24/7 access.</p>
        </div>

        <button onClick={openTouristPage} className="services-back-btn">Back to My Profile</button>
      </div>
    </div>
  );
}
export default ServicesView;