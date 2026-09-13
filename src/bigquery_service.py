"""
BigQuery integration service for Macro Pulse (hf-macro-dashboard).

Provides serverless data warehouse caching, high-speed query federation,
and pre-calculated quant marts in Google Cloud Platform (GCP).
"""

import os
import datetime
from typing import Optional, Tuple, Dict, Any
import pandas as pd

DEFAULT_GCP_PROJECT = os.getenv(
    "GCP_PROJECT",
    os.getenv("GOOGLE_CLOUD_PROJECT", "agentichackathon-506620")
)
DEFAULT_DATASET = "macropulse"

_BQ_AVAILABLE = False
try:
    from google.cloud import bigquery
    _BQ_AVAILABLE = True
except ImportError:
    bigquery = None  # type: ignore


def is_bigquery_available() -> bool:
    """Return True if google-cloud-bigquery is installed."""
    return _BQ_AVAILABLE


def get_client(project_id: Optional[str] = None) -> Tuple[Optional[Any], str, bool]:
    """Obtain an authenticated BigQuery client and project ID."""
    if not _BQ_AVAILABLE:
        return None, "", False
    proj = project_id or DEFAULT_GCP_PROJECT
    try:
        client = bigquery.Client(project=proj)
        return client, proj, True
    except Exception as e:
        return None, proj, False


def get_bq_status(project_id: Optional[str] = None, dataset_id: str = DEFAULT_DATASET) -> Dict[str, Any]:
    """Check connectivity and list tables in the dataset."""
    client, proj, ok = get_client(project_id)
    if not ok or client is None:
        return {
            "connected": False,
            "project": proj,
            "dataset": dataset_id,
            "tables": [],
            "error": "Failed to authenticate or library missing"
        }
    try:
        tables = [t.table_id for t in client.list_tables(f"{proj}.{dataset_id}")]
        return {
            "connected": True,
            "project": proj,
            "dataset": dataset_id,
            "tables": tables,
            "error": None
        }
    except Exception as e:
        return {
            "connected": False,
            "project": proj,
            "dataset": dataset_id,
            "tables": [],
            "error": str(e)
        }


def save_macro_to_bigquery(
    df: pd.DataFrame,
    project_id: Optional[str] = None,
    dataset_id: str = DEFAULT_DATASET,
    table_id: str = "macro_factors"
) -> bool:
    """Save macroeconomic factors dataframe to BigQuery."""
    client, proj, ok = get_client(project_id)
    if not ok or client is None:
        return False
    try:
        table_ref = f"{proj}.{dataset_id}.{table_id}"
        upload_df = df.copy()
        if "date" not in upload_df.columns:
            upload_df = upload_df.reset_index()
            if "index" in upload_df.columns:
                upload_df = upload_df.rename(columns={"index": "date"})
        upload_df["date"] = pd.to_datetime(upload_df["date"]).dt.date
        upload_df["updated_at"] = datetime.datetime.utcnow()

        # Clean column types for BigQuery
        for col in upload_df.columns:
            if upload_df[col].dtype == "bool":
                upload_df[col] = upload_df[col].astype(bool)
            elif upload_df[col].dtype == "object" and col != "date":
                upload_df[col] = upload_df[col].astype(str)

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            time_partitioning=bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="date"
            )
        )
        job = client.load_table_from_dataframe(upload_df, table_ref, job_config=job_config)
        job.result()
        return True
    except Exception as e:
        print(f"[BigQuery] Failed to save macro data: {e}")
        return False


def load_macro_from_bigquery(
    project_id: Optional[str] = None,
    dataset_id: str = DEFAULT_DATASET,
    table_id: str = "macro_factors"
) -> Optional[pd.DataFrame]:
    """Load macroeconomic factors dataframe from BigQuery with DatetimeIndex."""
    client, proj, ok = get_client(project_id)
    if not ok or client is None:
        return None
    try:
        query = f"SELECT * FROM `{proj}.{dataset_id}.{table_id}` ORDER BY date ASC"
        df = client.query(query).to_dataframe()
        if df.empty:
            return None
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        if "updated_at" in df.columns:
            df = df.drop(columns=["updated_at"])
        df.index.name = "date"
        return df
    except Exception as e:
        print(f"[BigQuery] Failed to load macro data: {e}")
        return None


def save_quant_signals_to_bigquery(
    signals_df: pd.DataFrame,
    project_id: Optional[str] = None,
    dataset_id: str = DEFAULT_DATASET,
    table_id: str = "quant_signals"
) -> bool:
    """Save quant scan signals to BigQuery."""
    client, proj, ok = get_client(project_id)
    if not ok or client is None:
        return False
    try:
        table_ref = f"{proj}.{dataset_id}.{table_id}"
        upload_df = signals_df.copy()
        upload_df["scan_date"] = datetime.date.today()
        upload_df["created_at"] = datetime.datetime.utcnow()

        # Handle boolean or string fields
        for col in upload_df.columns:
            if upload_df[col].dtype == "bool":
                upload_df[col] = upload_df[col].astype(bool)
            elif upload_df[col].dtype == "object":
                upload_df[col] = upload_df[col].astype(str)

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        job = client.load_table_from_dataframe(upload_df, table_ref, job_config=job_config)
        job.result()
        return True
    except Exception as e:
        print(f"[BigQuery] Failed to save quant signals: {e}")
        return False


def load_quant_signals_from_bigquery(
    project_id: Optional[str] = None,
    dataset_id: str = DEFAULT_DATASET,
    table_id: str = "quant_signals"
) -> Optional[pd.DataFrame]:
    """Load latest quant signals from BigQuery."""
    client, proj, ok = get_client(project_id)
    if not ok or client is None:
        return None
    try:
        query = f"SELECT * FROM `{proj}.{dataset_id}.{table_id}` ORDER BY score DESC"
        df = client.query(query).to_dataframe()
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"[BigQuery] Failed to load quant signals: {e}")
        return None
