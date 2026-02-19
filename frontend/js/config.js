//  API Endpoints 
export const ENDPOINTS = {
  summary:        '/api/summary',
  tripsByHour:    '/api/trips-by-hour',
  tripsByDay:     '/api/trips-by-day',
  fareByBorough:  '/api/avg-fare-by-borough',
  fareVsDistance: '/api/fare-vs-distance',
  topPickupZones:  '/api/top-pickup-zones',
  topDropoffZones: '/api/top-dropoff-zones',
  topRoutes:       '/api/top-routes',
  geojson:        '/api/geojson',
  boroughStats:   '/api/borough-stats',
};

// color for each borough (used in map and charts)
export const CHART_COLORS = [
  '#645cec', '#37b19d', '#ac4141', '#c7ae48',
  '#2a97af', '#35ab74', '#aa539e', '#c19211',
  '#29b061', '#a2392d', '#2c77a8', '#733b89',
];

// apply chart defaults
export function applyChartDefaults() {
  Chart.defaults.color = '#64748b';
  Chart.defaults.borderColor = '#e5e7eb';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
}
