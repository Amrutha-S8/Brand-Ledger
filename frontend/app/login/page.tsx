'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_role', data.role);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const demoUsers = [
    { email: 'manager@demo.com', role: 'Manager' },
    { email: 'reviewer@demo.com', role: 'Reviewer' },
    { email: 'creator@demo.com', role: 'Creator' },
  ];

  const fillDemoUser = (email: string) => {
    setEmail(email);
    setPassword('demo1234');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800 rounded-lg shadow-lg p-8">
        <h1 className="text-2xl font-bold text-white mb-6">Brand Ledger</h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-slate-300 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-blue-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-slate-300 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-blue-500 outline-none"
              required
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded transition disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-600">
          <p className="text-slate-400 text-sm mb-3">Demo Users (password: demo1234)</p>
          <div className="space-y-2">
            {demoUsers.map((user) => (
              <button
                key={user.email}
                onClick={() => fillDemoUser(user.email)}
                className="w-full text-left px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded text-sm transition"
              >
                {user.role}: {user.email}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
