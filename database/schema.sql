-- Urban Mobility Data Explorer - SQLite Schema

-- Zones lookup table
CREATE TABLE IF NOT EXISTS zones (
    zone_id INTEGER PRIMARY KEY,
    borough TEXT NOT NULL,
    zone_name TEXT NOT NULL,
    service_zone TEXT
);

-- Trips fact table
CREATE TABLE IF NOT EXISTS trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    ratecode_id INTEGER,
    store_and_fwd_flag TEXT,
    payment_type INTEGER,
    pickup_datetime TEXT NOT NULL,
    dropoff_datetime TEXT NOT NULL,
    pickup_zone_id INTEGER,
    dropoff_zone_id INTEGER,
    -- zone details added by pipeline
    pu_borough TEXT,
    do_borough TEXT,
    pu_zone TEXT,
    do_zone TEXT,
    pu_service_zone TEXT,
    do_service_zone TEXT,
    passenger_count INTEGER,
    trip_distance REAL,
    fare_amount REAL,
    extra REAL,
    mta_tax REAL,
    tip_amount REAL,
    tolls_amount REAL,
    improvement_surcharge REAL,
    congestion_surcharge REAL,
    total_amount REAL,
    -- engineered features
    trip_duration_min REAL,
    speed_mph REAL,
    cost_per_mile REAL,
    tip_percentage REAL,
    pickup_hour INTEGER,
    pickup_day_of_week TEXT,
    FOREIGN KEY (pickup_zone_id) REFERENCES zones(zone_id),
    FOREIGN KEY (dropoff_zone_id) REFERENCES zones(zone_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pickup_zone ON trips(pickup_zone_id);
CREATE INDEX IF NOT EXISTS idx_dropoff_zone ON trips(dropoff_zone_id);
CREATE INDEX IF NOT EXISTS idx_pickup_time ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_payment_type ON trips(payment_type);
CREATE INDEX IF NOT EXISTS idx_pickup_hour ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_pickup_dow ON trips(pickup_day_of_week);