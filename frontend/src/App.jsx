import { useState, useEffect, useCallback } from 'react';
import Map from './components/Map';
import Analytics from './components/Analytics';
import GeneratorList from './components/GeneratorList';
import FilterPanel from './components/FilterPanel';
import { fetchGenerators, fetchRealtimeGeneration } from './api';
import './App.css';

// Point in polygon check
function pointInPolygon(lat, lon, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0], yi = polygon[i][1];
    const xj = polygon[j][0], yj = polygon[j][1];
    if (((yi > lon) !== (yj > lon)) && (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  return inside;
}

function App() {
  const [generators, setGenerators] = useState([]);
  const [filteredGenerators, setFilteredGenerators] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);
  const [polygonCoords, setPolygonCoords] = useState(null);
  const [polygonGenerators, setPolygonGenerators] = useState([]);
  const [selectedGenerator, setSelectedGenerator] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [filters, setFilters] = useState({
    energySource: 'all',
    minCapacity: 0,
    states: '',
  });
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Load all generators with pagination
  const loadAllGenerators = useCallback(async () => {
    setLoading(true);
    setLoadingStatus('Loading solar generators...');

    try {
      // Load solar and wind separately to get more data
      const solar = await fetchGenerators({ energy_source: 'SUN', limit: 5000 });
      setLoadingStatus(`Loaded ${solar.length} solar generators. Loading wind...`);

      const wind = await fetchGenerators({ energy_source: 'WND', limit: 5000 });
      setLoadingStatus(`Loaded ${solar.length + wind.length} total generators.`);

      const allGens = [...solar, ...wind];
      setGenerators(allGens);
      setFilteredGenerators(allGens);

      return allGens;
    } catch (error) {
      console.error('Error loading generators:', error);
      setLoadingStatus('Error loading data');
      return [];
    }
  }, []);

  // Load realtime data
  const loadRealtimeData = useCallback(async () => {
    try {
      const realtime = await fetchRealtimeGeneration();
      setRealtimeData(realtime);
    } catch (error) {
      console.error('Error loading realtime data:', error);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    async function loadData() {
      await loadAllGenerators();
      await loadRealtimeData();
      setLoading(false);
    }
    loadData();
  }, [loadAllGenerators, loadRealtimeData]);

  // Auto-refresh realtime data every 5 minutes
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadRealtimeData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [autoRefresh, loadRealtimeData]);

  // Apply filters
  useEffect(() => {
    let filtered = [...generators];

    if (filters.energySource !== 'all') {
      filtered = filtered.filter(g => g.energy_source === filters.energySource);
    }

    if (filters.minCapacity > 0) {
      filtered = filtered.filter(g => g.capacity_mw >= filters.minCapacity);
    }

    if (filters.states) {
      const stateList = filters.states.split(',').map(s => s.trim().toUpperCase());
      filtered = filtered.filter(g => stateList.includes(g.state));
    }

    setFilteredGenerators(filtered);
  }, [generators, filters]);

  // Handle polygon drawn - filter from already loaded generators
  const handlePolygonCreated = useCallback((coords) => {
    setPolygonCoords(coords);

    // Filter generators that are inside the polygon
    const inside = filteredGenerators.filter(g =>
      pointInPolygon(g.lat, g.lon, coords)
    );
    setPolygonGenerators(inside);
  }, [filteredGenerators]);

  // Clear polygon
  const handlePolygonCleared = useCallback(() => {
    setPolygonCoords(null);
    setPolygonGenerators([]);
  }, []);

  // Recalculate polygon generators when filtered generators change
  useEffect(() => {
    if (polygonCoords) {
      const inside = filteredGenerators.filter(g =>
        pointInPolygon(g.lat, g.lon, polygonCoords)
      );
      setPolygonGenerators(inside);
    }
  }, [filteredGenerators, polygonCoords]);

  // Calculate summary stats
  const stats = {
    totalGenerators: filteredGenerators.length,
    solarCount: filteredGenerators.filter(g => g.energy_source === 'SUN').length,
    windCount: filteredGenerators.filter(g => g.energy_source === 'WND').length,
    totalCapacity: filteredGenerators.reduce((sum, g) => sum + g.capacity_mw, 0),
    solarCapacity: filteredGenerators.filter(g => g.energy_source === 'SUN')
      .reduce((sum, g) => sum + g.capacity_mw, 0),
    windCapacity: filteredGenerators.filter(g => g.energy_source === 'WND')
      .reduce((sum, g) => sum + g.capacity_mw, 0),
  };

  // Polygon stats
  const polygonStats = polygonCoords ? {
    total: polygonGenerators.length,
    solarCount: polygonGenerators.filter(g => g.energy_source === 'SUN').length,
    windCount: polygonGenerators.filter(g => g.energy_source === 'WND').length,
    solarCapacity: polygonGenerators.filter(g => g.energy_source === 'SUN')
      .reduce((sum, g) => sum + g.capacity_mw, 0),
    windCapacity: polygonGenerators.filter(g => g.energy_source === 'WND')
      .reduce((sum, g) => sum + g.capacity_mw, 0),
    totalCapacity: polygonGenerators.reduce((sum, g) => sum + g.capacity_mw, 0),
    states: [...new Set(polygonGenerators.map(g => g.state))],
  } : null;

  // Refresh handler
  const handleRefresh = async () => {
    setLoading(true);
    await loadRealtimeData();
    setLoading(false);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Renewable Energy Dashboard</h1>
        <span className="subtitle">U.S. EIA Data Visualization</span>
        <div className="header-actions">
          <button onClick={handleRefresh} disabled={loading}>
            Refresh Data
          </button>
          <label className="auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh (5min)
          </label>
        </div>
      </header>

      <div className="main-content">
        <aside className="sidebar">
          <FilterPanel filters={filters} setFilters={setFilters} />

          <div className="stats-card">
            <h3>Summary</h3>
            <div className="stat-row">
              <span>Total Generators:</span>
              <span className="stat-value">{stats.totalGenerators.toLocaleString()}</span>
            </div>
            <div className="stat-row">
              <span>Solar:</span>
              <span className="stat-value solar">{stats.solarCount.toLocaleString()}</span>
            </div>
            <div className="stat-row">
              <span>Wind:</span>
              <span className="stat-value wind">{stats.windCount.toLocaleString()}</span>
            </div>
            <div className="stat-row">
              <span>Total Capacity:</span>
              <span className="stat-value">{stats.totalCapacity.toLocaleString()} MW</span>
            </div>
          </div>

          {polygonStats && (
            <div className="stats-card polygon-stats">
              <h3>Selected Area</h3>
              <button className="clear-btn" onClick={handlePolygonCleared}>Clear</button>
              <div className="stat-row">
                <span>Generators:</span>
                <span className="stat-value">{polygonStats.total.toLocaleString()}</span>
              </div>
              <div className="stat-row">
                <span>Solar:</span>
                <span className="stat-value solar">
                  {polygonStats.solarCount.toLocaleString()} ({polygonStats.solarCapacity.toLocaleString()} MW)
                </span>
              </div>
              <div className="stat-row">
                <span>Wind:</span>
                <span className="stat-value wind">
                  {polygonStats.windCount.toLocaleString()} ({polygonStats.windCapacity.toLocaleString()} MW)
                </span>
              </div>
              <div className="stat-row">
                <span>Total Capacity:</span>
                <span className="stat-value">{polygonStats.totalCapacity.toLocaleString()} MW</span>
              </div>
              <div className="stat-row">
                <span>States:</span>
                <span className="stat-value">{polygonStats.states.join(', ') || 'None'}</span>
              </div>
            </div>
          )}
        </aside>

        <main className="map-container">
          {loading ? (
            <div className="loading">
              <div className="loading-spinner"></div>
              <p>{loadingStatus || 'Loading renewable energy data...'}</p>
            </div>
          ) : (
            <Map
              generators={filteredGenerators}
              onGeneratorSelect={setSelectedGenerator}
              onPolygonCreated={handlePolygonCreated}
              onPolygonCleared={handlePolygonCleared}
              selectedGenerator={selectedGenerator}
              polygonGenerators={polygonGenerators}
            />
          )}
        </main>

        <aside className="right-panel">
          <Analytics
            realtimeData={realtimeData}
            generators={filteredGenerators}
            polygonGenerators={polygonGenerators}
          />

          {selectedGenerator && (
            <div className="generator-detail">
              <h3>Selected Generator</h3>
              <p className="generator-name">{selectedGenerator.name}</p>
              <div className="detail-row">
                <span>State:</span> {selectedGenerator.state}
              </div>
              <div className="detail-row">
                <span>Type:</span> {selectedGenerator.technology}
              </div>
              <div className="detail-row">
                <span>Capacity:</span> {selectedGenerator.capacity_mw.toLocaleString()} MW
              </div>
              <div className="detail-row">
                <span>Coordinates:</span> {selectedGenerator.lat.toFixed(4)}, {selectedGenerator.lon.toFixed(4)}
              </div>
              {selectedGenerator.operating_year && (
                <div className="detail-row">
                  <span>Operating Since:</span> {selectedGenerator.operating_year}
                </div>
              )}
            </div>
          )}

          <GeneratorList
            generators={polygonGenerators.length > 0 ? polygonGenerators.slice(0, 50) : filteredGenerators.slice(0, 50)}
            onSelect={setSelectedGenerator}
            selectedId={selectedGenerator?.id}
            title={polygonGenerators.length > 0 ? 'Generators in Selection' : 'Top Generators'}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
