'use client';

import Link from 'next/link';

interface HeaderProps {
  onRefresh: () => void;
  loading: boolean;
  lastUpdated: string; // Add this line
}

export default function Header({ onRefresh, loading, lastUpdated }: HeaderProps) {
  return (
    <header className="py-6 border-b border-slate-200 dark:border-slate-800/50 mb-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tighter italic leading-none uppercase">
            Pulse
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-[10px] text-blue-600 dark:text-blue-500 font-bold uppercase tracking-widest">
              {loading ? 'Updating...' : `Ready • ${lastUpdated}`}
            </p>
            <Link 
              href="/admin" 
              className="text-slate-400 hover:text-blue-500 transition-colors" 
              onClick={(e) => e.stopPropagation()}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
      
      <button 
        onClick={onRefresh}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-black py-3 rounded-2xl shadow-lg uppercase tracking-widest transition-all active:scale-95 disabled:opacity-50"
      >
        {loading ? 'Fetching Latest Prices...' : 'Refresh Prices'}
      </button>
    </header>
  );
}