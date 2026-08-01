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
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('form'); // 'form' | 'processing'
  const [bookedSlots, setBookedSlots] = useState([]);

  useEffect(() => {
    api.get(`/services/${serviceId}`).then(r => setService(r.data)).catch(() => {});
  }, [serviceId]);

  // Fetch booked slots when date changes
  useEffect(() => {
    if (form.booking_date && serviceId) {
      api.get(`/bookings/available-slots/${serviceId}?booking_date=${form.booking_date}`)
        .then(r => setBookedSlots(r.data.booked_slots || []))
        .catch(() => setBookedSlots([]));
    }
  }, [form.booking_date, serviceId]);

  if (!user) { navigate('/login'); return null; }
  if (!service) return <div className="container booking-page"><p>Loading…</p></div>;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.time_slot) { setError('Please select a time slot'); return; }
    
    // Validate time slot is still available
    const isBooked = bookedSlots.includes(form.time_slot);
    const isPastTime = form.booking_date === minDate && (() => {
      const now = new Date();
      const [startTime] = form.time_slot.split('-');
      const [slotHour, slotMinute] = startTime.split(':').map(Number);
      return slotHour < now.getHours() || (slotHour === now.getHours() && slotMinute <= now.getMinutes());
    })();
    
    if (isBooked) { setError('Selected time slot was just booked. Please choose another time.'); return; }
    if (isPastTime) { setError('Selected time slot has passed. Please choose a future time.'); return; }
    
    setError('');
    setLoading(true);
    setStep('processing');
    try {
      // Step 1: Create the booking
      const booking = await api.post('/bookings', {
        service_id: parseInt(serviceId),
        ...form,
      });

      // Step 2: Create Stripe Checkout Session
      const checkoutRes = await api.post('/payments/create-checkout-session', {
        booking_id: booking.data.id,
      });

      // Step 3: Redirect to Stripe Checkout
      window.location.href = checkoutRes.data.checkout_url;

    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
      setStep('form');
    } finally {
      setLoading(false);
    }
  };

  // Get today as min-date (allow same-day bookings)
  const today = new Date();
  const minDate = today.toISOString().split('T')[0];

  if (step === 'processing') {
    return (
      <div className="container booking-page animate-fadeIn">
        <div className="glass-card payment-processing-card">
          <div className="payment-processing-spinner"></div>
          <h2>Preparing Your Checkout</h2>
          <p className="payment-processing-text">
            Redirecting you to our secure payment partner…
          </p>
          <div className="payment-security-badges">
            <span className="security-badge">🔒 256-bit SSL</span>
            <span className="security-badge">🛡️ Stripe Secured</span>
            <span className="security-badge">✓ PCI Compliant</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container booking-page animate-fadeIn">
      <h1>Book Service</h1>

      <div className="booking-summary glass-card">
        <h3>{service.title}</h3>
        <div className="summary-row"><span className="label">Provider</span><span>{service.provider?.business_name}</span></div>
        <div className="summary-row"><span className="label">Duration</span><span>{service.duration_minutes} min</span></div>
        <div className="summary-total"><span>Total</span><span className="gradient-text">₹{service.price?.toLocaleString()}</span></div>
      </div>

      {/* Stripe Trust Badge */}
      <div className="stripe-trust-bar">
        <svg className="stripe-logo" viewBox="0 0 60 25" xmlns="http://www.w3.org/2000/svg" width="60" height="25">
          <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95v3.32a12.3 12.3 0 0 1-4.56.88c-4.02 0-6.83-2.5-6.83-7.16 0-4.14 2.45-7.27 6.24-7.27 3.55 0 5.96 2.85 5.96 7.14v1.49zm-4.12-5.56c-.93 0-1.94.66-2.1 2.44h4.16c-.02-1.58-.73-2.44-2.06-2.44zM41.39 18.53c-1.13.47-2.47.54-3.37.54-3.38 0-5.7-2.25-5.7-6.83s2.67-6.92 5.98-6.92c.72 0 1.93.15 3.1.54v4.13a4.3 4.3 0 0 0-2.32-.75c-1.55 0-2.58 1.1-2.58 3.06s.95 2.89 2.5 2.89c.87 0 1.66-.25 2.38-.71v4.05zM30.2 5.68V.3h-4.18v5.38h-1.83v3.51h1.83v4.8c0 3.49 1.64 5.28 5.73 5.28.7 0 1.36-.06 2.02-.19V15.7a5.24 5.24 0 0 1-1.17.14c-1.17 0-2.4-.35-2.4-2.14V9.19h3.56V5.68H30.2zm-11.93 0H14.4v13.34h4.18V5.68h-.31zm-2.06-5.38c-1.36 0-2.46 1.04-2.46 2.33s1.1 2.33 2.46 2.33 2.46-1.04 2.46-2.33-1.1-2.33-2.46-2.33zM8.14 6.08c-1.62 0-2.9.57-3.72 1.41V5.68H.5v13.34h4.18v-7.1c0-1.63.74-2.4 1.9-2.4.93 0 1.62.56 1.62 1.7v7.8h4.18v-8.63c0-3.08-1.62-4.31-4.24-4.31z" fill="#A29BFE" fillRule="nonzero"></path>
        </svg>
        <span className="stripe-trust-text">Powered by Stripe · Secure payment</span>
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
            {form.booking_date ? (
              TIME_SLOTS.map(slot => {
                const isBooked = bookedSlots.includes(slot);
                const isPastTime = form.booking_date === minDate && (() => {
                  const now = new Date();
                  const [startTime] = slot.split('-');
                  const [slotHour, slotMinute] = startTime.split(':').map(Number);
                  return slotHour < now.getHours() || (slotHour === now.getHours() && slotMinute <= now.getMinutes());
                })();
                const isAvailable = !isBooked && !isPastTime;

                return (
                  <button
                    type="button"
                    key={slot}
                    disabled={!isAvailable}
                    className={`time-slot ${form.time_slot === slot ? 'selected' : ''} ${!isAvailable ? 'disabled' : ''}`}
                    onClick={() => isAvailable && setForm({ ...form, time_slot: slot })}
                    title={isBooked ? 'Provider is busy at this time' : isPastTime ? 'Time slot has passed' : ''}
                    style={!isAvailable ? { opacity: 0.4, cursor: 'not-allowed' } : {}}
                  >
                    {slot}
                    {isBooked && <span style={{ fontSize: '0.7rem', display: 'block', marginTop: '2px' }}>🔒 Busy</span>}
                  </button>
                );
              })
            ) : (
              <div style={{ gridColumn: '1 / -1', padding: '16px', textAlign: 'center', color: 'var(--text-muted)' }}>
                Select a date to see available time slots.
              </div>
            )}
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

        <button type="submit" className="btn btn-primary btn-block btn-lg btn-stripe-pay" disabled={loading}>
          <span className="btn-stripe-icon">🔒</span>
          {loading ? 'Redirecting to Stripe…' : `Pay ₹${service.price?.toLocaleString()} Securely`}
        </button>

        <p className="payment-disclaimer">
          You will be redirected to Stripe's secure checkout to complete payment. Your card details are never stored on our servers.
        </p>
      </form>
    </div>
  );
}
