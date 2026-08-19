import pandas as pd

# -----------------------------------------
# 1. Load raw data
# -----------------------------------------

input_file = "data/raw/tv_streaming_ad_sales.csv"
output_file = "data/processed/tv_streaming_ad_sales_clean.csv"

df = pd.read_csv(input_file)

print("Raw records:", len(df))


# -----------------------------------------
# 2. Convert data types
# -----------------------------------------

df["Date"] = pd.to_datetime(df["Date"])


# -----------------------------------------
# 3. Remove exact duplicate records
# -----------------------------------------

before = len(df)

df = df.drop_duplicates()

after = len(df)

print("Duplicates removed:", before - after)


# -----------------------------------------
# 4. Create calculated business fields
# -----------------------------------------

df["Delivery_Rate"] = (
    df["Delivered_Impressions"]
    / df["Booked_Impressions"]
)

df["Agency_Fee_Amount"] = (
    df["Gross_Revenue"]
    * df["Agency_Fee_Pct"]
)

df["Unsold_Units"] = (
    df["Inventory_Units"]
    - df["Sold_Units"]
)


# -----------------------------------------
# 5. Validate business rules
# -----------------------------------------

assert (df["Gross_Revenue"] >= 0).all()
assert (df["Net_Revenue"] >= 0).all()
assert (df["CPM"] >= 0).all()
assert (df["Sold_Units"] <= df["Inventory_Units"]).all()


# -----------------------------------------
# 6. Save processed dataset
# -----------------------------------------

df.to_csv(output_file, index=False)

print("Processed records:", len(df))
print("Processed file created successfully.")