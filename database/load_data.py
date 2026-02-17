import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('taxi_data.db')
cursor = conn.cursor()

print("Starting database population...")

# 1. Create tables
print("\n[1/3] Creating tables...")
with open('schema.sql', 'r') as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)
conn.commit()
print("Tables created successfully.")

# 2. Load zones
print("\n[2/3] Loading zones...")

zones_df = pd.read_csv('taxi_zone_lookup.csv')
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
print("Zones loaded successfully.")


# 3. Load trip data
print("\n[3/3] Loading trip data from yellow_tripdata_2019-01.csv...")
print("This may take a few minutes...")

chunk_size = 10000
chunks_loaded = 0

for chunk in pd.read_csv('yellow_tripdata_2019-01.csv', chunksize=chunk_size):

    chunk = chunk.rename(columns={
        'VendorID': 'vendor_id',
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'RatecodeID': 'ratecode_id',
        'PULocationID': 'pickup_zone_id',
        'DOLocationID': 'dropoff_zone_id'
    })

    chunk['pickup_datetime'] = pd.to_datetime(chunk['pickup_datetime'])
    chunk['dropoff_datetime'] = pd.to_datetime(chunk['dropoff_datetime'])

    # Engineered Features 

    chunk['trip_duration_min'] = (chunk['dropoff_datetime'] - chunk['pickup_datetime']).dt.total_seconds() / 60
    trip_hours = chunk['trip_duration_min'] / 60
    chunk['speed_mph'] = chunk['trip_distance'] / trip_hours.replace(0, None)
    chunk['cost_per_mile'] = chunk['total_amount'] / chunk['trip_distance'].replace(0, None)
    chunk['tip_percentage'] = (chunk['tip_amount'] / chunk['fare_amount'].replace(0, None)) * 100
    chunk['pickup_hour'] = chunk['pickup_datetime'].dt.hour
    chunk['pickup_day_of_week'] = chunk['pickup_datetime'].dt.day_name()

    # Zone columns populated later by pipeline
    chunk['pu_borough'] = None
    chunk['do_borough'] = None
    chunk['pu_zone'] = None
    chunk['do_zone'] = None
    chunk['pu_service_zone'] = None
    chunk['do_service_zone'] = None

    chunk['pickup_datetime'] = chunk['pickup_datetime'].astype(str)
    chunk['dropoff_datetime'] = chunk['dropoff_datetime'].astype(str)

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

# 4. Verify
print("\nVerifying database...")

cursor.execute("SELECT COUNT(*) FROM trips")
print(f"Total trips: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM zones")
print(f"Total zones: {cursor.fetchone()[0]}")

print("\nDatabase setup complete. File: taxi_data.db")

conn.close()