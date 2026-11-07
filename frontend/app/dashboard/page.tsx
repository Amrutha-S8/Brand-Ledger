'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    const role = localStorage.getItem('user_role');
    setUser({ role });
    setLoading(false);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    router.push('/login');
  };

  if (loading) {
    return <div className="text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded transition"
          >
            Logout
          </button>
        </div>

        <div className="bg-slate-800 rounded-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-white mb-2">Welcome</h2>
          <p className="text-slate-300">Role: {user?.role || 'User'}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-2">Brand Health</h3>
            <p className="text-3xl font-bold text-blue-400">92%</p>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-2">Active Rules</h3>
            <p className="text-3xl font-bold text-green-400">4</p>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-lg font-bold text-white mb-2">Pending Reviews</h3>
            <p className="text-3xl font-bold text-yellow-400">2</p>
          </div>
        </div>
      </div>
    </div>
  );
}
