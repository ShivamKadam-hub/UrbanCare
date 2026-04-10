import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import ServiceCard from '../components/ServiceCard';

const CATEGORIES = [
  { slug: 'cleaning', icon: '🧹', name: 'Cleaning', desc: 'Deep clean your home' },
  { slug: 'plumbing', icon: '🔧', name: 'Plumbing', desc: 'Fix leaks & pipes' },
  { slug: 'electrician', icon: '⚡', name: 'Electrician', desc: 'Wiring & repairs' },
  { slug: 'salon', icon: '💇', name: 'Salon', desc: 'Beauty at home' },
  { slug: 'painting', icon: '🎨', name: 'Painting', desc: 'Transform your walls' },
  { slug: 'carpentry', icon: '🪚', name: 'Carpentry', desc: 'Custom woodwork' },
  { slug: 'pest-control', icon: '🐛', name: 'Pest Control', desc: 'Bug-free living' },
  { slug: 'appliance-repair', icon: '🔩', name: 'Appliance Repair', desc: 'Fix your devices' },
];

export default function HomePage() {
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    api.get('/services?limit=8').then(r => setServices(r.data)).catch(() => {});
    api.get('/admin/categories').then(r => setCategories(r.data)).catch(() => {});
  }, []);

  const getCat = (catId) => {
    const c = categories.find(x => x.id === catId);
    return c ? { name: c.name, slug: c.slug } : { name: '', slug: '' };
  };

  return (
    <>
      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section className="hero">
        <div className="container">
          <div className="hero-content animate-fadeIn">
            <h1>Home Services,<br /><span className="gradient-text">Reimagined.</span></h1>
            <p>
              Book trusted professionals for cleaning, repairs, salon, and more — all at your doorstep, with just a few taps.
            </p>
            <div className="hero-actions">
              <Link to="/services" className="btn btn-primary btn-lg">Explore Services</Link>
              <Link to="/register" className="btn btn-secondary btn-lg">Become a Provider</Link>
            </div>
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-value gradient-text">500+</span>
                <span className="stat-label">Service Providers</span>
              </div>
              <div className="stat">
                <span className="stat-value gradient-text">10K+</span>
                <span className="stat-label">Happy Customers</span>
              </div>
              <div className="stat">
                <span className="stat-value gradient-text">25+</span>
                <span className="stat-label">Cities Served</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Categories ───────────────────────────────────────────────── */}
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2>Browse by <span className="gradient-text">Category</span></h2>
            <p>Find the perfect professional for every home need</p>
          </div>
          <div className="grid grid-4">
            {CATEGORIES.map((cat, i) => (
              <Link
                key={cat.slug}
                to={`/services?category=${cat.slug}`}
                className="glass-card category-card animate-fadeIn"
                style={{ animationDelay: `${i * 0.06}s` }}
                id={`category-${cat.slug}`}
              >
                <span className="cat-icon">{cat.icon}</span>
                <h3>{cat.name}</h3>
                <p>{cat.desc}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ── Popular Services ─────────────────────────────────────────── */}
      {services.length > 0 && (
        <section className="section" style={{ paddingTop: 0 }}>
          <div className="container">
            <div className="section-header">
              <h2>Popular <span className="gradient-text">Services</span></h2>
              <p>Top-rated services loved by thousands</p>
            </div>
            <div className="grid grid-4">
              {services.slice(0, 8).map((svc, i) => (
                <div key={svc.id} className="animate-fadeIn" style={{ animationDelay: `${i * 0.06}s` }}>
                  <ServiceCard service={svc} categoryName={getCat(svc.category_id).name} categorySlug={getCat(svc.category_id).slug} />
                </div>
              ))}
            </div>
            <div style={{ textAlign: 'center', marginTop: 48 }}>
              <Link to="/services" className="btn btn-secondary btn-lg">View All Services →</Link>
            </div>
          </div>
        </section>
      )}

      {/* ── CTA ──────────────────────────────────────────────────────── */}
      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="glass-card" style={{ padding: '64px 48px', textAlign: 'center' }}>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: 16 }}>
              Ready to grow your business?
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 32, maxWidth: 500, margin: '0 auto 32px' }}>
              Join hundreds of service providers earning more with UrbanCare. Sign up today and reach thousands of customers.
            </p>
            <Link to="/register" className="btn btn-accent btn-lg">Register as Provider</Link>
          </div>
        </div>
      </section>
    </>
  );
}
