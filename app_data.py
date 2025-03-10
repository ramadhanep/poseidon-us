import os
import pandas as pd
import requests
import time
import random

# Konfigurasi
DATA_DIR = "data"
SYMBOLS_FILE = "pluang_us_stocks.csv"
START_DATE = "2023-01-01"

# Buat folder data jika belum ada
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Load daftar saham dari CSV
df_symbols = pd.read_csv(SYMBOLS_FILE)
symbols = df_symbols["symbol"].tolist()

# Headers untuk bypass bot detection (User-Agent Spoofing)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Fungsi untuk scraping data Yahoo Finance langsung dari JSON API
def fetch_stock_data(symbol):
    """Scrape data saham dari Yahoo Finance & simpan ke CSV."""
    file_path = os.path.join(DATA_DIR, f"{symbol}.csv")

    # Cek apakah file sudah ada (update incremental)
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)

        if "Date" in df_existing.columns and not df_existing.empty:
            df_existing["Date"] = pd.to_datetime(df_existing["Date"], errors="coerce")
            last_date = df_existing["Date"].max()

            if pd.isna(last_date):  
                start_date = START_DATE
            else:
                start_date = (last_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            start_date = START_DATE
    else:
        start_date = START_DATE

    print(f"🔄 Menarik data untuk {symbol} dari {start_date}...")

    # Scraping dari Yahoo Finance
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1y"
    
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        # Ambil OHLCV dari response JSON
        if "chart" in data and "result" in data["chart"]:
            result = data["chart"]["result"][0]
            timestamps = result["timestamp"]
            ohlcv = result["indicators"]["quote"][0]

            # Konversi ke DataFrame
            df_new = pd.DataFrame({
                "Date": pd.to_datetime(timestamps, unit="s"),
                "Open": ohlcv["open"],
                "High": ohlcv["high"],
                "Low": ohlcv["low"],
                "Close": ohlcv["close"],
                "Volume": ohlcv["volume"]
            })

            # Simpan atau update file CSV
            if os.path.exists(file_path) and not df_existing.empty:
                df_new = pd.concat([df_existing, df_new], ignore_index=True)

            df_new.to_csv(file_path, index=False)
            print(f"✅ Data {symbol} tersimpan ke {file_path}")

        else:
            print(f"❌ Gagal mengambil data {symbol}: Response tidak valid.")

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")

# **Langsung Fetch Data Tanpa Batching**
for symbol in symbols:
    fetch_stock_data(symbol)

print("✅ Semua data telah diperbarui.")

