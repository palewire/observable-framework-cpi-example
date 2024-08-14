_This page is a demonstration of how to deploy an [Observable Framework](https://observablehq.com/framework) dashboard via GitHub Pages.

It recreates the main elements of the [latest PDF press release](https://www.bls.gov/news.release/pdf/cpi.pdf) of Consumer Price Index (CPI) data issued by the U.S. Bureau of Labor Statistics.

All of the code is available at [github.com/palewire/observable-framework-cpi-example](https://github.com/palewire/observable-framework-cpi-example), where you can find a step-by-step guide you can follow to create your own dashboard._

# Observable Framework CPI Example

An example of how to deploy an [Observable Framework](https://observablehq.com/framework) dashboard via GitHub Pages

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

Create a GitHub Actions workflow file in `.github/workflows/deploy.yaml`:

```yaml
name: "Build and Deploy"

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - id: checkout
        name: Checkout
        uses: actions/checkout@v4

      - id: setup-python
        name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pipenv'

      - id: install-pipenv
        name: Install pipenv
        run: curl https://raw.githubusercontent.com/pypa/pipenv/master/get-pipenv.py | python
        shell: bash

      - id: install-python-dependencies
        name: Install Python dependencies
        run: pipenv sync --dev
        shell: bash

      - id: setup-node
        name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20.11.0"
          cache: "npm"
          cache-dependency-path: package-lock.json

      - id: install-nodejs-dependencies
        name: Install Node.JS dependencies
        run: npm install --dev
        shell: bash

      - id: build
        name: Build
        run: pipenv run npm run build
        shell: bash

      - id: upload-release-candidate
        name: Upload release candidate
        uses: actions/upload-pages-artifact@v3
        with:
          path: "dist"
```

Next add a step to deploy the release candidate below the build step:

```yaml
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: build
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - id: deploy
        name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

Visit your repository's settings page. Click on the "Pages" tab. Select "GitHub Actions" from the Build and Deployment section's source dropdown.

Visit your repository's Actions tab. Click on the "Build and Deploy" workflow on the left-hand side. Click the "Run workflow" dropdown on the left-hand side. Click the green "Run workflow" button that appears.

A job should start soon after. Once it completes, your project should soon be available at `https://<username>.github.io/<repository>`.

In this case, my project is available at [palewire.github.io/observable-framework-cpi-example/](https://palewire.github.io/observable-framework-cpi-example/).