import { state } from './state.js';

var COLOR_PALETTE = ['#e8ecf0', '#c8d6f5', '#6c63ff', '#00c9a7', '#ffd93d', '#ff6b6b'];

// pick a color from the palette based on value
function getColor(value, maxVal) {
  if (!value) return COLOR_PALETTE[0];
  var ratio = Math.min(value / maxVal, 1);
  var i = Math.floor(ratio * (COLOR_PALETTE.length - 1));
  return COLOR_PALETTE[i];
}

// helper to build a modal stat row
function modalStat(label, value) {
  return '<div class="modal-stat">' +
    '<span class="modal-stat-label">' + label + '</span>' +
    '<span class="modal-stat-value">' + value + '</span></div>';
}

// helper to get zone ID from geojson properties
function zoneId(p)   { return p.zone_id || p.LocationID; }
function zoneName(p) { return p.zone_name || p.zone || p.Zone || 'Unknown Zone'; }
function borough(p)  { return p.borough || p.Borough || '\u2014'; }

// helper to get metric value for a zone based on selected metric
function metricVal(p, metric) {
  if (metric === 'count')    return p.pickup_count || 0;
  if (metric === 'dropoff')  return p.dropoff_count || 0;
  if (metric === 'fare')     return p.avg_fare || 0;
  return p.avg_distance || 0;
}

var METRIC_LABELS = {
  count: 'Pickup Count',
  dropoff: 'Dropoff Count',
  fare: 'Avg Fare ($)',
  distance: 'Avg Distance (mi)'
};

// render the choropleth map based on selected metric
export function renderMap() {
  var metric = document.getElementById('mapMetric').value;
  var geo = state.geojson;
  if (!geo) return;

  // build metric lookup
  var values = {};
  for (var i = 0; i < geo.features.length; i++) {
    var p = geo.features[i].properties;
    var id = zoneId(p);
    if (id != null) values[id] = metricVal(p, metric);
  }

  var nums = Object.values(values).filter(function (v) { return v > 0; });
  var maxVal = nums.length ? Math.max.apply(null, nums) : 1;

  // create map once
  if (!state.leafletMap) {
    state.leafletMap = L.map('map', {
      center: [40.735, -73.94],
      zoom: 11,
      zoomControl: true,
      attributionControl: true
    });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 18
    }).addTo(state.leafletMap);
  }

  // removes old layer
  if (state.geoLayer) {
    state.leafletMap.removeLayer(state.geoLayer);
    state.geoLayer = null;
  }

  state.geoLayer = L.geoJSON(geo, {
    style: function (feature) {
      var val = values[zoneId(feature.properties)] || 0;
      return { fillColor: getColor(val, maxVal), fillOpacity: 0.75, color: '#c8ced6', weight: 1 };
    },
    onEachFeature: function (feature, layer) {
      var p = feature.properties;
      var name = zoneName(p);
      var boro = borough(p);
      var pickups  = (p.pickup_count || 0).toLocaleString();
      var dropoffs = (p.dropoff_count || 0).toLocaleString();
      var fare = '$' + (p.avg_fare || 0).toFixed(2);
      var dist = (p.avg_distance || 0).toFixed(2) + ' mi';
      var dur  = (p.avg_duration_min || 0).toFixed(1) + ' min';

      // tooltip
      layer.bindTooltip(
        '<div class="info-panel">' +
          '<h4>' + name + '</h4>' +
          '<div><strong>Borough:</strong> ' + boro + '</div>' +
          '<div><strong>Pickups:</strong> ' + pickups + '</div>' +
          '<div><strong>Dropoffs:</strong> ' + dropoffs + '</div>' +
          '<div><strong>Avg Fare:</strong> ' + fare + '</div>' +
          '<div><strong>Avg Distance:</strong> ' + dist + '</div>' +
        '</div>',
        { sticky: true, className: '' }
      );

      // hover highlight
      layer.on('mouseover', function () {
        this.setStyle({ weight: 2, color: '#6c63ff', fillOpacity: 0.9 });
      });
      layer.on('mouseout', function () {
        state.geoLayer.resetStyle(this);
      });

      // Click → modal
      layer.on('click', function () {
        document.getElementById('modalTitle').textContent = name;
        document.getElementById('modalBody').innerHTML =
          '<div class="modal-stats">' +
            modalStat('Borough', boro) +
            modalStat('Pickups', pickups) +
            modalStat('Dropoffs', dropoffs) +
            modalStat('Avg Fare', fare) +
            modalStat('Avg Distance', dist) +
            modalStat('Avg Duration', dur) +
          '</div>';
        document.getElementById('zoneModal').classList.add('active');
      });
    }
  }).addTo(state.leafletMap);

  // legend
  if (!state.leafletMap._legendCtrl) {
    var legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
      var div = L.DomUtil.create('div', 'map-legend');
      div.id = 'mapLegend';
      return div;
    };
    legend.addTo(state.leafletMap);
    state.leafletMap._legendCtrl = legend;
  }

  var legendEl = document.getElementById('mapLegend');
  if (legendEl) {
    var steps = 5;
    var html = '<strong>' + METRIC_LABELS[metric] + '</strong><br>';
    for (var s = 0; s <= steps; s++) {
      var v = (maxVal / steps) * s;
      var label;
      if (metric === 'fare') label = '$' + v.toFixed(0);
      else if (metric === 'distance') label = v.toFixed(1) + ' mi';
      else label = v.toFixed(0);
      html += '<i style="background:' + getColor(v, maxVal) + '"></i> ' + label + '<br>';
    }
    legendEl.innerHTML = html;
  }
}

// bind event listener for metric dropdown
export function bindMapEvents() {
  document.getElementById('mapMetric').addEventListener('change', renderMap);
}
