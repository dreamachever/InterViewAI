import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { getCurrentUser } from '../api/users';
import type { User } from '../types/user';

interface AuthState {
  token: string | null;
  user: User | null;
  initializing: boolean;
  isAuthenticated: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(null);
  const [initializing, setInitializing] = useState(Boolean(token));

  const setToken = (nextToken: string | null) => {
    setTokenState(nextToken);
    if (nextToken) {
      localStorage.setItem('access_token', nextToken);
    } else {
      localStorage.removeItem('access_token');
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const handleLogout = () => logout();
    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, []);

  useEffect(() => {
    if (!token) {
      setInitializing(false);
      setUser(null);
      return;
    }
    setInitializing(true);
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        setToken(null);
        setUser(null);
      })
      .finally(() => setInitializing(false));
  }, [token]);

  const value = useMemo(
    () => ({
      token,
      user,
      initializing,
      isAuthenticated: Boolean(token),
      setToken,
      setUser,
      logout,
    }),
    [token, user, initializing],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
