import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('taxi_data.db')
cursor = conn.cursor()

print("Starting database population...")

# ============================================
# 1. Create tables from schema
# ============================================
print("\n[1/3] Creating tables...")
with open('schema.sql', 'r') as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)
conn.commit()
print("Tables created successfully.")

# ============================================
# 2. Load zones from taxi_zone_lookup.csv
# ============================================
print("\n[2/3] Loading zones...")

zones_df = pd.read_csv('taxi_zone_lookup.csv')

# Rename columns to match zones table
zones_df = zones_df.rename(columns={
    'LocationID': 'zone_id',
    'Borough': 'borough',
    'Zone': 'zone_name',
    'service_zone': 'service_zone'
})

# Keep only columns that exist in schema
zones_df = zones_df[['zone_id', 'borough', 'zone_name', 'service_zone']]

# Drop rows with missing required values
zones_df = zones_df.dropna(subset=['zone_id', 'borough', 'zone_name'])

zones_df.to_sql('zones', conn, if_exists='append', index=False)
conn.commit()
print("Zones loaded successfully.")

# ============================================
# 3. Load trip data
# ============================================
print("\n[3/3] Loading trip data from yellow_tripdata_2019-01.csv...")
print("This may take a few minutes...")

chunk_size = 10000
chunks_loaded = 0

for chunk in pd.read_csv('yellow_tripdata_2019-01.csv', chunksize=chunk_size):

    # Rename raw columns to match schema
    chunk = chunk.rename(columns={
        'VendorID': 'vendor_id',
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'RatecodeID': 'ratecode_id',
        'PULocationID': 'pickup_zone_id',
        'DOLocationID': 'dropoff_zone_id'
    })

    # Convert datetimes for calculations
    chunk['pickup_datetime'] = pd.to_datetime(chunk['pickup_datetime'])
    chunk['dropoff_datetime'] = pd.to_datetime(chunk['dropoff_datetime'])

    # ── Engineered Features ──────────────────────────────────

    # 1. Trip duration in minutes
    chunk['trip_duration_min'] = (
        chunk['dropoff_datetime'] - chunk['pickup_datetime']
    ).dt.total_seconds() / 60

    # 2. Speed in mph
    trip_hours = chunk['trip_duration_min'] / 60
    chunk['speed_mph'] = chunk['trip_distance'] / trip_hours.replace(0, None)

    # 3. Cost per mile
    chunk['cost_per_mile'] = chunk['total_amount'] / chunk['trip_distance'].replace(0, None)

    # 4. Tip percentage
    chunk['tip_percentage'] = (chunk['tip_amount'] / chunk['fare_amount'].replace(0, None)) * 100

    # 5. Pickup hour (0-23)
    chunk['pickup_hour'] = chunk['pickup_datetime'].dt.hour

    # 6. Pickup day of week
    chunk['pickup_day_of_week'] = chunk['pickup_datetime'].dt.day_name()

    # ── Zone name columns (will be empty for raw data) ───────
    # These get populated when pipeline runs and produces processed_trips.csv
    chunk['pu_borough'] = None
    chunk['do_borough'] = None
    chunk['pu_zone'] = None
    chunk['do_zone'] = None
    chunk['pu_service_zone'] = None
    chunk['do_service_zone'] = None

    # ── Convert datetimes back to string for SQLite ──────────
    chunk['pickup_datetime'] = chunk['pickup_datetime'].astype(str)
    chunk['dropoff_datetime'] = chunk['dropoff_datetime'].astype(str)

    # ── Select only columns in schema ────────────────────────
    columns = [
        'vendor_id', 'ratecode_id', 'store_and_fwd_flag', 'payment_type',
        'pickup_datetime', 'dropoff_datetime',
        'pickup_zone_id', 'dropoff_zone_id',
        'pu_borough', 'do_borough', 'pu_zone', 'do_zone',
        'pu_service_zone', 'do_service_zone',
        'passenger_count', 'trip_distance',
        'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount',
        'improvement_surcharge', 'congestion_surcharge', 'total_amount',
        'trip_duration_min', 'speed_mph', 'cost_per_mile',
        'tip_percentage', 'pickup_hour', 'pickup_day_of_week'
    ]

    chunk = chunk[columns]

    chunk.to_sql('trips', conn, if_exists='append', index=False)

    chunks_loaded += 1
    print(f"Processed {chunks_loaded * chunk_size:,} rows...")

conn.commit()
print("Trip data loaded successfully.")

# ============================================
# 4. Verify
# ============================================
print("\nVerifying database...")

cursor.execute("SELECT COUNT(*) FROM trips")
print(f"Total trips: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM zones")
print(f"Total zones: {cursor.fetchone()[0]}")

print("\nDatabase setup complete. File: taxi_data.db")

conn.close()