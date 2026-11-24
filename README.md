# Telco Customer Churn — Cohort & Churn Analytics

**Project Overview**
This repository contains a complete cohort and churn analysis of the IBM Telco Customer Churn dataset. The goal was to understand customer retention behavior over time, identify the primary drivers of churn, and provide actionable business recommendations.

### Key Findings
* **Baseline Churn:** 26.58% of the total customer base has churned.
* **Critical Drop-off:** Customers in their first year (0-12 months) are at the highest risk, with a churn rate of 47.68%.
* **Highest Risk Segment:** Fiber Optic users on a Month-to-Month contract without Tech Support churn at an alarming 57.52%.

### Technologies Used
* **Python** (Pandas, NumPy, Plotly) for data cleaning, cohort matrix generation, and visualizations.
* **VS Code** as the development environment.

### How to Run
1. Install requirements: `pip install -r requirements.txt`
2. Run the script: `python churn_analysis.py`