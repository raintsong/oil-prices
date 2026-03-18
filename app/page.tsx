'use client';
import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import PriceCard from '@/components/PriceCard';

const CATEGORIES = {
  retail_gas_nat: "US Retail Gas (AAA)",
  retail_gas_ma: "MA Retail Gas (AAA)",
  brent: "Brent Crude", wti: "WTI Crude", natgas: "Henry Hub",
  gasoline: "RBOB Gasoline", algonquin: "Algonquin Gas",
  heating_oil: "MA Heating Oil", jetfuel: "Jet Fuel Spot"
};

export default function Dashboard() {
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    const results: Record<string, any> = {};
    
    await Promise.all(Object.keys(CATEGORIES).map(async (cat) => {
      try {
        const res = await fetch(`/api/price/${cat}`);
        if (res.ok) results[cat] = await res.json();
      } catch (e) { console.error(e); }
    }));

    setPrices(results);
    setLoading(false);
  };

  useEffect(() => { fetchAll(); }, []);

  return (
    <div className="max-w-lg mx-auto">
      <Header onRefresh={fetchAll} loading={loading} />
      <div className="grid gap-4 pb-12">
        {Object.entries(CATEGORIES).map(([id, label]) => (
          <PriceCard key={id} label={label} data={prices[id]} loading={loading} />
        ))}
      </div>
    </div>
  );
}