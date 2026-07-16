import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      
      // Navigate based on role will be handled by App.tsx routing
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (role: string) => {
    const credentials: Record<string, { email: string; password: string }> = {
      admin: { email: 'admin@autosense.ai', password: 'admin123' },
      manager: { email: 'manager.mumbai@autosense.ai', password: 'manager123' },
      mechanic: { email: 'mechanic.mumbai@autosense.ai', password: 'mechanic123' },
      owner: { email: 'owner@example.com', password: 'owner123' },
    };

    const creds = credentials[role];
    if (creds) {
      setEmail(creds.email);
      setPassword(creds.password);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-blue-600 mb-2">AutoSense AI</h1>
          <p className="text-gray-600">Intelligent Vehicle Diagnosis Platform</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Sign In</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="your.email@example.com"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Quick Login Buttons (Dev Mode) */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center mb-3">Quick Login (Demo)</p>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => quickLogin('admin')}
                className="px-3 py-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Admin
              </button>
              <button
                onClick={() => quickLogin('manager')}
                className="px-3 py-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Manager
              </button>
              <button
                onClick={() => quickLogin('mechanic')}
                className="px-3 py-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Mechanic
              </button>
              <button
                onClick={() => quickLogin('owner')}
                className="px-3 py-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Owner
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-600 mt-6">
          © 2024 AutoSense AI. All rights reserved.
        </p>
      </div>
    </div>
  );
};

export default Login;
