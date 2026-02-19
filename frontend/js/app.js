import { ENDPOINTS, applyChartDefaults } from './config.js';
import { state } from './state.js';
import { fetchAPI, hideLoading } from './dataLoader.js';
import { renderKPIs } from './kpi.js';
import { renderTripsByHour, renderTripsByDay, renderFareByBorough, renderScatter, renderTopZones, renderTopDropoffZones } from './charts.js';
import { renderMap, bindMapEvents } from './map.js';
import { renderTopRoutes, bindSortEvents } from './routes.js';
import { initFilters, bindFilterEvents, renderActiveFilters } from './filters.js';

// all render functions in one list for easy iteration
var renderers = [
  renderKPIs, renderTripsByHour, renderTripsByDay, renderMap,
  renderFareByBorough, renderScatter, renderTopRoutes,
  renderTopZones, renderTopDropoffZones, renderActiveFilters
];

export function renderAll() {
  for (var i = 0; i < renderers.length; i++) renderers[i]();
}

// keys shared between ENDPOINTS object and state object
var DATA_KEYS = [
  'summary', 'tripsByHour', 'tripsByDay', 'fareByBorough',
  'fareVsDistance', 'topPickupZones', 'topDropoffZones',
  'topRoutes', 'geojson', 'boroughStats'
];

async function init() {
  applyChartDefaults();
  try {
    // fetch all endpoints in parallel using shared key list
    var results = await Promise.all(
      DATA_KEYS.map(function (key) { return fetchAPI(ENDPOINTS[key]); })
    );
    for (var i = 0; i < DATA_KEYS.length; i++) {
      state[DATA_KEYS[i]] = results[i];
    }

    initFilters();
    bindFilterEvents(renderAll);
    bindMapEvents();
    bindSortEvents(renderAll);

    // modal close on X button
    var modal = document.getElementById('zoneModal');
    var closeBtn = document.getElementById('modalClose');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        modal.classList.remove('active');
      });
    }
    // modal close on backdrop click
    if (modal) {
      modal.addEventListener('click', function (e) {
        if (e.target === modal) modal.classList.remove('active');
      });
    }

    renderAll();
    hideLoading();
  } catch (err) {
    console.error('Failed to load data:', err);
    document.getElementById('loadingOverlay').innerHTML =
      '<p style="color:var(--accent3);text-align:center;max-width:500px;">' +
      '<strong>Error loading data.</strong><br>' +
      'Make sure the Flask API is running on <code>http://localhost:5000</code></p>';
  }
}

document.addEventListener('DOMContentLoaded', init);
