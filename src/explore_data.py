import pandas as pd

# Location of our raw advertising dataset
file_path = "data/raw/tv_streaming_ad_sales.csv"

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(file_path)

# Convert Date from text to a true datetime datatype
df["Date"] = pd.to_datetime(df["Date"])

print("Dataset loaded successfully!")

# Display dataset dimensions
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# Display the first 5 records
print("\nFirst 5 records:")
print(df.head())
# -----------------------------------------
# Basic Data Profiling
# -----------------------------------------

print("\n--- DATASET SHAPE ---")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DATE RANGE ---")
print("Start Date:", df["Date"].min())
print("End Date:", df["Date"].max())

print("\n--- DUPLICATE ROWS ---")
print("Duplicates:", df.duplicated().sum())

print("\n--- NUMERIC SUMMARY ---")
print(df[
    [
        "Booked_Impressions",
        "Delivered_Impressions",
        "Fill_Rate",
        "CPM",
        "Gross_Revenue",
        "Net_Revenue",
        "Inventory_Units",
        "Sold_Units"
    ]
].describe())

print("\n--- BUSINESS RULE VALIDATION ---")

# Negative financial values should not exist
print("Negative Gross Revenue:",
      (df["Gross_Revenue"] < 0).sum())

print("Negative Net Revenue:",
      (df["Net_Revenue"] < 0).sum())

print("Negative CPM:",
      (df["CPM"] < 0).sum())

# Sold inventory should not exceed available inventory
print("Sold Units > Inventory Units:",
      (df["Sold_Units"] > df["Inventory_Units"]).sum())

# Check delivery performance
print("Under 90% Delivery:",
      (df["Fill_Rate"] < 0.90).sum())

print("Over 100% Delivery:",
      (df["Fill_Rate"] > 1.00).sum())

# Check our under-delivery flag
print("\nUnder Delivery Flag Counts:")
print(df["Under_Delivery_Flag"].value_counts())

# Check platforms
print("\nPlatform Counts:")
print(df["Platform"].value_counts())