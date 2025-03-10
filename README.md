# Poseidon US

**Poseidon US** is a Streamlit-based app that screens and analyzes US stocks based on technical indicators. It uses historical data stored in CSV files to calculate technical indicators (like the EMA 32) and then generates bullish, bearish, or neutral signals based on price behavior relative to the EMA. In addition, it offers a candlestick chart view for individual stocks with overlays for EMA 32.

## Features

- **Stock Screening:**  
  - Loads a list of US stocks from `pluang_us_stocks.csv`.
  - Reads individual stock data from CSV files in the `data` folder.
  - Calculates the EMA 32 using [pandas_ta](https://github.com/twopirllc/pandas-ta) and determines if a stock is bullish, bearish, or neutral.

- **Visual Analysis:**  
  - Displays stock badges for bullish, bearish, and neutral stocks.
  - Provides an interactive candlestick chart with EMA 32 overlay.
  - Uses Plotly for charting with a dark/light mode friendly design.

- **User Interface:**  
  - Sidebar menu with options for screening and viewing individual stocks.
  - Dynamic filtering and signal explanation for selected stocks.

## Prerequisites

- **Python 3.7+**