-- NYC Taxi Trip Database Schema
-- Database Design and Implementation

-- ============================================
-- DIMENSION TABLES (Reference Data)
-- ============================================

-- Vendors (Taxi Service Providers)
CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL
);

-- Payment Types
CREATE TABLE payment_types (
    payment_type_id INTEGER PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL
);

-- Rate Codes (Fare Types)
CREATE TABLE rate_codes (
    rate_code_id INTEGER PRIMARY KEY,
    rate_code_name VARCHAR(50) NOT NULL,
    description TEXT
);

-- Taxi Zones (Borough and Neighborhood Info)
CREATE TABLE taxi_zones (
    location_id INTEGER PRIMARY KEY,
    borough VARCHAR(50),
    zone_name VARCHAR(100),
    service_zone VARCHAR(50)
);

-- ============================================
-- FACT TABLE (Trip Records)
-- ============================================

CREATE TABLE trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    pickup_datetime TIMESTAMP NOT NULL,
    dropoff_datetime TIMESTAMP NOT NULL,
    passenger_count INTEGER,
    trip_distance REAL,
    rate_code_id INTEGER,
    store_and_fwd_flag CHAR(1),
    pickup_location_id INTEGER,
    dropoff_location_id INTEGER,
    payment_type_id INTEGER,
    fare_amount REAL,
    extra REAL,
    mta_tax REAL,
    tip_amount REAL,
    tolls_amount REAL,
    improvement_surcharge REAL,
    total_amount REAL,
    congestion_surcharge REAL,
    
    -- Foreign Key Constraints
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (pickup_location_id) REFERENCES taxi_zones(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES taxi_zones(location_id),
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(payment_type_id),
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id)
);

-- ============================================
-- INDEXES (For Query Performance)
-- ============================================

-- Time based queries
CREATE INDEX idx_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_dropoff_datetime ON trips(dropoff_datetime);

-- Location based queries
CREATE INDEX idx_pickup_location ON trips(pickup_location_id);
CREATE INDEX idx_dropoff_location ON trips(dropoff_location_id);

-- Common filters
CREATE INDEX idx_payment_type ON trips(payment_type_id);
CREATE INDEX idx_fare_amount ON trips(fare_amount);
CREATE INDEX idx_trip_distance ON trips(trip_distance);
CREATE INDEX idx_passenger_count ON trips(passenger_count);

-- Composite index for common queries
CREATE INDEX idx_pickup_time_location ON trips(pickup_datetime, pickup_location_id);