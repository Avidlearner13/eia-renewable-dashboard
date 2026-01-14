import { useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap, FeatureGroup } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';

// Fix for default marker icons in Leaflet with Vite
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Color mapping for energy sources
const getColor = (source) => {
  switch (source) {
    case 'SUN': return '#FFB800';  // Solar - yellow/orange
    case 'WND': return '#00A8E8';  // Wind - blue
    case 'WAT': return '#00C49A';  // Hydro - teal
    default: return '#888888';
  }
};

// Size based on capacity
const getRadius = (capacity) => {
  if (capacity >= 200) return 12;
  if (capacity >= 100) return 10;
  if (capacity >= 50) return 8;
  if (capacity >= 10) return 6;
  return 4;
};

// Component to handle map events
function MapEventHandler({ onPolygonCreated, onPolygonCleared }) {
  const handleCreated = (e) => {
    const { layer } = e;
    if (layer instanceof L.Polygon) {
      const coords = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
      onPolygonCreated(coords);
    }
  };

  const handleDeleted = () => {
    onPolygonCleared();
  };

  return (
    <FeatureGroup>
      <EditControl
        position="topright"
        onCreated={handleCreated}
        onDeleted={handleDeleted}
        draw={{
          rectangle: false,
          circle: false,
          circlemarker: false,
          marker: false,
          polyline: false,
          polygon: {
            allowIntersection: false,
            drawError: {
              color: '#e1e100',
              message: '<strong>Error:</strong> Polygon edges cannot cross!',
            },
            shapeOptions: {
              color: '#3388ff',
              fillOpacity: 0.2,
            },
          },
        }}
        edit={{
          edit: false,
        }}
      />
    </FeatureGroup>
  );
}

// Fly to selected generator
function FlyToGenerator({ generator }) {
  const map = useMap();

  useEffect(() => {
    if (generator) {
      map.flyTo([generator.lat, generator.lon], 10, { duration: 1 });
    }
  }, [generator, map]);

  return null;
}

function Map({ generators, onGeneratorSelect, onPolygonCreated, onPolygonCleared, selectedGenerator }) {
  const mapRef = useRef(null);

  // US center
  const center = [39.8283, -98.5795];
  const zoom = 4;

  // Memoize markers for performance
  const markers = useMemo(() => {
    return generators.map((gen) => (
      <CircleMarker
        key={gen.id}
        center={[gen.lat, gen.lon]}
        radius={getRadius(gen.capacity_mw)}
        pathOptions={{
          color: selectedGenerator?.id === gen.id ? '#ff0000' : getColor(gen.energy_source),
          fillColor: getColor(gen.energy_source),
          fillOpacity: 0.7,
          weight: selectedGenerator?.id === gen.id ? 3 : 1,
        }}
        eventHandlers={{
          click: () => onGeneratorSelect(gen),
        }}
      >
        <Popup>
          <div className="popup-content">
            <strong>{gen.name}</strong><br />
            <span style={{ color: getColor(gen.energy_source) }}>
              {gen.energy_source === 'SUN' ? '☀️ Solar' : gen.energy_source === 'WND' ? '🌬️ Wind' : '💧 Hydro'}
            </span><br />
            Capacity: {gen.capacity_mw.toLocaleString()} MW<br />
            State: {gen.state}<br />
            {gen.operating_year && <>Since: {gen.operating_year}</>}
          </div>
        </Popup>
      </CircleMarker>
    ));
  }, [generators, selectedGenerator, onGeneratorSelect]);

  return (
    <MapContainer
      ref={mapRef}
      center={center}
      zoom={zoom}
      style={{ height: '100%', width: '100%' }}
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Dark mode alternative */}
      {/* <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      /> */}

      <MapEventHandler
        onPolygonCreated={onPolygonCreated}
        onPolygonCleared={onPolygonCleared}
      />

      <FlyToGenerator generator={selectedGenerator} />

      {markers}
    </MapContainer>
  );
}

export default Map;
