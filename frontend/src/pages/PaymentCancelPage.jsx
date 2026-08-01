import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function PaymentCancelPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const bookingId = searchParams.get('booking_id');

  if (!user) { navigate('/login'); return null; }

  return (
    <div className="container payment-result-page animate-fadeIn">
      <div className="glass-card payment-result-card">

        <div className="payment-result-icon payment-result-icon--cancel">
          <svg className="cancel-svg" viewBox="0 0 52 52">
            <circle className="cancel-circle" cx="26" cy="26" r="25" fill="none"/>
            <path className="cancel-cross" fill="none" d="M16 16 36 36 M36 16 16 36"/>
          </svg>
        </div>

        <h2 className="payment-result-title">Payment Cancelled</h2>

        <p className="payment-result-subtitle">
          Your payment was not completed. Don't worry — your booking is saved and you can try paying again.
        </p>

        <div className="payment-cancel-info">
          <div className="cancel-info-item">
            <span className="cancel-info-icon">💡</span>
            <span>No amount was charged to your card</span>
          </div>
          <div className="cancel-info-item">
            <span className="cancel-info-icon">🕐</span>
            <span>Your booking slot is reserved for 30 minutes</span>
          </div>
          <div className="cancel-info-item">
            <span className="cancel-info-icon">🔄</span>
            <span>You can retry payment from your dashboard</span>
          </div>
        </div>

        <div className="payment-result-actions">
          {bookingId && (
            <button className="btn btn-primary btn-lg" onClick={() => navigate('/dashboard')}>
              Go to Dashboard & Pay
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => navigate('/services')}>
            Browse Services
          </button>
          <button className="btn" style={{ background: 'var(--bg-glass)', color: 'var(--text-secondary)' }} onClick={() => navigate('/')}>
            Return Home
          </button>
        </div>

        <div className="payment-security-footer">
          <span>🔒 Your payment information was not stored</span>
        </div>
      </div>
    </div>
  );
}
