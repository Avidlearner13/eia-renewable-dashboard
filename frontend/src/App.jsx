import { useState, useEffect } from 'react';
import Map from './components/Map';
import Analytics from './components/Analytics';
import GeneratorList from './components/GeneratorList';
import FilterPanel from './components/FilterPanel';
import { fetchGenerators, fetchRealtimeGeneration, fetchPolygonAnalytics } from './api';
import './App.css';

function App() {
  const [generators, setGenerators] = useState([]);
  const [filteredGenerators, setFilteredGenerators] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);
  const [polygonAnalytics, setPolygonAnalytics] = useState(null);
  const [selectedGenerator, setSelectedGenerator] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    energySource: 'all',
    minCapacity: 0,
    states: '',
  });

  // Initial data load
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [gens, realtime] = await Promise.all([
          fetchGenerators({ limit: 1000 }),
          fetchRealtimeGeneration(),
        ]);
        setGenerators(gens);
        setFilteredGenerators(gens);
        setRealtimeData(realtime);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

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

  // Handle polygon drawn
  const handlePolygonCreated = async (coords) => {
    try {
      const analytics = await fetchPolygonAnalytics(coords);
      setPolygonAnalytics(analytics);
    } catch (error) {
      console.error('Error fetching polygon analytics:', error);
    }
  };

  // Clear polygon
  const handlePolygonCleared = () => {
    setPolygonAnalytics(null);
  };

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

  return (
    <div className="app">
      <header className="header">
        <h1>Renewable Energy Dashboard</h1>
        <span className="subtitle">U.S. EIA Data Visualization</span>
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

          {polygonAnalytics && (
            <div className="stats-card polygon-stats">
              <h3>Selected Area</h3>
              <button className="clear-btn" onClick={handlePolygonCleared}>Clear</button>
              <div className="stat-row">
                <span>Generators:</span>
                <span className="stat-value">{polygonAnalytics.total_generators}</span>
              </div>
              <div className="stat-row">
                <span>Solar Capacity:</span>
                <span className="stat-value solar">
                  {polygonAnalytics.solar_capacity_mw.toLocaleString()} MW
                </span>
              </div>
              <div className="stat-row">
                <span>Wind Capacity:</span>
                <span className="stat-value wind">
                  {polygonAnalytics.wind_capacity_mw.toLocaleString()} MW
                </span>
              </div>
              <div className="stat-row">
                <span>States:</span>
                <span className="stat-value">{polygonAnalytics.states.join(', ')}</span>
              </div>
            </div>
          )}
        </aside>

        <main className="map-container">
          {loading ? (
            <div className="loading">Loading renewable energy data...</div>
          ) : (
            <Map
              generators={filteredGenerators}
              onGeneratorSelect={setSelectedGenerator}
              onPolygonCreated={handlePolygonCreated}
              onPolygonCleared={handlePolygonCleared}
              selectedGenerator={selectedGenerator}
            />
          )}
        </main>

        <aside className="right-panel">
          <Analytics
            realtimeData={realtimeData}
            generators={filteredGenerators}
            polygonAnalytics={polygonAnalytics}
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
            generators={filteredGenerators.slice(0, 50)}
            onSelect={setSelectedGenerator}
            selectedId={selectedGenerator?.id}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
