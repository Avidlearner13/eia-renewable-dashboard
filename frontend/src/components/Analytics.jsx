import { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer
} from 'recharts';

const COLORS = {
  solar: '#FFB800',
  wind: '#00A8E8',
  hydro: '#00C49A',
  total: '#8884d8',
};

function Analytics({ realtimeData, generators, polygonAnalytics }) {
  // Prepare data for charts
  const generationData = useMemo(() => {
    return realtimeData.map(r => ({
      name: r.region,
      solar: Math.max(0, r.solar_mwh),
      wind: Math.max(0, r.wind_mwh),
    }));
  }, [realtimeData]);

  // Capacity by source
  const capacityBySource = useMemo(() => {
    const solar = generators
      .filter(g => g.energy_source === 'SUN')
      .reduce((sum, g) => sum + g.capacity_mw, 0);
    const wind = generators
      .filter(g => g.energy_source === 'WND')
      .reduce((sum, g) => sum + g.capacity_mw, 0);
    const hydro = generators
      .filter(g => g.energy_source === 'WAT')
      .reduce((sum, g) => sum + g.capacity_mw, 0);

    return [
      { name: 'Solar', value: solar, color: COLORS.solar },
      { name: 'Wind', value: wind, color: COLORS.wind },
      { name: 'Hydro', value: hydro, color: COLORS.hydro },
    ].filter(d => d.value > 0);
  }, [generators]);

  // Capacity by state (top 10)
  const capacityByState = useMemo(() => {
    const stateMap = {};
    generators.forEach(g => {
      if (!stateMap[g.state]) {
        stateMap[g.state] = { solar: 0, wind: 0 };
      }
      if (g.energy_source === 'SUN') {
        stateMap[g.state].solar += g.capacity_mw;
      } else if (g.energy_source === 'WND') {
        stateMap[g.state].wind += g.capacity_mw;
      }
    });

    return Object.entries(stateMap)
      .map(([state, data]) => ({
        state,
        solar: data.solar,
        wind: data.wind,
        total: data.solar + data.wind,
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 8);
  }, [generators]);

  // Polygon-specific data
  const polygonCapacity = useMemo(() => {
    if (!polygonAnalytics) return null;
    return [
      { name: 'Solar', value: polygonAnalytics.solar_capacity_mw, color: COLORS.solar },
      { name: 'Wind', value: polygonAnalytics.wind_capacity_mw, color: COLORS.wind },
    ].filter(d => d.value > 0);
  }, [polygonAnalytics]);

  return (
    <div className="analytics">
      <div className="chart-section">
        <h3>Real-time Generation (MWh)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={generationData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis dataKey="name" tick={{ fill: '#ccc', fontSize: 10 }} />
            <YAxis tick={{ fill: '#ccc', fontSize: 10 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #444' }}
              formatter={(value) => value.toLocaleString() + ' MWh'}
            />
            <Legend />
            <Bar dataKey="solar" name="Solar" fill={COLORS.solar} />
            <Bar dataKey="wind" name="Wind" fill={COLORS.wind} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-section">
        <h3>Capacity by Source</h3>
        <ResponsiveContainer width="100%" height={180}>
          <PieChart>
            <Pie
              data={capacityBySource}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={70}
              paddingAngle={2}
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              labelLine={false}
            >
              {capacityBySource.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => value.toLocaleString() + ' MW'}
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #444' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-section">
        <h3>Capacity by State</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={capacityByState} layout="vertical" margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis type="number" tick={{ fill: '#ccc', fontSize: 10 }} />
            <YAxis dataKey="state" type="category" tick={{ fill: '#ccc', fontSize: 10 }} width={30} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #444' }}
              formatter={(value) => value.toLocaleString() + ' MW'}
            />
            <Bar dataKey="solar" name="Solar" stackId="a" fill={COLORS.solar} />
            <Bar dataKey="wind" name="Wind" stackId="a" fill={COLORS.wind} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {polygonAnalytics && polygonCapacity && polygonCapacity.length > 0 && (
        <div className="chart-section polygon-chart">
          <h3>Selected Area Capacity</h3>
          <ResponsiveContainer width="100%" height={150}>
            <PieChart>
              <Pie
                data={polygonCapacity}
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={55}
                paddingAngle={2}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value.toLocaleString()} MW`}
                labelLine={false}
              >
                {polygonCapacity.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => value.toLocaleString() + ' MW'}
                contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #444' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default Analytics;
