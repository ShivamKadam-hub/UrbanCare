import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const loc = useLocation();
  const active = (path) => loc.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="logo-icon">✦</span>
          UrbanCare
        </Link>

        <ul className="navbar-links">
          <li><Link to="/" className={active('/')}>Home</Link></li>
          <li><Link to="/services" className={active('/services')}>Services</Link></li>

          {!user ? (
            <>
              <li><Link to="/login" className={active('/login')}>Login</Link></li>
              <li><Link to="/register" className="btn btn-primary btn-sm">Get Started</Link></li>
            </>
          ) : (
            <>
              {user.role === 'customer' && (
                <li><Link to="/dashboard" className={active('/dashboard')}>Dashboard</Link></li>
              )}
              {user.role === 'provider' && (
                <li><Link to="/provider" className={active('/provider')}>Provider Dashboard</Link></li>
              )}
              {user.role === 'admin' && (
                <li><Link to="/admin" className={active('/admin')}>Admin</Link></li>
              )}
              <li>
                <button onClick={logout} style={{ color: 'var(--accent)' }}>Logout</button>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}
