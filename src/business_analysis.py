import pandas as pd

file_path = "data/processed/tv_streaming_ad_sales_clean.csv"

df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"])

print("Business analysis dataset loaded.")
print("Rows:", len(df))

# -----------------------------------------
# Executive KPIs
# -----------------------------------------

total_gross_revenue = df["Gross_Revenue"].sum()

total_net_revenue = df["Net_Revenue"].sum()

total_booked_impressions = df["Booked_Impressions"].sum()

total_delivered_impressions = df["Delivered_Impressions"].sum()

overall_delivery_rate = (
    total_delivered_impressions
    / total_booked_impressions
)

total_inventory = df["Inventory_Units"].sum()

total_sold_units = df["Sold_Units"].sum()

inventory_sell_through = (
    total_sold_units
    / total_inventory
)

under_delivery_count = (
    df["Under_Delivery_Flag"] == "Y"
).sum()

print("\n--- EXECUTIVE KPIs ---")

print(f"Gross Revenue: ${total_gross_revenue:,.2f}")
print(f"Net Revenue: ${total_net_revenue:,.2f}")

print(
    f"Booked Impressions: "
    f"{total_booked_impressions:,.0f}"
)

print(
    f"Delivered Impressions: "
    f"{total_delivered_impressions:,.0f}"
)

print(
    f"Overall Delivery Rate: "
    f"{overall_delivery_rate:.2%}"
)

print(
    f"Inventory Sell-Through: "
    f"{inventory_sell_through:.2%}"
)

print(
    f"Under-Delivery Records: "
    f"{under_delivery_count:,}"
)

# -----------------------------------------
# Platform Performance
# -----------------------------------------

platform_performance = (
    df.groupby("Platform")
      .agg(
          Gross_Revenue=("Gross_Revenue", "sum"),
          Net_Revenue=("Net_Revenue", "sum"),
          Booked_Impressions=("Booked_Impressions", "sum"),
          Delivered_Impressions=("Delivered_Impressions", "sum"),
          Inventory_Units=("Inventory_Units", "sum"),
          Sold_Units=("Sold_Units", "sum")
      )
      .reset_index()
)

platform_performance["Delivery_Rate"] = (
    platform_performance["Delivered_Impressions"]
    / platform_performance["Booked_Impressions"]
)

platform_performance["Sell_Through_Rate"] = (
    platform_performance["Sold_Units"]
    / platform_performance["Inventory_Units"]
)

print("\n--- PLATFORM PERFORMANCE ---")
print(platform_performance)

# -----------------------------------------
# Platform Revenue Efficiency
# -----------------------------------------

platform_efficiency = (
    df.groupby("Platform")
      .agg(
          Net_Revenue=("Net_Revenue", "sum"),
          Delivered_Impressions=("Delivered_Impressions", "sum")
      )
      .reset_index()
)

platform_efficiency["Effective_CPM"] = (
    platform_efficiency["Net_Revenue"]
    / platform_efficiency["Delivered_Impressions"]
    * 1000
)

print("\n--- PLATFORM REVENUE EFFICIENCY ---")

print(
    platform_efficiency.to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format,
            "Delivered_Impressions": "{:,.0f}".format,
            "Effective_CPM": "${:,.2f}".format
        }
    )
)

# -----------------------------------------
# Platform Revenue & Impression Share
# -----------------------------------------

platform_share = (
    df.groupby("Platform")
      .agg(
          Net_Revenue=("Net_Revenue", "sum"),
          Delivered_Impressions=("Delivered_Impressions", "sum")
      )
      .reset_index()
)

platform_share["Revenue_Share"] = (
    platform_share["Net_Revenue"]
    / platform_share["Net_Revenue"].sum()
)

platform_share["Impression_Share"] = (
    platform_share["Delivered_Impressions"]
    / platform_share["Delivered_Impressions"].sum()
)

print("\n--- PLATFORM SHARE ---")

print(
    platform_share.to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format,
            "Delivered_Impressions": "{:,.0f}".format,
            "Revenue_Share": "{:.2%}".format,
            "Impression_Share": "{:.2%}".format
        }
    )
)

# -----------------------------------------
# Network Performance
# -----------------------------------------

network_performance = (
    df.groupby(["Platform", "Network"])
      .agg(
          Net_Revenue=("Net_Revenue", "sum"),
          Delivered_Impressions=("Delivered_Impressions", "sum")
      )
      .reset_index()
)

network_performance["Effective_CPM"] = (
    network_performance["Net_Revenue"]
    / network_performance["Delivered_Impressions"]
    * 1000
)

network_performance = (
    network_performance
    .sort_values("Net_Revenue", ascending=False)
)

print("\n--- NETWORK PERFORMANCE ---")

print(
    network_performance.to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format,
            "Delivered_Impressions": "{:,.0f}".format,
            "Effective_CPM": "${:,.2f}".format
        }
    )
)

# -----------------------------------------
# Yearly Platform Revenue
# -----------------------------------------

yearly_platform = (
    df.groupby(["Year", "Platform"])
      .agg(
          Net_Revenue=("Net_Revenue", "sum")
      )
      .reset_index()
)

print("\n--- YEARLY PLATFORM REVENUE ---")

print(
    yearly_platform.to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format
        }
    )
)

# -----------------------------------------
# Year-over-Year YTD Revenue
# Jan-Jun 2026 vs Jan-Jun 2025
# -----------------------------------------

ytd_data = df[
    (
        (df["Year"] == 2025) |
        (df["Year"] == 2026)
    )
    &
    (df["Date"].dt.month <= 6)
]

ytd_revenue = (
    ytd_data.groupby(["Year", "Platform"])
            .agg(
                Net_Revenue=("Net_Revenue", "sum")
            )
            .reset_index()
)

print("\n--- YTD REVENUE: JAN-JUN ---")

print(
    ytd_revenue.to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format
        }
    )
)

# -----------------------------------------
# YoY Growth by Platform
# -----------------------------------------

ytd_pivot = ytd_revenue.pivot(
    index="Platform",
    columns="Year",
    values="Net_Revenue"
)

ytd_pivot["YoY_Growth"] = (
    (ytd_pivot[2026] - ytd_pivot[2025])
    / ytd_pivot[2025]
)

print("\n--- YTD YOY GROWTH ---")

print(
    ytd_pivot.to_string(
        formatters={
            2025: "${:,.2f}".format,
            2026: "${:,.2f}".format,
            "YoY_Growth": "{:.2%}".format
        }
    )
)

# -----------------------------------------
# Overall YTD YoY Growth
# -----------------------------------------

company_ytd = (
    ytd_data.groupby("Year")["Net_Revenue"]
            .sum()
)

company_yoy = (
    (company_ytd[2026] - company_ytd[2025])
    / company_ytd[2025]
)

print("\n--- COMPANY YTD PERFORMANCE ---")

print(f"2025 Jan-Jun Revenue: ${company_ytd[2025]:,.2f}")
print(f"2026 Jan-Jun Revenue: ${company_ytd[2026]:,.2f}")
print(f"YoY Growth: {company_yoy:.2%}")

# -----------------------------------------
# Monthly Revenue Trend
# -----------------------------------------

df["Year_Month"] = (
    df["Date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

monthly_revenue = (
    df.groupby(["Year_Month", "Platform"])
      .agg(
          Net_Revenue=("Net_Revenue", "sum")
      )
      .reset_index()
)

print("\n--- MONTHLY REVENUE TREND ---")

print(
    monthly_revenue.tail(12).to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format
        }
    )
)

# -----------------------------------------
# Monthly YTD Comparison
# -----------------------------------------

monthly_ytd = df[
    (df["Year"].isin([2025, 2026]))
    &
    (df["Date"].dt.month <= 6)
]

monthly_ytd = (
    monthly_ytd.groupby(
        ["Year", "Month", "Platform"]
    )
    .agg(
        Net_Revenue=("Net_Revenue", "sum")
    )
    .reset_index()
)

month_order = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6
}

monthly_ytd["Month_Number"] = (
    monthly_ytd["Month"].map(month_order)
)

monthly_ytd = monthly_ytd.sort_values(
    ["Month_Number", "Platform", "Year"]
)

print("\n--- MONTHLY YTD COMPARISON ---")

print(
    monthly_ytd.to_string(
        index=False,
        formatters={
            "Net_Revenue": "${:,.2f}".format
        }
    )
)