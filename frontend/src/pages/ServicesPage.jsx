import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import ServiceCard from '../components/ServiceCard';
import { Search } from 'lucide-react';

export default function ServicesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [catFilter, setCatFilter] = useState(searchParams.get('category') || '');
  const [loading, setLoading] = useState(true);

  const fetchServices = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      // Find category id from slug
      if (catFilter && categories.length) {
        const cat = categories.find(c => c.slug === catFilter);
        if (cat) params.category_id = cat.id;
      }
      const res = await api.get('/services', { params });
      setServices(res.data);
    } catch { /* empty */ }
    setLoading(false);
  };

  useEffect(() => {
    api.get('/admin/categories').then(r => setCategories(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (categories.length > 0 || !catFilter) fetchServices();
  }, [search, catFilter, categories]);

  const getCat = (catId) => {
    const c = categories.find(x => x.id === catId);
    return c ? { name: c.name, slug: c.slug } : { name: '', slug: '' };
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams(search ? { search } : {});
  };

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 80 }}>
      <div className="page-header">
        <h1>All <span className="gradient-text">Services</span></h1>
      </div>

      {/* Search & Filter */}
      <form className="search-bar" onSubmit={handleSearch}>
        <div className="search-input-wrap">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="form-control"
            placeholder="Search services…"
            style={{ paddingLeft: 44 }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            id="search-services"
          />
        </div>
        <select
          className="form-control"
          style={{ maxWidth: 200 }}
          value={catFilter}
          onChange={(e) => { setCatFilter(e.target.value); setSearchParams(e.target.value ? { category: e.target.value } : {}); }}
          id="filter-category"
        >
          <option value="">All Categories</option>
          {categories.map(c => <option key={c.id} value={c.slug}>{c.name}</option>)}
        </select>
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      {/* Results */}
      {loading ? (
        <div className="empty-state"><p>Loading services…</p></div>
      ) : services.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <p>No services found. Try a different search.</p>
        </div>
      ) : (
        <div className="grid grid-3">
          {services.map((svc, i) => (
            <div key={svc.id} className="animate-fadeIn" style={{ animationDelay: `${i * 0.04}s` }}>
              <ServiceCard service={svc} categoryName={getCat(svc.category_id).name} categorySlug={getCat(svc.category_id).slug} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
