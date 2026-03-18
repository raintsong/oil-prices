'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function AdminPage() {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setStatus('Sending to Redis...');
    
    const formData = new FormData(e.currentTarget);
    
    // Construct the payload for your Flask backend
    const payload = {
      date: formData.get('date'),
      national: formData.get('national'),
      ma: formData.get('ma')
    };

    try {
      const res = await fetch('/api/admin/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setStatus('✅ Update Successful!');
        (e.target as HTMLFormElement).reset();
      } else {
        const errorData = await res.json();
        setStatus(`❌ Error: ${errorData.message || 'Update failed'}`);
      }
    } catch (err) {
      setStatus('⚠️ Connection Error. Is Flask running?');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-10 p-8 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-2xl transition-all">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-black uppercase italic tracking-tighter text-slate-900 dark:text-white leading-none">
            Admin Update
          </h1>
          <p className="text-[10px] text-blue-600 font-bold uppercase tracking-widest mt-1">Manual Override</p>
        </div>
        <Link 
          href="/" 
          className="text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-blue-500 transition-colors border border-slate-200 dark:border-slate-800 px-3 py-1 rounded-full"
        >
          ← Back
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Date Input */}
        <div>
          <label className="block text-[10px] font-black uppercase text-slate-400 mb-2 tracking-widest">Effective Date</label>
          <input 
            name="date" 
            type="date" 
            required 
            className="w-full p-4 bg-slate-50 dark:bg-black/40 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all" 
          />
        </div>

        {/* National Price Input */}
        <div>
          <label className="block text-[10px] font-black uppercase text-slate-400 mb-2 tracking-widest">National Avg (AAA)</label>
          <input 
            name="national" 
            type="number" 
            step="0.001" 
            placeholder="e.g. 3.456" 
            required 
            className="w-full p-4 bg-slate-50 dark:bg-black/40 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all" 
          />
        </div>

        {/* MA Price Input */}
        <div>
          <label className="block text-[10px] font-black uppercase text-slate-400 mb-2 tracking-widest">MA Avg (AAA)</label>
          <input 
            name="ma" 
            type="number" 
            step="0.001" 
            placeholder="e.g. 3.210" 
            required 
            className="w-full p-4 bg-slate-50 dark:bg-black/40 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all" 
          />
        </div>

        {/* Submit Button */}
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-black py-4 rounded-2xl uppercase tracking-widest transition-all active:scale-95 disabled:opacity-50 shadow-lg shadow-blue-500/20"
        >
          {loading ? 'Processing...' : 'Push to Redis'}
        </button>

        {/* Status Message */}
        {status && (
          <div className="pt-2 text-center animate-pulse">
            <p className="text-[10px] font-black uppercase tracking-widest text-blue-600 dark:text-blue-400">
              {status}
            </p>
          </div>
        )}
      </form>
    </div>
  );
}