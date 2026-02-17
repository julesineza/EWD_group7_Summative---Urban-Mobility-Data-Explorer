import sqlite3

# Connect to database
conn = sqlite3.connect('taxi_data.db')
cursor = conn.cursor()

print("Testing database...\n")

# Test 1: Table counts
print("=== Table Record Counts ===")
cursor.execute("SELECT COUNT(*) FROM trips")
print(f"Trips: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM zones")
print(f"Zones: {cursor.fetchone()[0]}")

# Test 2: Sample trip showing engineered features
print("\n=== Sample Trip (With Engineered Features) ===")
cursor.execute("""
    SELECT trip_id, pickup_datetime, trip_distance,
           trip_duration_min, speed_mph, cost_per_mile,
           tip_percentage, pickup_hour, pickup_day_of_week,
           pu_borough, do_borough
    FROM trips
    LIMIT 1
""")
trip = cursor.fetchone()
print(f"Trip ID:          {trip[0]}")
print(f"Pickup:           {trip[1]}")
print(f"Distance:         {trip[2]} miles")
print(f"Duration:         {trip[3]:.2f} minutes")
print(f"Speed:            {trip[4]:.2f} mph")
print(f"Cost per mile:    ${trip[5]:.2f}")
print(f"Tip percentage:   {trip[6]:.2f}%")
print(f"Pickup hour:      {trip[7]}")
print(f"Day of week:      {trip[8]}")
print(f"Pickup Borough:   {trip[9]}")
print(f"Dropoff Borough:  {trip[10]}")

# Test 3: Join with zones
print("\n=== Join Test (Trip with Zone Info) ===")
cursor.execute("""
    SELECT t.trip_id, t.total_amount,
           z.borough, z.zone_name
    FROM trips t
    JOIN zones z ON t.pickup_zone_id = z.zone_id
    LIMIT 3
""")
for row in cursor.fetchall():
    print(f"Trip {row[0]}: ${row[1]:.2f} from {row[2]}, {row[3]}")

# Test 4: Trips by borough
print("\n=== Trips by Borough ===")
cursor.execute("""
    SELECT z.borough, COUNT(*) as trip_count
    FROM trips t
    JOIN zones z ON t.pickup_zone_id = z.zone_id
    GROUP BY z.borough
    ORDER BY trip_count DESC
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]:,} trips")

# Test 5: Busiest hours
print("\n=== Busiest Pickup Hours ===")
cursor.execute("""
    SELECT pickup_hour, COUNT(*) as trip_count
    FROM trips
    GROUP BY pickup_hour
    ORDER BY trip_count DESC
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"Hour {row[0]:02d}:00 - {row[1]:,} trips")

print("\nDatabase is working correctly!")

conn.close()