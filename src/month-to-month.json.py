import sys

import cpi

# Get the standard CPI-U series, seasonally adjusted
df = cpi.series.get(seasonally_adjusted=True).to_dataframe()

# Filter it down to monthly values
df = df[df.period_type == "monthly"].copy()

# Sort it by date
df = df.sort_values("date")

# Cut it down to the last 13 months, plus one
df = df.tail(13 + 1)

# Calculate the percentage change and round it to one decimal place, as the BLS does
df["change"] = (df.value.pct_change() * 100).round(1)

# Drop the first value
df = df.iloc[1:]

# Output the results
df.to_json(sys.stdout, orient="records", date_format="iso")