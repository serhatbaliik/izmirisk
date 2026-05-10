# 💧 İzmiRisk — Data-Driven Water Security Risk Modeling

### A District-Level Analysis for İzmir · 2010–2030

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://izmirisk.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat)]()

> **Live Dashboard →** [izmirisk.streamlit.app](https://izmirisk.streamlit.app)

-----

## 📌 Overview

İzmiRisk is an end-to-end data analytics project that develops a **Water Security Risk Index (WSRI)** for İzmir’s 11 central districts. Using open data from İZSU (İzmir Water and Sewerage Administration), the project transforms raw supply, consumption, and infrastructure data into an actionable, district-level composite risk score — and projects risk trends through 2030 under three scenarios.

This project was presented as a **poster at WAMS 2026** (II. Workshop on Applied Mathematics and Statistics, İzmir University of Economics) and accepted as a senior thesis in the Department of Mathematics.

**Advisors:** Asst. Prof. Dr. Necla KOÇHAN · Asst. Prof. Dr. Ömür SALTIK
**Institution:** İzmir University of Economics, Faculty of Arts and Sciences

-----

## 🎯 Key Features

|Feature                       |Description                                                                       |
|------------------------------|----------------------------------------------------------------------------------|
|📊 **Composite Risk Index**    |Entropy-weighted WSRI combining 4 indicators into a single 0–100 score            |
|🔁 **Bootstrap Simulation**    |Synthetic historical data (2010–2019) generated from 4 years of real data         |
|📈 **Trend Analysis**          |Mann-Kendall non-parametric test for temporal trend detection                     |
|🗺️ **Spatial Analysis**        |Moran’s I & LISA for spatial autocorrelation and clustering                       |
|🔮 **2030 Projections**        |Three CAGR-based scenarios: optimistic (×0.5), baseline (×1.0), pessimistic (×1.5)|
|🧭 **Interactive Dashboard**   |Risk map, district comparison tool, simulator, animated time series, radar chart  |
|📋 **District Recommendations**|Personalized policy recommendations per district based on risk category           |

-----

## 🧪 Methodology

### 1. Data Collection & Normalization

District-level data collected from İzmir Metropolitan Municipality Open Data Portal and official İZSU water management reports. All indicators normalized to a 0–100 scale using min-max normalization.

### 2. Bootstrap-Based Historical Simulation

Due to limited pre-2020 data availability, missing values for 2010–2019 were reconstructed using a **block bootstrap resampling** approach. This preserves temporal continuity while maintaining statistical properties of the original series.

```
x̃ₜ = (xₜ₊₁ + xₜ) / 2 + εₜ,   εₜ ~ N(0, σ²)
```

### 3. Water Security Risk Index (WSRI)

The WSRI is constructed as an entropy-weighted composite of four normalized indicators:

```
WSRI = Σ wᵢ · xᵢ
```

Where weights `wᵢ` are derived from Shannon entropy to objectively reflect the information content of each indicator.

**Indicators:**

- Per-capita water consumption
- Consumption growth rate (CAGR)
- Supply constraint ratio
- Administrative water loss rate

### 4. Temporal & Spatial Analysis

- **Mann-Kendall test** (S statistic, τ = -0.368, p < 0.001): significant declining trend confirmed system-wide
- **Moran’s I** (-0.111, p > 0.05): no significant spatial clustering — districts are spatially dispersed in risk

### 5. 2030 Scenario Projections

Future WSRI values modeled using regression-based trend projection:

```
Xₜ = β₀ + β₁t + ε
```

Three scenarios modeled by scaling the trend slope β₁ with multipliers: 0.5 (optimistic), 1.0 (baseline), 1.5 (pessimistic).

-----

## 📊 Results Summary

|District  |2023 WSRI|Risk Category|2030 Baseline|
|----------|---------|-------------|-------------|
|Bornova   |67.0     |🔴 High       |62.0         |
|Çiğli     |62.0     |🔴 High       |56.0         |
|Bayraklı  |61.0     |🔴 High       |54.0         |
|Buca      |54.0     |🟠 Medium-High|47.0         |
|Gaziemir  |56.0     |🟠 Medium-High|50.0         |
|Balçova   |44.0     |🟡 Medium     |38.0         |
|Karabağlar|45.0     |🟡 Medium     |40.0         |


> Despite structural improvements in all four indicators, high-risk districts remain at risk of breaching the critical threshold (60) even under the baseline scenario.

-----

## 🛠️ Tech Stack

```
Data & Analysis          Visualization            Deployment
─────────────────        ──────────────────       ──────────────
Python 3.10+             Streamlit                Streamlit Cloud
Pandas                   Plotly                   GitHub
NumPy                    Folium / GeoPandas
SciPy                    Matplotlib / Seaborn
Statsmodels (MK test)
Scikit-learn
```

-----

## 🚀 Run Locally

```bash
# Clone the repository
git clone https://github.com/serhatbaliik/izmirisk.git
cd izmirisk

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

-----

## 📁 Project Structure

```
izmirisk/
├── app.py                  # Main Streamlit application (~3000 lines)
├── requirements.txt
├── data/
│   ├── raw/                # Original İZSU open data
│   └── processed/          # Bootstrap-extended time series (2010–2023)
├── analysis/
│   ├── bootstrap.py        # Block bootstrap simulation
│   ├── wsri.py             # Entropy-weighted index calculation
│   ├── mann_kendall.py     # Trend analysis
│   └── spatial.py          # Moran's I & LISA
└── assets/
    └── screenshots/
```

-----

## 📂 Data Sources

1. İzmir Metropolitan Municipality Open Data Portal (İZSU) — District-level water consumption, loss rates, subscriber counts (2020–2023)
1. İzmir Water and Sewerage Administration (İZSU) — Official water management reports
1. UN-Water (2018) — Water Security & the Global Water Agenda

-----

## 📸 Screenshots

> Dashboard screenshots available at [izmirisk.streamlit.app](https://izmirisk.streamlit.app)

-----

## 📄 Citation

If you use this work, please cite:

```
Balık, S. (2026). İzmiRisk: Data-Driven Water Risk Modeling —
A District-Level Analysis for İzmir. Senior Thesis,
İzmir University of Economics, Department of Mathematics.
Advisors: Koçhan, N. & Saltık, Ö.
```

-----

## 📬 Contact

**Serhat Balık**
Mathematics · İzmir University of Economics
[LinkedIn](https://linkedin.com/in/serhatbalik) · [GitHub](https://github.com/serhatbaliik)

> Open to opportunities in **Data Analytics · Financial Analysis · Reporting & Dashboard Development**

-----

<p align="center">
  <i>Built with Python & Streamlit · İzmir, 2026</i>
</p>
