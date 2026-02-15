"""
exclusion_log.py – Transparency
----------------------------------
Maintain a structured log of every record excluded or flagged as suspicious
during cleaning.  The log can be exported to CSV for the technical report.
"""

from pathlib import Path
from typing import Optional

import pandas as pd


class ExclusionLog:
    """Accumulates excluded rows with the reason for exclusion."""

    def __init__(self) -> None:
        self._entries: list[pd.DataFrame] = []

    def record(self, rows: pd.DataFrame, reason: str) -> None:
        """
        Append a batch of excluded rows together with a human-readable reason.

        Parameters
        ----------
        rows : pd.DataFrame
            The rows being removed from the dataset.
        reason : str
            Why these rows were excluded (e.g. "Fare outlier").
        """
        if rows.empty:
            return
        chunk = rows.copy()
        chunk["_exclusion_reason"] = reason
        self._entries.append(chunk)

    @property
    def total_excluded(self) -> int:
        return sum(len(e) for e in self._entries)

    def summary(self) -> pd.DataFrame:
        """Return a DataFrame with count of exclusions per reason."""
        if not self._entries:
            return pd.DataFrame(columns=["reason", "count"])
        combined = pd.concat(self._entries, ignore_index=True)
        return (
            combined.groupby("_exclusion_reason")
            .size()
            .reset_index(name="count")
            .rename(columns={"_exclusion_reason": "reason"})
            .sort_values("count", ascending=False)
        )

    def to_dataframe(self) -> pd.DataFrame:
        """Return every excluded row (with reason column)."""
        if not self._entries:
            return pd.DataFrame()
        return pd.concat(self._entries, ignore_index=True)

    def save(self, path: Optional[Path] = None) -> Path:
        """
        Write the full exclusion log to CSV.
        Default location: <project_root>/data_pipeline/exclusion_log.csv
        """
        if path is None:
            path = Path(__file__).resolve().parent / "exclusion_log.csv"
        df = self.to_dataframe()
        df.to_csv(path, index=False)
        return path

    def print_summary(self) -> None:
        """Pretty-print exclusion counts by reason."""
        s = self.summary()
        print("\n──── Exclusion summary ────")
        if s.empty:
            print("  No records excluded.")
        else:
            for _, row in s.iterrows():
                print(f"  {row['reason']:<55} {row['count']:>8,}")
            print(f"  {'TOTAL':<55} {self.total_excluded:>8,}")
        print()
