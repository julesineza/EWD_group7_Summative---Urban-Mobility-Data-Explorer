import sqlite3
import pandas as pd
from pathlib import Path

#setup paths relative to this script
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
OUTPUT_DIR = ROOT_DIR / "data_pipeline" / "output"

#connect to SQLite database
conn = sqlite3.connect(BASE_DIR / 'taxi_data.db')
cursor = conn.cursor()

print("Starting database population...")

#create tables
print("\n[1/3] Creating tables...")
with open(BASE_DIR / 'schema.sql', 'r') as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)
conn.commit()
print("Tables created successfully.")

#load zones
print("\n[2/3] Loading zones...")

zones_df = pd.read_csv(ROOT_DIR / 'taxi_zone_lookup.csv')
zones_df = zones_df.rename(columns={
    'LocationID': 'zone_id',
    'Borough': 'borough',
    'Zone': 'zone_name',
    'service_zone': 'service_zone'
})

zones_df = zones_df[['zone_id', 'borough', 'zone_name', 'service_zone']]
zones_df = zones_df.dropna(subset=['zone_id', 'borough', 'zone_name'])
zones_df.to_sql('zones', conn, if_exists='append', index=False)
conn.commit()
print(f"Zones loaded successfully. ({len(zones_df)} rows)")


# load trip data from pipeline output
trips_path = OUTPUT_DIR / "processed_trips.csv"
print(f"\n[3/3] Loading cleaned trip data from {trips_path}...")

if not trips_path.exists():
    print(f"Error: {trips_path} not found. Run the data pipeline first.")
    conn.close()
    exit(1)

print("This may take a few minutes...")

chunk_size = 10000
chunks_loaded = 0
total_rows = 0

for chunk in pd.read_csv(trips_path, chunksize=chunk_size):

    # Rename columns from pipeline output to match the database schema
    chunk = chunk.rename(columns={
        'VendorID': 'vendor_id',
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'RatecodeID': 'ratecode_id',
        'PULocationID': 'pickup_zone_id',
        'DOLocationID': 'dropoff_zone_id',
        'PU_Borough': 'pu_borough',
        'PU_Zone': 'pu_zone',
        'PU_ServiceZone': 'pu_service_zone',
        'DO_Borough': 'do_borough',
        'DO_Zone': 'do_zone',
        'DO_ServiceZone': 'do_service_zone',
    })

    # Select only the columns the schema expects
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

    # Keep only columns that exist in the data
    available_cols = [c for c in columns if c in chunk.columns]
    chunk = chunk[available_cols]

    chunk.to_sql('trips', conn, if_exists='append', index=False)

    chunks_loaded += 1
    total_rows += len(chunk)
    print(f"  Processed {total_rows:,} rows...")

conn.commit()
print(f"Trip data loaded successfully. ({total_rows:,} total rows)")

# 4. Verify
print("\nVerifying database...")

cursor.execute("SELECT COUNT(*) FROM trips")
print(f"Total trips: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM zones")
print(f"Total zones: {cursor.fetchone()[0]}")

print(f"\nDatabase setup complete. File: {BASE_DIR / 'taxi_data.db'}")

conn.close()