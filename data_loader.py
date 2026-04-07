"""
Data loader: reads the multi-header Excel file and maps columns to standard names.
"""

import sys
import pandas as pd
import numpy as np
from config import VARIABLE_ALIASES, HEADER_ROW, VARNAME_ROW_OFFSET


def load_survey(path: str, weight_col: str = "Weight") -> pd.DataFrame:
    """
    Read the survey Excel file with its 3-row header structure.

    Returns a clean DataFrame with standardised column names and typed values.
    """
    raw = pd.read_excel(path, header=HEADER_ROW)

    # Row 0 (after the header) contains the short variable names
    varname_row = raw.iloc[VARNAME_ROW_OFFSET]
    data = raw.iloc[VARNAME_ROW_OFFSET + 1:].copy().reset_index(drop=True)

    # Build a mapping: column-position → internal name
    varname_to_pos = {}
    for pos, val in enumerate(varname_row):
        if pd.notna(val) and isinstance(val, str):
            varname_to_pos[val.strip()] = pos

    col_rename = {}
    matched = {}
    for internal_name, aliases in VARIABLE_ALIASES.items():
        for alias in aliases:
            if alias in varname_to_pos:
                col_pos = varname_to_pos[alias]
                original_col = raw.columns[col_pos]
                col_rename[original_col] = internal_name
                matched[internal_name] = alias
                break

    data = data.rename(columns=col_rename)

    # Override weight column if user specified something different
    if weight_col != "Weight" and weight_col in VARIABLE_ALIASES:
        pass  # already handled
    elif weight_col not in data.columns and "Weight" in data.columns:
        pass  # default is fine

    # ── Type coercion ──
    if "Weight" in data.columns:
        data["Weight"] = pd.to_numeric(data["Weight"], errors="coerce")
    if "WeeklyWeight" in data.columns:
        data["WeeklyWeight"] = pd.to_numeric(data["WeeklyWeight"], errors="coerce")
    if "Week" in data.columns:
        data["Week"] = pd.to_datetime(data["Week"], errors="coerce")
    if "Year" in data.columns:
        data["Year"] = pd.to_numeric(data["Year"], errors="coerce")

    # ── Validation ──
    required = ["Week", "Weight", "RecruitShort", "Difficulty", "FutStaffChange", "FutConcern"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        print(f"WARNING: Could not map these required variables: {missing}")
        print(f"  Matched variables: {matched}")
        print(f"  Available variable names in file: {list(varname_to_pos.keys())[:30]}...")

    n = len(data)
    n_valid_weight = data["Weight"].notna().sum() if "Weight" in data.columns else 0
    weeks = sorted(data["Week"].dropna().unique()) if "Week" in data.columns else []
    years = sorted(data["Year"].dropna().unique()) if "Year" in data.columns else []

    print(f"Loaded {n} records across {len(weeks)} week(s)")
    print(f"  Valid weights: {n_valid_weight}/{n}")
    print(f"  Years in data: {[int(y) for y in years]}")
    print(f"  Week range: {weeks[0].strftime('%Y-%m-%d') if weeks else 'N/A'} → {weeks[-1].strftime('%Y-%m-%d') if weeks else 'N/A'}")
    print(f"  Columns mapped: {matched}")

    return data


def filter_by_year(df: pd.DataFrame, year_from: int = None, year_to: int = None) -> pd.DataFrame:
    """
    Filter the dataset by year range.

    Parameters
    ----------
    df : DataFrame with a 'Year' column (or 'Week' as fallback)
    year_from : minimum year (inclusive), e.g. 2016
    year_to : maximum year (inclusive), e.g. 2026

    Returns filtered DataFrame.
    """
    original_n = len(df)

    if "Year" in df.columns:
        year_col = df["Year"]
    elif "Week" in df.columns:
        year_col = df["Week"].dt.year
    else:
        print("WARNING: No Year or Week column found — skipping year filter")
        return df

    mask = pd.Series(True, index=df.index)
    if year_from is not None:
        mask &= year_col >= year_from
    if year_to is not None:
        mask &= year_col <= year_to

    filtered = df[mask].copy().reset_index(drop=True)
    label_parts = []
    if year_from is not None:
        label_parts.append(f">= {year_from}")
    if year_to is not None:
        label_parts.append(f"<= {year_to}")
    label = " and ".join(label_parts)

    print(f"  Year filter ({label}): {original_n} → {len(filtered)} records")

    return filtered
