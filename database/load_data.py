import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('taxi_data.db')
cursor = conn.cursor()

print("Starting database population...")

# ============================================
# 1. Create tables from schema
# ============================================
print("\n[1/4] Creating tables...")
with open('schema.sql', 'r') as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)
conn.commit()
print("Tables created successfully.")

# ============================================
# 2. Load reference data (dimension tables)
# ============================================

print("\n[2/4] Loading reference data...")

# Vendors
vendors = [
    (1, 'Creative Mobile Technologies, LLC'),
    (2, 'VeriFone Inc.')
]
cursor.executemany('INSERT INTO vendors VALUES (?, ?)', vendors)

# Payment Types
payment_types = [
    (1, 'Credit card'),
    (2, 'Cash'),
    (3, 'No charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided trip')
]
cursor.executemany('INSERT INTO payment_types VALUES (?, ?)', payment_types)

# Rate Codes
rate_codes = [
    (1, 'Standard rate', 'Standard metered rate'),
    (2, 'JFK', 'JFK airport flat fare'),
    (3, 'Newark', 'Newark airport flat fare'),
    (4, 'Nassau or Westchester', 'Nassau or Westchester County'),
    (5, 'Negotiated fare', 'Negotiated fare'),
    (6, 'Group ride', 'Group ride')
]
cursor.executemany('INSERT INTO rate_codes VALUES (?, ?, ?)', rate_codes)

# Load taxi zones from downloaded taxi_zone_lookup.csv
print("Loading taxi zones from taxi_zone_lookup.csv...")
zones_df = pd.read_csv('taxi_zone_lookup.csv')

# Rename columns to match database schema
zones_df = zones_df.rename(columns={
    'LocationID': 'location_id',
    'Borough': 'borough',
    'Zone': 'zone_name',
    'service_zone': 'service_zone'
})

zones_df.to_sql('taxi_zones', conn, if_exists='append', index=False)

conn.commit()
print("Reference data loaded successfully.")

# ============================================
# 3. Load trip data from downloaded CSV
# ============================================

print("\n[3/4] Loading trip data from yellow_tripdata_2019-01.csv...")
print("This may take a few minutes...")

# Load downloaded trip data in chunks
chunk_size = 10000
chunks_loaded = 0

for chunk in pd.read_csv('yellow_tripdata_2019-01.csv', chunksize=chunk_size):
    # Rename columns to match database schema
    chunk = chunk.rename(columns={
        'VendorID': 'vendor_id',
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'RatecodeID': 'rate_code_id',
        'PULocationID': 'pickup_location_id',
        'DOLocationID': 'dropoff_location_id'
    })
    
    # Select columns that match our schema
    columns = [
        'vendor_id', 'pickup_datetime', 'dropoff_datetime',
        'passenger_count', 'trip_distance', 'rate_code_id',
        'store_and_fwd_flag', 'pickup_location_id', 'dropoff_location_id',
        'payment_type', 'fare_amount', 'extra', 'mta_tax',
        'tip_amount', 'tolls_amount', 'improvement_surcharge',
        'total_amount', 'congestion_surcharge'
    ]
    
    chunk = chunk[columns]
    chunk = chunk.rename(columns={'payment_type': 'payment_type_id'})
    
    # Insert into database
    chunk.to_sql('trips', conn, if_exists='append', index=False)
    
    chunks_loaded += 1
    rows_processed = chunks_loaded * chunk_size
    print(f"Processed {rows_processed:,} rows...")

conn.commit()
print("Trip data loaded successfully.")

# ============================================
# 4. Verify data
# ============================================

print("\n[4/4] Verifying database integrity...")

cursor.execute("SELECT COUNT(*) FROM trips")
trip_count = cursor.fetchone()[0]
print(f"Total trips in database: {trip_count:,}")

cursor.execute("SELECT COUNT(*) FROM taxi_zones")
zone_count = cursor.fetchone()[0]
print(f"Total taxi zones: {zone_count}")

cursor.execute("SELECT COUNT(*) FROM vendors")
vendor_count = cursor.fetchone()[0]
print(f"Total vendors: {vendor_count}")

cursor.execute("SELECT COUNT(*) FROM payment_types")
payment_count = cursor.fetchone()[0]
print(f"Total payment types: {payment_count}")

print("\nDatabase setup complete.")
print(f"Database file created: taxi_data.db")
print("Location: " + conn.execute("PRAGMA database_list").fetchone()[2])

conn.close()