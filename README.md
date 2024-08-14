# Observable Framework CPI Example

This is an example of [Observable Framework](https://observablehq.com/framework) project. 

```bash
npx @observablehq/framework@latest create
```

```bash
◇  Where should we create your project?
│  ./observable-framework-cpi-example
│
◇  What should we title your project?
│  Observable Framework CPI Example
│
◇  Include sample files to help you get started?
│  No, create an empty project
│
◇  Install dependencies?
│  Yes, via npm
│
◇  Initialize git repository?
│  Yes
```

```bash
cd ./observable-framework-cpi-example
```

```bash
pipenv install pandas cpi
```

Create a data loader for our first chart in `src/month-to-month.py`:

```python
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
```

Load it into our project in `src/index.md` with a fenced js block.

```js
const monthToMonth = await FileAttachment("month-to-month.json").json({typed: true}).then(data => {
  return data.map(d => {
    return {
      month: new Date(d.date),
      change: d.change
    }
  });
});
```

Use Observable Plot to add a simple bar chart that roughly matches what the BLS puts out.

```js
Plot.plot({
  title: "One-month percent change in CPI for All Urban Consumers (CPI-U), seasonally adjusted",
  marks: [
    Plot.barY(monthToMonth, {
        x: "month",
        y: "change",
        fill: "steelblue",
        tip: true
    })
  ],
  x: {label: null},
  y: {label: "Percent Change", tickFormat: d => `${d}%`}
})
```

```js
const latest = monthToMonth.at(-1);
```

```js
# Consumer Price Index – ${d3.utcFormat("%B %Y")(latest.month)}
```

```js
const latest = monthToMonth.at(-1);
const previous = monthToMonth.at(-2);
```

```js
The Consumer Price Index for All Urban Consumers (CPI-U) changed ${latest.change} percent on a seasonally
adjusted basis, after changing ${previous.change} percent in ${d3.utcFormat("%B")(previous.month)}, the U.S. Bureau of Labor Statistics reported today.
```

```js
const describe = (change) => {
  if (change > 0) {
    return `rose ${change} percent`;
  } else if (change < 0) {
    return `fell ${Math.abs(change)} percent`;
  } else {
    return "staying unchanged";
  }
}
```

```js
The Consumer Price Index for All Urban Consumers (CPI-U) ${describe(latest.change)} on a seasonally
adjusted basis, after ${describe(previous.change)} in ${d3.utcFormat("%B")(previous.month)}, the U.S. Bureau of Labor Statistics reported today.
```

```python
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

# Round the percentage change to one decimal place
df["change"] = df["change"].round(1)

# Output the results
df.to_json(sys.stdout, orient="records", date_format="iso")
```


```js
const yearOverYear = await FileAttachment("year-over-year.json").json({typed: true}).then(data => {
  return data.map(d => {
    return {
      month: new Date(d.date),
      change: d.change,
      series_items_name: d.series_items_name
    }
  });
});
```

```js
Plot.plot({
  title: " 12-month percent change in CPI for All Urban Consumers (CPI-U), not seasonally adjusted",
  marks: [
    Plot.line(yearOverYear, {
        x: "month",
        y: "change",
        stroke: "series_items_name",
    }),
    Plot.dot(yearOverYear, {x: "month", y: "change", fill: "series_items_name"})
  ],
  color: {legend: true},
  x: {label: null},
  y: {label: "Percent Change", tickFormat: d => `${d}%`, grid: true}
})
```

```js
const latestAllItems = yearOverYear.filter(d => d.series_items_name === "All items").at(-1);
const latestCore = yearOverYear.filter(d => d.series_items_name === "All items less food and energy").at(-1);
```

```js
Over the last 12 months, the all items index ${describe(latestAllItems.change)} before seasonal adjustment. The index for all items less food and energy ${describe(latestCore.change)}.
```
