import sys

import cpi
import pandas as pd

def get_dataframe(**kwargs):
    # Get the data the user asks for
    df = cpi.series.get(**kwargs).to_dataframe()
    
    # Filter it down to monthly values
    df = df[df.period_type == "monthly"].copy()

    # Sort it by date
    df = df.sort_values("date")

    # Get the 12 month percent change
    df["change"] = df.value.pct_change(12) * 100

    # Slice it down to the last 13 months
    df = df.tail(13)

    # Return it
    return df

# Get the standard CPI-U series, but not seasonally adjusted
all_df = get_dataframe(seasonally_adjusted=False)

# Get the same series but for the 'core' CPI, which excludes food and energy
core_df = get_dataframe(
    items="All items less food and energy",
    seasonally_adjusted=False
)

# Concatenate the two series
df = pd.concat([all_df, core_df])

# Round the percentage change to one decimal place
df["change"] = df["change"].round(1)

# Output the results
df.to_json(sys.stdout, orient="records", date_format="iso")