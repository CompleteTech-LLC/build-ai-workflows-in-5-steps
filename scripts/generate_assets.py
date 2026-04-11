#!/usr/bin/env python3
"""Generate the synthetic source PDF + target dashboard PNG for
Sample Bistro & Co. — the lesson's default example assets.

Run `python scripts/generate_assets.py` from the project root to
regenerate assets/source_financial_pack.pdf and assets/target_dashboard.png.

Deterministic via random.seed, so regenerating gives byte-identical output.
Requires: reportlab, matplotlib, pypdf.
"""
import random
from pathlib import Path

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rlcolors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

random.seed(1337)

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

BUSINESS = "Sample Bistro & Co."
PERIOD = "For the YTD ending January 2024"
FY_LABEL = "FY 2024"

# Non-calendar fiscal year: April through March. YTD ending January = 11 months shown.
MONTHS = ["Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]

# (alloc2, accounts2, accounts, ytd_total)
# Revenue shown negative per pivot-table convention; expenses positive.
# All numbers are fictional, chosen to preserve the lesson's teaching moments:
# - Non-calendar fiscal year (Apr-Mar)
# - Negative revenue signs
# - Owner Salary line (ambiguous compensation)
# - Equipment Purchases in opex section (capex-vs-opex flag)
# - Donations line (policy-aware classification)
# - Miscellaneous Expense > materiality threshold
# - Discount Meals / Refunds (contra-revenue ambiguity)
ROWS = [
    ("Gross Profit", "Beverage",   "Sales - Beverages",        -420_000),
    ("Gross Profit", "Beverage",   "Beverage Purchases",        102_000),
    ("Gross Profit", "Food Sales", "Sales - Food",           -1_410_000),
    ("Gross Profit", "Food Sales", "Food Purchases",            485_000),
    ("Gross Profit", "Food Sales", "Discount Meals",             18_500),
    ("Gross Profit", "Discounts",  "Discounts",                  14_200),
    ("Gross Profit", "Discounts",  "Refund",                      2_400),
    ("Gross Profit", "Retail",     "Sales - Retail",            -85_000),
    ("Gross Profit", "Packaging",  "Packaging Purchases",        22_500),
    ("Gross Profit", "Packaging",  "Boxes Purchases",             8_200),
    ("Gross Profit", "Packaging",  "Packaging Sales",           -55_800),
    ("Expenses",     "Operating",  "Cash Over and Short",           820),
    ("Expenses",     "Operating",  "Equipment Rental",            9_600),
    ("Expenses",     "Operating",  "Repairs and Maintenance",    21_800),
    ("Expenses",     "Operating",  "Advertising and Promotion",  18_400),
    ("Expenses",     "Operating",  "Donations",                   4_500),
    ("Expenses",     "Operating",  "Vehicle Expense - Other",     7_200),
    ("Expenses",     "Operating",  "Commissions",                 3_100),
    ("Expenses",     "Operating",  "Staff uniforms",              3_400),
    ("Expenses",     "Operating",  "Bank Service Charges",        4_800),
    ("Expenses",     "Operating",  "Cleaning Purchases",          7_200),
    ("Expenses",     "Operating",  "Consumable Purchases",       12_400),
    ("Expenses",     "Operating",  "Depreciation Expense",       48_000),
    ("Expenses",     "Operating",  "Dues and Subscriptions",      3_600),
    ("Expenses",     "Operating",  "Electricity usage",          52_000),
    ("Expenses",     "Operating",  "Equipment Purchases",        42_000),
    ("Expenses",     "Operating",  "Gas Purchases",              14_500),
    ("Expenses",     "Operating",  "Insurance Expense",          28_000),
    ("Expenses",     "Operating",  "Miscellaneous Expense",      18_700),
    ("Expenses",     "Operating",  "Petrol",                      4_200),
    ("Expenses",     "Operating",  "Owner Salary",               85_000),
    ("Expenses",     "Operating",  "Printing Purchases",          2_200),
    ("Expenses",     "Operating",  "Professional Fees",          15_000),
    ("Expenses",     "Operating",  "Rent and Rates",            360_000),
    ("Expenses",     "Operating",  "Staff Food Purchases",        9_500),
    ("Expenses",     "Operating",  "Staff Salaries",             82_000),
    ("Expenses",     "Operating",  "Staff Transport",             6_200),
    ("Expenses",     "Operating",  "Staff Wages",               395_000),
    ("Expenses",     "Operating",  "Stationary Purchases",          900),
    ("Expenses",     "Operating",  "Telephone",                   3_800),
    ("Expenses",     "Operating",  "Central Kitchen Rent",       60_000),
    ("Expenses",     "Operating",  "Bonus",                      12_000),
    ("Expenses",     "Operating",  "Casual Wages",               32_000),
    ("Expenses",     "Operating",  "PAYE",                       58_000),
]


def distribute_monthly(ytd_total: int, n_months: int = 11) -> list[int]:
    """Split a YTD total across n_months with small noise; sum equals ytd exactly."""
    if ytd_total == 0:
        return [0] * n_months
    base = ytd_total / n_months
    vals = [round(base * (0.80 + random.random() * 0.40)) for _ in range(n_months - 1)]
    vals.append(int(ytd_total - sum(vals)))
    return vals


def build_distributions():
    """Compute per-row monthly distributions once (deterministic via random.seed)."""
    rows_with_monthly = []
    col_sums = [0] * len(MONTHS)
    grand_total = 0
    for alloc2, acc2, account, ytd in ROWS:
        monthly = distribute_monthly(ytd)
        rows_with_monthly.append((alloc2, acc2, account, monthly, ytd))
        for i, v in enumerate(monthly):
            col_sums[i] += v
        grand_total += ytd
    return rows_with_monthly, col_sums, grand_total


def fmt(n: int) -> str:
    """Pivot-style number formatting: commas, parens for negatives, blank for zero."""
    if n == 0:
        return ""
    return f"{n:,}"


def generate_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(letter),
        leftMargin=0.35 * inch, rightMargin=0.35 * inch,
        topMargin=0.35 * inch, bottomMargin=0.35 * inch,
        title=f"{BUSINESS} — Financial Pack",
        author="Sample Bistro & Co. (synthetic)",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Title"],
        fontSize=13, alignment=TA_LEFT, spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "subtitle", parent=styles["Normal"],
        fontSize=9, alignment=TA_LEFT, spaceAfter=2,
    )

    story = [
        Paragraph(f"<b>{BUSINESS}</b>", title_style),
        Paragraph(PERIOD, subtitle_style),
        Paragraph("IS Alloc   (Multiple Items)", subtitle_style),
        Spacer(1, 4),
    ]

    rows_with_monthly, col_sums, grand_total = build_distributions()

    header = ["IS Alloc2", "Accounts2", "Accounts"] + MONTHS + ["Grand Total"]
    table_data = [header]
    for alloc2, acc2, account, monthly, ytd in rows_with_monthly:
        row = [alloc2, acc2, account] + [fmt(v) for v in monthly] + [fmt(ytd)]
        table_data.append(row)

    # Grand total row
    total_row = ["Grand Total", "", ""] + [fmt(v) for v in col_sums] + [fmt(grand_total)]
    table_data.append(total_row)

    # Column widths (sum must fit ~10.2in usable width in landscape letter)
    col_widths = [
        0.65 * inch,  # Alloc2
        0.65 * inch,  # Accounts2
        1.20 * inch,  # Accounts
    ] + [0.55 * inch] * len(MONTHS) + [0.85 * inch]  # 0.65+0.65+1.20+6.05+0.85 = 9.40in

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("FONT",        (0, 0), (-1, 0), "Helvetica-Bold", 7),
        ("FONT",        (0, 1), (-1, -1), "Helvetica", 6),
        ("BACKGROUND",  (0, 0), (-1, 0), rlcolors.HexColor("#2e3440")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), rlcolors.whitesmoke),
        ("ALIGN",       (0, 0), (2, -1), "LEFT"),
        ("ALIGN",       (3, 0), (-1, -1), "RIGHT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",        (0, 0), (-1, -1), 0.25, rlcolors.HexColor("#c0c0c0")),
        ("TOPPADDING",  (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        # Grand total row styling
        ("FONT",        (0, -1), (-1, -1), "Helvetica-Bold", 6),
        ("BACKGROUND",  (0, -1), (-1, -1), rlcolors.HexColor("#e5e9f0")),
        ("LINEABOVE",   (0, -1), (-1, -1), 0.75, rlcolors.HexColor("#4c566a")),
    ]))
    story.append(table)

    # Footer cost percentages
    story.append(Spacer(1, 6))

    def pct_row(label: str, center: float, spread: float) -> list[str]:
        vals = [f"{round(center + random.uniform(-spread, spread), 2)}%" for _ in MONTHS]
        return ["", "", label] + vals + [""]

    footer_data = [
        header,  # repeat for alignment
        pct_row("Food Cost Percentage", 32.5, 2.5),
        pct_row("Beverage Cost Percentage", 24.0, 3.5),
        pct_row("Sit Down Percentage", 62.0, 2.5),
        pct_row("Take Away Percentage", 38.0, 2.5),
    ]
    footer_table = Table(footer_data, colWidths=col_widths)
    footer_table.setStyle(TableStyle([
        ("FONT",         (0, 0), (-1, 0), "Helvetica-Bold", 7),
        ("FONT",         (0, 1), (-1, -1), "Helvetica-Oblique", 6),
        ("BACKGROUND",   (0, 0), (-1, 0), rlcolors.HexColor("#2e3440")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), rlcolors.whitesmoke),
        ("ALIGN",        (0, 0), (2, -1), "LEFT"),
        ("ALIGN",        (3, 0), (-1, -1), "RIGHT"),
        ("GRID",         (0, 0), (-1, -1), 0.25, rlcolors.HexColor("#c0c0c0")),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))
    story.append(footer_table)

    doc.build(story)


def generate_dashboard(output_path: Path):
    """Render a dark-themed financial scorecard PNG matching the lesson's target aesthetic."""
    BG       = "#0a0a12"
    PANEL    = "#14141c"
    BORDER   = "#2a2a38"
    TEXT     = "#e8e8ef"
    LABEL    = "#8f8fa8"
    MUTED    = "#6e6e88"
    GREEN    = "#48d1a4"
    AMBER    = "#e8a72e"
    RED      = "#ea6454"
    BLUE     = "#4aa8d8"

    fig = plt.figure(figsize=(15, 9), facecolor=BG)
    gs = gridspec.GridSpec(
        3, 5, figure=fig,
        hspace=0.55, wspace=0.45,
        top=0.90, bottom=0.06, left=0.035, right=0.97,
        height_ratios=[1.0, 1.3, 1.0],
    )

    fig.text(0.035, 0.955,
             f"Tax Readiness & Financial Health Scorecard",
             color=TEXT, fontsize=16, fontweight="bold")
    fig.text(0.035, 0.928,
             f"{BUSINESS}   ·   {FY_LABEL}",
             color=LABEL, fontsize=10)

    def style_panel(ax, title=None):
        ax.set_facecolor(PANEL)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
            spine.set_linewidth(1.2)
        if title:
            ax.text(0.03, 1.08, title, color=LABEL, fontsize=9,
                    fontweight="bold", transform=ax.transAxes)

    # --- Panel 1: Estimated Tax Liability (top-left, 3 cols) ---
    ax_tax = fig.add_subplot(gs[0, :3])
    style_panel(ax_tax, "ESTIMATED TAX LIABILITY")
    ax_tax.text(0.03, 0.55, "$32,800", color=GREEN,
                fontsize=44, fontweight="bold", transform=ax_tax.transAxes, va="center")
    ax_tax.text(0.03, 0.18, f"{FY_LABEL} estimate, before quarterly payments",
                color=MUTED, fontsize=9, transform=ax_tax.transAxes)
    ax_tax.text(0.57, 0.55, "QUARTERLY DUE", color=LABEL, fontsize=8,
                transform=ax_tax.transAxes, fontweight="bold")
    ax_tax.text(0.57, 0.35, "$8,200", color=TEXT, fontsize=20,
                fontweight="bold", transform=ax_tax.transAxes)
    ax_tax.text(0.57, 0.18, "Next payment: April 15, 2024",
                color=MUTED, fontsize=8, transform=ax_tax.transAxes)

    # --- Panel 2: Action Items (top-right, 2 cols) ---
    ax_act = fig.add_subplot(gs[0, 3:])
    style_panel(ax_act, "ACTION ITEMS")
    items = [
        (AMBER, "3 expenses may be miscategorized", "$18,700 in 'Miscellaneous'"),
        (RED,   "Equipment Purchases flagged for capex review", "$42,000"),
        (BLUE,  "Owner Salary needs entity-specific tax rule", "$85,000"),
    ]
    for i, (color, title, subtitle) in enumerate(items):
        y = 0.72 - i * 0.24
        ax_act.text(0.05, y, "\u25cf", color=color, fontsize=13,
                    transform=ax_act.transAxes, va="center")
        ax_act.text(0.11, y + 0.03, title, color=TEXT, fontsize=9,
                    transform=ax_act.transAxes, va="center")
        ax_act.text(0.11, y - 0.06, subtitle, color=MUTED, fontsize=7,
                    transform=ax_act.transAxes, va="center")

    # --- Panel 3: Deduction Tracker (middle-left, 3 cols) ---
    ax_ded = fig.add_subplot(gs[1, :3])
    style_panel(ax_ded, "DEDUCTION TRACKER BY CATEGORY")
    categories = [
        ("Payroll & Benefits",  600_000),
        ("Rent & Facilities",   420_000),
        ("Depreciation",         48_000),
        ("Insurance",            28_000),
        ("Miscellaneous",        18_700),
        ("Marketing",            18_400),
        ("Professional Services",15_000),
        ("Other Opex",           95_000),
    ]
    names  = [c[0] for c in categories]
    values = [c[1] for c in categories]
    colors_bar = [GREEN] * len(categories)
    colors_bar[names.index("Miscellaneous")] = AMBER  # flagged bucket
    positions = list(range(len(categories)))
    ax_ded.barh(positions, values, color=colors_bar, height=0.65)
    ax_ded.set_yticks(positions)
    ax_ded.set_yticklabels(names, color=TEXT, fontsize=8)
    ax_ded.invert_yaxis()
    ax_ded.tick_params(colors=LABEL, length=0)
    ax_ded.set_xticks([])
    for spine_name, spine in ax_ded.spines.items():
        if spine_name in ("top", "right", "bottom"):
            spine.set_visible(False)
    for pos, val in zip(positions, values):
        ax_ded.text(val + max(values) * 0.012, pos, f"${val/1000:.0f}k",
                    color=TEXT, fontsize=8, va="center")

    # --- Panel 4: Financial Health Ratios (middle-right, 2 cols) ---
    ax_rat = fig.add_subplot(gs[1, 3:])
    style_panel(ax_rat, "FINANCIAL HEALTH (plain English)")
    ratios = [
        ("Current Ratio",   "1.8",  "healthy",    GREEN,
         "You can cover short-term bills 1.8x over."),
        ("Debt-to-Equity",  "0.42", "low",        GREEN,
         "Conservative capital structure."),
        ("Gross Margin",    "66%",  "watch",      AMBER,
         "Slightly below peer average for this size."),
    ]
    for i, (name, val, label_text, color, explanation) in enumerate(ratios):
        y = 0.78 - i * 0.27
        ax_rat.text(0.05, y, name, color=LABEL, fontsize=8,
                    transform=ax_rat.transAxes)
        ax_rat.text(0.05, y - 0.08, val, color=TEXT, fontsize=20,
                    fontweight="bold", transform=ax_rat.transAxes)
        ax_rat.text(0.35, y - 0.06, label_text, color=color, fontsize=9,
                    fontweight="bold", transform=ax_rat.transAxes)
        ax_rat.text(0.35, y - 0.13, explanation, color=MUTED, fontsize=7,
                    transform=ax_rat.transAxes)

    # --- Panel 5: Quarterly Trend (bottom, full width) ---
    ax_trn = fig.add_subplot(gs[2, :])
    style_panel(ax_trn, "QUARTERLY HEALTH TREND")
    quarters = ["Q1 FY24", "Q2 FY24", "Q3 FY24", "Q4 FY24*"]
    metrics = {
        "Revenue":          ["$420k", "$465k", "$510k", "$565k"],
        "Gross Margin":     ["65%",   "66%",   "66%",   "67%"],
        "Operating Income": ["$38k",  "$42k",  "$49k",  "$55k"],
        "Cash on Hand":     ["$85k",  "$92k",  "$98k",  "$105k"],
    }
    row_labels = list(metrics.keys())
    n_cols = len(quarters)

    # Hand-drawn table (matplotlib's ax.table looks crude on dark bg)
    col_w = 0.20
    first_col_w = 0.22
    for j, q in enumerate(quarters):
        x = 0.30 + j * col_w
        ax_trn.text(x, 0.82, q, color=LABEL, fontsize=9,
                    fontweight="bold", ha="center", transform=ax_trn.transAxes)
    for i, label in enumerate(row_labels):
        y = 0.62 - i * 0.16
        ax_trn.text(0.03, y, label, color=LABEL, fontsize=9,
                    transform=ax_trn.transAxes)
        for j, val in enumerate(metrics[label]):
            x = 0.30 + j * col_w
            ax_trn.text(x, y, val, color=TEXT, fontsize=10,
                        fontweight="bold", ha="center", transform=ax_trn.transAxes)

    # Subtle divider under header
    ax_trn.plot([0.02, 0.98], [0.72, 0.72], color=BORDER, linewidth=0.6,
                transform=ax_trn.transAxes, clip_on=False)

    # Footer note
    fig.text(0.035, 0.02,
             f"{BUSINESS}  ·  Synthetic example data for educational demo only — not real financial figures.",
             color="#4a4a5c", fontsize=7)

    plt.savefig(str(output_path), dpi=120, facecolor=fig.get_facecolor(),
                bbox_inches=None)
    plt.close(fig)


if __name__ == "__main__":
    pdf_path  = ASSETS / "source_financial_pack.pdf"
    dash_path = ASSETS / "target_dashboard.png"

    generate_pdf(pdf_path)
    print(f"Wrote {pdf_path.name}  ({pdf_path.stat().st_size:,} bytes)")

    generate_dashboard(dash_path)
    print(f"Wrote {dash_path.name}  ({dash_path.stat().st_size:,} bytes)")

    # Verify PDF extraction still lands teaching moments
    import pypdf
    reader = pypdf.PdfReader(str(pdf_path))
    text = "\n".join(p.extract_text() or "" for p in reader.pages)
    print()
    print(f"PDF extraction length: {len(text):,} characters")
    checks = [
        ("Owner Salary",           "owner pay ambiguity"),
        ("Equipment Purchases",    "capex-vs-opex flag"),
        ("Donations",              "policy classification"),
        ("Miscellaneous Expense",  "materiality threshold"),
        ("Discount Meals",         "contra-revenue"),
        ("Sample Bistro",          "anonymized business name"),
        ("January 2024",           "non-calendar fiscal period"),
    ]
    for phrase, label in checks:
        present = phrase in text
        marker = "OK " if present else "MISS"
        print(f"  [{marker}]  {label:30s} ({phrase!r})")
