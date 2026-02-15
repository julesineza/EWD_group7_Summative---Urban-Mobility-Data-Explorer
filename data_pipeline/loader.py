"""
Load the csv files and the geojson together
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

TRIP_DATA_PATH = ROOT / "yellow_tripdata_2019-01.csv"
ZONE_LOOKUP_PATH = ROOT / "taxi_zone_lookup.csv"
ZONE_SHAPEFILE_PATH = ROOT / "taxi_zones" / "taxi_zones.shp"


def load_trip_data(path= TRIP_DATA_PATH):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError: 
        raise FileNotFoundError(
            f"Trip data file not found at {path}. Please download it from the project README and place it there."
        )   
    return df


def load_zone_lookup(path= ZONE_LOOKUP_PATH):
    df = pd.read_csv(path)
    return df


def load_zone_geodata(path= ZONE_SHAPEFILE_PATH):
    gdf = gpd.read_file(path)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")
    return gdf



def integrate_zones(trips: pd.DataFrame, zones: pd.DataFrame,):
    # Pickup merge
    trips = trips.merge(
        zones,
        left_on="PULocationID",
        right_on="LocationID",
        how="left",
    )

    #rename the Borough and zone so we know which is for pickup and for dropoff
    trips = trips.rename(
        columns={"Borough": "PU_Borough", "Zone": "PU_Zone", "service_zone": "PU_ServiceZone"}
    ).drop(columns=["LocationID"], errors="ignore")

    #drop-off merge
    trips = trips.merge(
        zones,
        left_on="DOLocationID",
        right_on="LocationID",
        how="left",
    )
    #rename the Borough and zone so we know which is for pickup and for dropoff
    trips = trips.rename(
        columns={"Borough": "DO_Borough", "Zone": "DO_Zone", "service_zone": "DO_ServiceZone"}
    ).drop(columns=["LocationID"], errors="ignore")

    return trips

#function to build the geojson data with location ids
def build_zone_geodataframe(zones: pd.DataFrame,zone_geo: gpd.GeoDataFrame,) -> gpd.GeoDataFrame:
    merged = zone_geo.merge(zones, on="LocationID", how="left")
    return merged
