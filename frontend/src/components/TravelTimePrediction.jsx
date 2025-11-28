import React, { useState } from 'react';

export default function TravelTimePrediction() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const [start, setStart] = useState('Berlin');
  const [end, setEnd] = useState('München');
  const [hoursWindow, setHoursWindow] = useState(12);

  const findOptimalDeparture = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        `/api/v1/travel-time/optimal-departure?start=${start}&end=${end}&hours_window=${hoursWindow}`
      );

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString('de-DE', {
      weekday: 'short',
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTrafficColor = (level) => {
    const colors = {
      'sehr gering': 'bg-green-100 text-green-800 border-green-300',
      'gering': 'bg-green-50 text-green-700 border-green-200',
      'mittel': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'hoch': 'bg-orange-100 text-orange-800 border-orange-300',
      'sehr hoch': 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[level] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 space-y-4">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          🕐 Travel Time Prediction
        </h2>
        <p className="text-gray-600 mb-6">
          Finde den optimalen Startzeitpunkt basierend auf Verkehrsprognosen
        </p>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start
              </label>
              <input
                type="text"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ziel
              </label>
              <input
                type="text"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Suchfenster (Stunden)
            </label>
            <input
              type="range"
              min="4"
              max="24"
              value={hoursWindow}
              onChange={(e) => setHoursWindow(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-gray-600 text-center mt-1">
              {hoursWindow} Stunden
            </div>
          </div>

          <button
            onClick={findOptimalDeparture}
            disabled={loading || !start || !end}
            className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-colors ${
              loading || !start || !end
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? '⏳ Analysiere...' : '🔍 Optimalen Zeitpunkt finden'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">❌ Fehler:</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {/* Recommendation */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-6 shadow-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  ⭐ Empfohlener Startzeitpunkt
                </h3>
                <div className="space-y-2">
                  <div className="text-2xl font-bold text-green-700">
                    {formatTime(result.recommendation.departure_time)}
                  </div>
                  <div className="text-sm text-gray-600">
                    Ankunft: {formatTime(result.recommendation.arrival_time)}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-green-600">
                  {result.recommendation.predicted_time_minutes} min
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Basis: {result.recommendation.base_time_minutes} min
                </div>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-3 gap-3">
              <div className="bg-white rounded p-2 text-center">
                <div className="text-xs text-gray-500">Verzögerung</div>
                <div className="font-bold text-orange-600">
                  +{result.recommendation.delay_minutes} min
                </div>
              </div>
              <div className="bg-white rounded p-2 text-center">
                <div className="text-xs text-gray-500">Verkehrslage</div>
                <div className={`text-xs font-medium px-2 py-1 rounded border ${getTrafficColor(result.recommendation.traffic_level)}`}>
                  {result.recommendation.traffic_level}
                </div>
              </div>
              <div className="bg-white rounded p-2 text-center">
                <div className="text-xs text-gray-500">Konfidenz</div>
                <div className="font-bold text-blue-600">
                  {(result.recommendation.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>

          {/* Alternatives */}
          {result.alternatives && result.alternatives.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-lg mb-3">🔄 Alternative Zeiten</h3>
              <div className="space-y-2">
                {result.alternatives.map((alt, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200 hover:border-blue-300 transition-colors"
                  >
                    <div>
                      <div className="font-medium text-gray-800">
                        {formatTime(alt.departure_time)}
                      </div>
                      <div className="text-xs text-gray-500">
                        Ankunft: {formatTime(alt.arrival_time)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-gray-700">
                        {alt.predicted_time_minutes} min
                      </div>
                      <div className={`text-xs px-2 py-1 rounded border mt-1 ${getTrafficColor(alt.traffic_level)}`}>
                        {alt.traffic_level}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {result.total_options_analyzed}
                </div>
                <div className="text-xs text-gray-600">Optionen analysiert</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {result.search_window_hours}h
                </div>
                <div className="text-xs text-gray-600">Zeitfenster</div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
            💡 <strong>Tipp:</strong> Die Vorhersage basiert auf typischen Verkehrsmustern 
            (Rush Hour, etc.) und aktuellen Live-Daten der Autobahn API.
          </div>
        </div>
      )}
    </div>
  );
}
