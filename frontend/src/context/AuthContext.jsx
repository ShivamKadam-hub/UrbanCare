import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('uc_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentToken = localStorage.getItem('uc_token');
    if (!currentToken || currentToken === 'null' || currentToken === 'undefined') {
      setToken(null);
      setUser(null);
      setLoading(false);
      return;
    }

    api.get('/auth/me', { headers: { Authorization: `Bearer ${currentToken}` } })
      .then((res) => {
        setUser(res.data);
        setToken(currentToken);
      })
      .catch(() => {
        localStorage.removeItem('uc_token');
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);  // run once on mount

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const t = res.data.access_token;

    if (!t) {
      throw new Error('Login did not return access_token');
    }

    localStorage.setItem('uc_token', t);
    setToken(t);

    const me = await api.get('/auth/me', { headers: { Authorization: `Bearer ${t}` } });
    setUser(me.data);
    return me.data;
  };

  const register = async (data) => {
    const res = await api.post('/auth/register', data);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('uc_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
