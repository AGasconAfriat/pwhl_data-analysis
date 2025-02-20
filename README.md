# pwhl_data-analysis

## Introduction

## Project Overview

Analysing data from the PWHL

## Files

### Files Showing the Development Process

* `skater_stats_to_csv.ipynb`: A notebook showing how to create a dataset from PWHL skater statistics and save it as a CSV file.
* `skater_stats.csv`: A sample CSV file containing PWHL skater statistics.
* `visualizations.ipynb`: A notebook showing how to create different types of visualizations based on skater statistics.

### Files To Run the Dashboard

* `step1_get_stats.py`: A script to scrape the data and save it into a CSV file.
* `full_stats.csv`: A CSV file generated using `step1_get_stats.py`.
* `step2_run_dashboard.py`: A script to run the interactive dashboard.

## Script Dependencies

To run the scripts (`.py` files), you need certain packages installed. For example, I had to run the following commands in command line/terminal before the scripts.

```
pip install setuptools
python -m pip install packaging
python -m pip install pandas dash
pip install httpx==0.20 dash plotly
```

An easy way to see if you are lacking anything is to try to run the script, then install the appropriate package if you get an error message about missing dependencies.