import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const sessionId = searchParams.get('session_id');
  const bookingId = searchParams.get('booking_id');

  const [verifying, setVerifying] = useState(true);
  const [paymentData, setPaymentData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) {
      setVerifying(false);
      setError('Invalid payment session.');
      return;
    }

    const verify = async () => {
      try {
        const res = await api.get(`/payments/verify/${sessionId}`);
        setPaymentData(res.data);
      } catch (err) {
        setError('Could not verify payment. Please check your dashboard.');
      } finally {
        setVerifying(false);
      }
    };

    // Small delay to let webhook process
    const timer = setTimeout(verify, 1500);
    return () => clearTimeout(timer);
  }, [sessionId]);

  if (!user) { navigate('/login'); return null; }

  if (verifying) {
    return (
      <div className="container payment-result-page animate-fadeIn">
        <div className="glass-card payment-result-card">
          <div className="payment-processing-spinner"></div>
          <h2>Verifying Payment…</h2>
          <p className="payment-result-subtitle">Please wait while we confirm your payment with Stripe.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container payment-result-page animate-fadeIn">
        <div className="glass-card payment-result-card">
          <div className="payment-result-icon payment-result-icon--warning">⚠️</div>
          <h2>Verification Issue</h2>
          <p className="payment-result-subtitle">{error}</p>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const isCompleted = paymentData?.payment_status === 'completed';

  return (
    <div className="container payment-result-page animate-fadeIn">
      <div className="glass-card payment-result-card">

        {/* Animated Success Circle */}
        <div className={`payment-result-icon ${isCompleted ? 'payment-result-icon--success' : 'payment-result-icon--pending'}`}>
          {isCompleted ? (
            <svg className="checkmark-svg" viewBox="0 0 52 52">
              <circle className="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
              <path className="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
            </svg>
          ) : (
            <span>⏳</span>
          )}
        </div>

        <h2 className="payment-result-title">
          {isCompleted ? 'Payment Successful!' : 'Payment Processing'}
        </h2>

        <p className="payment-result-subtitle">
          {isCompleted
            ? 'Your booking has been confirmed and is ready to go.'
            : 'Your payment is being processed. It will reflect in your dashboard shortly.'}
        </p>

        {/* Payment Details Card */}
        {paymentData && (
          <div className="payment-details-card">
            <div className="payment-detail-row">
              <span className="payment-detail-label">Service</span>
              <span className="payment-detail-value">{paymentData.service_title}</span>
            </div>
            <div className="payment-detail-row">
              <span className="payment-detail-label">Date</span>
              <span className="payment-detail-value">{paymentData.booking_date}</span>
            </div>
            <div className="payment-detail-row">
              <span className="payment-detail-label">Time</span>
              <span className="payment-detail-value">{paymentData.time_slot}</span>
            </div>
            <div className="payment-detail-row">
              <span className="payment-detail-label">Booking ID</span>
              <span className="payment-detail-value">#{paymentData.booking_id}</span>
            </div>
            {paymentData.transaction_id && (
              <div className="payment-detail-row">
                <span className="payment-detail-label">Transaction</span>
                <span className="payment-detail-value payment-detail-txn">{paymentData.transaction_id}</span>
              </div>
            )}
            <div className="payment-detail-row payment-detail-total">
              <span className="payment-detail-label">Amount Paid</span>
              <span className="payment-detail-value gradient-text">₹{paymentData.amount?.toLocaleString()}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="payment-result-actions">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/dashboard')}>
            View My Bookings
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/services')}>
            Browse More Services
          </button>
        </div>

        {/* Security Footer */}
        <div className="payment-security-footer">
          <span>🔒 Payment secured by Stripe</span>
        </div>
      </div>
    </div>
  );
}
