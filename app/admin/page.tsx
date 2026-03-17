'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import PriceCard from '@/components/PriceCard';

// Mapping categories to friendly labels
const CATEGORIES = {
  brent: "Brent Crude",
  wti: "WTI Crude",
  natgas: "Henry Hub",
  gasoline: "RBOB Gasoline",
  algonquin: "Algonquin Gas",
  retail_gas_nat: "US Retail Gas (AAA)",
  retail_gas_ma: "MA Retail Gas (AAA)",
  heating_oil: "MA Heating Oil",
  jetfuel: "Jet Fuel Spot"
};

export default function Dashboard() {
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  const fetchAllPrices = async () => {
    setLoading(true);
    const results: Record<string, any> = {};

    // Map through categories and fetch each from the Flask API
    await Promise.all(
      Object.keys(CATEGORIES).map(async (cat) => {
        try {
          const res = await fetch(`/api/price/${cat}`);
          if (res.ok) {
            results[cat] = await res.json();
          }
        } catch (err) {
          console.error(`Error fetching ${cat}:`, err);
        }
      })
    );

    setPrices(results);
    setLoading(false);
  };

  // Initial load on mount
  useEffect(() => {
    fetchAllPrices();
  }, []);

  return (
    <div className="pb-12">
      {/* Our Header component with the refresh trigger */}
      <Header onRefresh={fetchAllPrices} loading={loading} />

      {/* The Dashboard Grid */}
      <div className="grid gap-4">
        {Object.entries(CATEGORIES).map(([id, label]) => (
          <PriceCard 
            key={id} 
            label={label} 
            data={prices[id]} 
            loading={loading} 
          />
        ))}
      </div>
      
      <footer className="mt-8 text-center">
        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest opacity-50">
          Pulse Energy Data • Next.js + Flask Hybrid
        </p>
      </footer>
    </div>
  );
}