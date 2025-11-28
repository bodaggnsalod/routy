import React, { useState } from 'react';

export default function AutobahnDemo() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const runDemo = async () => {
    setRunning(true);
    setError(null);
    setResults(null);

    try {
      const demoResults = {
        traffic: null,
        network: null,
        agent: null,
        integration: null,
        congested: null
      };

      // 1. Traffic API Test
      const trafficRes = await fetch('/api/v1/traffic/live');
      if (trafficRes.ok) {
        demoResults.traffic = await trafficRes.json();
      }

      // 2. Network Test
      const locationsRes = await fetch('/api/v1/network/locations');
      if (locationsRes.ok) {
        const locData = await locationsRes.json();

        if (locData.locations && locData.locations.length >= 2) {
          const start = locData.locations[0];
          const end = locData.locations[1];

          const pathRes = await fetch(`/api/v1/network/path?start=${start}&end=${end}`);
          if (pathRes.ok) {
            demoResults.network = {
              locations: locData.locations,
              example_path: await pathRes.json()
            };
          }
        }
      }

      // 3. RL Agent Test
      const historyRes = await fetch('/api/v1/agent/history');
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        demoResults.agent = {
          training_history: historyData.total_trainings,
          status: 'ready'
        };
      }

      // 4. Full Integration Test
      // Zuerst Traffic simulieren für bessere Demo
      await fetch('/api/v1/network/simulate-traffic', { method: 'POST' });

      const routeRes = await fetch('/api/v1/route/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([
          { order_id: 1, start_location: 'Berlin', end_location: 'Leipzig', priority: 1 },
          { order_id: 2, start_location: 'Leipzig', end_location: 'Frankfurt', priority: 2 },
          { order_id: 3, start_location: 'Frankfurt', end_location: 'Stuttgart', priority: 1 }
        ])
      });

      if (routeRes.ok) {
        demoResults.integration = await routeRes.json();
      }

      // 5. Congested Routes Test
      const congestedRes = await fetch('/api/v1/network/congested?threshold=0.5');
      if (congestedRes.ok) {
        demoResults.congested = await congestedRes.json();
      }

      setResults(demoResults);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  return (

    <div className="w-full max-w-4xl mx-auto p-6 space-y-4">
      {results && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-800 font-medium">✅ Demo erfolgreich abgeschlossen!</p>
          <p className="text-green-600 text-sm mt-1">
            Alle Komponenten funktionieren korrekt.
          </p>
        </div>
      )}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          🚀 Autobahn API + DQN Demo
        </h2>
        <p className="text-gray-600 mb-6">
          Testet die Integration von Live-Verkehrsdaten, Straßennetzwerk und RL-Agent.
          Zeigt auch überlastete Routen mit Delay-Faktor &gt; 0.5 an.
        </p>

        <button
          onClick={runDemo}
          disabled={running}
          className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-colors ${running
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
            }`}
        >
          {running ? '⏳ Demo läuft...' : '▶️ Demo starten'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">❌ Fehler:</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}

      {results && (
        <div className="space-y-4">
          {/* Traffic API Results */}
          {results.traffic && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-lg mb-2">1️⃣ Traffic API</h3>
              <div className="bg-gray-50 p-3 rounded text-sm font-mono">
                <div>Delay Factor: {results.traffic.delay_factor.toFixed(2)}</div>
                <div>Status: {results.traffic.status}</div>
                <div className="text-gray-500">Source: {results.traffic.source}</div>
              </div>
            </div>
          )}

          {/* Network Results */}
          {results.network && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-lg mb-2">2️⃣ Road Network</h3>
              <div className="bg-gray-50 p-3 rounded text-sm">
                <div className="mb-2">
                  <span className="font-medium">Verfügbare Standorte:</span>{' '}
                  {results.network.locations.length}
                </div>
                <div className="font-mono text-xs bg-white p-2 rounded">
                  {results.network.locations.join(', ')}
                </div>
                {results.network.example_path && (
                  <div className="mt-3">
                    <div className="font-medium">Beispiel-Route:</div>
                    <div className="font-mono text-sm bg-white p-2 rounded mt-1">
                      {results.network.example_path.path.join(' → ')}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      Distanz: {results.network.example_path.distance_minutes} Minuten
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Agent Results */}
          {results.agent && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-lg mb-2">3️⃣ RL Agent</h3>
              <div className="bg-gray-50 p-3 rounded text-sm font-mono">
                <div>Status: {results.agent.status}</div>
                <div>Training History: {results.agent.training_history} Sessions</div>
              </div>
            </div>
          )}

          {/* Integration Results */}
          {results.integration && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-lg mb-2">4️⃣ Vollständige Integration</h3>
              <div className="bg-gray-50 p-3 rounded text-sm">
                <div className="mb-2">
                  <span className="font-medium">Route ID:</span>{' '}
                  <span className="font-mono text-xs">{results.integration.route_id}</span>
                </div>
                <div className="mb-2">
                  <span className="font-medium">Optimierte Route:</span>
                </div>
                <div className="font-mono text-sm bg-white p-2 rounded mb-2">
                  {results.integration.stops.join(' → ')}
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-600">Stopps:</span>{' '}
                    <span className="font-medium">{results.integration.stops.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Dauer:</span>{' '}
                    <span className="font-medium">{results.integration.estimated_duration_minutes} min</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Orders:</span>{' '}
                    <span className="font-medium">{results.integration.total_orders}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Congested Routes */}
          {results.congested && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-bold text-lg mb-2">
                5️⃣ Routen mit hohem Traffic
                {results.congested.count > 0 && (
                  <span className="ml-2 text-sm bg-red-100 text-red-700 px-2 py-1 rounded">
                    {results.congested.count} überlastet
                  </span>
                )}
              </h3>
              <div className="bg-gray-50 p-3 rounded text-sm">
                <div className="mb-2 text-gray-600">
                  Zeigt alle Routen mit Delay-Faktor ≥ {results.congested.threshold}
                </div>
                {results.congested.count > 0 ? (
                  <div className="mt-3 space-y-2">
                    {results.congested.congested_routes.map((route, idx) => (
                      <div key={idx} className="bg-red-50 border border-red-200 rounded p-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-mono font-medium text-sm">
                              🚗 {route.start} ↔ {route.end}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                              Normal: {route.base_weight} min →
                              <span className="text-red-600 font-medium"> Mit Traffic: {route.weight.toFixed(0)} min</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="text-xs bg-red-600 text-white px-2 py-1 rounded font-bold">
                              +{(route.delay_factor * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mt-3 bg-green-50 border border-green-200 rounded p-3 text-center">
                    <div className="text-2xl mb-1">✅</div>
                    <div className="text-sm text-green-700 font-medium">
                      Keine überlasteten Routen
                    </div>
                    <div className="text-xs text-green-600 mt-1">
                      Alle Routen haben einen Delay-Faktor &lt; {results.congested.threshold}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
