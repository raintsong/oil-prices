'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import PriceCard from '@/components/PriceCard';

// Mapping categories to friendly labels for the UI
const CATEGORIES = {
  brent: "Brent Crude",
  wti: "WTI Crude",
  natgas: "Henry Hub",
  gasoline: "RBOB Gasoline",
//   algonquin: "Algonquin Gas",
  retail_gas_nat: "US Retail Gas (AAA)",
  retail_gas_ma: "MA Retail Gas (AAA)",
  heating_oil: "MA Heating Oil",
  jetfuel: "Jet Fuel Spot"
};

export default function Dashboard() {
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState('');

  /**
   * Fetches all price data from the Flask API in parallel.
   * Updates the global 'lastUpdated' timestamp upon completion.
   */
  const fetchAllPrices = async () => {
    setLoading(true);
    const results: Record<string, any> = {};

    try {
      // Fetch all categories simultaneously for maximum speed
      await Promise.all(
        Object.keys(CATEGORIES).map(async (cat) => {
          try {
            const res = await fetch(`/api/price/${cat}`);
            if (res.ok) {
              results[cat] = await res.json();
            } else {
              console.error(`Failed to fetch ${cat}: ${res.status}`);
            }
          } catch (err) {
            console.error(`Network error fetching ${cat}:`, err);
          }
        })
      );

      setPrices(results);

      // Format the timestamp: "Mar 17, 8:35 PM"
      const now = new Date();
      const formattedTime = now.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
      
      setLastUpdated(formattedTime);
    } catch (globalErr) {
      console.error("Critical error in fetchAllPrices:", globalErr);
    } finally {
      setLoading(false);
    }
  };

  // Initial data load when the component mounts
  useEffect(() => {
    fetchAllPrices();
  }, []);

  return (
    <main className="max-w-xl mx-auto px-4 pb-12">
      {/* Header handles the branding, the global refresh button, 
          and displays the sync status/timestamp.
      */}
      <Header 
        onRefresh={fetchAllPrices} 
        loading={loading} 
        lastUpdated={lastUpdated} 
      />

      {/* The Dashboard Grid:
          Iterates through our categories and renders a PriceCard for each.
      */}
      <div className="grid gap-4 sm:grid-cols-1">
        {Object.entries(CATEGORIES).map(([id, label]) => (
          <PriceCard 
            key={id} 
            label={label} 
            data={prices[id]} 
            loading={loading} 
          />
        ))}
      </div>
      
      <footer className="mt-12 text-center border-t border-slate-100 dark:border-slate-800 pt-8">
        <p className="text-[10px] text-slate-400 font-black uppercase tracking-[0.2em] opacity-50">
          Pulse Energy Analytics • Next.js + Flask + Redis
        </p>
      </footer>
    </main>
  );
}