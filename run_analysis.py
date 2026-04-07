#!/usr/bin/env python3
"""
Recruitment Survey Analysis — CLI entry point.

Usage:
    python run_analysis.py <input_excel> [-o OUTPUT_DIR] [--weight-col WEIGHT_COL]

Example:
    python run_analysis.py Book1.xlsx
    python run_analysis.py Book1.xlsx -o results/ --weight-col WeeklyWeight
"""

import argparse
import os
import sys
import time

from data_loader import load_survey
from indicators import run_all_analyses
from excel_report import write_excel
from dashboard import build_dashboard


def main():
    parser = argparse.ArgumentParser(
        description="Recruitment Survey Analysis — Fuel Shock MO Weekly Update"
    )
    parser.add_argument(
        "input_file",
        help="Path to the survey Excel file (.xlsx)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Output directory (default: ./output/)",
    )
    parser.add_argument(
        "--weight-col",
        default="Weight",
        help="Weight variable to use: 'Weight' (monthly, default) or 'WeeklyWeight'",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        print(f"Error: file not found — {args.input_file}")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 60)
    print("  Recruitment Survey Analysis")
    print("=" * 60)
    print()

    # 1. Load
    print("[1/4] Loading data...")
    t0 = time.time()
    df = load_survey(args.input_file, weight_col=args.weight_col)
    print(f"      Done in {time.time() - t0:.1f}s\n")

    # 2. Calculate
    print("[2/4] Calculating indicators...")
    t0 = time.time()
    results = run_all_analyses(df, weight_col=args.weight_col)
    print(f"      Done in {time.time() - t0:.1f}s\n")

    # Print summary
    nat = results["national"]
    latest = nat.iloc[-1]
    print("      ┌─────────────────────────────────────────────┐")
    print(f"      │  Latest week: {latest['Week'].strftime('%Y-%m-%d') if hasattr(latest['Week'], 'strftime') else latest['Week']:>27s}  │")
    print(f"      │  Recruitment Rate (RR):       {latest['RR']*100:>10.1f}%     │")
    print(f"      │  Recruitment Difficulty (RD):  {latest['RD']*100:>10.1f}%     │")
    print(f"      │  Future Staff Increase (FSI):  {latest['FSI']*100:>10.1f}%     │")
    print(f"      │  Cost Concern:                 {latest['Cost_Concern']*100:>10.1f}%     │")
    print(f"      │  N = {int(latest['N']):>4d}   Total Weight = {latest['Sum_Weight']:>9.1f}     │")
    print("      └─────────────────────────────────────────────┘\n")

    # 3. Excel
    print("[3/4] Writing Excel report...")
    t0 = time.time()
    excel_path = os.path.join(args.output_dir, "Recruitment_Survey_Stats.xlsx")
    write_excel(results, excel_path)
    print(f"      Done in {time.time() - t0:.1f}s\n")

    # 4. Dashboard
    print("[4/4] Building HTML dashboard...")
    t0 = time.time()
    html_path = os.path.join(args.output_dir, "Recruitment_Survey_Dashboard.html")
    build_dashboard(results, html_path)
    print(f"      Done in {time.time() - t0:.1f}s\n")

    print("=" * 60)
    print("  Complete!")
    print(f"  Excel  → {os.path.abspath(excel_path)}")
    print(f"  HTML   → {os.path.abspath(html_path)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
