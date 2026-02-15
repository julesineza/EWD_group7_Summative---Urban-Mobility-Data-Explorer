import pandas as pd


def engineer_features(df):
    """Add all derived features and return the enriched DataFrame."""
    df = _add_trip_duration(df)
    df = _add_speed(df)
    df = _add_cost_per_mile(df)
    df = _add_tip_percentage(df)
    df = _add_temporal_features(df)
    print(f"[features] Engineered 6 derived features on {len(df):,} records")
    return df



def _add_trip_duration(df):
    pu, do = "tpep_pickup_datetime", "tpep_dropoff_datetime"
    if pu in df.columns and do in df.columns:
        delta = pd.to_datetime(df[do]) - pd.to_datetime(df[pu])
        df["trip_duration_min"] = delta.dt.total_seconds() / 60.0
    return df


def _add_speed(df):
    if "trip_duration_min" in df.columns and "trip_distance" in df.columns:
        hours = df["trip_duration_min"] / 60.0
        # avoid division by zero
        df["speed_mph"] = df["trip_distance"] / hours.replace(0, float("nan"))
    return df


def _add_cost_per_mile(df):
    if "total_amount" in df.columns and "trip_distance" in df.columns:
        df["cost_per_mile"] = df["total_amount"] / df["trip_distance"].replace(0, float("nan"))
    return df


def _add_tip_percentage(df):
    if "tip_amount" in df.columns and "fare_amount" in df.columns:
        df["tip_percentage"] = (
            df["tip_amount"] / df["fare_amount"].replace(0, float("nan"))
        ) * 100.0
    return df


def _add_temporal_features(df):
    col = "tpep_pickup_datetime"
    if col in df.columns:
        dt = pd.to_datetime(df[col])
        df["pickup_hour"] = dt.dt.hour
        df["pickup_day_of_week"] = dt.dt.day_name()
    return df
