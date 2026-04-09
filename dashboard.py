"""
Dashboard generator: injects analysis data into the HTML template.
"""

import json
import os
import numpy as np
import pandas as pd


def _serialise(obj):
    """JSON serialiser for numpy/pandas types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        if np.isnan(obj):
            return None
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, (pd.Timestamp,)):
        return obj.strftime("%Y-%m-%d")
    raise TypeError(f"Not serialisable: {type(obj)}")


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of dicts with clean types."""
    records = df.to_dict(orient="records")
    for row in records:
        for k, v in row.items():
            if isinstance(v, pd.Timestamp):
                row[k] = v.strftime("%Y-%m-%d")
            elif isinstance(v, (float, np.floating)) and np.isnan(v):
                row[k] = None
    return records


def build_dashboard(results: dict, output_path: str):
    """
    Read the HTML template, inject JSON data, and write the dashboard file.

    Parameters
    ----------
    results : dict of DataFrames from indicators.run_all_analyses()
    output_path : file path for the .html output
    """
    # Prepare JSON payload
    viz = {}
    viz["national"] = _df_to_records(results["national"])

    for key in ["cost_State", "cost_Industry", "cost_GCC", "cost_ARIA", "cost_BusinessSize"]:
        out_key = f"cost_by_{key.split('_', 1)[1].lower()}"
        if key in results:
            viz[out_key] = _df_to_records(results[key])

    if "by_State" in results:
        # For the state bar chart, take the latest week only
        df = results["by_State"]
        latest_week = df["Week"].max()
        viz["by_state"] = _df_to_records(df[df["Week"] == latest_week])

    if "concern_distribution" in results:
        viz["concern_distribution"] = _df_to_records(results["concern_distribution"])

    # Weekly component data for the date-range slider (num_w + den_w per week × dimension)
    comp_map = [
        ("state", "State"), ("industry", "Industry"), ("gcc", "GCC"),
        ("aria", "ARIA"), ("businesssize", "BusinessSize"),
    ]
    for out_key, result_suffix in comp_map:
        comp_key = f"cost_components_{result_suffix}"
        if comp_key in results and not results[comp_key].empty:
            viz[f"cost_components_{out_key}"] = _df_to_records(results[comp_key])

    data_json = json.dumps(viz, default=_serialise)

    # Load template
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    template_path = os.path.join(template_dir, "dashboard_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Inject data
    html = html.replace("{{DATA_JSON}}", data_json)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard saved  → {output_path}")