"""Synthetic fixture: verifies packaging without credentials or financial data."""
from pathlib import Path


def run_workflow(source_path: str, target_dashboard_path: str, ai=None) -> dict:
    """Count words in a supplied text file; no image rendering or AI calls."""
    return {"word_count": len(Path(source_path).read_text(encoding="utf-8").split()),
            "target_dashboard_path": target_dashboard_path}
