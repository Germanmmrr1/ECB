import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# 1. Load your CSV file (change filename if needed)
df = pd.read_csv("ecb_data.csv")

# 2. Clean up whitespace/case in Item and Time columns (prevents invisible mismatches)
df["Item"] = df["Item"].str.strip()
df["Time"] = df["Time"].astype(str).str.strip()

# 3. Keep only the last Value for each (Item, Time) combination if duplicates exist
df = df.sort_values(["Item", "Time"])  # so the last value is kept
df_unique = df.drop_duplicates(subset=["Item", "Time"], keep="last")

# 4. Pivot the DataFrame: Items as rows, Dates as columns, Values as content
pivot = df_unique.pivot(index="Item", columns="Time", values="Value")

# 5. Optionally, sort columns chronologically
pivot = pivot.reindex(sorted(pivot.columns), axis=1)

# 6. Save or inspect result
pivot.to_csv("pivoted_ecb_items.csv")


# Replace NaN with 0 for the test
pivot_clean = pivot.dropna(thresh=100)
zeroed = pivot_clean.fillna(0)

# Calculate the proportion of zeros per row
zero_fraction = (zeroed == 0).sum(axis=1) / zeroed.shape[1]

# Keep only items where less than 90% of columns are zero
pivot_clean = pivot_clean[zero_fraction < 0.9]
pivot_clean.to_csv("pivoted_ecb_items_clean.csv")


# List of relevant item names
items_to_plot = [
    'Lending to euro area credit institutions related to monetary policy operations denominated in euro',
    'Securities held for monetary policy purposes',
    'Securities of euro area residents denominated in euro',
    'Liabilities to euro area credit institutions related to monetary policy operations denominated in euro',
    'Banknotes in circulation',
    'Deposit facility',
    'Current accounts'
]

traducciones = {
    'Lending to euro area credit institutions related to monetary policy operations denominated in euro': "Préstamos a bancos de la zona euro por operaciones de política monetaria (en euros)",
    'Securities held for monetary policy purposes': "Valores mantenidos con fines de política monetaria",
    'Securities of euro area residents denominated in euro': "Valores de residentes en la zona euro denominados en euros",
    'Liabilities to euro area credit institutions related to monetary policy operations denominated in euro': "Pasivos frente a bancos de la zona euro por operaciones de política monetaria (en euros)",
    'Banknotes in circulation': "Billetes en circulación",
    'Deposit facility': "Facilidad de depósito",
    'Current accounts': "Cuentas corrientes"
}

# Check available items in your cleaned data
print("Items present for analysis:")
print([item for item in items_to_plot if item in pivot_clean.index])

# Plot each key variable
for item in items_to_plot:
    if item in pivot_clean.index:
        plt.figure(figsize=(12, 5))
        pivot_clean.loc[item].T.astype(float).plot()
        plt.title(f"{traducciones.get(item, item)} (Fuente: BCE)", fontsize=15)
        plt.xlabel("Fecha")
        plt.ylabel("Millones de euros")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        print(f"Not found in data: {item}")

# Calculate and print key metrics (growth, std deviation)
for item in items_to_plot:
    if item in pivot_clean.index:
        data = pivot_clean.loc[item].astype(float)
        first_date = data.first_valid_index()
        last_date = data.last_valid_index()
        first_value = data[first_date]
        last_value = data[last_date]
        growth = (last_value - first_value) / first_value * 100 if first_value != 0 else float('nan')
        std_dev = data.std()
        print(f"\n{item}:")
        print(f"  Start ({first_date}): {first_value:,.2f}")
        print(f"  End   ({last_date}): {last_value:,.2f}")
        print(f"  Growth: {growth:.2f}%")
        print(f"  Standard deviation: {std_dev:,.2f}")

# Correlation analysis
df_vars = pivot_clean.loc[[item for item in items_to_plot if item in pivot_clean.index]].T.astype(float)
print("\nCorrelation matrix:")
print(df_vars.corr())

# Example ratio plot: Bank reserves / Banknotes
if (
    'Liabilities to euro area credit institutions related to monetary policy operations denominated in euro' in pivot_clean.index and
    'Banknotes in circulation' in pivot_clean.index
):
    reserves = pivot_clean.loc['Liabilities to euro area credit institutions related to monetary policy operations denominated in euro'].astype(float)
    cash = pivot_clean.loc['Banknotes in circulation'].astype(float)
    ratio = reserves / cash
    plt.figure(figsize=(12, 5))
    ratio.plot()
    plt.title("Ratio: Bank Reserves / Banknotes in Circulation")
    plt.xlabel("Date")
    plt.ylabel("Ratio")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
