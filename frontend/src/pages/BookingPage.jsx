import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

const TIME_SLOTS = [
  '08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00',
  '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00',
  '16:00-17:00', '17:00-18:00', '18:00-19:00', '19:00-20:00',
];

export default function BookingPage() {
  const { serviceId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [service, setService] = useState(null);
  const [form, setForm] = useState({ booking_date: '', time_slot: '', address: '', notes: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get(`/services/${serviceId}`).then(r => setService(r.data)).catch(() => {});
  }, [serviceId]);

  if (!user) { navigate('/login'); return null; }
  if (!service) return <div className="container booking-page"><p>Loading…</p></div>;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.time_slot) { setError('Please select a time slot'); return; }
    setError('');
    setLoading(true);
    try {
      const booking = await api.post('/bookings', {
        service_id: parseInt(serviceId),
        ...form,
      });

      // Simulate payment
      await api.post('/payments', {
        booking_id: booking.data.id,
        amount: service.price,
        method: 'card',
      });

      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Booking failed.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container booking-page animate-fadeIn">
        <div className="glass-card" style={{ padding: 48, textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>✅</div>
          <h2 style={{ marginBottom: 12 }}>Booking Confirmed!</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
            Your booking for <strong>{service.title}</strong> on <strong>{form.booking_date}</strong> at <strong>{form.time_slot}</strong> has been confirmed and paid.
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>View My Bookings</button>
        </div>
      </div>
    );
  }

  // Get tomorrow as min-date
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split('T')[0];

  return (
    <div className="container booking-page animate-fadeIn">
      <h1>Book Service</h1>

      <div className="booking-summary glass-card">
        <h3>{service.title}</h3>
        <div className="summary-row"><span className="label">Provider</span><span>{service.provider?.business_name}</span></div>
        <div className="summary-row"><span className="label">Duration</span><span>{service.duration_minutes} min</span></div>
        <div className="summary-total"><span>Total</span><span className="gradient-text">₹{service.price?.toLocaleString()}</span></div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="booking-date">Select Date</label>
          <input
            id="booking-date"
            type="date"
            className="form-control"
            min={minDate}
            required
            value={form.booking_date}
            onChange={(e) => setForm({ ...form, booking_date: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label>Select Time Slot</label>
          <div className="time-slots">
            {TIME_SLOTS.map(slot => (
              <button
                type="button"
                key={slot}
                className={`time-slot ${form.time_slot === slot ? 'selected' : ''}`}
                onClick={() => setForm({ ...form, time_slot: slot })}
              >
                {slot}
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="booking-address">Address</label>
          <textarea
            id="booking-address"
            className="form-control"
            placeholder="Enter your full address…"
            required
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="booking-notes">Notes (optional)</label>
          <input
            id="booking-notes"
            className="form-control"
            placeholder="Any special instructions?"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </div>

        <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={loading}>
          {loading ? 'Processing…' : `Pay ₹${service.price?.toLocaleString()} & Book`}
        </button>
      </form>
    </div>
  );
}
