# TV & Streaming Analytics — V2 Requirements

## Document Status

- Version: Draft 1
- Project phase: V2 design
- V1 status: Completed and merged into `main`
- Primary V2 dataset target: 250,000 ad-sales delivery records
- Historical period: January 2022 through June 2026
- Market scope: United States TV and streaming advertising

## 1. Purpose

V2 will extend the completed V1 analytical MVP into a more realistic, scalable and production-oriented data platform.

V1 validated the core analytical requirements, including:

- Business grain
- Power BI star schema
- Revenue and impression measures
- Effective CPM analysis
- YTD and prior-year comparisons
- Campaign under-delivery analysis
- Campaign-platform severity analysis
- Inventory and sell-through analysis
- Executive and diagnostic report design

V2 will retain the successful V1 analytical concepts while redesigning the source data, generation logic and processing architecture.

## 2. Confirmed V1 Findings

The V1 analysis produced the following business findings:

- Streaming generated more revenue despite delivering fewer impressions than Linear TV.
- Streaming maintained a materially higher effective CPM than Linear TV.
- Streaming revenue growth offset the decline in Linear TV revenue.
- Campaign delivery risk needed to be evaluated at the `Campaign_ID + Platform` grain.
- Network-level analysis was useful as a diagnostic breakdown but changed the grain of campaign-level calculations.
- Weighted ratios were required for sell-through and delivery metrics rather than averages of row-level percentages.
- Executive reporting and detailed diagnostic analysis should be separated into different report pages.

## 3. Confirmed V1 Limitations

The V1 dataset and model exposed the following limitations:

### 3.1 Limited historical depth

V1 contained only three years of data, with 2026 represented as January through June YTD. This limited long-term trend, seasonality and forecasting analysis.

### 3.2 Simplified network and platform structure

Each network or streaming service was associated with only one platform. The model did not represent parent media brands operating both Linear TV and Streaming properties.

### 3.3 Limited cross-platform campaign complexity

Campaigns could be analyzed by platform, but the source structure did not explicitly model campaign placements, budget allocation or booked-impression allocation across multiple media properties.

### 3.4 Flat sell-through behavior

Sell-through remained narrowly concentrated around 96% across advertiser industries, genres, platforms and dayparts.

This indicated that V1 varied inventory volume but did not sufficiently model independent supply-and-demand behavior.

### 3.5 Limited market evolution

Streaming and Linear TV CPM values were structurally different but remained nearly flat across years. The data did not adequately represent:

- Streaming adoption growth
- Shifting advertiser budgets
- Changing platform revenue share
- Event-driven demand
- Seasonal pricing pressure
- Media-property scarcity
- Device-mix changes

### 3.6 Source data was already highly curated

The V1 dataset contained relatively clean analytical records. It did not provide enough opportunity to demonstrate:

- Bronze-layer ingestion
- Silver-layer standardization
- Data-quality quarantine
- Surrogate-key creation
- Many-to-many relationship resolution
- Incremental processing
- Gold-layer dimensional modeling

## 4. V2 Design Objectives

V2 must:

1. Generate realistic synthetic source-system data calibrated to public U.S. media-industry trends.
2. Support five years of historical analysis from January 2022 through June 2026.
3. Generate 250,000 primary ad-sales delivery records.
4. Allow the same generator to create smaller development samples and larger scale-test datasets.
5. Represent parent media brands with both Linear TV and Streaming properties.
6. Support campaigns placed across multiple media properties and platforms.
7. Model inventory supply and advertiser demand independently.
8. Produce meaningful variation in sell-through, CPM, revenue and delivery risk.
9. Preserve realistic correlations without making the data mechanically predictable.
10. Create raw source tables suitable for Fabric Bronze ingestion.
11. Transform raw records into validated Silver datasets.
12. Produce a clean Gold star schema for Power BI.
13. Support future forecasting, machine learning and RAG-based analytical extensions.
14. Document every major business assumption and validation rule.
15. Preserve reproducibility through configurable parameters and a fixed random seed.

## 5. Dataset Scale Strategy

The generator will support three dataset sizes:

| Dataset tier | Approximate rows | Purpose |
|---|---:|---|
| Development sample | 50,000 | GitHub sample, testing and rapid iteration |
| Primary portfolio dataset | 250,000 | Power BI, Fabric, SQL and ML development |
| Scale-test dataset | 1,000,000 | Optional Fabric and Databricks performance testing |

The GitHub repository will contain the generator, documentation and a manageable sample. Large generated datasets will not be committed directly to Git.

## 6. V2 Source-System Tables

V2 will generate multiple source tables rather than one fully curated analytical CSV.

### 6.1 Media Brands

File:

`media_brands.csv`

Grain:

One row per parent media brand.

Example attributes:

- `Media_Brand_ID`
- `Media_Brand_Name`
- `Ownership_Type`
- `Headquarters_Region`
- `Active_From_Date`
- `Active_To_Date`

A media brand may own multiple Linear TV and Streaming properties.

### 6.2 Media Properties

File:

`media_properties.csv`

Grain:

One row per individual broadcast network, cable network, streaming service or FAST property.

Example attributes:

- `Media_Property_ID`
- `Media_Brand_ID`
- `Media_Property_Name`
- `Platform`
- `Distribution_Type`
- `Content_Tier`
- `Primary_Content_Type`
- `Ad_Sales_Model`
- `Launch_Date`
- `Active_Flag`

Each media property belongs to one platform, but a parent media brand may own properties across multiple platforms.

Example:

| Parent brand | Media property | Platform |
|---|---|---|
| Vista Media | Vista Broadcast | Linear TV |
| Vista Media | Vista+ | Streaming |

### 6.3 Advertisers

File:

`advertisers.csv`

Grain:

One row per advertiser.

Example attributes:

- `Advertiser_ID`
- `Advertiser_Name`
- `Advertiser_Industry`
- `Advertiser_Size`
- `Primary_Region`
- `Streaming_Adoption_Profile`
- `Active_From_Date`
- `Active_To_Date`

The streaming-adoption profile will influence how quickly an advertiser shifts budget from Linear TV to Streaming.

### 6.4 Campaigns

File:

`campaigns.csv`

Grain:

One row per advertising campaign.

Example attributes:

- `Campaign_ID`
- `Advertiser_ID`
- `Campaign_Name`
- `Campaign_Objective`
- `Start_Date`
- `End_Date`
- `Total_Budget`
- `Target_Impressions`
- `Target_Audience`
- `Campaign_Status`

A campaign may run across multiple platforms and media properties.

### 6.5 Campaign Placements

File:

`campaign_placements.csv`

Grain:

One row per `Campaign_ID + Media_Property_ID` placement.

Example attributes:

- `Campaign_Placement_ID`
- `Campaign_ID`
- `Media_Property_ID`
- `Allocated_Budget`
- `Budget_Allocation_Pct`
- `Booked_Impressions`
- `Placement_Start_Date`
- `Placement_End_Date`
- `Buying_Method`
- `Guaranteed_Flag`

This table resolves the many-to-many business relationship between campaigns and media properties.

### 6.6 Programs

File:

`programs.csv`

Grain:

One row per program or content title.

Example attributes:

- `Program_ID`
- `Program_Name`
- `Genre`
- `Content_Type`
- `Live_Flag`
- `Sports_Flag`
- `Premium_Content_Flag`

### 6.7 Program Distribution

File:

`program_distribution.csv`

Grain:

One row per `Program_ID + Media_Property_ID` combination.

Example attributes:

- `Program_Distribution_ID`
- `Program_ID`
- `Media_Property_ID`
- `Available_From_Date`
- `Available_To_Date`
- `Distribution_Window`
- `Exclusive_Flag`

This table represents programs distributed across multiple Linear TV and Streaming properties.

### 6.8 Daily Ad Delivery

File:

`ad_delivery_daily.csv`

Target size:

Approximately 250,000 rows for the primary portfolio dataset.

Grain:

One row per:

`Date + Campaign_Placement_ID + Program_ID + Region + Device_Type + Daypart`

Example measures and attributes:

- `Date`
- `Campaign_Placement_ID`
- `Program_ID`
- `Region`
- `Device_Type`
- `Daypart`
- `Booked_Impressions`
- `Delivered_Impressions`
- `CPM`
- `Gross_Revenue`
- `Agency_Fee_Pct`
- `Agency_Fee_Amount`
- `Net_Revenue`
- `Under_Delivery_Flag`

### 6.9 Daily Inventory

File:

`inventory_daily.csv`

Grain:

One row per:

`Date + Media_Property_ID + Program_ID + Region + Device_Type + Daypart`

Example measures:

- `Available_Inventory_Units`
- `Demand_Units`
- `Sold_Units`
- `Unsold_Units`
- `Sell_Through_Rate`
- `Demand_Index`
- `Inventory_Scarcity_Index`

Inventory will be stored separately from campaign delivery because the two processes operate at different business grains.

## 7. Business Grain Decisions

V2 will contain two principal analytical facts.

### 7.1 Ad Delivery Fact

Business process:

Campaign execution, impression delivery and advertising revenue.

Grain:

`Date + Campaign Placement + Program + Region + Device Type + Daypart`

Principal measures:

- Booked impressions
- Delivered impressions
- Impression shortfall
- Gross revenue
- Agency fee
- Net revenue

### 7.2 Inventory Fact

Business process:

Advertising inventory availability, demand and sales.

Grain:

`Date + Media Property + Program + Region + Device Type + Daypart`

Principal measures:

- Available inventory units
- Demand units
- Sold units
- Unsold units
- Sell-through rate
- Inventory scarcity

Inventory values must not be repeated across campaign-delivery records because that would cause double counting.

## 8. Many-to-Many Business Relationships

V2 will intentionally model realistic many-to-many business relationships in the source layer.

### Campaign to Media Property

- One campaign can run on many media properties.
- One media property can carry many campaigns.
- `campaign_placements` resolves this relationship.

### Program to Media Property

- One program may appear on multiple Linear TV and Streaming properties.
- One media property distributes many programs.
- `program_distribution` resolves this relationship.

The Gold Power BI model should avoid direct many-to-many relationships wherever a fact or bridge table can express the relationship clearly.

## 9. Dimensional-Modeling Principle

The raw source structure and the final analytical structure do not need to be identical.

- Bronze preserves the generated source tables.
- Silver validates and standardizes their relationships.
- Gold creates conformed dimensions, facts and any required bridges.
- Power BI consumes the Gold analytical model.

This separation allows V2 to demonstrate realistic source complexity without exposing unnecessary ambiguity to report users.

## 10. Market Calibration Approach

V2 is synthetic, but its direction and scale will be calibrated to publicly available U.S. television and digital-video advertising benchmarks.

The objective is not to reproduce any company’s proprietary data. Public benchmarks will establish reasonable market direction, while the generator creates fictional brands, properties, advertisers and campaigns.

### Public market anchors

- IAB reported that U.S. digital-video advertising spend increased 18% in 2024 to approximately $64 billion.
- IAB reported that CTV advertising spend increased from approximately $20.3 billion in 2023 to $23.6 billion in 2024.
- IAB projected approximately $26.6 billion in CTV advertising spend for 2025.
- Nielsen reported that Streaming represented 44.8% of U.S. television viewing in May 2025.
- Nielsen reported that Streaming reached 47.5% of television viewing in December 2025.
- IAB projected U.S. digital-video advertising spend to exceed $80 billion in 2026.

These benchmarks support a multi-year shift toward Streaming, while Linear TV remains important for live sports, news, major events and premium reach.

### Public sources

- IAB 2025 Digital Video Ad Spend Report:
  https://www.iab.com/news/ctv-rebounds-to-double-digit-growth-in-2024/

- Nielsen Streaming Milestone — May 2025:
  https://www.nielsen.com/news-center/2025/streaming-reaches-historic-tv-milestone-eclipses-combined-broadcast-and-cable-viewing-for-first-time/

- Nielsen Streaming Viewing Share — December 2025:
  https://www.nielsen.com/news-center/2026/streaming-shatters-multiple-records-in-december-2025-with-47-5-of-tv-viewing-according-to-nielsens-the-gauge/

- IAB 2026 Digital Video Outlook:
  https://www.iab.com/news/u-s-digital-video-ad-spend-to-surpass-80b-in-2026/

## 11. Yearly Platform Assumptions

The following values are synthetic modeling assumptions informed by public market direction. They are not presented as actual industry measurements.

| Year | Streaming share of delivery activity | Linear TV share | Streaming base CPM | Linear TV base CPM |
|---|---:|---:|---:|---:|
| 2022 | 35% | 65% | $27.00 | $24.00 |
| 2023 | 40% | 60% | $29.00 | $23.80 |
| 2024 | 46% | 54% | $31.00 | $23.50 |
| 2025 | 52% | 48% | $33.00 | $23.20 |
| 2026 YTD | 57% | 43% | $34.00 | $23.00 |

Actual generated values will vary by:

- Media property
- Content tier
- Program and genre
- Daypart
- Device
- Region
- Advertiser industry
- Buying method
- Season
- Event period
- Inventory scarcity

The distributions must overlap. Streaming should generally have a higher CPM, but not every Streaming record should cost more than every Linear TV record.

## 12. Supply-and-Demand Model

V2 will generate advertising inventory supply and advertiser demand as related but separate processes.

### 12.1 Inventory supply

Available inventory will be influenced by:

- Platform
- Media property
- Program duration
- Content type
- Daypart
- Region
- Device
- Day of week
- Season
- Live-event availability

### 12.2 Advertiser demand

Demand will be influenced by:

- Platform adoption by year
- Advertiser industry
- Campaign objective
- Audience targeting requirements
- Program genre
- Premium-content status
- Daypart
- Seasonality
- Major events
- Media-property reach
- Buying method

### 12.3 Demand index

The generator will calculate an internal demand index using weighted factors.

Conceptual logic:

`Demand Index = Base Demand × Platform Factor × Year Factor × Daypart Factor × Genre Factor × Seasonality Factor × Event Factor × Advertiser Factor × Random Variation`

The demand index will influence both sell-through and CPM pressure.

### 12.4 Sold units

Conceptual logic:

`Sold Units = Minimum of Available Inventory Units and Demand Units`

### 12.5 Unsold units

Conceptual logic:

`Unsold Units = Available Inventory Units − Sold Units`

### 12.6 Sell-through rate

Conceptual logic:

`Sell-Through Rate = Sold Units ÷ Available Inventory Units`

Sell-through will be recalculated from aggregated Sold Units and Available Inventory Units. Row-level percentages must not be averaged.

### 12.7 Inventory scarcity

Conceptual logic:

`Inventory Scarcity Index = Demand Units ÷ Available Inventory Units`

Expected interpretation:

- Less than 0.70: excess inventory
- 0.70–0.90: balanced inventory
- 0.90–1.00: high utilization
- Greater than 1.00: demand exceeds available inventory

## 13. Expected Demand Patterns

V2 should create realistic but imperfect patterns.

### Platform

- Streaming demand increases across years.
- Linear TV demand gradually declines overall.
- Linear TV remains strong for live sports, news and major events.
- Streaming growth differs by advertiser industry.

### Daypart

- Prime time generally produces stronger demand and higher CPM.
- Early morning generally has more unsold inventory.
- Daytime demand varies by advertiser industry and content type.
- Late-night Streaming may outperform comparable Linear TV inventory.

### Genre and content

- Live sports and premium events produce high demand and scarcity.
- News demand increases around major political and breaking-news periods.
- Entertainment demand rises around major premieres.
- Kids and family content have distinct seasonal patterns.
- Standard library content generally has lower CPM than premium or live content.

### Advertiser industry

- Retail and CPG increase demand during holiday periods.
- Pharma demand remains relatively stable.
- Auto demand varies with product-launch and promotional cycles.
- Technology advertisers adopt Streaming earlier.
- Finance and telecom maintain cross-platform allocations.
- Political demand is concentrated around election periods.

### Seasonality

- Q4 generally has the strongest advertising demand.
- January may soften following holiday spending.
- Major sporting events create temporary demand spikes.
- Election periods create localized and time-bound Linear TV and Streaming demand.
- Summer behavior varies by content type and platform.

### Controlled variation

Generated trends must not be perfectly smooth.

The generator must include:

- Random variation around expected values
- Occasional platform reversals
- Media-property-specific performance
- Advertiser-specific behavior
- Outlier campaigns
- Temporary demand shocks
- Over- and under-performing programs

This variation prevents the dataset from becoming mechanically predictable.

## 14. Medallion Architecture Responsibilities

### 14.1 Bronze Layer

Purpose:

Preserve generated source-system data in its original form.

Responsibilities:

- Ingest all source files without business-level transformations
- Preserve source identifiers
- Add ingestion timestamp
- Add source-file name
- Add batch identifier
- Retain valid and invalid source records
- Support audit and replay

Bronze should not silently correct source-quality problems.

### 14.2 Silver Layer

Purpose:

Create validated, standardized and reusable business data.

Responsibilities:

- Standardize column names and data types
- Normalize platform and category values
- Remove exact duplicates
- Identify conflicting duplicates
- Validate required fields
- Validate campaign and placement dates
- Validate foreign-key references
- Validate campaign-allocation percentages
- Validate financial and impression calculations
- Quarantine invalid records
- Create standardized business keys
- Handle late-arriving reference records
- Produce reusable clean tables

### 14.3 Gold Layer

Purpose:

Provide business-ready analytical models.

Responsibilities:

- Create conformed dimensions
- Assign surrogate keys
- Create `FactAdDelivery`
- Create `FactInventory`
- Create required bridge tables
- Create reusable aggregate tables when justified
- Support Power BI semantic models
- Support Direct Lake or another appropriate Fabric connectivity mode
- Preserve documented business grain
- Expose certified analytical measures and attributes

## 15. Controlled Source-Quality Scenarios

V2 will intentionally introduce a small, documented amount of source-system complexity.

Potential scenarios:

- Exact duplicate delivery records
- Duplicate business keys with conflicting attributes
- Missing optional values
- Missing required values
- Unknown media-property references
- Unknown advertiser references
- Campaign placement outside the campaign date range
- Placement allocation percentages not totaling 100%
- Sold units exceeding inventory
- Delivered impressions outside acceptable tolerance
- Negative or zero CPM
- Invalid platform labels
- Inconsistent advertiser-industry spelling
- Late-arriving media properties
- Inactive properties receiving transactions

The generator must identify which scenarios were intentionally injected so Silver validation results can be reconciled.

Target quality-exception rate:

Approximately 0.5%–1.0% of applicable source records.

## 16. Data-Quality Handling

Each Silver validation rule should assign:

- `Validation_Status`
- `Validation_Rule_ID`
- `Validation_Message`
- `Quarantine_Flag`
- `Processing_Batch_ID`
- `Processed_Timestamp`

Records should be:

- Accepted
- Corrected through an approved mapping
- Quarantined for review
- Rejected when structurally unusable

No invalid record should disappear without an auditable outcome.

## 17. Reproducibility Requirements

The generator must support configurable parameters, including:

- Row count
- Start date
- End date
- Random seed
- Quality-exception rate
- Output directory
- Dataset tier
- Optional scale-test mode

The same parameters and random seed should reproduce the same dataset.

Example future command:

`python src/generate_v2_data.py --rows 250000 --seed 42 --quality-rate 0.0075`

The generator should also write a run manifest containing:

- Generator version
- Runtime timestamp
- Input parameters
- Random seed
- Output files
- Row counts
- Quality scenarios injected
- Validation summary

## 18. Validation and Reconciliation Requirements

The generator and transformation layers must produce auditable validation results.

### Structural validation

- Required files exist
- Required columns exist
- Column data types are valid
- Business keys are present
- Duplicate business keys are identified
- Date ranges are valid

### Referential-integrity validation

- Every media property references a valid media brand
- Every campaign references a valid advertiser
- Every campaign placement references a valid campaign and media property
- Every delivery record references a valid campaign placement and program
- Every inventory record references valid media-property and program combinations

### Financial validation

- CPM is non-negative
- Gross revenue is non-negative
- Net revenue is non-negative
- Agency fee amount reconciles to gross revenue and agency-fee percentage
- Net revenue reconciles to gross revenue less agency fee
- Allocated campaign budgets do not materially exceed total campaign budgets

### Impression validation

- Booked impressions are non-negative
- Delivered impressions are non-negative
- Impression shortfall is calculated consistently
- Under-delivery flags match the approved business threshold
- Campaign-platform calculations reconcile with transaction-level records

### Inventory validation

- Available inventory is non-negative
- Demand units are non-negative
- Sold units do not exceed available inventory
- Unsold units equal available inventory less sold units
- Sell-through rate is derived from aggregated sold and available units
- Scarcity classifications match the documented thresholds

### Allocation validation

Campaign-placement allocation percentages should total 100% within an approved tolerance.

Suggested tolerance:

`99.5%–100.5%`

Records outside the tolerance should be quarantined or flagged for review.

## 19. V2 Success Criteria

V2 will be considered successful when:

1. The generator creates reproducible datasets at 50,000, 250,000 and optional 1,000,000-row scales.
2. Five-year platform trends are visible without being perfectly smooth.
3. Streaming growth and Linear TV pressure are directionally consistent with documented market assumptions.
4. Sell-through varies meaningfully across platform, daypart, genre, season and advertiser industry.
5. CPM and sell-through share demand drivers without becoming mechanically identical.
6. Cross-platform campaigns allocate budget and impressions across multiple media properties.
7. Parent-brand analysis works across Linear TV and Streaming properties.
8. Bronze preserves all generated source records and batch metadata.
9. Silver identifies, corrects or quarantines documented quality scenarios.
10. Gold facts and dimensions reconcile to accepted Silver records.
11. Power BI measures reconcile with Python and SQL validation outputs.
12. V2 supports YTD, YoY, seasonality and multi-year trend analysis.
13. The primary 250,000-row model performs acceptably in Power BI and Fabric.
14. Project documentation clearly separates public benchmarks from synthetic assumptions.
15. The repository provides enough documentation for another developer to reproduce the dataset.

## 20. Out of Scope for Initial V2 Delivery

The following items are deferred until the core V2 pipeline and semantic model are stable:

- Real customer or proprietary advertising data
- Production deployment to external users
- Real-time streaming ingestion
- Full enterprise security implementation
- Advanced MLOps
- Automated model retraining
- RAG-based analytical assistant
- Agentic workflow automation
- Multi-cloud production deployment
- One-million-row optimization beyond initial scale testing

These capabilities may be added in later project phases.

## 21. Planned Implementation Phases

### Phase 1 — Requirements and source design

- Finalize business assumptions
- Finalize source tables and grain
- Define relationship rules
- Define data-quality scenarios
- Define validation expectations

### Phase 2 — Python generator

- Build reusable configuration
- Generate reference tables
- Generate campaigns and placements
- Generate inventory supply and demand
- Generate daily delivery transactions
- Inject controlled source-quality scenarios
- Produce run manifest and validation summary

### Phase 3 — Local validation

- Validate output with Python
- Reconcile row counts
- Reconcile financial measures
- Reconcile impressions
- Verify expected market trends
- Test the 50,000-row development dataset

### Phase 4 — Fabric Bronze and Silver

- Ingest raw source files into Bronze
- Add ingestion and batch metadata
- Standardize and validate Silver tables
- Create quarantine outputs
- Reconcile accepted, corrected and rejected records

### Phase 5 — Fabric Gold

- Create conformed dimensions
- Create `FactAdDelivery`
- Create `FactInventory`
- Create required bridges
- Assign surrogate keys
- Create analytical aggregates where justified

### Phase 6 — Power BI V2

- Connect to Gold
- Reuse validated V1 business measures
- Update measures for the V2 grains
- Add multi-year and cross-platform analysis
- Compare V1 and V2 findings
- Validate performance and usability

### Phase 7 — Advanced analytics

- Forecast revenue and demand
- Predict campaign under-delivery risk
- Evaluate feature importance
- Add ML model documentation
- Prepare curated analytical content for a future RAG assistant

## 22. Engineering Outcomes

The completed V2 solution should demonstrate:

- Clear translation of business requirements into data architecture
- Explicit business-grain definitions
- Appropriate separation of delivery and inventory facts
- Resolution of many-to-many business relationships
- Reusable conformed dimensions
- Reproducible synthetic-data generation
- Auditable data-quality controls
- Clear Bronze, Silver and Gold responsibilities
- Reconciliation across Python, SQL, Fabric and Power BI
- Scalable processing across multiple dataset sizes
- Documented architectural decisions and tradeoffs
- Traceability from V1 analytical findings to V2 design improvements