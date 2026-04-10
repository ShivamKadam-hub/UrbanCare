import { Link } from 'react-router-dom';

const CATEGORY_ICONS = {
  cleaning: '🧹', plumbing: '🔧', electrician: '⚡', salon: '💇',
  painting: '🎨', carpentry: '🪚', 'pest-control': '🐛', 'appliance-repair': '🔩',
};

export default function ServiceCard({ service, categoryName, categorySlug }) {
  const icon = CATEGORY_ICONS[categorySlug] || '🔧';
  return (
    <Link to={`/services/${service.id}`} className="glass-card service-card" id={`service-card-${service.id}`}>
      <div className="service-card-img">{icon}</div>
      <div className="service-card-body">
        <span className="sc-category">{categoryName || 'Service'}</span>
        <h3>{service.title}</h3>
        <p className="sc-desc">{service.description?.slice(0, 100)}{service.description?.length > 100 ? '…' : ''}</p>
        <div className="service-card-footer">
          <span className="sc-price">₹{service.price?.toLocaleString()}</span>
          <span className="sc-duration">⏱ {service.duration_minutes} min</span>
        </div>
      </div>
    </Link>
  );
}
