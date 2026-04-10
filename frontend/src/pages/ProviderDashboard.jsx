import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Package, DollarSign, Clock, CheckCircle, PlusCircle, Briefcase } from 'lucide-react';

const STATUS_BADGE = {
  pending: 'badge-warning', confirmed: 'badge-primary',
  completed: 'badge-success', rejected: 'badge-danger', cancelled: 'badge-danger',
};

export default function ProviderDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('requests');
  const [bookings, setBookings] = useState([]);
  const [payments, setPayments] = useState([]);
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newService, setNewService] = useState({ category_id: '', title: '', description: '', price: '', duration_minutes: 60 });
  const [msg, setMsg] = useState('');

  useEffect(() => {
    if (!user || user.role !== 'provider') { navigate('/login'); return; }
    api.get('/bookings').then(r => setBookings(r.data)).catch(() => {});
    api.get('/payments').then(r => setPayments(r.data)).catch(() => {});
    api.get('/services').then(r => setServices(r.data)).catch(() => {});
    api.get('/admin/categories').then(r => setCategories(r.data)).catch(() => {});
  }, [user]);

  if (!user) return null;

  const totalEarnings = payments.reduce((a, p) => a + p.amount, 0);

  const handleStatusChange = async (bookingId, status) => {
    try {
      await api.patch(`/bookings/${bookingId}/status`, { status });
      setBookings(prev => prev.map(b => b.id === bookingId ? { ...b, status } : b));
      
      // Refresh payments when booking is completed (earnings should update)
      if (status === 'completed') {
        const res = await api.get('/payments').catch(() => ({}));
        if (res.data) setPayments(res.data);
      }
    } catch { /* empty */ }
  };

  const handleAddService = async (e) => {
    e.preventDefault();
    setMsg('');
    try {
      await api.post('/services', { ...newService, category_id: parseInt(newService.category_id), price: parseFloat(newService.price), duration_minutes: parseInt(newService.duration_minutes) });
      setMsg('Service added successfully!');
      setNewService({ category_id: '', title: '', description: '', price: '', duration_minutes: 60 });
      const res = await api.get('/services');
      setServices(res.data);
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Failed to add service.');
    }
  };

  return (
    <div className="dashboard">
      <aside className="dash-sidebar">
        <div style={{ padding: '0 28px 24px', borderBottom: '1px solid var(--border)', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 44, height: 44, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--secondary), var(--primary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700
            }}>{user.name?.[0]}</div>
            <div>
              <div style={{ fontWeight: 600 }}>{user.name}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Provider</div>
            </div>
          </div>
        </div>
        <ul className="sidebar-nav">
          <li><button className={tab === 'requests' ? 'active' : ''} onClick={() => setTab('requests')}><Clock size={18} /> Booking Requests</button></li>
          <li><button className={tab === 'services' ? 'active' : ''} onClick={() => setTab('services')}><Briefcase size={18} /> My Services</button></li>
          <li><button className={tab === 'add' ? 'active' : ''} onClick={() => setTab('add')}><PlusCircle size={18} /> Add Service</button></li>
          <li><button className={tab === 'earnings' ? 'active' : ''} onClick={() => setTab('earnings')}><DollarSign size={18} /> Earnings</button></li>
        </ul>
      </aside>

      <main className="dash-content animate-fadeIn">
        {/* Stats */}
        <div className="grid grid-4" style={{ marginBottom: 40 }}>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(0,206,201,0.15)', color: 'var(--secondary)' }}><Package size={22} /></div>
            <div className="stat-value">{services.length}</div>
            <div className="stat-label">Services</div>
          </div>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(253,203,110,0.15)', color: 'var(--warning)' }}><Clock size={22} /></div>
            <div className="stat-value">{bookings.filter(b => b.status === 'pending').length}</div>
            <div className="stat-label">Pending</div>
          </div>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(0,184,148,0.15)', color: 'var(--success)' }}><CheckCircle size={22} /></div>
            <div className="stat-value">{bookings.filter(b => b.status === 'completed').length}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="glass-card stat-card">
            <div className="stat-icon" style={{ background: 'rgba(108,92,231,0.15)', color: 'var(--primary-light)' }}><DollarSign size={22} /></div>
            <div className="stat-value">₹{totalEarnings.toLocaleString()}</div>
            <div className="stat-label">Total Earnings</div>
          </div>
        </div>

        {tab === 'requests' && (
          <>
            <h1>Booking Requests</h1>
            {bookings.length === 0 ? (
              <div className="empty-state"><div className="empty-icon">📋</div><p>No booking requests.</p></div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Service</th><th>Customer</th><th>Date</th><th>Time</th><th>Status</th><th>Actions</th></tr></thead>
                <tbody>
                  {bookings.map(b => (
                    <tr key={b.id}>
                      <td>{b.service?.title || `#${b.service_id}`}</td>
                      <td>{b.customer?.name || '—'}</td>
                      <td>{b.booking_date}</td>
                      <td>{b.time_slot}</td>
                      <td><span className={`badge ${STATUS_BADGE[b.status]}`}>{b.status}</span></td>
                      <td style={{ display: 'flex', gap: 8 }}>
                        {b.status === 'pending' && (
                          <>
                            <button className="btn btn-success btn-sm" onClick={() => handleStatusChange(b.id, 'confirmed')}>Accept</button>
                            <button className="btn btn-danger btn-sm" onClick={() => handleStatusChange(b.id, 'rejected')}>Reject</button>
                          </>
                        )}
                        {b.status === 'confirmed' && (
                          <button className="btn btn-primary btn-sm" onClick={() => handleStatusChange(b.id, 'completed')}>Complete</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {tab === 'services' && (
          <>
            <h1>My Services</h1>
            {services.length === 0 ? (
              <div className="empty-state"><div className="empty-icon">📦</div><p>No services added yet.</p></div>
            ) : (
              <table className="data-table">
                <thead><tr><th>Title</th><th>Price</th><th>Duration</th><th>Active</th></tr></thead>
                <tbody>
                  {services.map(s => (
                    <tr key={s.id}>
                      <td>{s.title}</td>
                      <td>₹{s.price?.toLocaleString()}</td>
                      <td>{s.duration_minutes} min</td>
                      <td><span className={`badge ${s.is_active ? 'badge-success' : 'badge-danger'}`}>{s.is_active ? 'Yes' : 'No'}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {tab === 'add' && (
          <>
            <h1>Add New Service</h1>
            {msg && <div className={`alert ${msg.includes('success') ? 'alert-success' : 'alert-error'}`}>{msg}</div>}
            <div className="glass-card" style={{ padding: 32, maxWidth: 500 }}>
              <form onSubmit={handleAddService}>
                <div className="form-group">
                  <label>Category</label>
                  <select className="form-control" required value={newService.category_id} onChange={e => setNewService({ ...newService, category_id: e.target.value })}>
                    <option value="">Select category</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="form-group"><label>Title</label><input className="form-control" required value={newService.title} onChange={e => setNewService({ ...newService, title: e.target.value })} /></div>
                <div className="form-group"><label>Description</label><textarea className="form-control" value={newService.description} onChange={e => setNewService({ ...newService, description: e.target.value })} /></div>
                <div className="form-group"><label>Price (₹)</label><input type="number" className="form-control" required min="1" value={newService.price} onChange={e => setNewService({ ...newService, price: e.target.value })} /></div>
                <div className="form-group"><label>Duration (minutes)</label><input type="number" className="form-control" required min="15" value={newService.duration_minutes} onChange={e => setNewService({ ...newService, duration_minutes: e.target.value })} /></div>
                <button type="submit" className="btn btn-primary btn-block">Add Service</button>
              </form>
            </div>
          </>
        )}

        {tab === 'earnings' && (
          <>
            <h1>Earnings Dashboard</h1>
            <div className="glass-card" style={{ padding: 32 }}>
              <h2 style={{ fontSize: '2.5rem', fontWeight: 900, marginBottom: 8 }} className="gradient-text">₹{totalEarnings.toLocaleString()}</h2>
              <p style={{ color: 'var(--text-muted)' }}>Total earnings from {payments.length} transactions</p>
            </div>
            {payments.length > 0 && (
              <table className="data-table" style={{ marginTop: 24 }}>
                <thead><tr><th>Transaction ID</th><th>Amount</th><th>Method</th><th>Date</th></tr></thead>
                <tbody>
                  {payments.map(p => (
                    <tr key={p.id}>
                      <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{p.transaction_id}</td>
                      <td>₹{p.amount?.toLocaleString()}</td>
                      <td>{p.method}</td>
                      <td>{p.paid_at ? new Date(p.paid_at).toLocaleDateString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </main>
    </div>
  );
}
