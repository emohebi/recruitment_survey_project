"""
Indicator calculation engine: computes weighted proportions per the business rules.
"""

import pandas as pd
import numpy as np
from config import INDICATORS, BREAKDOWNS


def _weighted_proportion(df: pd.DataFrame, spec: dict, weight_col: str = "Weight") -> dict:
    """
    Calculate a single weighted indicator from a DataFrame subset.

    Returns dict with: value, numerator_weight, denominator_weight, n_valid
    """
    sub = df.copy()

    # Apply pre-filter (e.g. RD only among recruiters)
    if "pre_filter" in spec:
        for col, vals in spec["pre_filter"].items():
            if col in sub.columns:
                sub = sub[sub[col].isin(vals)]

    col = spec["filter_col"]
    if col not in sub.columns:
        return {"value": np.nan, "num_w": 0, "den_w": 0, "n": 0}

    # Determine valid denominator rows
    denom_rule = spec["denominator"]
    if denom_rule == "__all_non_blank__":
        valid = sub[sub[col].notna() & (sub[col].astype(str).str.strip() != "")]
    elif denom_rule == "__excl_unsure_blank__":
        valid = sub[
            sub[col].notna()
            & (sub[col].astype(str).str.strip() != "")
            & (sub[col] != "Unsure")
        ]
    else:
        valid = sub[sub[col].isin(denom_rule)]

    if valid.empty or valid[weight_col].sum() == 0:
        return {"value": np.nan, "num_w": 0, "den_w": 0, "n": 0}

    num = valid[valid[col].isin(spec["numerator"])][weight_col].sum()
    den = valid[weight_col].sum()

    return {"value": num / den, "num_w": num, "den_w": den, "n": len(valid)}


def calc_all_indicators(df: pd.DataFrame, weight_col: str = "Weight") -> dict:
    """Calculate all four indicators for a given DataFrame slice."""
    result = {"N": len(df), "Sum_Weight": df[weight_col].sum() if weight_col in df.columns else 0}
    for key, spec in INDICATORS.items():
        r = _weighted_proportion(df, spec, weight_col)
        result[key] = r["value"]
    return result


def calc_national_by_week(df: pd.DataFrame, weight_col: str = "Weight") -> pd.DataFrame:
    """National-level indicators by week."""
    rows = []
    for week in sorted(df["Week"].dropna().unique()):
        sub = df[df["Week"] == week]
        r = calc_all_indicators(sub, weight_col)
        r["Week"] = week
        rows.append(r)
    return pd.DataFrame(rows)


def calc_by_dimension(df: pd.DataFrame, dim_col: str, weight_col: str = "Weight") -> pd.DataFrame:
    """Indicators broken down by week × dimension."""
    rows = []
    weeks = sorted(df["Week"].dropna().unique())
    for dim_val in sorted(df[dim_col].dropna().unique()):
        for week in weeks:
            sub = df[(df["Week"] == week) & (df[dim_col] == dim_val)]
            if sub.empty:
                continue
            r = calc_all_indicators(sub, weight_col)
            r["Week"] = week
            r[dim_col] = dim_val
            rows.append(r)
    return pd.DataFrame(rows)


def calc_cost_impact(df: pd.DataFrame, dim_col: str, weight_col: str = "Weight") -> pd.DataFrame:
    """
    Cost concern rate by a single dimension (collapsed across all weeks).
    Used for the 'which regions/industries are most impacted' analysis.
    """
    spec = INDICATORS["Cost_Concern"]
    rows = []
    for dim_val in sorted(df[dim_col].dropna().unique()):
        sub = df[df[dim_col] == dim_val]
        r = _weighted_proportion(sub, spec, weight_col)
        rows.append({
            dim_col: dim_val,
            "Cost_Concern": r["value"],
            "N": r["n"],
            "Sum_Weight": r["den_w"],
        })
    result = pd.DataFrame(rows)
    return result.sort_values("Cost_Concern", ascending=False).reset_index(drop=True)


def calc_concern_distribution(df: pd.DataFrame, weight_col: str = "Weight") -> pd.DataFrame:
    """Full distribution of FutConcern categories (excl. unsure & blank)."""
    col = "FutConcern"
    valid = df[df[col].notna() & (df[col].astype(str).str.strip() != "") & (df[col] != "Unsure")]
    total_w = valid[weight_col].sum()
    rows = []
    for concern in valid[col].unique():
        sub = valid[valid[col] == concern]
        w = sub[weight_col].sum()
        rows.append({
            "Concern": concern,
            "Pct": (w / total_w * 100) if total_w > 0 else 0,
            "N": len(sub),
            "Sum_Weight": w,
        })
    return pd.DataFrame(rows).sort_values("Pct", ascending=False).reset_index(drop=True)


def run_all_analyses(df: pd.DataFrame, weight_col: str = "Weight") -> dict:
    """
    Run every analysis and return a dict of DataFrames.

    Keys:
        national, by_State, by_Industry, by_GCC, by_BusinessSize, by_ARIA, by_CCRoS,
        cost_State, cost_Industry, cost_GCC, concern_distribution
    """
    results = {}

    # National time series
    results["national"] = calc_national_by_week(df, weight_col)

    # Breakdowns by week × dimension
    for key, dim in BREAKDOWNS.items():
        col = dim["col"]
        if col in df.columns:
            results[f"by_{key}"] = calc_by_dimension(df, col, weight_col)

    # Cost impact rankings
    for key in ["State", "Industry", "GCC"]:
        col = BREAKDOWNS[key]["col"]
        if col in df.columns:
            results[f"cost_{key}"] = calc_cost_impact(df, col, weight_col)

    # Full concern distribution
    results["concern_distribution"] = calc_concern_distribution(df, weight_col)

    return results
