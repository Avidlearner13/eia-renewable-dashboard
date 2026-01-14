function GeneratorList({ generators, onSelect, selectedId }) {
  const getSourceIcon = (source) => {
    switch (source) {
      case 'SUN': return '☀️';
      case 'WND': return '🌬️';
      case 'WAT': return '💧';
      default: return '⚡';
    }
  };

  const getSourceColor = (source) => {
    switch (source) {
      case 'SUN': return '#FFB800';
      case 'WND': return '#00A8E8';
      case 'WAT': return '#00C49A';
      default: return '#888888';
    }
  };

  return (
    <div className="generator-list">
      <h3>Top Generators ({generators.length})</h3>
      <div className="list-container">
        {generators.map((gen) => (
          <div
            key={gen.id}
            className={`generator-item ${selectedId === gen.id ? 'selected' : ''}`}
            onClick={() => onSelect(gen)}
          >
            <div className="generator-icon" style={{ color: getSourceColor(gen.energy_source) }}>
              {getSourceIcon(gen.energy_source)}
            </div>
            <div className="generator-info">
              <div className="generator-item-name">{gen.name}</div>
              <div className="generator-meta">
                {gen.state} • {gen.capacity_mw.toLocaleString()} MW
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default GeneratorList;
