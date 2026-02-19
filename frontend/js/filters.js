import { state } from './state.js';
import { ENDPOINTS } from './config.js';
import { fetchAPI } from './dataLoader.js';

// client-side filters for borough, day, hour range, fare range, distance range
export function initFilters() {
  var select = document.getElementById('filterBorough');
  if (!select || !state.boroughStats.length) return;

  for (var i = 0; i < state.boroughStats.length; i++) {
    var opt = document.createElement('option');
    opt.value = state.boroughStats[i].borough;
    opt.textContent = state.boroughStats[i].borough;
    select.appendChild(opt);
  }
}

// helper to parse number inputs (returns null if invalid or empty)
function parseNum(id) {
  var el = document.getElementById(id);
  if (!el || el.value === '') return null;
  var n = parseFloat(el.value);
  return isNaN(n) ? null : n;
}

//read current filter values from inputs and return as an object
export function getClientFilters() {
  return {
    day:     document.getElementById('filterDay').value || '',
    hourMin: parseNum('filterHourMin'),
    hourMax: parseNum('filterHourMax'),
    fareMin: parseNum('filterFareMin'),
    fareMax: parseNum('filterFareMax'),
    distMin: parseNum('filterDistMin'),
    distMax: parseNum('filterDistMax')
  };
}

// build query string from client-side filters (for scatterplot)
export function renderActiveFilters() {
  var container = document.getElementById('activeFilters');
  if (!container) return;

  var f = getClientFilters();
  var borough = document.getElementById('filterBorough').value || '';
  var tags = [];

  if (borough)
    tags.push({ label: 'Borough: ' + borough, key: 'borough' });
  if (f.day)
    tags.push({ label: 'Day: ' + f.day, key: 'day' });
  if (f.hourMin != null || f.hourMax != null)
    tags.push({ label: 'Hours: ' + (f.hourMin || 0) + ' \u2013 ' + (f.hourMax || 23), key: 'hour' });
  if (f.fareMin != null || f.fareMax != null)
    tags.push({ label: 'Fare: $' + (f.fareMin || 0) + ' \u2013 $' + (f.fareMax || '\u221e'), key: 'fare' });
  if (f.distMin != null || f.distMax != null)
    tags.push({ label: 'Dist: ' + (f.distMin || 0) + ' \u2013 ' + (f.distMax || '\u221e') + ' mi', key: 'dist' });

  if (!tags.length) { container.innerHTML = ''; return; }

  var html = '';
  for (var i = 0; i < tags.length; i++) {
    html += '<span class="filter-tag">' + tags[i].label +
      '<button class="tag-remove" data-clear="' + tags[i].key + '">\u2715</button></span>';
  }
  container.innerHTML = html;
}

// map of filter keys to input element IDs
var FILTER_IDS = {
  borough: ['filterBorough'],
  day:     ['filterDay'],
  hour:    ['filterHourMin', 'filterHourMax'],
  fare:    ['filterFareMin', 'filterFareMax'],
  dist:    ['filterDistMin', 'filterDistMax']
};

var ALL_FILTER_IDS = [
  'filterBorough', 'filterDay', 'filterHourMin', 'filterHourMax',
  'filterFareMin', 'filterFareMax', 'filterDistMin', 'filterDistMax'
];

// clear a specific filter input by key
function clearFilter(key) {
  var ids = FILTER_IDS[key] || [];
  for (var i = 0; i < ids.length; i++) {
    var el = document.getElementById(ids[i]);
    if (el) el.value = '';
  }
}

// build query string from client-side filters (for API requests)
function getFilterQueryString() {
  var borough = document.getElementById('filterBorough').value;
  if (!borough) return '';
  return '?borough=' + encodeURIComponent(borough);
}

var FETCH_KEYS = [
  'summary', 'tripsByHour', 'tripsByDay', 'fareByBorough',
  'fareVsDistance', 'topPickupZones', 'topDropoffZones', 'topRoutes', 'geojson'
];

// fetch filtered data from API and update state
async function fetchFilteredData() {
  var suffix = getFilterQueryString();
  var results = await Promise.all(
    FETCH_KEYS.map(function (key) { return fetchAPI(ENDPOINTS[key] + suffix); })
  );
  for (var i = 0; i < FETCH_KEYS.length; i++) {
    state[FETCH_KEYS[i]] = results[i];
  }
}

// bind event listeners for filter inputs and buttons
export function bindFilterEvents(renderCallback) {
  // Apply button
  document.getElementById('btnApplyFilter').addEventListener('click', async function () {
    try {
      await fetchFilteredData();
      renderCallback();
    } catch (err) {
      console.error('Filter apply failed:', err);
    }
  });

  // reset button
  document.getElementById('btnResetFilter').addEventListener('click', async function () {
    for (var i = 0; i < ALL_FILTER_IDS.length; i++) {
      var el = document.getElementById(ALL_FILTER_IDS[i]);
      if (el) el.value = '';
    }
    try {
      await fetchFilteredData();
      renderCallback();
    } catch (err) {
      console.error('Filter reset failed:', err);
    }
  });

  // tag remove buttons (event delegation)
  var activeFilters = document.getElementById('activeFilters');
  if (activeFilters) {
    activeFilters.addEventListener('click', async function (e) {
      var btn = e.target.closest('.tag-remove');
      if (!btn) return;
      var key = btn.dataset.clear;
      clearFilter(key);
      if (key === 'borough') {
        try { await fetchFilteredData(); } catch (err) { console.error(err); }
      }
      renderCallback();
    });
  }
}
