function FilterPanel({ filters, setFilters }) {
  const handleSourceChange = (e) => {
    setFilters(prev => ({ ...prev, energySource: e.target.value }));
  };

  const handleCapacityChange = (e) => {
    setFilters(prev => ({ ...prev, minCapacity: Number(e.target.value) }));
  };

  const handleStatesChange = (e) => {
    setFilters(prev => ({ ...prev, states: e.target.value }));
  };

  return (
    <div className="filter-panel">
      <h3>Filters</h3>

      <div className="filter-group">
        <label>Energy Source</label>
        <select value={filters.energySource} onChange={handleSourceChange}>
          <option value="all">All Sources</option>
          <option value="SUN">Solar</option>
          <option value="WND">Wind</option>
          <option value="WAT">Hydro</option>
        </select>
      </div>

      <div className="filter-group">
        <label>Min Capacity (MW)</label>
        <input
          type="range"
          min="0"
          max="200"
          step="10"
          value={filters.minCapacity}
          onChange={handleCapacityChange}
        />
        <span className="range-value">{filters.minCapacity} MW</span>
      </div>

      <div className="filter-group">
        <label>States (comma-separated)</label>
        <input
          type="text"
          placeholder="CA, TX, FL"
          value={filters.states}
          onChange={handleStatesChange}
        />
      </div>

      <div className="filter-tip">
        <strong>Tip:</strong> Use the polygon tool on the map to select a custom area and view analytics.
      </div>
    </div>
  );
}

export default FilterPanel;
