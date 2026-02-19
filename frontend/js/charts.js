import { state, charts } from './state.js';
import { CHART_COLORS } from './config.js';
import { getClientFilters } from './filters.js';

// Utility to destroy a Chart.js instance if it exists

function destroyChart(name) {
  if (charts[name]) { charts[name].destroy(); charts[name] = null; }
}

// format large numbers: 12500 → "13k"
function shortNum(v) {
  return v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v;
}

// Standard bar dataset with rounded corners
function barDataset(label, data, colors, maxBar) {
  return {
    label: label,
    data: data,
    backgroundColor: colors,
    borderRadius: 4,
    maxBarThickness: maxBar || 40
  };
}

// vertical bar chart options (trips-style)
function verticalBarOpts(suffix) {
  return {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function (ctx) { return ctx.parsed.y.toLocaleString() + ' ' + suffix; }
        }
      }
    },
    scales: {
      x: { grid: { display: false } },
      y: { beginAtZero: true, ticks: { callback: shortNum } }
    }
  };
}

// horizontal bar chart options (zone-style)
function horizontalBarOpts(tooltipFn) {
  return {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: tooltipFn } }
    },
    scales: {
      x: { beginAtZero: true, ticks: { callback: shortNum } },
      y: { grid: { display: false } }
    }
  };
}

// trips by Hour of Day
export function renderTripsByHour() {
  var f = getClientFilters();
  var rows = state.tripsByHour;
  if (!rows || !rows.length) return;

  if (f.hourMin != null) rows = rows.filter(function (r) { return r.hour >= f.hourMin; });
  if (f.hourMax != null) rows = rows.filter(function (r) { return r.hour <= f.hourMax; });
  if (!rows.length) { destroyChart('hour'); return; }

  var labels = rows.map(function (r) { return r.hour + ':00'; });
  var data = rows.map(function (r) { return r.trip_count; });
  var colors = rows.map(function (r) {
    var isPeak = (r.hour >= 7 && r.hour <= 10) || (r.hour >= 17 && r.hour <= 20);
    return isPeak ? '#d92727' : '#335cd7';
  });

  destroyChart('hour');
  charts.hour = new Chart(document.getElementById('chartHour'), {
    type: 'bar',
    data: { labels: labels, datasets: [barDataset('Trips', data, colors, 32)] },
    options: verticalBarOpts('trips')
  });
}

// trips by Day of Week
export function renderTripsByDay() {
  var f = getClientFilters();
  var rows = state.tripsByDay;
  if (!rows || !rows.length) return;

  if (f.day) rows = rows.filter(function (r) { return r.day === f.day; });
  if (!rows.length) { destroyChart('day'); return; }

  var labels = rows.map(function (r) { return r.day.slice(0, 3); });
  var data = rows.map(function (r) { return r.trip_count; });
  var colors = rows.map(function (r) {
    return (r.day === 'Saturday' || r.day === 'Sunday') ? '#f2c512' : '#101a23';
  });

  destroyChart('day');
  charts.day = new Chart(document.getElementById('chartDay'), {
    type: 'bar',
    data: { labels: labels, datasets: [barDataset('Trips', data, colors, 48)] },
    options: verticalBarOpts('trips')
  });
}

// average Fare by Borough
export function renderFareByBorough() {
  var rows = state.fareByBorough;
  if (!rows || !rows.length) return;

  var labels = rows.map(function (r) { return r.borough; });
  var data = rows.map(function (r) { return r.avg_fare; });
  var colors = labels.map(function (_, i) { return CHART_COLORS[i % CHART_COLORS.length]; });

  destroyChart('fareBorough');
  charts.fareBorough = new Chart(document.getElementById('chartFareBorough'), {
    type: 'bar',
    data: { labels: labels, datasets: [barDataset('Avg Fare ($)', data, colors, 64)] },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: function (ctx) { return '$' + ctx.parsed.x.toFixed(2); } } }
      },
      scales: {
        x: { beginAtZero: true, ticks: { callback: function (v) { return '$' + v; } } },
        y: { grid: { display: false } }
      }
    }
  });
}

// Fare vs Distance scatterplot
export function renderScatter() {
  var f = getClientFilters();
  var rows = state.fareVsDistance;
  if (!rows || !rows.length) return;

  // Filter out zero and extreme values for better visualization
  var filtered = rows.filter(function (r) {
    return r.trip_distance > 0 && r.fare_amount > 0 && r.trip_distance < 50 && r.fare_amount < 200;
  });

  // Apply client-side filters
  if (f.fareMin != null) filtered = filtered.filter(function (r) { return r.fare_amount >= f.fareMin; });
  if (f.fareMax != null) filtered = filtered.filter(function (r) { return r.fare_amount <= f.fareMax; });
  if (f.distMin != null) filtered = filtered.filter(function (r) { return r.trip_distance >= f.distMin; });
  if (f.distMax != null) filtered = filtered.filter(function (r) { return r.trip_distance <= f.distMax; });
  if (!filtered.length) { destroyChart('scatter'); return; }

  var points = filtered.map(function (r) { return { x: r.trip_distance, y: r.fare_amount }; });

  destroyChart('scatter');
  charts.scatter = new Chart(document.getElementById('chartScatter'), {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Trip',
        data: points,
        backgroundColor: 'rgba(108,99,255,0.35)',
        pointRadius: 2.5,
        pointHoverRadius: 5
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function (ctx) { return ctx.parsed.x.toFixed(1) + ' mi — $' + ctx.parsed.y.toFixed(2); }
          }
        }
      },
      scales: {
        x: { title: { display: true, text: 'Distance (mi)' }, beginAtZero: true },
        y: { title: { display: true, text: 'Total Fare ($)' }, beginAtZero: true }
      }
    }
  });
}

// Top 10 Pickup Zones
export function renderTopZones() {
  var rows = state.topPickupZones;
  if (!rows || !rows.length) return;

  var labels = rows.map(function (r) { return r.zone_name; });
  var data = rows.map(function (r) { return r.pickup_count; });
  var colors = labels.map(function (_, i) { return CHART_COLORS[i % CHART_COLORS.length]; });

  destroyChart('topZones');
  charts.topZones = new Chart(document.getElementById('chartTopZones'), {
    type: 'bar',
    data: { labels: labels, datasets: [barDataset('Pickups', data, colors)] },
    options: horizontalBarOpts(function (ctx) { return ctx.parsed.x.toLocaleString() + ' pickups'; })
  });
}

// Top 10 Dropoff Zones
export function renderTopDropoffZones() {
  var rows = state.topDropoffZones;
  if (!rows || !rows.length) return;

  var labels = rows.map(function (r) { return r.zone_name; });
  var data = rows.map(function (r) { return r.dropoff_count; });
  var colors = labels.map(function (_, i) { return CHART_COLORS[(i + 3) % CHART_COLORS.length]; });

  destroyChart('topDropoffZones');
  charts.topDropoffZones = new Chart(document.getElementById('chartTopDropoffZones'), {
    type: 'bar',
    data: { labels: labels, datasets: [barDataset('Dropoffs', data, colors)] },
    options: horizontalBarOpts(function (ctx) { return ctx.parsed.x.toLocaleString() + ' dropoffs'; })
  });
}