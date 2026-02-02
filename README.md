## Forecasting Financial Inclusion in Ethiopia
A forecasting system that tracks Ethiopia's digital financial transformation using time series methods, built for the 10 Academy Week 10 Challenge.

## Project Overview
This project builds a forecasting system to predict Ethiopia's progress on two core dimensions of financial inclusion as defined by the World Bank's Global Findex:

Access  —  Account Ownership Rate
Usage — Digital Payment Adoption Rate
The system analyzes how events like product launches, policy changes, and infrastructure investments affect inclusion outcomes, and forecasts Access and Usage for 2025-2027.

## Project Structure
```ethiopia-fi-forecast/
├── .github/workflows/
│   └── unittests.yml          # CI/CD pipeline
├── data/
│   ├── raw/                   # Starter dataset
│   │   ├── ethiopia_fi_unified_data.csv
│   │   └── reference_codes.csv
│   └── processed/             # Analysis-ready data
│       └── ethiopia_fi_unified_data_enriched.csv
├── notebooks/
│   ├── 01_data_exploration_enrichment.ipynb
│   └── 02_exploratory_data_analysis.ipynb
├── src/                       # Source code modules
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── tests/                     # Unit tests
├── models/                    # Trained models
├── reports/
│   └── figures/               # Generated plots
├── requirements.txt           # Python dependencies
├── data_enrichment_log.md     # Documentation of data additions
├── r.md                       # Schema design documentation
├── ch.md                      # Challenge requirements
└── README.md   
```
Quick Start
1. Environment Setup
# Clone the repository
git clone <repository-url>
cd Forecasting-Financial-Inclusion-in-Ethiopia

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
2. Run Analysis Notebooks
# Start Jupyter
jupyter notebook

# Run notebooks in order:
# 1. notebooks/data_exploration_enrichment.ipynb
# 2. notebooks/exploratory_data_analysis.ipynb
3. Launch Dashboard
# Run Streamlit dashboard
streamlit run dashboard/app.py
Data Schema
The project uses a unified data schema where all records share the same structure. The record_type field indicates how to interpret each row:

## Record Type	Count	Description
observation	14	Measured values (Findex surveys, operator reports, infrastructure data)
event	8	Policies, product launches, market entries, milestones
impact_link	10	Modeled relationships between events and indicators
target	2	Official policy goals (e.g., NFIS-II targets)
Key Design Principle
Events are pillar-neutral: Events have category (policy, product_launch, etc.) but no pillar assignment. Their effects on specific indicators are captured through impact_link records, preventing biased modeling.

## Key Findings
🔍 The Inclusion Paradox
Account ownership growth decelerated to +3pp (2021-2024) despite massive mobile money expansion (65M+ accounts opened). This suggests market saturation, overlapping accounts, or barriers beyond infrastructure.

## 📱 Mobile Money Still Niche
Mobile money accounts represent only 9.45% of adults vs 49% overall account ownership. Traditional banking dominates.

## 🚀 Usage Explosion Among Users
P2P transactions grew from 8.5M to 15.2M monthly (+79% in 2 years), showing strong engagement among existing digital payment users.

## 🏗️ Infrastructure Ready, Barriers Elsewhere
85% 4G coverage and 120% mobile penetration indicate infrastructure isn't the constraint. Barriers likely include affordability, digital literacy, and trust.

### ⏰ Event Impacts Take Time
Events have measurable but delayed impacts, often 12-18 months (e.g., Telebirr launch in May 2021 preceded mobile money doubling by 2024).

## Tasks Completed
✅ Task 1: Data exploration and enrichment

Loaded and validated unified schema
Added 6 new records (observations, events, impact_links)
Documented all changes in data_enrichment_log.md
## ✅ Task 2: Exploratory Data Analysis

Coverage heatmap showing temporal gaps
Trend analysis for Access and Usage indicators
Event timeline overlays using impact_link joins
5+ key insights with supporting evidence
Data quality assessment
## 🔄 Task 3: Event Impact Modeling (Next)

## 🔄 Task 4: Forecasting Access and Usage (Next)

## 🔄 Task 5: Dashboard Development (Nex)