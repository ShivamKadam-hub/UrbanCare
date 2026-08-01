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
  const [reviewModal, setReviewModal] = useState(null);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    api.get('/bookings').then(r => setBookings(r.data)).catch(() => {});
    api.get('/payments').then(r => setPayments(r.data)).catch(() => {});
  }, [user]);

  const handleSubmitReview = async (bookingId) => {
    if (!reviewRating || reviewRating < 1 || reviewRating > 5) {
      alert('Please select a rating between 1 and 5');
      return;
    }
    setReviewSubmitting(true);
    try {
      await api.post('/reviews', {
        booking_id: bookingId,
        rating: reviewRating,
        comment: reviewComment || undefined,
      });
      alert('Review submitted successfully!');
      setReviewModal(null);
      setReviewRating(5);
      setReviewComment('');
      // Refresh bookings to reflect review status
      api.get('/bookings').then(r => setBookings(r.data)).catch(() => {});
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit review');
    } finally {
      setReviewSubmitting(false);
    }
  };

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
                  <tr><th>Service</th><th>Date</th><th>Time</th><th>Status</th><th>Amount</th><th>Action</th></tr>
                </thead>
                <tbody>
                  {bookings.map(b => {
                    const handlePayNow = async () => {
                      try {
                        const res = await api.post('/payments/create-checkout-session', {
                          booking_id: b.id,
                        });
                        window.location.href = res.data.checkout_url;
                      } catch (err) {
                        alert(err.response?.data?.detail || 'Payment failed');
                      }
                    };
                    return (
                      <tr key={b.id}>
                        <td>{b.service?.title || `Service #${b.service_id}`}</td>
                        <td>{b.booking_date}</td>
                        <td>{b.time_slot}</td>
                        <td><span className={`badge ${STATUS_BADGE[b.status] || ''}`}>{b.status}</span></td>
                        <td>₹{b.service?.price?.toLocaleString() || '—'}</td>
                        <td>
                          {b.status === 'pending' ? (
                            <button className="btn btn-primary btn-sm" onClick={handlePayNow}>💳 Pay Now</button>
                          ) : b.status === 'completed' ? (
                            <div style={{ display: 'flex', gap: 8 }}>
                              <button className="btn btn-primary btn-sm" onClick={handlePayNow}>💳 Pay Now</button>
                              <button className="btn btn-secondary btn-sm" onClick={() => setReviewModal(b.id)} style={{ background: 'rgba(108,92,231,0.15)', color: 'var(--primary-light)', border: '1px solid var(--primary)' }}>⭐ Review</button>
                            </div>
                          ) : '—'}
                        </td>
                      </tr>
                    );
                  })}
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

      {/* Review Modal */}
      {reviewModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setReviewModal(null)}>
          <div className="glass-card" style={{ padding: 32, maxWidth: 400, borderRadius: 12 }} onClick={e => e.stopPropagation()}>
            <h2 style={{ marginBottom: 20 }}>Leave a Review</h2>
            <div className="form-group">
              <label>Rating (1-5 stars)</label>
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                {[1, 2, 3, 4, 5].map(i => (
                  <button
                    key={i}
                    onClick={() => setReviewRating(i)}
                    style={{
                      fontSize: 28, background: 'none', border: 'none', cursor: 'pointer',
                      opacity: i <= reviewRating ? 1 : 0.3, transform: i <= reviewRating ? 'scale(1.1)' : 'scale(1)',
                      transition: 'all 0.2s'
                    }}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label>Comment (optional)</label>
              <textarea
                className="form-control"
                value={reviewComment}
                onChange={e => setReviewComment(e.target.value)}
                placeholder="Share your experience..."
                rows={4}
                style={{ resize: 'vertical', fontFamily: 'inherit' }}
              />
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
              <button className="btn btn-primary" onClick={() => handleSubmitReview(reviewModal)} disabled={reviewSubmitting} style={{ flex: 1 }}>
                {reviewSubmitting ? 'Submitting...' : 'Submit Review'}
              </button>
              <button className="btn" onClick={() => setReviewModal(null)} style={{ flex: 1 }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
