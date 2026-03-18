'use client';

interface PriceCardProps {
  label: string;
  data: any;
  loading: boolean;
}

const fmt = (val: any) => {
  const num = parseFloat(val);
  return isNaN(num) ? "0.00" : num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

export default function PriceCard({ label, data, loading }: PriceCardProps) {
  if (loading) return <div className="loading-shimmer h-44 w-full rounded-3xl border border-slate-200 dark:border-slate-800" />;
  
  if (!data || data.price === undefined) {
    return (
      <div className="p-6 bg-slate-50 dark:bg-slate-900/40 rounded-3xl border border-dashed border-slate-200 dark:border-slate-800">
        <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2">{label}</h3>
        <p className="text-[10px] font-bold text-rose-500 uppercase tracking-widest italic">Data Not Available</p>
      </div>
    );
  }

  const isGas = label.toLowerCase().includes("gas");
  const isManual = data.source?.toLowerCase().includes("manual");

  // Display price: 3 decimals for gas, 2 for oil
  const displayPrice = isGas ? parseFloat(data.price).toFixed(3) : fmt(data.price);

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm transition-all hover:shadow-md">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-400">{label}</h3>
        {isManual && (
          <span className="text-[8px] bg-blue-600/10 text-blue-600 px-2 py-0.5 rounded-full font-black uppercase">
            {data.days_ago === 0 ? 'Live Update' : `${data.days_ago}d Old`}
          </span>
        )}
      </div>
      
      <div className="flex items-baseline gap-1 mb-4">
        <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tighter italic">
          ${displayPrice}
        </span>
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          {isGas ? '/gal' : '/bbl'}
        </span>
      </div>

      {/* History Grid with Absolute Prices */}
      <div className="grid grid-cols-3 gap-4 py-4 border-y border-slate-50 dark:border-slate-800/50">
        {[
          { id: '1D', pct: data.change_1d, abs: data.abs_1d },
          { id: '7D', pct: data.history?.d7_pct, abs: data.history?.d7_abs },
          { id: '30D', pct: data.history?.d30_pct, abs: data.history?.d30_abs }
        ].map((item) => {
          const hasData = item.pct !== undefined && item.pct !== null;
          const isPos = (item.pct || 0) >= 0;
          
          return (
            <div key={item.id} className={!hasData ? 'opacity-30' : ''}>
              <p className="text-[8px] font-black text-slate-400 uppercase mb-1">{item.id}</p>
              <p className={`text-[11px] font-black leading-tight ${!hasData ? 'text-slate-400' : isPos ? 'text-emerald-500' : 'text-rose-500'}`}>
                {hasData ? `${isPos ? '+' : ''}${item.pct}%` : 'N/A'}
              </p>
              <p className="text-[9px] font-bold text-slate-400 tabular-nums">
                {hasData && item.abs ? `${item.abs > 0 ? '+' : ''}${item.abs.toFixed(2)}` : '--'}
              </p>
            </div>
          );
        })}
      </div>
      <div className="mt-4 pt-4 border-t border-slate-50 dark:border-slate-800/50">
        <div className="flex justify-between items-center">
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
            2026 CY Peak
          </span>
          <div className="text-right">
            <p className="text-[11px] font-black text-slate-900 dark:text-white leading-none">
              {/* Using 3 decimals for anything related to Fuel/Gas categories */}
              ${(label.toLowerCase().includes("fuel") || label.toLowerCase().includes("oil") || isGas) 
                  ? data.peak_2026?.val.toFixed(3) 
                  : data.peak_2026?.val.toFixed(2)}
            </p>
            <p className="text-[8px] font-bold text-slate-400 uppercase">
              On {data.peak_2026?.date || 'N/A'}
            </p>
          </div>
        </div>
      </div>
      <div className="mt-4 flex justify-between items-center text-[9px] font-bold uppercase tracking-widest">
        <p className="text-slate-400">As of {data.date || 'N/A'}</p>
        <a href={data.link} target="_blank" className="text-blue-600 hover:text-blue-500 transition-colors">
          Source →
        </a>
      </div>
    </div>
  );
}