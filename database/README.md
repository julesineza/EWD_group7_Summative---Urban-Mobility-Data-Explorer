# Database Setup

## Quick Info
SQLite database with NYC Yellow Taxi trip data.
2 tables: zones (dimension) and trips (fact) with engineered features.

## Database Structure

### zones table
Location reference data (265 NYC taxi zones).
- zone_id, borough, zone_name, service_zone

### trips table
Cleaned trip records with engineered features.
- Raw fields: vendor_id, payment_type, dates, distances, fares
- Zone fields: pu_borough, do_borough, pu_zone, do_zone, pu_service_zone, do_service_zone
- Engineered: trip_duration_min, speed_mph, cost_per_mile, tip_percentage, pickup_hour, pickup_day_of_week

## Files
- `schema.sql` - Creates tables and indexes
- `load_data.py` - Loads and enriches data from CSV files
- `test_database.py` - Tests database and shows sample queries

## Setup Instructions

### Requirements
```bash
pip3 install pandas
```

### Data Files Needed
- yellow_tripdata_2019-01.csv
- taxi_zone_lookup.csv

### Build Database
```bash
python3 load_data.py
```

### Test Database
```bash
python3 test_database.py
```

## Indexes
- idx_pickup_zone - Location queries
- idx_dropoff_zone - Location queries
- idx_pickup_time - Time queries
- idx_payment_type - Payment filtering
- idx_pickup_hour - Hour-based analysis
- idx_pickup_dow - Day of week analysis

## Engineered Features
| Feature | Calculation |
|---------|-------------|
| trip_duration_min | dropoff - pickup in minutes |
| speed_mph | trip_distance / hours |
| cost_per_mile | total_amount / trip_distance |
| tip_percentage | (tip / fare) × 100 |
| pickup_hour | hour extracted from pickup_datetime |
| pickup_day_of_week | day name from pickup_datetime |

## Author
Esther Mahoro - Database Implementation