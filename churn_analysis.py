import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# ---------- 0. Paths ----------
BASE = Path(__file__).parent
# UPDATED TO MATCH YOUR FILENAME
DATA_FILE = BASE / "data" / "telco_customer_churn.csv"   
OUT_DIR = BASE / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# ---------- 1. Load & Clean ----------
df = pd.read_csv(DATA_FILE)

# TotalCharges sometimes has blanks -> coerce to numeric
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
before = len(df)
df = df.dropna(subset=["TotalCharges"]).copy()
print(f"Dropped {before - len(df)} rows with missing TotalCharges")

# Convert target to 0/1 for easy math
df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)

# ---------- 2. Baseline churn ----------
total_customers = len(df)
churned = df["ChurnFlag"].sum()
baseline_churn = churned / total_customers * 100

print(f"\nTotal customers: {total_customers:,}")
print(f"Churned customers: {churned:,}")
print(f"Baseline churn rate: {baseline_churn:.2f}%")

# ---------- 3. Tenure cohorts ----------
bins = [0, 12, 24, 36, 48, 60, 72]
labels = ["0-12", "13-24", "25-36", "37-48", "49-60", "61-72"]
df["tenure_cohort"] = pd.cut(df["tenure"], bins=bins, labels=labels, include_lowest=True)

cohort_summary = (
    df.groupby("tenure_cohort", observed=True)
      .agg(customers=("customerID", "count"),
           churned=("ChurnFlag", "sum"))
)
cohort_summary["churn_rate_%"] = (cohort_summary["churned"] / cohort_summary["customers"] * 100).round(2)
print("\n--- Churn by tenure cohort ---")
print(cohort_summary)
cohort_summary.to_csv(OUT_DIR / "churn_by_tenure_cohort.csv")

# ---------- 4. Cohort retention matrix ----------
month_points = list(range(0, 73, 3))   # Month 0,3,6,...,72
retention_records = []

for cohort in labels:
    subset = df[df["tenure_cohort"] == cohort]
    if len(subset) == 0:
        continue
    for m in month_points:
        active = (subset["tenure"] >= m).mean() * 100
        retention_records.append(
            {"cohort": cohort, "month": m, "retention_%": round(active, 2)}
        )

retention_df = pd.DataFrame(retention_records)
retention_matrix = retention_df.pivot(index="cohort", columns="month", values="retention_%")
retention_matrix.to_csv(OUT_DIR / "cohort_retention_matrix.csv")
print("\n--- Cohort Retention Matrix (%) ---")
print(retention_matrix.round(1))

# ---------- 5. High-risk segment analysis ----------
risk_seg = (
    df.groupby(["InternetService", "TechSupport", "Contract"], observed=True)
      .agg(customers=("customerID", "count"),
           churned=("ChurnFlag", "sum"))
      .reset_index()
)
risk_seg["churn_rate_%"] = (risk_seg["churned"] / risk_seg["customers"] * 100).round(2)
risk_seg = risk_seg[risk_seg["customers"] >= 50]          
risk_seg = risk_seg.sort_values("churn_rate_%", ascending=False)
risk_seg.to_csv(OUT_DIR / "high_risk_segments.csv", index=False)

print("\n--- Top 10 highest-churn segments ---")
print(risk_seg.head(10).to_string(index=False))

# ---------- 6. Visualizations ----------
fig_heat = px.imshow(
    retention_matrix,
    labels=dict(x="Months since joining", y="Tenure cohort", color="Retention %"),
    text_auto=".0f",
    color_continuous_scale="RdYlGn",
    title="Cohort Retention Matrix — % of customers still active",
    aspect="auto",
)
fig_heat.update_layout(width=1100, height=500)
fig_heat.write_html(OUT_DIR / "cohort_retention_heatmap.html")
fig_heat.write_image(OUT_DIR / "cohort_retention_heatmap.png")

fig_bar = px.bar(
    cohort_summary.reset_index(),
    x="tenure_cohort",
    y="churn_rate_%",
    color="churn_rate_%",
    color_continuous_scale="Reds",
    text="churn_rate_%",
    title="Churn rate by tenure cohort",
)
fig_bar.write_html(OUT_DIR / "churn_by_cohort_bar.html")
fig_bar.write_image(OUT_DIR / "churn_by_cohort_bar.png")

top10 = risk_seg.head(10).copy()
top10["label"] = top10["InternetService"] + " | " + top10["TechSupport"] + " | " + top10["Contract"]
fig_risk = px.bar(
    top10,
    x="churn_rate_%",
    y="label",
    orientation="h",
    color="churn_rate_%",
    color_continuous_scale="Reds",
    text="churn_rate_%",
    title="Top 10 highest-churn customer segments",
)
fig_risk.update_layout(yaxis={"categoryorder": "total ascending"})
fig_risk.write_html(OUT_DIR / "top_risk_segments.html")
fig_risk.write_image(OUT_DIR / "top_risk_segments.png")

print("\nAll outputs written to:", OUT_DIR)