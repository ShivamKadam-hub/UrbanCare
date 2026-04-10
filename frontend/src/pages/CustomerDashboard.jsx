import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Calendar, CreditCard, Star, User } from 'lucide-react';

const STATUS_BADGE = {
  pending: 'badge-warning', confirmed: 'badge-primary',
  completed: 'badge-success', rejected: 'badge-danger', cancelled: 'badge-danger',
};

export default function CustomerDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('bookings');
  const [bookings, setBookings] = useState([]);
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    api.get('/bookings').then(r => setBookings(r.data)).catch(() => {});
    api.get('/payments').then(r => setPayments(r.data)).catch(() => {});
  }, [user]);

  if (!user) return null;

  const totalSpent = payments.reduce((a, p) => a + p.amount, 0);

  return (
    <div className="dashboard">
      <aside className="dash-sidebar">
        <div style={{ padding: '0 28px 24px', borderBottom: '1px solid var(--border)', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 44, height: 44, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700
            }}>{user.name?.[0]}</div>
            <div>
              <div style={{ fontWeight: 600 }}>{user.name}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Customer</div>
            </div>
          </div>
        </div>
        <ul className="sidebar-nav">
          <li><button className={tab === 'bookings' ? 'active' : ''} onClick={() => setTab('bookings')}><Calendar size={18} /> My Bookings</button></li>
          <li><button className={tab === 'payments' ? 'active' : ''} onClick={() => setTab('payments')}><CreditCard size={18} /> Payments</button></li>
          <li><button className={tab === 'profile' ? 'active' : ''} onClick={() => setTab('profile')}><User size={18} /> Profile</button></li>
        </ul>
      </aside>

      <main className="dash-content animate-fadeIn">
        {/* Stats */}
        <div className="grid grid-3" style={{ marginBottom: 40 }}>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(108,92,231,0.15)', color: 'var(--primary-light)' }}><Calendar size={22} /></div>
            <div className="stat-value">{bookings.length}</div>
            <div className="stat-label">Total Bookings</div>
          </div>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(0,184,148,0.15)', color: 'var(--success)' }}><Star size={22} /></div>
            <div className="stat-value">{bookings.filter(b => b.status === 'completed').length}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(253,121,168,0.15)', color: 'var(--accent)' }}><CreditCard size={22} /></div>
            <div className="stat-value">₹{totalSpent.toLocaleString()}</div>
            <div className="stat-label">Total Spent</div>
          </div>
        </div>

        {tab === 'bookings' && (
          <>
            <h1>My Bookings</h1>
            {bookings.length === 0 ? (
              <div className="empty-state"><div className="empty-icon">📅</div><p>No bookings yet.</p></div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr><th>Service</th><th>Date</th><th>Time</th><th>Status</th><th>Amount</th></tr>
                </thead>
                <tbody>
                  {bookings.map(b => (
                    <tr key={b.id}>
                      <td>{b.service?.title || `Service #${b.service_id}`}</td>
                      <td>{b.booking_date}</td>
                      <td>{b.time_slot}</td>
                      <td><span className={`badge ${STATUS_BADGE[b.status] || ''}`}>{b.status}</span></td>
                      <td>₹{b.service?.price?.toLocaleString() || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {tab === 'payments' && (
          <>
            <h1>Payment History</h1>
            {payments.length === 0 ? (
              <div className="empty-state"><div className="empty-icon">💳</div><p>No payments yet.</p></div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Transaction ID</th><th>Amount</th><th>Method</th><th>Status</th><th>Date</th></tr></thead>
                <tbody>
                  {payments.map(p => (
                    <tr key={p.id}>
                      <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{p.transaction_id || '—'}</td>
                      <td>₹{p.amount?.toLocaleString()}</td>
                      <td>{p.method}</td>
                      <td><span className={`badge ${p.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>{p.status}</span></td>
                      <td>{p.paid_at ? new Date(p.paid_at).toLocaleDateString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {tab === 'profile' && (
          <>
            <h1>Profile</h1>
            <div className="glass-card" style={{ padding: 32, maxWidth: 500 }}>
              <div className="form-group"><label>Name</label><input className="form-control" value={user.name} readOnly /></div>
              <div className="form-group"><label>Email</label><input className="form-control" value={user.email} readOnly /></div>
              <div className="form-group"><label>Phone</label><input className="form-control" value={user.phone || '—'} readOnly /></div>
              <div className="form-group"><label>Member Since</label><input className="form-control" value={new Date(user.created_at).toLocaleDateString()} readOnly /></div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
