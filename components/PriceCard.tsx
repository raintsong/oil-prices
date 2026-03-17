'use client';

// Define the shape of the data coming from Flask
interface PriceData {
  current: number;
  source_name: string;
  source_url: string;
  as_of: string;
  d1: { abs: number; pct: number };
  d7: { abs: number; pct: number };
  d30: { abs: number; pct: number };
  peak_2026?: { val: number; date: string };
}

const fmt = (val: number) => val.toLocaleString('en-US', { 
  minimumFractionDigits: 2, 
  maximumFractionDigits: 2 
});

const StatBox = ({ label, stat }: { label: string; stat: any }) => {
  if (!stat) return <div className="bg-slate-50 dark:bg-black/20 p-2 rounded-xl h-12" />;
  const isPos = stat.abs >= 0;
  const color = isPos ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400';
  return (
    <div className="bg-slate-50 dark:bg-black/40 p-2 rounded-xl border border-slate-200 dark:border-slate-800/50 text-center">
      <p className="text-[8px] text-slate-400 dark:text-slate-600 font-black uppercase mb-1">{label}</p>
      <p className={`${color} text-[11px] font-bold leading-none mb-1`}>
        {isPos ? '+' : ''}${fmt(Math.abs(stat.abs))}
      </p>
      <p className={`${color} text-[9px] font-medium opacity-60 leading-none`}>
        {isPos ? '+' : ''}{stat.pct}%
      </p>
    </div>
  );
};

export default function PriceCard({ label, data, loading }: { label: string; data?: PriceData; loading: boolean }) {
  if (loading) return <div className="loading-shimmer h-44 rounded-3xl" />;
  
  if (!data) return (
    <div className="h-44 flex flex-col items-center justify-center bg-slate-100 dark:bg-slate-900/50 rounded-3xl border border-slate-200 dark:border-slate-800">
      <p className="text-[10px] font-black text-rose-500 uppercase">{label}</p>
      <p className="text-[9px] text-slate-400 uppercase font-bold mt-1 tracking-widest">No Data Available</p>
    </div>
  );

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-5 shadow-sm transition-all">
      <div className="flex justify-between items-start mb-4">
        <div>
          <a href={data.source_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 group italic">
            <h2 className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-wider group-hover:underline">{label}</h2>
          </a>
          <p className="text-[8px] text-slate-400 dark:text-slate-600 font-bold uppercase mt-0.5">{data.source_name}</p>
          <p className="text-[9px] text-slate-400 dark:text-slate-500 font-bold uppercase mt-1">{data.as_of}</p>
        </div>
        <div className="text-3xl font-mono font-bold text-slate-900 dark:text-white tracking-tighter">
          ${fmt(data.current)}
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-2">
        <StatBox label="1D" stat={data.d1} />
        <StatBox label="7D" stat={data.d7} />
        <StatBox label="30D" stat={data.d30} />
      </div>

      {data.peak_2026 && (
        <div className="mt-3 py-1.5 px-3 bg-amber-500/10 border border-amber-500/20 rounded-xl flex justify-between items-center">
          <span className="text-[9px] font-black text-amber-600 dark:text-amber-500 uppercase tracking-tighter">
            2026 High ({data.peak_2026.date})
          </span>
          <span className="text-[10px] font-bold text-amber-700 dark:text-amber-500">
            ${fmt(data.peak_2026.val)}
          </span>
        </div>
      )}
    </div>
  );
}