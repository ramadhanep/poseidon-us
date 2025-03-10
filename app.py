import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from datetime import datetime
import os

# Konfigurasi halaman wide
st.set_page_config(page_title="Poseidon US", layout="wide")

# Load daftar saham
SYMBOLS_FILE = "pluang_us_stocks.csv"
DATA_DIR = "data"
screening_files = ["0.csv", "1.csv", "2.csv"]
df_symbols = pd.read_csv(SYMBOLS_FILE)
symbols = df_symbols["symbol"].tolist()

# Fungsi untuk mengambil data saham dari file CSV
def fetch_stock_data(symbol):
    file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date")  # Sort biar nggak anomali
        return df
    else:
        return pd.DataFrame()

# Fungsi untuk menghitung indikator teknikal
def calculate_indicators(df):
    if df.empty:
        return df
    df = df.copy()
    df["EMA_32"] = ta.ema(df["Close"], 32)
    return df

# Fungsi untuk menentukan sinyal bullish/bearish/non-trending
def get_signal(df):
    if df.empty:
        return "Neutral", "#808080", "Data tidak tersedia"
    
    last_row = df.iloc[-1]
    signal = "Neutral"
    color = "#808080"  # Default abu-abu
    explanation = "Saham dalam kondisi sideways atau tidak memiliki momentum kuat."
    
    last_two_days = df.tail(2)
    breakout_condition = ((last_two_days["Close"] > last_two_days["EMA_32"]) & (last_two_days["Close"].shift(1) <= last_two_days["EMA_32"].shift(1))).any()
    
    if breakout_condition:
        signal = "Bullish"
        color = "#008000"  # Hijau lebih gelap
        explanation = "Harga telah breakout EMA 32 dalam 1-3 hari terakhir, menunjukkan momentum bullish. Volume dapat digunakan sebagai konfirmasi tambahan."
    elif last_row["Close"] < last_row["EMA_32"]:
        signal = "Bearish"
        color = "#FF0000"  # Merah
        explanation = "Harga breakdown di bawah EMA 32, menunjukkan potensi tren turun. Volume dapat digunakan sebagai konfirmasi tambahan."
    
    return signal, color, explanation

# Simpan hasil screening ke file CSV
def save_screening_results(filename, stocks):
    df = pd.DataFrame(stocks, columns=["symbol", "icon", "color", "explanation"])
    df.to_csv(os.path.join(DATA_DIR, filename), index=False)

# Sidebar Menu
st.sidebar.title("Poseidon US")
st.sidebar.markdown(
    f"© {datetime.now().year} Created by [Ramadhan](https://ramadhanep.com)",
    unsafe_allow_html=True
)
menu = st.sidebar.radio("Menu", ["🚀 Screening", "📊 View"])

if menu == "🚀 Screening":
    # Screening untuk saham bullish
    bullish_stocks = []
    bearish_stocks = []
    neutral_stocks = []
    
    for _, row in df_symbols.iterrows():
        symbol = row["symbol"]
        df = fetch_stock_data(symbol)
        df = calculate_indicators(df)
        signal, color, explanation = get_signal(df)
        
        if signal == "Bullish":
            bullish_stocks.append((symbol, row["icon"], color, explanation))
        elif signal == "Bearish":
            bearish_stocks.append((symbol, row["icon"], color, explanation))
        else:
            neutral_stocks.append((symbol, row["icon"], color, explanation))
    
    # Simpan hasil screening ke file CSV
    save_screening_results("0.csv", bullish_stocks)
    save_screening_results("1.csv", bearish_stocks)
    save_screening_results("2.csv", neutral_stocks)
    
    def display_stock_badges(title, stocks):
        st.markdown(f"### {title}", unsafe_allow_html=True)
        if stocks:
            st.markdown(
                "".join(
                    [
                        f'<span style="display:inline-block; border-bottom: 1px solid {color}; padding:10px; color:white; margin-right:10px; vertical-align:middle;"><img src="{icon}" width="20" style="vertical-align:middle;"> {symbol}</span>'
                        for symbol, icon, color, _ in stocks
                    ]
                ),
                unsafe_allow_html=True
            )
    
    display_stock_badges("🚀 Bullish Stocks", bullish_stocks)
    display_stock_badges("🔻 Bearish Stocks", bearish_stocks)
    display_stock_badges("⚖️ Neutral Stocks", neutral_stocks)

if menu == "📊 View":
    # Load daftar saham dari hasil screening yang sudah disimpan
    sorted_symbols = []
    for file in screening_files:
        file_path = os.path.join(DATA_DIR, file)
        if os.path.exists(file_path):
            df_screening = pd.read_csv(file_path)
            sorted_symbols.extend(df_screening["symbol"].tolist())
    
    # Dropdown saham dengan prioritas berdasarkan screening
    selected_stock = st.sidebar.selectbox("Pilih Saham", sorted_symbols)
    stock_info = df_symbols[df_symbols["symbol"] == selected_stock].iloc[0]
    df = fetch_stock_data(selected_stock)
    df = calculate_indicators(df)
    signal, color, explanation = get_signal(df)
    latest_price = df.iloc[-1]["Close"] if not df.empty else "N/A"
    
    # Tampilan informasi saham & sinyal
    st.markdown(f'## <img src="{stock_info["icon"]}" width="50" style="vertical-align:middle;"> {selected_stock} (${latest_price:,.2f})', unsafe_allow_html=True)
    st.markdown(f"### {stock_info['name']}", unsafe_allow_html=True)
    st.markdown(f'<span style="background-color:{color}; padding:5px; border-radius:5px; color:white; font-size:20px;">Signal: {signal}</span>', unsafe_allow_html=True)
    st.write(f"**Penjelasan:** {explanation}")
    
    # Plot Candlestick Chart
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Candlestick",
                increasing=dict(line=dict(color="#00d7da"), fillcolor="#00d7da"),
                decreasing=dict(line=dict(color="#f9f9f9"), fillcolor="#f9f9f9")
            ),
            go.Scatter(
                x=df['Date'],
                y=df["EMA_32"],
                mode='lines',
                line=dict(color='#00d7da', width=2),
                name="EMA 32"
            )
        ]
    )
    fig.update_layout(height=800)
    st.plotly_chart(fig)
