import React, { useEffect, useRef } from 'react';
import germanyCoords from '../../germany_coords.json';

const GermanyMap = () => {
  const canvasRef = useRef(null);

  // Deutsche Städte über 500k Einwohner mit geografischen Koordinaten
  // Format: [lon, lat] -> umgerechnet auf normalized coords
  const cities = [
    { name: 'Berlin', lat: 52.52, lon: 13.405, population: 3850000 },
    { name: 'Hamburg', lat: 53.551, lon: 9.993, population: 1900000 },
    { name: 'München', lat: 48.137, lon: 11.576, population: 1560000 },
    { name: 'Köln', lat: 50.937, lon: 6.96, population: 1090000 },
    { name: 'Frankfurt', lat: 50.11, lon: 8.682, population: 760000 },
    { name: 'Stuttgart', lat: 48.775, lon: 9.182, population: 630000 },
    { name: 'Düsseldorf', lat: 51.227, lon: 6.773, population: 620000 },
    { name: 'Dortmund', lat: 51.514, lon: 7.468, population: 590000 },
    { name: 'Essen', lat: 51.455, lon: 7.012, population: 580000 },
    { name: 'Leipzig', lat: 51.34, lon: 12.37, population: 600000 },
    { name: 'Bremen', lat: 53.075, lon: 8.807, population: 570000 },
    { name: 'Dresden', lat: 51.05, lon: 13.738, population: 560000 },
    { name: 'Hannover', lat: 52.375, lon: 9.738, population: 540000 },
    { name: 'Nürnberg', lat: 49.453, lon: 11.077, population: 520000 },
  ];

  // Deutschland Bounding Box (ungefähr)
  const germanyBounds = {
    minLat: 47.27, // Süden (Alpen)
    maxLat: 55.06, // Norden (Nordsee)
    minLon: 5.87,  // Westen (NRW)
    maxLon: 15.04, // Osten (Sachsen)
  };

  // Konvertiere geografische Koordinaten zu Canvas-Pixeln
  const geoToCanvas = (lat, lon, width, height) => {
    const x = ((lon - germanyBounds.minLon) / (germanyBounds.maxLon - germanyBounds.minLon)) * width;
    // Y-Achse ist invertiert (Canvas 0 ist oben)
    const y = (1 - (lat - germanyBounds.minLat) / (germanyBounds.maxLat - germanyBounds.minLat)) * height;
    return { x, y };
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Hintergrund
    ctx.fillStyle = '#f0f9ff';
    ctx.fillRect(0, 0, width, height);

    // Deutschland-Umriss zeichnen
    if (germanyCoords && germanyCoords.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = '#1e40af';
      ctx.lineWidth = 2;
      ctx.fillStyle = '#dbeafe';

      // germany_coords.json enthält normalisierte Koordinaten [x, y]
      // Diese müssen auf Canvas-Größe skaliert werden
      germanyCoords.forEach((point, index) => {
        const x = point[0] * width;
        const y = point[1] * height;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }

    // Städte einzeichnen
    cities.forEach(city => {
      const pos = geoToCanvas(city.lat, city.lon, width, height);

      // Stadt-Marker (Kreis)
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 6, 0, 2 * Math.PI);
      ctx.fillStyle = '#dc2626';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Stadt-Name
      ctx.fillStyle = '#1f2937';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(city.name, pos.x, pos.y - 12);

      // Einwohnerzahl
      ctx.fillStyle = '#6b7280';
      ctx.font = '10px sans-serif';
      ctx.fillText(
        `${(city.population / 1000000).toFixed(1)}M`,
        pos.x,
        pos.y + 20
      );
    });

    // Legende
    ctx.fillStyle = '#fff';
    ctx.fillRect(10, 10, 200, 80);
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1;
    ctx.strokeRect(10, 10, 200, 80);

    ctx.fillStyle = '#1f2937';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Deutschland Karte', 20, 30);

    ctx.font = '11px sans-serif';
    ctx.fillStyle = '#6b7280';
    ctx.fillText(`${cities.length} Städte > 500k Einwohner`, 20, 50);

    // Marker-Beispiel in Legende
    ctx.beginPath();
    ctx.arc(30, 70, 5, 0, 2 * Math.PI);
    ctx.fillStyle = '#dc2626';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = '#6b7280';
    ctx.fillText('Stadt-Marker', 45, 75);

  }, []);

  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-6xl w-full">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Deutschland Karte</h2>
          <p className="text-sm text-gray-600 mt-1">
            Interaktive Karte mit allen Städten über 500.000 Einwohner
          </p>
        </div>
        
        <div className="border border-gray-300 rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            width={1200}
            height={1400}
            className="w-xl h-auto"
            style={{ maxHeight: '80vh' }}
          />
        </div>

        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-600">
          {cities
            .sort((a, b) => b.population - a.population)
            .map(city => (
              <div key={city.name} className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-600 rounded-full"></div>
                <span className="font-medium">{city.name}</span>
                <span className="text-gray-400">
                  {(city.population / 1000000).toFixed(1)}M
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default GermanyMap;
