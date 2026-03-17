import os
import yfinance as yf
import requests
from flask import Flask, jsonify, send_from_directory
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
EIA_KEY = os.environ.get("EIA_API_KEY")

def fetch_ticker_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="40d").dropna()
        live = ticker.history(period="1d", interval="1m").dropna()
        if hist.empty or live.empty: return None
        
        latest_price = float(live['Close'].iloc[-1])
        as_of = live.index[-1].strftime('%b %d, %I:%M %p')
        
        def calc(past):
            abs_v = latest_price - past
            return {"abs": round(abs_v, 2), "pct": round((abs_v / past) * 100, 2)}
        
        return {
            "current": round(latest_price, 2),
            "as_of": as_of,
            "d1": calc(hist['Close'].iloc[-2]),
            "d7": calc(hist['Close'].iloc[-6]),
            "d30": calc(hist['Close'].iloc[0])
        }
    except: return None

def fetch_eia_standard(series_id, label_suffix=""):
    if not EIA_KEY: return None
    url = f"https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key={EIA_KEY}&frequency=weekly&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&length=10"
    try:
        res = requests.get(url).json()
        data = res['response']['data']
        latest_val = float(data[0]['value'])
        as_of = datetime.strptime(data[0]['period'], '%Y-%m-%d').strftime('%b %d') + label_suffix
        def calc(idx):
            past = float(data[idx]['value'])
            return {"abs": round(latest_val - past, 2), "pct": round(((latest_val - past) / past) * 100, 2)}
        return {"current": round(latest_val, 2), "as_of": as_of, "d1": calc(1), "d7": calc(2), "d30": calc(4)}
    except: return None

def fetch_realtime_ma_gas():
    # Estimates current pump price by applying Futures trend to last Weekly EIA report
    try:
        eia_data = fetch_eia_standard("EMM_EPMR_PTE_SMA_DPG")
        ticker = yf.Ticker("RB=F")
        hist = ticker.history(period="10d")
        trend_pct = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
        
        estimated_price = eia_data['current'] * (1 + trend_pct)
        return {
            "current": round(estimated_price, 2),
            "as_of": datetime.now().strftime('%b %d, %I:%M %p'),
            "d1": {"abs": round(estimated_price - eia_data['current'], 2), "pct": round(trend_pct * 100, 2)},
            "d7": eia_data['d7'], "d30": eia_data['d30']
        }
    except: return None

@app.route('/api/price/<category>')
def get_single_price(category):
    mapping = {"brent": "BZ=F", "wti": "CL=F", "natgas": "NG=F", "gasoline": "RB=F"}
    if category == "retail_gas": return jsonify(fetch_realtime_ma_gas())
    if category == "heating_oil": return jsonify(fetch_eia_standard("W_EPD2F_PRS_SMA_DPG", " (Weekly)"))
    if category in mapping: return jsonify(fetch_ticker_data(mapping[category]))
    return jsonify({"error": "Invalid category"}), 400

@app.route('/')
def index():
    return send_from_directory('../public', 'index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)