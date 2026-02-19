export const state = {
  summary: null,
  tripsByHour: [],
  tripsByDay: [],
  fareByBorough: [],
  fareVsDistance: [],
  topPickupZones: [],
  topDropoffZones: [],
  topRoutes: [],
  geojson: null,
  boroughStats: [],
  leafletMap: null,
  geoLayer: null,
};

// chart instances stored here for easy destruction before re-rendering
export const charts = {
  hour: null,
  day: null,
  fareBorough: null,
  scatter: null,
  topZones: null,
  topDropoffZones: null,
};
