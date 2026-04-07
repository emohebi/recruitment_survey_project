# Recruitment Survey Analysis — Fuel Shock MO Weekly Update

This project calculates weighted indicators from weekly employer recruitment survey data and produces:

1. **Excel report** with national and breakdown statistics across multiple dimensions
2. **Interactive HTML dashboard** with time series charts and cost impact analysis

## Indicators

| Indicator | Description | Exclusions |
|-----------|-------------|------------|
| **RR** (Recruitment Rate) | % of employers currently recruiting or recruited in past month | Excl. "Unsure" |
| **RD** (Recruitment Difficulty) | % of recruiting employers who experienced difficulty | Excl. "Unsure" |
| **FSI** (Future Staff Increase) | % expecting to increase staff over next 3 months | Incl. "Unsure" in denominator |
| **Cost Concern** | % citing Costs as greatest future concern | Excl. "Unsure" and blanks |

All proportions use **sum of weights**, not raw counts.

## Setup

```bash
pip install pandas openpyxl
```

No other dependencies required. The HTML dashboard is self-contained (Chart.js loaded via CDN).

## Usage

```bash
python run_analysis.py path/to/survey_data.xlsx
```

### Options

```
python run_analysis.py data.xlsx                       # defaults: output to ./output/
python run_analysis.py data.xlsx -o results/           # custom output directory
python run_analysis.py data.xlsx --year-from 2016      # only data from 2016 onwards
python run_analysis.py data.xlsx --year-from 2020 --year-to 2025  # year range
python run_analysis.py data.xlsx --weight-col Weight   # specify weight column (default: Weight)
```

### Output

The script creates two files in the output directory:

- `Recruitment_Survey_Stats.xlsx` — Multi-sheet workbook with indicators by Week, State, Industry, Region, Business Size, and Remoteness
- `Recruitment_Survey_Dashboard.html` — Interactive dashboard (open in any browser)

## Input File Format

The Excel file must have **3 header rows**:
- Row 1: Section group names
- Row 2: Long descriptive column names
- Row 3: **Variable names** (used for column mapping)

Data starts from row 4. Required variable names (in row 3):

| Variable | Column purpose |
|----------|---------------|
| `Week` | Week ending date |
| `Weight` | Monthly weight for proportions |
| `RecruitShort` | Yes/No — recruited in past month |
| `Difficulty` / `Difficult` | Yes/No/Unsure — difficulty recruiting |
| `FutStaffChange` / `Futstaffchange` | Increase/Remain the same/Decrease |
| `FutConcern` | Greatest future concern category |
| `State` | State / Territory |
| `GCC` | Greater Capital City / Rest of State |
| `CCRoS` | Combined Capital City / Rest of State |
| `ARIA` | Remoteness (ARIA) |
| `Industry06` | ANZSIC Division |
| `BusinessSize` | Small / Medium / Large |

## Project Structure

```
recruitment_survey_project/
├── README.md
├── run_analysis.py          # CLI entry point
├── config.py                # Column mappings & indicator definitions
├── data_loader.py           # Reads & validates the Excel input
├── indicators.py            # Weighted indicator calculation engine
├── excel_report.py          # Excel output with formatting
├── dashboard.py             # HTML dashboard generator
└── templates/
    └── dashboard_template.html
```
