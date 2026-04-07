"""
Configuration: column mappings, indicator definitions, and constants.
"""

# ── Variable names expected in the header-row of the input Excel ──
# Maps our internal name → possible variable names found in row 3 of the spreadsheet.
# The loader tries each alias in order and uses the first match.
VARIABLE_ALIASES = {
    "Week":           ["Week"],
    "Weight":         ["Weight"],
    "WeeklyWeight":   ["WeeklyWeight"],
    "RecruitShort":   ["RecruitShort"],
    "Difficulty":     ["Difficult", "Difficulty"],
    "FutStaffChange": ["Futstaffchange", "FutStaffChange"],
    "FutConcern":     ["FutConcern"],
    "State":          ["State"],
    "GCC":            ["GCC"],
    "CCRoS":          ["CCRoS"],
    "ARIA":           ["ARIA"],
    "Industry06":     ["Industry06"],
    "BusinessSize":   ["BusinessSize"],
    "Year":           ["Year"],
}

# Which row (0-indexed, after the pandas header row) contains the variable names
HEADER_ROW = 2        # pandas header= argument (row 3 in Excel = index 2)
VARNAME_ROW_OFFSET = 0  # first data-row offset after header that holds variable names

# ── Indicator specs ──
# Each indicator defines:
#   filter_col   – column to evaluate
#   numerator    – value(s) counted in the numerator
#   denominator  – "valid" values for the denominator
#   excl_unsure  – whether to exclude Unsure from denominator
#   excl_blank   – whether to exclude blank/NaN from denominator
INDICATORS = {
    "RR": {
        "label": "Recruitment Rate",
        "filter_col": "RecruitShort",
        "numerator": ["Yes"],
        "denominator": ["Yes", "No"],
        "description": "Proportion of employers currently recruiting or who recruited in the past month",
    },
    "RD": {
        "label": "Recruitment Difficulty Rate",
        "filter_col": "Difficulty",
        "numerator": ["Yes"],
        "denominator": ["Yes", "No"],
        "pre_filter": {"RecruitShort": ["Yes"]},   # only among recruiters
        "description": "Proportion of recruiting employers who experienced difficulty",
    },
    "FSI": {
        "label": "Future Staff Increase",
        "filter_col": "FutStaffChange",
        "numerator": ["Increase"],
        "denominator": "__all_non_blank__",        # includes Unsure
        "description": "Proportion expecting to increase staffing over next 3 months",
    },
    "Cost_Concern": {
        "label": "Costs as Greatest Concern",
        "filter_col": "FutConcern",
        "numerator": ["Costs"],
        "denominator": "__excl_unsure_blank__",    # excludes both Unsure and blank
        "description": "Proportion citing Costs as greatest concern (excl. unsure & blank)",
    },
}

# ── Breakdown dimensions ──
BREAKDOWNS = {
    "State":        {"col": "State",        "label": "State / Territory"},
    "Industry":     {"col": "Industry06",   "label": "Industry (ANZSIC Division)"},
    "GCC":          {"col": "GCC",          "label": "Region (GCC)"},
    "BusinessSize": {"col": "BusinessSize", "label": "Business Size"},
    "ARIA":         {"col": "ARIA",         "label": "Remoteness (ARIA)"},
    "CCRoS":        {"col": "CCRoS",        "label": "Capital City / Rest of State"},
}

# ── Excel formatting ──
EXCEL_HEADER_COLOR = "2F5496"
EXCEL_FONT = "Arial"
