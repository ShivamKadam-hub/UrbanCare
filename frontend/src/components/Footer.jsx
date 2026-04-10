import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-brand">
            <div style={{ fontSize: '1.4rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem'
              }}>✦</span>
              UrbanCare
            </div>
            <p>Your one-stop destination for trusted and professional home services. From cleaning to salon — we've got you covered.</p>
          </div>
          <div>
            <h4>Services</h4>
            <ul>
              <li><Link to="/services">Cleaning</Link></li>
              <li><Link to="/services">Plumbing</Link></li>
              <li><Link to="/services">Electrician</Link></li>
              <li><Link to="/services">Salon</Link></li>
            </ul>
          </div>
          <div>
            <h4>Company</h4>
            <ul>
              <li><Link to="/">About Us</Link></li>
              <li><Link to="/">Careers</Link></li>
              <li><Link to="/">Blog</Link></li>
              <li><Link to="/">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4>Support</h4>
            <ul>
              <li><Link to="/">Help Center</Link></li>
              <li><Link to="/">Safety</Link></li>
              <li><Link to="/">Terms of Service</Link></li>
              <li><Link to="/">Privacy Policy</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          © {new Date().getFullYear()} UrbanCare. All rights reserved. Built with ❤️
        </div>
      </div>
    </footer>
  );
}
