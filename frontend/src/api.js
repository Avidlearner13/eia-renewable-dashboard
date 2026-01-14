/**
 * API client for EIA Renewable Energy backend
 */

const API_BASE = 'http://localhost:8000/api';

export async function fetchGenerators(params = {}) {
  const searchParams = new URLSearchParams();
  if (params.states) searchParams.set('states', params.states);
  if (params.energy_source) searchParams.set('energy_source', params.energy_source);
  if (params.min_capacity) searchParams.set('min_capacity', params.min_capacity);
  if (params.limit) searchParams.set('limit', params.limit);

  const response = await fetch(`${API_BASE}/generators?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch generators');
  return response.json();
}

export async function fetchGeneratorsInBounds(bounds) {
  const searchParams = new URLSearchParams({
    min_lat: bounds.south,
    max_lat: bounds.north,
    min_lon: bounds.west,
    max_lon: bounds.east,
    limit: 1000,
  });

  const response = await fetch(`${API_BASE}/generators/bounds?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch generators in bounds');
  return response.json();
}

export async function fetchRealtimeGeneration(regions = null) {
  const searchParams = new URLSearchParams();
  if (regions) searchParams.set('regions', regions.join(','));

  const response = await fetch(`${API_BASE}/generation/realtime?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch realtime generation');
  return response.json();
}

export async function fetchCapacityByState(states = null) {
  const searchParams = new URLSearchParams();
  if (states) searchParams.set('states', states.join(','));

  const response = await fetch(`${API_BASE}/capacity/by-state?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch capacity');
  return response.json();
}

export async function fetchPolygonAnalytics(coordinates) {
  const searchParams = new URLSearchParams({
    coordinates: JSON.stringify(coordinates),
  });

  const response = await fetch(`${API_BASE}/analytics/polygon?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch polygon analytics');
  return response.json();
}
