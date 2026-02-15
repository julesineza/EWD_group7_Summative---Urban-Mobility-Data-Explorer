"""
In this file we now bring everything together 
1.load the data - using loader.py
2.Intergate it - loader.py again
3.clean the data - clear.py
4.Normalize it - feature_engineering.py
6.Export the data - Export the data in the output direcotry     
"""

from pathlib import Path

from data_pipeline.loader import (
    load_trip_data,
    load_zone_geodata,
    load_zone_lookup,
    integrate_zones,
    build_zone_geodataframe,
)
from data_pipeline.cleaner import clean
from data_pipeline.normalizer import normalize
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.exclusion_log import ExclusionLog


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data_pipeline" / "output"


def run_pipeline():

    #ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    #load th edata
    trips = load_trip_data()
    zones = load_zone_lookup()
    zone_geo = load_zone_geodata()

    #integrating the data 
    trips = integrate_zones(trips, zones)
    zones_full = build_zone_geodataframe(zones, zone_geo)

    #clean the data
    log = ExclusionLog()
    trips = clean(trips, log)

    #normalization
    trips = normalize(trips)

    #feature engineering
    trips = engineer_features(trips)

    #export the data now 
    trips_path = OUTPUT_DIR / "processed_trips.csv"
    trips.to_csv(trips_path, index=False)
    print(f"[pipeline] Saved processed trips → {trips_path.name}")

    geo_path = OUTPUT_DIR / "processed_zones.geojson"
    zones_full.to_file(geo_path, driver="GeoJSON")
    print(f"[pipeline] Saved zone geodata   → {geo_path.name}")

    #output the log file for errors
    log_path = OUTPUT_DIR / "exclusion_log.csv"
    log.save(log_path)
    log.print_summary()

    print("Pipeline completed")


if __name__ == "__main__":
    run_pipeline()
