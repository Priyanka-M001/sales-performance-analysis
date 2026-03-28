import pandas as pd

# Load base dataset
df = pd.read_csv("raw_data.csv")

# Convert date
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)

# Remove duplicates only
print(df[df.duplicated()])

# Create Month_Year
df["Month_Year"] = df["Order Date"].dt.to_period("M")

# Monthly split (CORRECT NOW)
for month, data in df.groupby("Month_Year"):
    data.to_csv(f"data/sales_{month}.csv", index=False)

# KPIs
total_sales = df["Sales"].sum()
avg_order_value = df["Sales"].mean()
total_orders = df["Order ID"].nunique()

# Monthly sales
monthly_sales = df.groupby("Month_Year")["Sales"].sum().reset_index()
monthly_sales = monthly_sales.sort_values("Month_Year")
monthly_sales["MoM_Growth_%"] = (monthly_sales["Sales"].pct_change() * 100).round(1)

# Category analysis
category_sales = df.groupby("Category")["Sales"].sum().reset_index()
category_sales["Sales_%"] = (category_sales["Sales"] / total_sales * 100).round(1)

# Region analysis
region_sales = df.groupby("Region")["Sales"].sum().reset_index().sort_values("Sales", ascending=False)

# Alerts
def sales_flag(x):
    if pd.isna(x):
        return "Not Available"
    elif x <= -20:
        return "Drop Alert"
    elif x >= 20:
        return "Spike Alert"
    return "Normal"

monthly_sales["Sales_Status"] = monthly_sales["MoM_Growth_%"].apply(sales_flag)

# Category risk
category_monthly = df.groupby(["Month_Year", "Category"])["Sales"].sum().reset_index()
category_monthly["MoM_Growth_%"] = category_monthly.groupby("Category")["Sales"].pct_change() * 100

category_monthly["Risk_Flag"] = category_monthly["MoM_Growth_%"].apply(
    lambda x: "Not Available" if pd.isna(x) else ("Risk" if x <= -20 else "OK")
)

# Save outputs
df.to_csv(r"output\clean_superstore.csv", index=False)
monthly_sales.to_csv(r"output\monthly_sales.csv", index=False)
category_sales.to_csv(r"output\category_sales.csv", index=False)
region_sales.to_csv(r"output\region_sales.csv", index=False)
category_monthly.to_csv(r"output\category_risk.csv", index=False)

# Summary
latest = monthly_sales.iloc[-1]

summary = {
    "Month": str(latest["Month_Year"]),
    "Sales": round(latest["Sales"], 1),
    "Growth_%": latest["MoM_Growth_%"],
    "Status": latest["Sales_Status"]
}

print(summary)