from flask import Blueprint, jsonify
import yfinance as yf
import requests
from datetime import datetime
from api.utils import redis, EIA_KEY, LINKS

prices_bp = Blueprint('prices', __name__)

def fetch_ticker_data(symbol, category):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="40d").dropna()
        live = ticker.history(period="1d", interval="1m").dropna()
        ytd = ticker.history(start="2026-01-01").dropna()
        
        latest = float(live['Close'].iloc[-1])
        peak_val = float(ytd['High'].max())
        peak_date = ytd['High'].idxmax().strftime('%b %d')
        
        def calc(past):
            abs_v = latest - past
            return {"abs": round(abs_v, 2), "pct": round((abs_v / past) * 100, 2)}
        
        return {
            "current": latest,
            "as_of": live.index[-1].strftime('%b %d, %I:%M %p'),
            "peak_2026": {"val": peak_val, "date": peak_date},
            "source_name": "Yahoo Finance", "source_url": LINKS.get(category),
            "d1": calc(hist['Close'].iloc[-2]), 
            "d7": calc(hist['Close'].iloc[-6]), 
            "d30": calc(hist['Close'].iloc[0])
        }
    except: return None

def fetch_eia_v2(route, series_id, category, freq="weekly", label=""):
    if not EIA_KEY: return None
    url = f"https://api.eia.gov/v2/{route}/data/?api_key={EIA_KEY}&frequency={freq}&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&length=40"
    try:
        res = requests.get(url).json()
        data = res['response']['data']
        curr = float(data[0]['value'])
        as_of = datetime.strptime(data[0]['period'], '%Y-%m-%d').strftime('%b %d') + label
        def calc(idx):
            past = float(data[idx]['value'])
            return {"abs": round(curr - past, 2), "pct": round(((curr - past) / past) * 100, 2)}
        return {
            "current": curr, "as_of": as_of, 
            "source_name": "US EIA", "source_url": LINKS.get(category),
            "d1": calc(1), "d7": calc(5 if freq=="daily" else 2), "d30": calc(len(data)-1)
        }
    except: return None

@prices_bp.route('/api/price/<category>')
def get_price(category):
    # 1. Manual Gas Overrides
    if category in ["retail_gas_nat", "retail_gas_ma"]:
        suffix = "nat" if "nat" in category else "ma"
        try:
            m_price = redis.get(f'manual_price_{suffix}')
            m_date = redis.get('manual_date')
            if m_price:
                return jsonify({
                    "current": float(m_price), "as_of": f"{m_date} (Manual)",
                    "source_name": "Manual Input / AAA", "source_url": LINKS[category],
                    "d1": None, "d7": None, "d30": None
                })
        except: pass
        return jsonify({"error": "No data available"}), 404

    # 2. Yahoo Finance Tickers
    yf_map = {"brent": "BZ=F", "wti": "CL=F", "natgas": "NG=F", "gasoline": "RB=F"}
    if category in yf_map:
        return jsonify(fetch_ticker_data(yf_map[category], category))
    
    # 3. EIA Hubs
    if category == "heating_oil": 
        return jsonify(fetch_eia_v2("petroleum/pri/wfr", "W_EPD2F_PRS_SMA_DPG", category, "weekly", " (Weekly)"))
    if category == "jetfuel": 
        return jsonify(fetch_eia_v2("petroleum/pri/spt", "EER_EPJK_PF4_RGC_DPG", category, "daily", " (Spot)"))
    if category == "algonquin": 
        return jsonify(fetch_eia_v2("natural-gas/pri/fut", "NG_PRI_FUT_S1_D", category, "daily", " (Spot)"))
    
    return jsonify({"error": "Invalid category"}), 400