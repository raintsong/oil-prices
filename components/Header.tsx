'use client';

export default function Header({ onRefresh, loading }: { onRefresh: () => void, loading: boolean }) {
  return (
    <header className="py-6 border-b border-slate-200 dark:border-slate-800/50 mb-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tighter italic leading-none uppercase">
            Pulse
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-[10px] text-blue-600 dark:text-blue-500 font-bold uppercase tracking-widest">
              {loading ? 'Updating...' : 'Ready'}
            </p>
          </div>
        </div>
      </div>
      <button 
        onClick={onRefresh}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-black py-3 rounded-2xl shadow-lg uppercase tracking-widest transition-all active:scale-95 disabled:opacity-50"
      >
        {loading ? 'Fetching Data...' : 'Refresh Prices'}
      </button>
    </header>
  );
}