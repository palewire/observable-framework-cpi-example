import sys

import cpi
import pandas as pd

# Get the standard CPI-U series, but not seasonally adjusted
all_df = cpi.series.get(seasonally_adjusted=False).to_dataframe()

# Filter it down to monthly values
all_df = all_df[all_df.period_type == "monthly"].copy()

# Sort it by date
all_df = all_df.sort_values("date")

# Get the 12 month percent change
all_df["change"] = all_df.value.pct_change(12) * 100

# Slice it down to the last 13 months
all_df = all_df.tail(13)

# Get the same series but for the 'core' CPI, which excludes food and energy
core_df = cpi.series.get(
    items="All items less food and energy",
    seasonally_adjusted=False
).to_dataframe()

# Filter it down to monthly values
core_df = core_df[core_df.period_type == "monthly"].copy()

# Sort it by date
core_df = core_df.sort_values("date")

# Get the 12 month percent change
core_df["change"] = core_df.value.pct_change(12) * 100

# Slice it down to the last 13 months
core_df = core_df.tail(13)

# Concatenate the two series
df = pd.concat([all_df, core_df])

# Round the percentage change to two decimal places
df["change"] = df["change"].round(1)

# Output the results
df.to_json(sys.stdout, orient="records", date_format="iso")