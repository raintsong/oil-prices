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
  if (loading) return <div className="loading-shimmer h-40 w-full rounded-3xl border border-slate-200 dark:border-slate-800" />;
  
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

  return (
    <div className="p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-400">{label}</h3>
        {isManual && (
          <span className="text-[8px] bg-blue-600/10 text-blue-600 px-2 py-0.5 rounded-full font-black uppercase">
            {data.days_ago === 0 ? 'Updated Today' : `${data.days_ago} Days Old`}
          </span>
        )}
      </div>
      
      <div className="flex items-baseline gap-1 mb-4">
        <span className="text-3xl font-black text-slate-900 dark:text-white tracking-tighter italic">
          ${isGas ? parseFloat(data.price).toFixed(3) : fmt(data.price)}
        </span>
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          {isGas ? '/gal' : '/bbl'}
        </span>
      </div>

      {/* History Grid */}
      <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-50 dark:border-slate-800/50">
        {[
          { label: '1D', val: data.change_1d },
          { label: '7D', val: data.history?.d7_pct },
          { label: '30D', val: data.history?.d30_pct }
        ].map((item) => (
          <div key={item.label}>
            <p className="text-[8px] font-black text-slate-400 uppercase mb-1">{item.label}</p>
            <p className={`text-[10px] font-bold ${item.val === undefined ? 'text-slate-300' : item.val >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
              {item.val !== undefined ? `${item.val >= 0 ? '+' : ''}${item.val}%` : 'N/A'}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-4 flex justify-between items-center">
        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
          As of {data.date || 'N/A'}
        </p>
        <a href={data.link || "#"} target="_blank" className="text-[9px] font-black text-blue-600 uppercase tracking-widest">
          Source →
        </a>
      </div>
    </div>
  );
}