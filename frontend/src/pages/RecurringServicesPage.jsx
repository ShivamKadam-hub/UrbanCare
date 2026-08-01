import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import RecurringServices from '../components/RecurringServices';
import { useAuth } from '../context/AuthContext';

export default function RecurringServicesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (user.role !== 'customer') {
      if (user.role === 'provider') {
        navigate('/provider');
      } else if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    }
  }, [user, navigate]);

  if (!user || user.role !== 'customer') {
    return null;
  }

  return <RecurringServices />;
}
