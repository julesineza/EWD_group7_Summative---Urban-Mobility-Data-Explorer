import { state } from './state.js';

// render KPI values in the summary section
export function renderKPIs() {
  const d = state.summary;
  if (!d) return;
  document.getElementById('kpiTrips').textContent   = (d.total_trips || 0).toLocaleString();
  document.getElementById('kpiAvgFare').textContent  = '$' + (d.avg_fare || 0).toFixed(2);
  document.getElementById('kpiAvgDist').textContent  = (d.avg_distance || 0).toFixed(2) + ' mi';
  document.getElementById('kpiAvgDur').textContent   = (d.avg_duration_min || 0).toFixed(1) + ' min';
}
