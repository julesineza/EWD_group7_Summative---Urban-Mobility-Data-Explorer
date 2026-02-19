import pandas as pd

from data_pipeline.exclusion_log import ExclusionLog


MIN_TRIP_DISTANCE_MI = 0.01          
MAX_TRIP_DISTANCE_MI = 200.0         
MIN_FARE = 0.0                       
MAX_FARE = 5_000.0                   
MIN_TRIP_DURATION_SEC = 30           
MAX_TRIP_DURATION_SEC = 12 * 3_600   
EARLIEST_DATE = "2019-01-01"
LATEST_DATE = "2019-02-01"

CRITICAL_COLUMNS = [
    "PULocationID",
    "DOLocationID",
    "trip_distance",
    "fare_amount",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
]



def clean(df: pd.DataFrame, log: ExclusionLog) :
    """Run all cleaning steps in sequence and return the cleaned DataFrame."""
    df = _remove_duplicates(df, log)
    df = _drop_missing_critical(df, log)
    df = _remove_distance_outliers(df, log)
    df = _remove_fare_outliers(df, log)
    df = _remove_temporal_outliers(df, log)
    df = _remove_duration_outliers(df, log)
    df = _remove_negative_passengers(df, log)
    print(f"[cleaner] {len(df):,} records remain after cleaning")
    return df


def _remove_duplicates(df: pd.DataFrame, log: ExclusionLog) -> pd.DataFrame:
    mask = df.duplicated()
    n = mask.sum()
    if n:
        log.record(df[mask], reason="Exact duplicate row")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} duplicate rows")
    return df


def _drop_missing_critical(df: pd.DataFrame, log: ExclusionLog):
    present_cols = [c for c in CRITICAL_COLUMNS if c in df.columns]
    mask = df[present_cols].isnull().any(axis=1)
    n = mask.sum()
    if n:
        log.record(df[mask], reason="Missing critical column value")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} rows with missing critical values")
    return df


def _remove_distance_outliers(df: pd.DataFrame, log: ExclusionLog):
    if "trip_distance" not in df.columns:
        return df
    mask = (df["trip_distance"] < MIN_TRIP_DISTANCE_MI) | (df["trip_distance"] > MAX_TRIP_DISTANCE_MI)
    n = mask.sum()
    if n:
        log.record(df[mask], reason=f"Distance outlier (<{MIN_TRIP_DISTANCE_MI} or >{MAX_TRIP_DISTANCE_MI} mi)")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} distance outliers")
    return df


def _remove_fare_outliers(df: pd.DataFrame, log: ExclusionLog) :
    if "fare_amount" not in df.columns:
        return df
    mask = (df["fare_amount"] < MIN_FARE) | (df["fare_amount"] > MAX_FARE)
    n = mask.sum()
    if n:
        log.record(df[mask], reason=f"Fare outlier (<${MIN_FARE} or >${MAX_FARE})")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} fare outliers")
    return df


def _remove_temporal_outliers(df: pd.DataFrame, log: ExclusionLog) :
    """Remove trips with pickup dates outside the expected month."""
    col = "tpep_pickup_datetime"
    if col not in df.columns:
        return df

    # Ensure datetime
    df[col] = pd.to_datetime(df[col], errors="coerce")
    mask = (df[col] < pd.Timestamp(EARLIEST_DATE)) | (df[col] >= pd.Timestamp(LATEST_DATE)) | df[col].isna()
    n = mask.sum()
    if n:
        log.record(df[mask], reason=f"Pickup date outside {EARLIEST_DATE} – {LATEST_DATE}")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} temporal outliers")
    return df


def _remove_duration_outliers(df: pd.DataFrame, log: ExclusionLog) :
    """Remove trips whose duration is implausibly short or long."""
    pu, do = "tpep_pickup_datetime", "tpep_dropoff_datetime"
    if pu not in df.columns or do not in df.columns:
        return df

    df[pu] = pd.to_datetime(df[pu], errors="coerce")
    df[do] = pd.to_datetime(df[do], errors="coerce")

    duration_sec = (df[do] - df[pu]).dt.total_seconds()
    mask = (duration_sec < MIN_TRIP_DURATION_SEC) | (duration_sec > MAX_TRIP_DURATION_SEC)
    n = mask.sum()
    if n:
        log.record(df[mask], reason=f"Duration outlier (<{MIN_TRIP_DURATION_SEC}s or >{MAX_TRIP_DURATION_SEC}s)")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} duration outliers")
    return df


def _remove_negative_passengers(df: pd.DataFrame, log: ExclusionLog) :
    if "passenger_count" not in df.columns:
        return df
    mask = df["passenger_count"] < 0
    n = mask.sum()
    if n:
        log.record(df[mask], reason="Negative passenger count")
        df = df[~mask]
        print(f"[cleaner] Removed {n:,} rows with negative passenger count")
    return df
