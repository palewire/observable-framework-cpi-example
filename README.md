# Observable Framework CPI Example

A demonstration of how to deploy an [Observable Framework](https://observablehq.com/framework) dashboard via [GitHub Pages](https://pages.github.com/).

It recreates the main elements of the [latest press release](https://www.bls.gov/news.release/pdf/cpi.pdf) of Consumer Price Index data issued by the U.S. Bureau of Labor Statistics. You can see the published page at [palewire.github.io/observable-framework-cpi-example/](https://palewire.github.io/observable-framework-cpi-example/).

Follow the brief tutorial below to learn how it was created, and how you can publish a dashboard of your own.

## Table of Contents

* [Requirements](#requirements)
* [Create a new project](#create-a-new-project)
* [Load data with Python](#load-data-with-python)
* [Create a chart](#create-a-chart)
* [Template the data into text](#template-the-data-into-text)
* [Once more, with feeling](#once-more-with-feeling)
* [Deploy with GitHub Pages](#deploy-with-github-pages)

## Requirements

* [Node.js](https://nodejs.org/en/)
* [Python](https://www.python.org/)
* [Pipenv](https://pipenv.pypa.io/en/latest/)

## Create a new project

The first step is to open your terminal and use Node.JS to create a new project with the Observable Framework's `create` command.

```bash
npx @observablehq/framework@latest create
```

You will be prompted to answer a few questions about your project. Here's how I approached it. The key thing I'd recommend is that you choose to start with an empty project. Otherwise you'll have to delete a lot of example files. You'll also want to make a git repostitory.

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

Navigate into the project directory that was created:

```bash
cd ./observable-framework-cpi-example
```

## Load data with Python

We're going to use Python to load the data we need for our dashboard. We'll use the [`cpi`](https://palewi.re/docs/cpi/) library to get the Consumer Price Index data we need. It will be installed in a virtual environment with `pipenv`, along with the [`pandas`](https://pandas.pydata.org/) library for data manipulation.

```bash
pipenv install pandas cpi
```

Now you have all the dependencies you need. In your terminal start up the Observable test server inside the Python environment.

```bash
pipenv run npm run dev
```

That will start a local server at `http://localhost:3000/` where you can see your project take shape as you add code.

Create a data loader for our first chart in `src/month-to-month.py`:

```python
# Import the system module so we can write the data to stdout, a technique recommended by Observable
import sys

# Import the cpi module so we can get the data we need
import cpi

# Get the standard CPI-U series, seasonally adjusted, so we can compare it month-to-month
df = cpi.series.get(seasonally_adjusted=True).to_dataframe()

# Filter it down to monthly values, excluding annual averages
df = df[df.period_type == "monthly"].copy()

# Sort it by date so we can calculate the percentage change
df = df.sort_values("date")

# Cut it down to the last 13 months, plus one, so we can cover the same time range as the BLS's PDF chart
df = df.tail(13 + 1)

# Calculate the percentage change and round it to one decimal place, as the BLS does
df["change"] = (df.value.pct_change() * 100).round(1)

# Drop the first value, which is the 14th month we only needed for the calculation
df = df.iloc[1:]

# Output the results to stdout in JSON format
df.to_json(sys.stdout, orient="records", date_format="iso")
```

## Create a chart

Now open up the `src/index.md` that lays out your page. Clear out everything there and load the data inside a fenced JavaScript code block:

``````md
```js
const monthToMonth = await FileAttachment("month-to-month.json").json({typed: true}).then(data => {
  // Loop through the data and return a polished up, trimmed down version
  return data.map(d => {
    return {
      month: new Date(d.date),
      change: d.change
    }
  });
});
```
``````

Use [Observable Plot](https://observablehq.com/plot/) to add a simple bar chart that roughly matches what the BLS puts out. If your test server is running, it should appear on the page soon after you save.

``````md
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
``````

## Template the data into text

Pull out the last record from the data array into another fenced code block:

``````md
```js
const latest = monthToMonth.at(-1);
```
``````

Fit it into a headline that matches the BLS press release using a [template literal](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals) and [d3's formatting tool](https://d3js.org/d3-time-format):

```md
# Consumer Price Index – ${d3.utcFormat("%B %Y")(latest.month)}
```

To compare it with the previous month, add another line of code that pulls out the previous month's value.

``````md
```js
const latest = monthToMonth.at(-1);
const previous = monthToMonth.at(-2);
```
``````

Now fit that into the same sentence the BLS uses to lead its press release:

```md
The Consumer Price Index for All Urban Consumers (CPI-U) changed ${latest.change} percent on a seasonally
adjusted basis, after changing ${previous.change} percent in ${d3.utcFormat("%B")(previous.month)}, the U.S. Bureau of Labor Statistics reported today.
```

Get more descriptive with the changes by adding a function that describes them:

``````md
```js
const latest = monthToMonth.at(-1);
const previous = monthToMonth.at(-2);

const describe = (change) => {
  if (change > 0) {
    return `rose ${change} percent`;
  } else if (change < 0) {
    return `fell ${Math.abs(change)} percent`;
  } else {
    return "stayed unchanged";
  }
}
```
``````

Which can be put to use by editing the sentence to read:

```md
The Consumer Price Index for All Urban Consumers (CPI-U) ${describe(latest.change)} on a seasonally
adjusted basis, after it ${describe(previous.change)} in ${d3.utcFormat("%B")(previous.month)}, the U.S. Bureau of Labor Statistics reported today.
```

## Once more, with feeling

To get a little more practice, let's add a second chart that shows the year-over-year change in the Consumer Price Index. That's what the media is referring to when they talk about the inflation rate.

Create a new Python file at `src/year-over-year.py` where we'll calculate the statistics we need:

```python
import sys

import cpi
import pandas as pd  # This time we'll need to import pandas


# Define a function that does the math ...
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

# Using our function to get the standard CPI-U series, but not seasonally adjusted
all_df = get_dataframe(seasonally_adjusted=False)

# Get the same series but for the 'core' CPI, which excludes food and energy
# This series has historically been less volatile than the overall index, 
# so some experts see it as a better measure of inflation.
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

Now go back to `src/index.md` and load the new data:

``````md
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
``````

Add another Plot with each of our two data series as a line on the same chart:

``````md
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
``````

Pull out the latest value for each series:

``````md
```js
const latestAllItems = yearOverYear.filter(d => d.series_items_name === "All items").at(-1);
const latestCore = yearOverYear.filter(d => d.series_items_name === "All items less food and energy").at(-1);
```
``````

Fit that into a similar sentence to the first chart:

```md
Over the last 12 months, the all items index ${describe(latestAllItems.change)} before seasonal adjustment. The index for all items less food and energy ${describe(latestCore.change)}.
```

Boom. You've got a simple dashboard that's ready to deploy.

## Deploy with GitHub Pages

Create a [GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) workflow file in `.github/workflows/deploy.yaml`. Start by adding a step to build the project once a day:

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

Next add a step at the bottom to deploy the release candidate:

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

Commit all of your work with git. Go to GitHub and create a new repository. Link it to your local repository. Push your work to GitHub.

Visit your repository's settings page. Click on the "Pages" tab. Select "GitHub Actions" from the Build and Deployment section's source dropdown. This will enable GitHub Pages for your repository.

Visit your repository's Actions tab. Click on the "Build and Deploy" workflow on the left-hand side. Click the "Run workflow" dropdown on the left-hand side. Click the green "Run workflow" button that appears.

A job should start soon after. Once it completes, your project should soon be available at `https://<username>.github.io/<repository-name>`.

In this case, my project is available at [palewire.github.io/observable-framework-cpi-example/](https://palewire.github.io/observable-framework-cpi-example/).

That's it! You've deployed an Observable Framework dashboard via GitHub Pages. 🎉

If you want to see the finished code in one place, check out the files in this repository's `src` directory.