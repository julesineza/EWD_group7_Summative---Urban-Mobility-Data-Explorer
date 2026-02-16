import sqlite3

# Connect to your database
conn = sqlite3.connect('taxi_data.db')
cursor = conn.cursor()

print("Testing your database...\n")

# Test 1: Count records in each table
print("=== Table Record Counts ===")
cursor.execute("SELECT COUNT(*) FROM trips")
print(f"Trips: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM taxi_zones")
print(f"Taxi Zones: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM vendors")
print(f"Vendors: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM payment_types")
print(f"Payment Types: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM rate_codes")
print(f"Rate Codes: {cursor.fetchone()[0]}")

# Test 2: Sample trip data
print("\n=== Sample Trip ===")
cursor.execute("SELECT * FROM trips LIMIT 1")
trip = cursor.fetchone()
print(f"Trip ID: {trip[0]}")
print(f"Pickup: {trip[2]}")
print(f"Distance: {trip[5]} miles")
print(f"Fare: ${trip[11]}")

# Test 3: Join test - get borough name for a trip
print("\n=== Join Test (Trip with Borough Info) ===")
cursor.execute("""
    SELECT t.trip_id, t.pickup_datetime, t.total_amount,
           z.borough, z.zone_name
    FROM trips t
    JOIN taxi_zones z ON t.pickup_location_id = z.location_id
    LIMIT 3
""")

for row in cursor.fetchall():
    print(f"Trip {row[0]}: ${row[2]:.2f} from {row[3]}, {row[4]}")

print("\n✓ Database is working correctly!")

conn.close()