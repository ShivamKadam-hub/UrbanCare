import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/client';
import { Star, Clock, MapPin } from 'lucide-react';

const CATEGORY_ICONS = {
  cleaning: '🧹', plumbing: '🔧', electrician: '⚡', salon: '💇',
  painting: '🎨', carpentry: '🪚', 'pest-control': '🐛', 'appliance-repair': '🔩',
};

export default function ServiceDetailPage() {
  const { id } = useParams();
  const [service, setService] = useState(null);
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    api.get(`/services/${id}`).then(r => setService(r.data)).catch(() => {});
    api.get(`/reviews/service/${id}`).then(r => setReviews(r.data)).catch(() => {});
  }, [id]);

  if (!service) return <div className="container" style={{ padding: '80px 0' }}><div className="empty-state"><p>Loading…</p></div></div>;

  const icon = CATEGORY_ICONS[service.category?.slug] || '🔧';
  const avgRating = reviews.length ? (reviews.reduce((a, r) => a + r.rating, 0) / reviews.length).toFixed(1) : 'N/A';

  return (
    <div className="container service-detail animate-fadeIn">
      <div className="service-detail-header">
        <div className="service-detail-img">{icon}</div>
        <div className="service-detail-info">
          <span className="sd-category">{service.category?.name}</span>
          <h1>{service.title}</h1>
          <div className="sd-price gradient-text">₹{service.price?.toLocaleString()}</div>
          <div className="sd-duration">
            <Clock size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} />
            {service.duration_minutes} minutes
          </div>
          <p className="sd-desc">{service.description}</p>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
            <span className="badge badge-primary" style={{ fontSize: '0.85rem' }}>
              <Star size={14} style={{ marginRight: 4 }} /> {avgRating} ({reviews.length} reviews)
            </span>
            <span className="badge badge-info">
              By {service.provider?.business_name}
            </span>
          </div>

          <Link to={`/booking/${service.id}`} className="btn btn-primary btn-lg">
            Book Now
          </Link>
        </div>
      </div>

      {/* Reviews */}
      <section>
        <h2 style={{ marginBottom: 24 }}>Customer Reviews</h2>
        {reviews.length === 0 ? (
          <div className="empty-state"><p>No reviews yet. Be the first to review!</p></div>
        ) : (
          reviews.map(r => (
            <div key={r.id} className="glass-card review-card">
              <div className="reviewer">
                <div className="reviewer-avatar">{r.customer?.name?.[0] || '?'}</div>
                <div>
                  <div className="reviewer-name">{r.customer?.name}</div>
                  <div className="review-date">{new Date(r.created_at).toLocaleDateString()}</div>
                </div>
                <div className="stars" style={{ marginLeft: 'auto' }}>
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} size={14} fill={i < r.rating ? 'currentColor' : 'none'} />
                  ))}
                </div>
              </div>
              {r.comment && <p className="review-text">{r.comment}</p>}
            </div>
          ))
        )}
      </section>
    </div>
  );
}
