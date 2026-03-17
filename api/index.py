import os
import yfinance as yf
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

# Tickers: Brent (BZ=F), WTI (CL=F), Henry Hub Nat Gas (NG=F), Gasoline (RB=F)
TICKERS = {
    "brent": "BZ=F",
    "wti": "CL=F",
    "natgas": "NG=F",
    "gasoline": "RB=F"
}

def get_stats(symbol):
    ticker = yf.Ticker(symbol)
    # Fetch 40 days to ensure we have a full month of trading days
    df = ticker.history(period="40d").dropna()
    
    if len(df) < 2:
        return None

    latest = float(df['Close'].iloc[-1])
    
    def calc_change(past_val):
        abs_chg = latest - past_val
        pct_chg = (abs_chg / past_val) * 100
        return {"abs": round(abs_chg, 2), "pct": round(pct_chg, 2)}

    return {
        "current": round(latest, 2),
        "d1": calc_change(df['Close'].iloc[-2]),
        "d7": calc_change(df['Close'].iloc[-6] if len(df) >= 6 else df['Close'].iloc[0]),
        "d30": calc_change(df['Close'].iloc[0])
    }

@app.route('/api/prices')
def get_prices():
    results = {}
    for key, symbol in TICKERS.items():
        data = get_stats(symbol)
        if data:
            results[key] = data
    return jsonify(results)

@app.route('/')
def index():
    # Make sure your 'public' folder is at the root
    return send_from_directory('../public', 'index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)