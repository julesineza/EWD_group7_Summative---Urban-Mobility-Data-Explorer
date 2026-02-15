import pandas as pd

DATETIME_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
]

NUMERIC_COLUMNS = [
    "trip_distance",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "passenger_count",
]

CATEGORICAL_TEXT_COLUMNS = [
    "PU_Borough",
    "DO_Borough",
    "PU_Zone",
    "DO_Zone",
    "PU_ServiceZone",
    "DO_ServiceZone",
    "store_and_fwd_flag",
]

CATEGORICAL_ID_COLUMNS = [
    "VendorID",
    "RatecodeID",
    "PULocationID",
    "DOLocationID",
    "payment_type",
]



def normalize(df: pd.DataFrame):
    df = _normalize_datetimes(df)
    df = _normalize_numerics(df)
    df = _normalize_text_categories(df)
    df = _normalize_id_categories(df)
    return df


def _normalize_datetimes(df: pd.DataFrame):
    for col in DATETIME_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    return df


def _normalize_numerics(df: pd.DataFrame):
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

#Strip whitespace and title-case text categorical columns.
def _normalize_text_categories(df: pd.DataFrame):
    for col in CATEGORICAL_TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df


def _normalize_id_categories(df: pd.DataFrame):
    for col in CATEGORICAL_ID_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df
