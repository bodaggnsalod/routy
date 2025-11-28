import React, { useEffect, useState } from 'react';
import TravelTimePrediction from './TravelTimePrediction';

export default function Landing() {
  const [status, setStatus] = useState({ ok: false, text: 'loading' });
  const [showTravelTime, setShowTravelTime] = useState(false);

  useEffect(() => {
    let mounted = true;
    async function fetchHealth() {
      try {
        const res = await fetch('/health');
        if (!mounted) return;
        if (!res.ok) {
          setStatus({ ok: false, text: 'error' });
          return;
        }
        const data = await res.json();
        setStatus({ ok: data.status === 'ok', text: data.status || 'ok' });
      } catch (e) {
        if (!mounted) return;
        setStatus({ ok: false, text: 'offline' });
      }
    }
    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (showTravelTime) {
    return <TravelTimePrediction />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <img src="/@logo.jpg" alt="logo" className="mx-auto w-48 h-48 object-contain" />
        <div className="mt-6 inline-flex items-center space-x-3">
          <span
            className={`inline-block w-3 h-3 rounded-full ${status.ok ? 'bg-green-500' : 'bg-red-500'}`}
            aria-hidden="true"
          />
          <span className="text-sm text-gray-700">API: {status.text}</span>
        </div>
        <div className="mt-8">
          <button
            onClick={() => setShowTravelTime(true)}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors duration-200"
          >
            Travel Time Prediction
          </button>
        </div>
      </div>
    </div>
  );
}