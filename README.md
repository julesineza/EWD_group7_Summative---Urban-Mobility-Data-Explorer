# Urban Mobility Data Explorer — NYC Taxi Analytics Dashboard

> **Group 7 — Enterprise Web Development Summative Assignment**

A full-stack data engineering and visualization platform that ingests, cleans, enriches, and visualizes **January 2019 NYC Yellow Taxi trip data** from the NYC Taxi & Limousine Commission (TLC). The system combines a Python ETL pipeline, a SQLite relational database, a Flask REST API, and an interactive web dashboard to uncover actionable insights into urban transportation patterns.

**Video Walkthrough:** [Watch the demo on Google Drive](https://drive.google.com/YOUR_VIDEO_LINK_HERE)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Data Sources](#data-sources)
4. [Project Structure](#project-structure)
5. [Setup & Installation](#setup--installation)
6. [Running the Application](#running-the-application)
7. [Data Pipeline](#data-pipeline)
8. [Database Design](#database-design)
9. [Backend API](#backend-api)
10. [Frontend Dashboard](#frontend-dashboard)
11. [Feature Engineering](#feature-engineering)
12. [Data Cleaning & Transparency](#data-cleaning--transparency)
13. [Technologies Used](#technologies-used)
14. [Team Participation](#team-participation)

---

## Project Overview

This project addresses the challenge of making sense of massive urban mobility datasets. Using the official NYC TLC data — comprising **trip records (Fact Table)**, **zone lookups (Dimension Table)**, and **spatial boundaries (Spatial Metadata)** — the system implements a complete data analytics pipeline:

- **Extract & Load** raw CSV and shapefile data
- **Clean & Validate** records with full audit trail
- **Normalize** data types for consistent storage
- **Engineer** 6 derived features for deeper analysis
- **Store** data in a normalized relational SQLite database
- **Serve** processed data through a Flask REST API
- **Visualize** insights via an interactive web dashboard

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES (Raw Files)                     │
│  yellow_tripdata_2019-01.csv │ taxi_zone_lookup.csv │ taxi_zones/│
└──────────────┬───────────────┴──────────────┬──────┴────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE (Python)                       │
│  loader.py → cleaner.py → normalizer.py → feature_engineering.py│
│                     ↓ exclusion_log.py                           │
│              pipeline.py (orchestrator)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ processed_trips.csv
                           │ processed_zones.geojson
                           │ exclusion_log.csv
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                  DATABASE (SQLite)                                │
│  schema.sql → load_data.py → taxi_data.db                       │
│  Tables: zones (dimension)  │  trips (fact + enriched)          │
│  6 indexes for query performance                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                  BACKEND API (Flask)                              │
│  API.py — 10 RESTful endpoints on port 5000                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ JSON responses
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│               FRONTEND DASHBOARD (HTML/CSS/JS)                   │
│  Chart.js charts │ Leaflet choropleth map │ Sortable routes table│
│  KPI cards │ Client-side filters │ Zone detail modals            │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Sources

All data is sourced from the **NYC Taxi & Limousine Commission (TLC)**:

| File                          | Type             | Description                                                                                    | Download                                                                                          |
| ----------------------------- | ---------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `yellow_tripdata_2019-01.csv` | Fact Table       | ~7.6M raw trip-level records with timestamps, distances, rate codes, and itemized fare details | [Download](https://drive.google.com/file/d/1qMJ3xv9g6ZeWx87QKOm1UDny8HKyWi8p/view?usp=drive_link) |
| `taxi_zone_lookup.csv`        | Dimension Table  | Categorical mapping for `PULocationID` and `DOLocationID` (Boroughs, Zones, Service Zones)     | [Download](https://drive.google.com/file/d/1eHZfLLXOeVAdNrK3LVvkmJcMXBhJ2-9d/view?usp=drive_link) |
| `taxi_zones/`                 | Spatial Metadata | GeoJSON/Shapefile spatial boundaries (polygons) for each Taxi Zone ID                          | [Download](https://drive.google.com/file/d/1nc0Y35CX2M9E97LojHpzPKBicDmpufFJ/view?usp=drive_link) |

Refer to the [TLC Trip Record User Guide](https://www.nyc.gov/assets/tlc/downloads/pdf/trip_record_user_guide.pdf) for technical field definitions.

---

## Project Structure

```
EWD_group7_Summative---Urban-Mobility-Data-Explorer/
│
├── README.md                          # This file
├── yellow_tripdata_2019-01.csv        # Raw trip data (Fact Table)
├── taxi_zone_lookup.csv               # Zone lookup (Dimension Table)
├── taxi_zones/                        # Spatial metadata (Shapefiles)
│   ├── taxi_zones.shp
│   ├── taxi_zones.dbf
│   ├── taxi_zones.prj
│   ├── taxi_zones.shx
│   ├── taxi_zones.sbn
│   ├── taxi_zones.sbx
│   └── taxi_zones.shp.xml
│
├── data_pipeline/                     # ETL Pipeline
│   ├── __init__.py                    # Package initializer
│   ├── pipeline.py                    # Pipeline orchestrator
│   ├── loader.py                      # Data loading & zone integration
│   ├── cleaner.py                     # Data cleaning & outlier removal
│   ├── normalizer.py                  # Data type standardization
│   ├── feature_engineering.py         # Derived feature calculation
│   ├── exclusion_log.py               # Exclusion audit trail
│   └── output/                        # Pipeline outputs
│       ├── processed_trips.csv        # Cleaned & enriched trip data
│       ├── processed_zones.geojson    # Zone boundaries with metadata
│       ├── exclusion_log.csv          # Full exclusion audit log
│       └── exclusion_reason_summary.csv
│
├── database/                          # Database layer
│   ├── schema.sql                     # DDL — table & index definitions
│   ├── load_data.py                   # Data insertion script
│   ├── test_database.py              # Database verification tests
│   └── README.md                      # Database documentation
│
├── backend/                           # Flask REST API
│   └── API.py                         # API server (10 endpoints)
│
└── frontend/                          # Web dashboard
    ├── index.html                     # Dashboard layout
    ├── css/
    │   └── styles.css                 # Dashboard styling
    └── js/
        ├── app.js                     # App entry point & initialization
        ├── charts.js                  # Chart.js chart renderers
        ├── config.js                  # API endpoints & chart config
        ├── dataLoader.js              # API data fetching utilities
        ├── filters.js                 # Filter logic & UI
        ├── kpi.js                     # KPI card rendering
        ├── map.js                     # Leaflet choropleth map
        ├── routes.js                  # Top routes table & sorting
        └── state.js                   # Centralized application state
```

---

## Setup & Installation

### Prerequisites

- **Python 3.8+** (verify with `python3 --version`)
- **pip** (Python package manager)
- **Git** (to clone the repository)
- A modern web browser (Chrome, Firefox, Edge, or Safari)

### 1. Clone the Repository

```bash
git clone https://github.com/julesineza/EWD_group7_Summative---Urban-Mobility-Data-Explorer.git
cd EWD_group7_Summative---Urban-Mobility-Data-Explorer
```

### 2. Install Python Dependencies

```bash
pip3 install flask pandas geopandas
```

> **Note:** `geopandas` depends on `fiona`, `shapely`, and `pyproj`. If installation fails, try:
>
> ```bash
> pip3 install shapely fiona pyproj
> pip3 install geopandas
> ```

### 3. Download the Source Data

Download the following files and place them in the **project root directory**:

1. **Trip Data** — [yellow_tripdata_2019-01.csv](https://drive.google.com/file/d/1qMJ3xv9g6ZeWx87QKOm1UDny8HKyWi8p/view?usp=drive_link) → place in project root
2. **Zone Lookup** — [taxi_zone_lookup.csv](https://drive.google.com/file/d/1eHZfLLXOeVAdNrK3LVvkmJcMXBhJ2-9d/view?usp=drive_link) → place in project root
3. **Spatial Data** — [taxi_zones/](https://drive.google.com/drive/folders/1rYP-gFryjMNyYADYRPU3_yA_pAPR8r2N?usp=drive_link) → place entire folder in project root

### 4. Verify File Placement

Your project root should contain:

```
├── yellow_tripdata_2019-01.csv
├── taxi_zone_lookup.csv
└── taxi_zones/
    ├── taxi_zones.shp
    ├── taxi_zones.dbf
    ├── taxi_zones.prj
    └── taxi_zones.shx
```

---

## Running the Application

Execute the following steps **in order**:

### Step 1: Run the Data Pipeline

```bash
python3 -m data_pipeline.pipeline
```

This will:

- Load the raw CSV and shapefile data
- Integrate zone metadata into trip records
- Clean data (remove duplicates, outliers, invalid records)
- Normalize data types
- Engineer 6 derived features
- Export processed files to `data_pipeline/output/`
- Print an exclusion summary report

**Expected output:** `processed_trips.csv`, `processed_zones.geojson`, and `exclusion_log.csv` in `data_pipeline/output/`

> Processing ~7.6M rows may take several minutes depending on your machine.

### Step 2: Load Data into the Database

```bash
python3 database/load_data.py
```

This will:

- Create the SQLite database at `database/taxi_data.db`
- Execute `schema.sql` to create the `zones` and `trips` tables with indexes
- Insert zone data from the lookup CSV
- Insert processed trip data in 10,000-row batches
- Print verification counts

### Step 3: Verify the Database (Optional)

```bash
python3 database/test_database.py
```

Runs 5 smoke tests: record counts, sample trip inspection, zone joins, borough grouping, and busiest hours.

### Step 4: Start the Flask API Server

```bash
python3 backend/API.py
```

The server starts on **http://localhost:5000** in debug mode.

### Step 5: Open the Dashboard

Navigate to **http://localhost:5000** in your browser. The dashboard will automatically fetch data from the API and render all visualizations.

---

## Data Pipeline

The pipeline (`data_pipeline/pipeline.py`) orchestrates 5 sequential ETL stages:

### 1. Data Loading (`loader.py`)

- Reads `yellow_tripdata_2019-01.csv` into a pandas DataFrame
- Reads `taxi_zone_lookup.csv` for zone dimension data
- Reads `taxi_zones/taxi_zones.shp` as a GeoDataFrame (reprojected to EPSG:4326)
- Integrates zone names into trip records via left joins on `PULocationID` and `DOLocationID`

### 2. Data Cleaning (`cleaner.py`)

Applies 7 sequential cleaning steps with configurable thresholds:

| Step                  | Rule                       | Threshold                                                                            |
| --------------------- | -------------------------- | ------------------------------------------------------------------------------------ |
| Remove duplicates     | Exact duplicate rows       | —                                                                                    |
| Drop missing critical | Null in key columns        | `PULocationID`, `DOLocationID`, `trip_distance`, `fare_amount`, pickup/dropoff times |
| Distance outliers     | Out-of-range trip distance | 0.01–200 miles                                                                       |
| Fare outliers         | Out-of-range fare amount   | $0–$5,000                                                                            |
| Temporal outliers     | Pickups outside date range | 2019-01-01 to 2019-02-01                                                             |
| Duration outliers     | Unreasonable trip duration | 30 seconds–12 hours                                                                  |
| Negative passengers   | Negative passenger count   | ≥ 0                                                                                  |

### 3. Data Normalization (`normalizer.py`)

- **Datetimes:** Converted to UTC-aware datetime objects
- **Numerics:** Coerced to float/int with error handling
- **Text categories:** Stripped whitespace, title-cased
- **ID categories:** Converted to nullable `Int64` type

### 4. Feature Engineering (`feature_engineering.py`)

Six derived features calculated from raw columns (see [Feature Engineering](#feature-engineering) section).

### 5. Export

Outputs three files to `data_pipeline/output/`:

- `processed_trips.csv` — cleaned, normalized, enriched trip data
- `processed_zones.geojson` — zone boundaries with metadata
- `exclusion_log.csv` — full audit trail of excluded records

---

## Database Design

### Schema (SQLite)

The database uses a **normalized relational schema** with two tables:

#### `zones` (Dimension Table)

| Column         | Type         | Description           |
| -------------- | ------------ | --------------------- |
| `zone_id`      | INTEGER (PK) | Taxi Zone location ID |
| `borough`      | TEXT         | NYC borough name      |
| `zone_name`    | TEXT         | Zone name             |
| `service_zone` | TEXT         | Service zone category |

#### `trips` (Fact Table + Enriched Features)

| Column                  | Type                        | Description                       |
| ----------------------- | --------------------------- | --------------------------------- |
| `trip_id`               | INTEGER (PK, autoincrement) | Unique trip identifier            |
| `vendor_id`             | INTEGER                     | TPEP provider                     |
| `pickup_datetime`       | TEXT                        | Pickup timestamp                  |
| `dropoff_datetime`      | TEXT                        | Dropoff timestamp                 |
| `passenger_count`       | REAL                        | Number of passengers              |
| `trip_distance`         | REAL                        | Trip distance in miles            |
| `pu_location_id`        | INTEGER (FK → zones)        | Pickup zone                       |
| `do_location_id`        | INTEGER (FK → zones)        | Dropoff zone                      |
| `ratecode_id`           | INTEGER                     | Rate code                         |
| `payment_type`          | INTEGER                     | Payment method                    |
| `fare_amount`           | REAL                        | Base fare                         |
| `extra`                 | REAL                        | Extras and surcharges             |
| `mta_tax`               | REAL                        | MTA tax                           |
| `tip_amount`            | REAL                        | Tip amount                        |
| `tolls_amount`          | REAL                        | Tolls                             |
| `improvement_surcharge` | REAL                        | Improvement surcharge             |
| `total_amount`          | REAL                        | Total charged amount              |
| `congestion_surcharge`  | REAL                        | Congestion surcharge              |
| `pu_borough`            | TEXT                        | Pickup borough name               |
| `pu_zone`               | TEXT                        | Pickup zone name                  |
| `pu_service_zone`       | TEXT                        | Pickup service zone               |
| `do_borough`            | TEXT                        | Dropoff borough name              |
| `do_zone`               | TEXT                        | Dropoff zone name                 |
| `do_service_zone`       | TEXT                        | Dropoff service zone              |
| `trip_duration_min`     | REAL                        | _Engineered:_ Duration in minutes |
| `speed_mph`             | REAL                        | _Engineered:_ Average speed       |
| `cost_per_mile`         | REAL                        | _Engineered:_ Cost efficiency     |
| `tip_percentage`        | REAL                        | _Engineered:_ Tip as % of fare    |
| `pickup_hour`           | INTEGER                     | _Engineered:_ Hour of pickup      |
| `pickup_day_of_week`    | TEXT                        | _Engineered:_ Day name            |

### Indexes

```sql
CREATE INDEX idx_pickup_zone    ON trips(pu_location_id);
CREATE INDEX idx_dropoff_zone   ON trips(do_location_id);
CREATE INDEX idx_pickup_time    ON trips(pickup_datetime);
CREATE INDEX idx_payment_type   ON trips(payment_type);
CREATE INDEX idx_pickup_hour    ON trips(pickup_hour);
CREATE INDEX idx_pickup_dow     ON trips(pickup_day_of_week);
```

### Entity-Relationship

```
┌──────────────┐       ┌──────────────────────────────────┐
│    zones     │       │             trips                │
├──────────────┤       ├──────────────────────────────────┤
│ zone_id (PK) │◄──────│ pu_location_id (FK)              │
│ borough      │       │ do_location_id (FK)              │
│ zone_name    │◄──────│ trip_id (PK)                     │
│ service_zone │       │ vendor_id, pickup_datetime, ...  │
└──────────────┘       │ trip_duration_min, speed_mph,    │
                       │ cost_per_mile, tip_percentage,   │
                       │ pickup_hour, pickup_day_of_week  │
                       └──────────────────────────────────┘
```

---

## Backend API

The Flask backend (`backend/API.py`) serves **10 RESTful endpoints** on port **5000**:

| Method | Endpoint                   | Description                                                    | Parameters              |
| ------ | -------------------------- | -------------------------------------------------------------- | ----------------------- |
| GET    | `/`                        | Serves the frontend dashboard                                  | —                       |
| GET    | `/api/summary`             | Aggregate KPIs (total trips, avg fare/distance/duration/speed) | —                       |
| GET    | `/api/trips-by-hour`       | Trip count per hour (0–23)                                     | —                       |
| GET    | `/api/trips-by-day`        | Trip count per weekday (Mon–Sun)                               | —                       |
| GET    | `/api/top-pickup-zones`    | Top pickup zones by trip count                                 | `?limit=N` (default 10) |
| GET    | `/api/top-dropoff-zones`   | Top dropoff zones by trip count                                | `?limit=N` (default 10) |
| GET    | `/api/borough-stats`       | Aggregate statistics per borough                               | —                       |
| GET    | `/api/avg-fare-by-borough` | Avg fare, total trips, cost/mile, tip % by borough             | —                       |
| GET    | `/api/top-routes`          | Top pickup→dropoff route pairs                                 | `?limit=N` (default 15) |
| GET    | `/api/geojson`             | Zone GeoJSON enriched with database statistics                 | —                       |

### Example API Response

```bash
curl http://localhost:5000/api/summary
```

```json
{
  "total_trips": 7456123,
  "avg_fare": 12.85,
  "avg_distance": 3.02,
  "avg_duration_min": 15.4,
  "avg_speed": 12.6
}
```

---

## Frontend Dashboard

The single-page dashboard (`frontend/index.html`) provides 6 visualization sections:

### KPI Summary Cards

Four cards displaying total trips, average fare, average distance, and average duration.

### Time Trend Analysis

- **Trips by Hour** — Bar chart showing trip volume across 24 hours with peak hours (7–10 AM, 5–8 PM) highlighted in red
- **Trips by Day** — Bar chart showing trip volume across weekdays with weekends highlighted in yellow

### Geographic Heatmap

An interactive **Leaflet choropleth map** of NYC taxi zones with:

- Selectable metric (Pickup Count, Dropoff Count, Avg Fare, Avg Distance)
- Color-coded zones with dynamic legend
- Tooltips showing zone details
- Click-to-open zone detail modals

### Economic Analysis

- **Average Fare by Borough** — Horizontal bar chart comparing fare levels across NYC boroughs
- **Fare vs Distance Scatter** — Scatter plot revealing the relationship between trip distance and fare amount

### Trip Flow Analysis

- **Top 15 Routes** — Sortable table showing the most popular pickup→dropoff zone pairs with proportional trip-count bars
- **Top Pickup Zones** — Horizontal bar chart of the 10 busiest pickup locations
- **Top Dropoff Zones** — Horizontal bar chart of the 10 busiest dropoff locations

### Filtering & Interactivity

- **Borough filter** — Server-side filtering by NYC borough
- **Day of week filter** — Client-side weekday selection
- **Hour range** — Filter by pickup hour (0–23)
- **Fare range** — Filter by fare amount
- **Distance range** — Filter by trip distance
- **Active filter tags** — Visual indicators with one-click removal
- **Zone detail modals** — Click any zone on the map or route in the table for full statistics

---

## Feature Engineering

Six derived features provide deeper analytical insight:

| Feature              | Formula                        | Justification                                                                                       |
| -------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------- |
| `trip_duration_min`  | (dropoff − pickup) / 60        | Core metric for understanding trip length beyond distance — captures traffic and congestion effects |
| `speed_mph`          | distance ÷ (duration in hours) | Reveals traffic patterns, congestion zones, and time-of-day performance differences                 |
| `cost_per_mile`      | total_amount ÷ distance        | Economic efficiency metric — enables comparison of ride value across zones and times                |
| `tip_percentage`     | (tip ÷ fare) × 100             | Service quality proxy and economic behavior indicator — varies by payment type and location         |
| `pickup_hour`        | Hour from pickup timestamp     | Enables temporal aggregation to identify rush hours, shift patterns, and demand cycles              |
| `pickup_day_of_week` | Day name from pickup timestamp | Captures weekly demand rhythms — weekday commuting vs. weekend leisure travel patterns              |

> Division-by-zero cases (e.g., 0 distance or 0 fare) are handled by replacing the divisor with `NaN` before calculation.

---

## Data Cleaning & Transparency

All excluded records are logged in `data_pipeline/output/exclusion_log.csv` with the reason for exclusion. A summary is also printed during pipeline execution and saved to `exclusion_reason_summary.csv`.

### Exclusion Categories

| Reason                   | Description                          |
| ------------------------ | ------------------------------------ |
| `duplicate`              | Exact duplicate rows                 |
| `missing_critical_field` | Null value in a required column      |
| `distance_outlier`       | Trip distance < 0.01 or > 200 miles  |
| `fare_outlier`           | Fare amount < $0 or > $5,000         |
| `temporal_outlier`       | Pickup datetime outside January 2019 |
| `duration_outlier`       | Duration < 30 seconds or > 12 hours  |
| `negative_passengers`    | Passenger count < 0                  |

This approach ensures full **auditability** — every record removed from the dataset can be traced and justified.

---

## Technologies Used

| Layer             | Technology                           | Purpose                                            |
| ----------------- | ------------------------------------ | -------------------------------------------------- |
| **Data Pipeline** | Python 3, pandas, geopandas          | ETL processing, data cleaning, feature engineering |
| **Database**      | SQLite                               | Relational data storage with indexing              |
| **Backend**       | Flask (Python)                       | REST API serving JSON data                         |
| **Frontend**      | HTML5, CSS3, JavaScript (ES Modules) | Dashboard layout and interactivity                 |
| **Charting**      | Chart.js 4.4.4                       | Bar charts, scatter plots                          |
| **Mapping**       | Leaflet 1.9.4 + CARTO tiles          | Interactive choropleth map                         |
| **Spatial**       | Shapely, Fiona, pyproj               | Shapefile processing and reprojection              |

---

## Team Participation

> See the [Team Participation Sheet](https://docs.google.com/spreadsheets/d/1pZ9fSsnPsfiMNAu_0zPSMu-GANdrzXXkEsr9TffDvGQ/edit?usp=sharing) for detailed meeting notes and individual contributions.

---
