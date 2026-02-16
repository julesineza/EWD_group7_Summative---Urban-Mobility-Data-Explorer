# Database Setup

## Quick Info
SQLite database with NYC taxi trip data. 5 normalized tables with indexes.

## Files
- `schema.sql` - Creates all tables
- `load_data.py` - Loads data from CSV files
- `database_dump.sql` - Pre-loaded database backup (not in GitHub due to size)
- `test_database.py` - Tests if database works

## How to Use

### Option 1: Use the Dump File (Fastest)
**Note:** `database_dump.sql` (121MB) is too large for GitHub.  
Contact team member for Google Drive link, or use Option 2.
```bash
sqlite3 taxi_data.db < database_dump.sql
python3 test_database.py
```

### Option 2: Build From Scratch
You need:
- yellow_tripdata_2019-01.csv
- taxi_zone_lookup.csv

Then:
```bash
pip3 install pandas
python3 load_data.py
```

## Database Tables
- **trips** - All trip records (main table)
- **taxi_zones** - Borough and zone names
- **vendors** - Taxi companies (2 vendors)
- **payment_types** - Payment methods (6 types)
- **rate_codes** - Fare types (6 codes)

## Sample Query
```sql
sqlite3 taxi_data.db

SELECT z.borough, COUNT(*) as trips
FROM trips t
JOIN taxi_zones z ON t.pickup_location_id = z.location_id
GROUP BY z.borough;
```

## Database Design
- Normalized (3NF) - no repeated data
- Foreign keys link tables together
- Indexes on datetime and location columns for fast queries

## Author
Esther Mahoro - Database Implementation