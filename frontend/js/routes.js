import { state } from './state.js';

var sortKey = 'trip_count';
var sortDir = 'desc';

// helper to build a modal stat row
function modalStat(label, value, fullWidth) {
  var style = fullWidth ? ' style="grid-column:1/-1;"' : '';
  return '<div class="modal-stat"' + style + '>' +
    '<span class="modal-stat-label">' + label + '</span>' +
    '<span class="modal-stat-value">' + value + '</span></div>';
}

// render the top routes table
export function renderTopRoutes() {
  var rows = state.topRoutes;
  if (!rows || !rows.length) return;

  // Sort a copy
  rows = rows.slice().sort(function (a, b) {
    var va = a[sortKey];
    var vb = b[sortKey];
    if (typeof va === 'string') { va = va.toLowerCase(); vb = vb.toLowerCase(); }
    if (va < vb) return sortDir === 'asc' ? -1 : 1;
    if (va > vb) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  // find max for bar width calculation
  var maxTrips = 0;
  for (var i = 0; i < rows.length; i++) {
    if (rows[i].trip_count > maxTrips) maxTrips = rows[i].trip_count;
  }

  // build table rows with bar visualization
  var html = '';
  for (var i = 0; i < rows.length; i++) {
    var r = rows[i];
    var pct = (r.trip_count / maxTrips * 100).toFixed(0);
    html +=
      '<tr class="route-row"' +
        ' data-pickup="' + r.pickup_zone + '"' +
        ' data-dropoff="' + r.dropoff_zone + '"' +
        ' data-trips="' + r.trip_count + '"' +
        ' data-pborough="' + (r.pickup_borough || '') + '"' +
        ' data-dborough="' + (r.dropoff_borough || '') + '">' +
      '<td><span class="rank-badge">' + (i + 1) + '</span></td>' +
      '<td>' + r.pickup_zone + '</td>' +
      '<td>' + r.dropoff_zone + '</td>' +
      '<td>' + r.trip_count.toLocaleString() + '</td>' +
      '<td><div class="trip-bar" style="width:' + pct + '%"></div></td>' +
      '</tr>';
  }
  document.querySelector('#routesTable tbody').innerHTML = html;

  // update sort indicators
  var headers = document.querySelectorAll('#routesTable .sortable');
  for (var j = 0; j < headers.length; j++) {
    var th = headers[j];
    th.classList.remove('sort-asc', 'sort-desc');
    var icon = th.querySelector('.sort-icon');
    if (th.dataset.sort === sortKey) {
      th.classList.add(sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
      if (icon) icon.textContent = sortDir === 'asc' ? '\u25B2' : '\u25BC';
    } else {
      if (icon) icon.textContent = '\u21C5';
    }
  }
}

// bind click events for sorting and row details
export function bindSortEvents(renderCallback) {
  var headers = document.querySelectorAll('#routesTable .sortable');
  for (var i = 0; i < headers.length; i++) {
    headers[i].addEventListener('click', function () {
      var key = this.dataset.sort;
      if (sortKey === key) {
        sortDir = sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey = key;
        sortDir = (key === 'trip_count') ? 'desc' : 'asc';
      }
      renderCallback();
    });
  }

  // row click 
  var tbody = document.querySelector('#routesTable tbody');
  if (tbody) {
    tbody.addEventListener('click', function (e) {
      var row = e.target.closest('.route-row');
      if (!row) return;

      var pickup   = row.dataset.pickup;
      var dropoff  = row.dataset.dropoff;
      var trips    = parseInt(row.dataset.trips).toLocaleString();
      var pBorough = row.dataset.pborough || '\u2014';
      var dBorough = row.dataset.dborough || '\u2014';

      document.getElementById('modalTitle').textContent = pickup + ' \u2192 ' + dropoff;
      document.getElementById('modalBody').innerHTML =
        '<div class="modal-stats">' +
          modalStat('Pickup Zone', pickup) +
          modalStat('Pickup Borough', pBorough) +
          modalStat('Dropoff Zone', dropoff) +
          modalStat('Dropoff Borough', dBorough) +
          modalStat('Total Trips', trips, true) +
        '</div>';
      document.getElementById('zoneModal').classList.add('active');
    });
  }
}
