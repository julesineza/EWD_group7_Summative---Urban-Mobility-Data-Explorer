import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, g, render_template

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
if not FRONTEND_DIR.exists():
    # Fallback for a trailing-space folder name: "frontend "
    FRONTEND_DIR = PROJECT_ROOT / "frontend "
DB_PATH = PROJECT_ROOT / "database" / "taxi_data.db"

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path="",
)


def get_db():
    """Open one connection per request and reuse it."""
    if "_database" not in g:
        g._database = sqlite3.connect(str(DB_PATH))
        g._database.row_factory = sqlite3.Row  # this makes the rows behave like dicts for easier querying
    return g._database


@app.teardown_appcontext
def close_db(exception):
    """Automatically close DB when the request ends."""
    db = g.pop("_database", None)
    if db is not None:
        db.close()


def query(sql, args=(), one=False):
    """Run a query and return results as a list of dicts."""
    cur = get_db().execute(sql, args)
    rows = [dict(row) for row in cur.fetchall()]
    return rows[0] if one and rows else rows


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    """Total trips, average fare, distance, and duration."""
    data = query("""
        SELECT
            COUNT(*)               AS total_trips,
            ROUND(AVG(fare_amount), 2)      AS avg_fare,
            ROUND(AVG(trip_distance), 2)    AS avg_distance,
            ROUND(AVG(trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(speed_mph), 2)        AS avg_speed_mph
        FROM trips
    """, one=True)
    return jsonify(data)


@app.route("/api/trips-by-hour")
def trips_by_hour():
    """Trip count per hour of day (0-23). → bar chart."""
    rows = query("""
        SELECT pickup_hour AS hour, COUNT(*) AS trip_count
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    """)
    return jsonify(rows)


@app.route("/api/trips-by-day")
def trips_by_day():
    """Trip count per day of week. → bar chart (weekday vs weekend)."""
    rows = query("""
        SELECT pickup_day_of_week AS day, COUNT(*) AS trip_count
        FROM trips
        GROUP BY pickup_day_of_week
        ORDER BY
            CASE pickup_day_of_week
                WHEN 'Monday'    THEN 1
                WHEN 'Tuesday'   THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday'  THEN 4
                WHEN 'Friday'    THEN 5
                WHEN 'Saturday'  THEN 6
                WHEN 'Sunday'    THEN 7
            END
    """)
    return jsonify(rows)




@app.route("/api/top-pickup-zones")
def top_pickup_zones():
    """Top 10 zones by pickup count. → ranked list / bar chart."""
    limit = request.args.get("limit", 10, type=int)
    rows = query("""
        SELECT
            z.zone_name,
            z.borough,
            COUNT(*) AS pickup_count
        FROM trips t
        JOIN zones z ON t.pickup_zone_id = z.zone_id
        GROUP BY z.zone_id
        ORDER BY pickup_count DESC
        LIMIT ?
    """, (limit,))
    return jsonify(rows)


@app.route("/api/top-dropoff-zones")
def top_dropoff_zones():
    """Top 10 zones by dropoff count."""
    limit = request.args.get("limit", 10, type=int)
    rows = query("""
        SELECT
            z.zone_name,
            z.borough,
            COUNT(*) AS dropoff_count
        FROM trips t
        JOIN zones z ON t.dropoff_zone_id = z.zone_id
        GROUP BY z.zone_id
        ORDER BY dropoff_count DESC
        LIMIT ?
    """, (limit,))
    return jsonify(rows)


@app.route("/api/borough-stats")
def borough_stats():
    """Aggregate stats per borough."""
    rows = query("""
        SELECT
            z.borough,
            COUNT(*)                          AS trip_count,
            ROUND(AVG(t.fare_amount), 2)      AS avg_fare,
            ROUND(AVG(t.trip_distance), 2)    AS avg_distance,
            ROUND(AVG(t.trip_duration_min), 2) AS avg_duration_min,
            ROUND(AVG(t.speed_mph), 2)        AS avg_speed_mph
        FROM trips t
        JOIN zones z ON t.pickup_zone_id = z.zone_id
        GROUP BY z.borough
        ORDER BY trip_count DESC
    """)
    return jsonify(rows)


@app.route("/api/avg-fare-by-borough")
def avg_fare_by_borough():
    """Average fare per borough. → bar chart."""
    rows = query("""
        SELECT
            z.borough,
            ROUND(AVG(t.fare_amount), 2)    AS avg_fare,
            ROUND(AVG(t.total_amount), 2)   AS avg_total,
            ROUND(AVG(t.cost_per_mile), 2)  AS avg_cost_per_mile,
            ROUND(AVG(t.tip_percentage), 2) AS avg_tip_pct
        FROM trips t
        JOIN zones z ON t.pickup_zone_id = z.zone_id
        GROUP BY z.borough
        ORDER BY avg_fare DESC
    """)
    return jsonify(rows)




@app.route("/api/top-routes")
def top_routes():
    """Top pickup → dropoff routes by frequency."""
    limit = request.args.get("limit", 15, type=int)
    rows = query("""
        SELECT
            pz.zone_name  AS pickup_zone,
            pz.borough    AS pickup_borough,
            dz.zone_name  AS dropoff_zone,
            dz.borough    AS dropoff_borough,
            COUNT(*)      AS trip_count
        FROM trips t
        JOIN zones pz ON t.pickup_zone_id  = pz.zone_id
        JOIN zones dz ON t.dropoff_zone_id = dz.zone_id
        GROUP BY t.pickup_zone_id, t.dropoff_zone_id
        ORDER BY trip_count DESC
        LIMIT ?
    """, (limit,))
    return jsonify(rows)



@app.route("/api/geojson")
def geojson():
    """Serve the processed zones GeoJSON enriched with DB stats."""
    geojson_path = Path(__file__).resolve().parents[1] / "data_pipeline" / "output" / "processed_zones.geojson"
    if not geojson_path.exists():
        return jsonify({"error": "GeoJSON file not found"}), 404

    # Build a lookup of zone stats from the database
    stats = query("""
        WITH pickup AS (
            SELECT
                pickup_zone_id AS zone_id,
                COUNT(*) AS pickup_count,
                AVG(fare_amount) AS avg_fare,
                AVG(trip_distance) AS avg_distance,
                AVG(trip_duration_min) AS avg_duration_min
            FROM trips
            GROUP BY pickup_zone_id
        ),
        dropoff AS (
            SELECT
                dropoff_zone_id AS zone_id,
                COUNT(*) AS dropoff_count
            FROM trips
            GROUP BY dropoff_zone_id
        )
        SELECT
            z.zone_id,
            z.zone_name,
            z.borough,
            COALESCE(p.pickup_count, 0) AS pickup_count,
            ROUND(COALESCE(p.avg_fare, 0), 2) AS avg_fare,
            ROUND(COALESCE(p.avg_distance, 0), 2) AS avg_distance,
            ROUND(COALESCE(p.avg_duration_min, 0), 2) AS avg_duration_min,
            COALESCE(d.dropoff_count, 0) AS dropoff_count
        FROM zones z
        LEFT JOIN pickup p ON p.zone_id = z.zone_id
        LEFT JOIN dropoff d ON d.zone_id = z.zone_id
    """)
    stats_by_id = {row["zone_id"]: row for row in stats}

    import json
    with open(geojson_path) as f:
        data = json.load(f)

    # Attach stats + ensure we expose zone_id in each feature
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        zone_id = props.get("LocationID") or props.get("zone_id")
        if zone_id is not None:
            zone_id = int(zone_id)
            props["zone_id"] = zone_id
            props.update(stats_by_id.get(zone_id, {}))
        feature["properties"] = props

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)