import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '', email: '', password: '', phone: '',
    role: 'customer', business_name: '', experience_years: 0,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="glass-card auth-card animate-fadeIn" style={{ maxWidth: 500 }}>
        <h1>Create Account</h1>
        <p className="auth-subtitle">Join UrbanCare today</p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="reg-name">Full Name</label>
            <input id="reg-name" className="form-control" placeholder="John Doe" required value={form.name} onChange={set('name')} />
          </div>
          <div className="form-group">
            <label htmlFor="reg-email">Email</label>
            <input id="reg-email" type="email" className="form-control" placeholder="you@example.com" required value={form.email} onChange={set('email')} />
          </div>
          <div className="form-group">
            <label htmlFor="reg-password">Password</label>
            <input id="reg-password" type="password" className="form-control" placeholder="Min 6 characters" required value={form.password} onChange={set('password')} />
          </div>
          <div className="form-group">
            <label htmlFor="reg-phone">Phone</label>
            <input id="reg-phone" className="form-control" placeholder="+91-9876543210" value={form.phone} onChange={set('phone')} />
          </div>
          <div className="form-group">
            <label htmlFor="reg-role">I want to</label>
            <select id="reg-role" className="form-control" value={form.role} onChange={set('role')}>
              <option value="customer">Book Services (Customer)</option>
              <option value="provider">Offer Services (Provider)</option>
            </select>
          </div>

          {form.role === 'provider' && (
            <>
              <div className="form-group">
                <label htmlFor="reg-business">Business Name</label>
                <input id="reg-business" className="form-control" placeholder="Your Business" value={form.business_name} onChange={set('business_name')} />
              </div>
              <div className="form-group">
                <label htmlFor="reg-exp">Years of Experience</label>
                <input id="reg-exp" type="number" className="form-control" min="0" value={form.experience_years} onChange={set('experience_years')} />
              </div>
            </>
          )}

          <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={loading}>
            {loading ? 'Creating…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
