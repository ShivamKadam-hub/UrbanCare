import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Users, Briefcase, ShoppingBag, BarChart3, Tag, Calendar } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const STATUS_BADGE = {
  pending: 'badge-warning', confirmed: 'badge-primary',
  completed: 'badge-success', rejected: 'badge-danger', cancelled: 'badge-danger',
};
const PIE_COLORS = ['#6C5CE7', '#00CEC9', '#00B894', '#E17055', '#FDCB6E'];

export default function AdminPanel() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('analytics');
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [providers, setProviders] = useState([]);
  const [categories, setCategories] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [newCat, setNewCat] = useState({ name: '', slug: '', icon: '', description: '' });
  const [catMsg, setCatMsg] = useState('');

  useEffect(() => {
    if (!user || user.role !== 'admin') { navigate('/login'); return; }
    api.get('/admin/analytics').then(r => setAnalytics(r.data)).catch(() => {});
    api.get('/admin/users').then(r => setUsers(r.data)).catch(() => {});
    api.get('/admin/providers').then(r => setProviders(r.data)).catch(() => {});
    api.get('/admin/categories').then(r => setCategories(r.data)).catch(() => {});
    api.get('/admin/bookings').then(r => setBookings(r.data)).catch(() => {});
  }, [user]);

  if (!user) return null;

  const handleApprove = async (id) => {
    await api.patch(`/admin/providers/${id}/approve`);
    setProviders(prev => prev.map(p => p.id === id ? { ...p, is_approved: true } : p));
  };

  const handleToggleUser = async (id) => {
    const res = await api.patch(`/admin/users/${id}/toggle`);
    setUsers(prev => prev.map(u => u.id === id ? res.data : u));
  };

  const handleAddCategory = async (e) => {
    e.preventDefault();
    setCatMsg('');
    try {
      await api.post('/admin/categories', newCat);
      setCatMsg('Category added!');
      setNewCat({ name: '', slug: '', icon: '', description: '' });
      const r = await api.get('/admin/categories');
      setCategories(r.data);
    } catch (err) {
      setCatMsg(err.response?.data?.detail || 'Failed');
    }
  };

  // Chart data
  const bookingStatusData = analytics?.bookings_by_status
    ? Object.entries(analytics.bookings_by_status).map(([k, v]) => ({ name: k, value: v }))
    : [];

  const statsData = analytics ? [
    { name: 'Users', value: analytics.total_users },
    { name: 'Providers', value: analytics.total_providers },
    { name: 'Services', value: analytics.total_services },
    { name: 'Bookings', value: analytics.total_bookings },
  ] : [];

  return (
    <div className="dashboard">
      <aside className="dash-sidebar">
        <div style={{ padding: '0 28px 24px', borderBottom: '1px solid var(--border)', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 44, height: 44, borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--accent), var(--primary))',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700
            }}>{user.name?.[0]}</div>
            <div>
              <div style={{ fontWeight: 600 }}>{user.name}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Admin</div>
            </div>
          </div>
        </div>
        <ul className="sidebar-nav">
          <li><button className={tab === 'analytics' ? 'active' : ''} onClick={() => setTab('analytics')}><BarChart3 size={18} /> Analytics</button></li>
          <li><button className={tab === 'users' ? 'active' : ''} onClick={() => setTab('users')}><Users size={18} /> Users</button></li>
          <li><button className={tab === 'providers' ? 'active' : ''} onClick={() => setTab('providers')}><Briefcase size={18} /> Providers</button></li>
          <li><button className={tab === 'categories' ? 'active' : ''} onClick={() => setTab('categories')}><Tag size={18} /> Categories</button></li>
          <li><button className={tab === 'bookings' ? 'active' : ''} onClick={() => setTab('bookings')}><Calendar size={18} /> Bookings</button></li>
        </ul>
      </aside>

      <main className="dash-content animate-fadeIn">
        {tab === 'analytics' && analytics && (
          <>
            <h1>Analytics Dashboard</h1>
            <div className="grid grid-4" style={{ marginBottom: 40 }}>
              <div className="glass-card stat-card">
                <div className="stat-icon" style={{ background: 'rgba(108,92,231,0.15)', color: 'var(--primary-light)' }}><Users size={22} /></div>
                <div className="stat-value">{analytics.total_users}</div>
                <div className="stat-label">Total Users</div>
              </div>
              <div className="glass-card stat-card">
                <div className="stat-icon" style={{ background: 'rgba(0,206,201,0.15)', color: 'var(--secondary)' }}><Briefcase size={22} /></div>
                <div className="stat-value">{analytics.total_providers}</div>
                <div className="stat-label">Providers</div>
              </div>
              <div className="glass-card stat-card">
                <div className="stat-icon" style={{ background: 'rgba(0,184,148,0.15)', color: 'var(--success)' }}><ShoppingBag size={22} /></div>
                <div className="stat-value">{analytics.total_bookings}</div>
                <div className="stat-label">Bookings</div>
              </div>
              <div className="glass-card stat-card">
                <div className="stat-icon" style={{ background: 'rgba(253,121,168,0.15)', color: 'var(--accent)' }}><BarChart3 size={22} /></div>
                <div className="stat-value">₹{analytics.total_revenue.toLocaleString()}</div>
                <div className="stat-label">Revenue</div>
              </div>
            </div>

            {analytics.pending_approvals > 0 && (
              <div className="alert alert-error" style={{ marginBottom: 24 }}>
                ⚠️ {analytics.pending_approvals} provider registration(s) pending approval
              </div>
            )}

            <div className="grid grid-2">
              <div className="glass-card" style={{ padding: 28 }}>
                <h3 style={{ marginBottom: 20 }}>Platform Overview</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={statsData}>
                    <XAxis dataKey="name" stroke="var(--text-muted)" />
                    <YAxis stroke="var(--text-muted)" />
                    <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8 }} />
                    <Bar dataKey="value" fill="var(--primary)" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="glass-card" style={{ padding: 28 }}>
                <h3 style={{ marginBottom: 20 }}>Bookings by Status</h3>
                {bookingStatusData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={bookingStatusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                        {bookingStatusData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                      </Pie>
                      <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 8 }} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : <div className="empty-state"><p>No booking data yet.</p></div>}
              </div>
            </div>
          </>
        )}

        {tab === 'users' && (
          <>
            <h1>Manage Users</h1>
            <table className="data-table">
              <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Active</th><th>Action</th></tr></thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td>{u.name}</td>
                    <td>{u.email}</td>
                    <td><span className="badge badge-primary">{u.role}</span></td>
                    <td><span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>{u.is_active ? 'Yes' : 'No'}</span></td>
                    <td><button className="btn btn-secondary btn-sm" onClick={() => handleToggleUser(u.id)}>{u.is_active ? 'Deactivate' : 'Activate'}</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {tab === 'providers' && (
          <>
            <h1>Manage Providers</h1>
            <table className="data-table">
              <thead><tr><th>Business</th><th>Experience</th><th>Approved</th><th>Action</th></tr></thead>
              <tbody>
                {providers.map(p => (
                  <tr key={p.id}>
                    <td>{p.business_name}</td>
                    <td>{p.experience_years} yrs</td>
                    <td><span className={`badge ${p.is_approved ? 'badge-success' : 'badge-warning'}`}>{p.is_approved ? 'Approved' : 'Pending'}</span></td>
                    <td>{!p.is_approved && <button className="btn btn-success btn-sm" onClick={() => handleApprove(p.id)}>Approve</button>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {tab === 'categories' && (
          <>
            <h1>Manage Categories</h1>
            {catMsg && <div className="alert alert-success">{catMsg}</div>}
            <div className="glass-card" style={{ padding: 28, marginBottom: 32, maxWidth: 500 }}>
              <h3 style={{ marginBottom: 16 }}>Add Category</h3>
              <form onSubmit={handleAddCategory}>
                <div className="form-group"><label>Name</label><input className="form-control" required value={newCat.name} onChange={e => setNewCat({ ...newCat, name: e.target.value })} /></div>
                <div className="form-group"><label>Slug</label><input className="form-control" required value={newCat.slug} onChange={e => setNewCat({ ...newCat, slug: e.target.value })} /></div>
                <div className="form-group"><label>Icon (emoji)</label><input className="form-control" value={newCat.icon} onChange={e => setNewCat({ ...newCat, icon: e.target.value })} /></div>
                <div className="form-group"><label>Description</label><input className="form-control" value={newCat.description} onChange={e => setNewCat({ ...newCat, description: e.target.value })} /></div>
                <button type="submit" className="btn btn-primary">Add Category</button>
              </form>
            </div>
            <table className="data-table">
              <thead><tr><th>Icon</th><th>Name</th><th>Slug</th><th>Description</th></tr></thead>
              <tbody>
                {categories.map(c => (
                  <tr key={c.id}>
                    <td>{c.icon}</td>
                    <td>{c.name}</td>
                    <td>{c.slug}</td>
                    <td>{c.description?.slice(0, 60)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

        {tab === 'bookings' && (
          <>
            <h1>All Bookings</h1>
            <table className="data-table">
              <thead><tr><th>ID</th><th>Date</th><th>Time</th><th>Status</th><th>Address</th></tr></thead>
              <tbody>
                {bookings.map(b => (
                  <tr key={b.id}>
                    <td>#{b.id}</td>
                    <td>{b.booking_date}</td>
                    <td>{b.time_slot}</td>
                    <td><span className={`badge ${STATUS_BADGE[b.status]}`}>{b.status}</span></td>
                    <td>{b.address?.slice(0, 40)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </main>
    </div>
  );
}
