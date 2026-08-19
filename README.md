# TV & Streaming AI Analytics Platform

End-to-end TV and streaming advertising analytics project focused on modern BI, data engineering, cloud analytics, machine learning, and AI-assisted analytics.

## Project Objective

Build an enterprise-style analytics platform to analyze advertising revenue, inventory, and delivery performance across Linear TV and Streaming.

The project will demonstrate:

- Python and Pandas analytics
- SQL and dimensional modeling
- Power BI semantic modeling and dashboards
- Microsoft Fabric and OneLake
- Lakehouse and Medallion architecture
- PySpark and Delta Lake
- Databricks
- Machine learning and revenue forecasting
- RAG / Generative AI analytics
- Security, governance, monitoring, and CI/CD

## Dataset

Synthetic TV and Streaming advertising dataset containing approximately 25,000 commercial-delivery records covering 2024 through June 2026.

Key data includes:

- Linear TV and Streaming
- Networks and programs
- Advertisers and industries
- Regions and devices
- Booked and delivered impressions
- CPM
- Gross and net revenue
- Inventory and sold units
- Delivery performance

## Current Progress

### Phase 1 - Data Profiling and Preparation

Completed using Python and Pandas:

- Dataset profiling and schema validation
- Missing-value and duplicate checks
- Business-rule validation
- Date transformations
- Data-quality checks
- Processed analytics dataset

### Phase 2 - Business Analytics

Implemented analysis for:

- Gross and Net Revenue
- Booked and Delivered Impressions
- Delivery Rate
- Inventory Sell-Through
- Under-Delivery
- Platform and Network Performance
- Effective CPM
- Revenue and Impression Share
- YTD and YoY Revenue
- Monthly Revenue Trends

## Key Findings

- Net Revenue: approximately $508.7M
- Overall Delivery Rate: approximately 97.4%
- Inventory Sell-Through: approximately 96.0%
- Streaming generates approximately 51.6% of Net Revenue from 42.7% of delivered impressions
- Streaming Effective CPM: approximately $32.89
- Linear TV Effective CPM: approximately $23.01
- 2026 YTD company revenue growth: approximately 0.7%
- Streaming 2026 YTD revenue growth: approximately 4.2%
- Linear TV 2026 YTD revenue growth: approximately -2.9%

## Current Architecture

```text
Raw Advertising Data
        |
        v
Python / Pandas
        |
        v
Data Profiling & Validation
        |
        v
Business Analytics
        |
        v
Processed Dataset
        |
        v
Power BI
```

## Target Architecture

```text
Source Systems
       |
       v
Fabric Data Factory
       |
       v
OneLake
       |
       v
Bronze
       |
       v
PySpark / Delta Lake
       |
       v
Silver
       |
       v
SQL / Transformations
       |
       v
Gold Dimensional Model
       |
       v
Semantic Model / Direct Lake
       |
       v
Power BI
       |
       +------------------+
       |                  |
       v                  v
ML Forecasting       RAG / GenAI
```

## Technology Stack

**Current:** Python, Pandas, Git, GitHub, SQL, Power BI

**Planned:** Microsoft Fabric, OneLake, Lakehouse, PySpark, Delta Lake, Direct Lake, Databricks, Azure, ML, RAG/GenAI, CI/CD, Security and Governance

## Next Phase

Power BI semantic modeling and executive dashboard development, including:

- Star schema
- Fact and dimension tables
- Date dimension
- Relationships
- DAX measures
- Time intelligence
- RLS
- Performance optimization

The project will then migrate into Microsoft Fabric using an enterprise-style Bronze, Silver, and Gold Lakehouse architecture.