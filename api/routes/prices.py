from flask import Blueprint, jsonify
import yfinance as yf
import requests
from datetime import datetime
from api.utils import redis, get_manual_prices, EIA_KEY, LINKS

prices_bp = Blueprint('prices', __name__)

def fetch_ticker_data(symbol, category):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="40d").dropna()
        live = ticker.history(period="1d", interval="1m").dropna()
        
        latest = float(live['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2])
        
        # Calculate 1-day change percentage for the PriceCard
        change_pct = ((latest - prev_close) / prev_close) * 100
        
        return {
            "price": latest, # Mapped from 'current'
            "date": live.index[-1].strftime('%b %d, %I:%M %p'), # Mapped from 'as_of'
            "change_1d": round(change_pct, 2),
            "source": "Yahoo Finance",
            "link": LINKS.get(category),
            # Keep your extra data if you want to use it later
            "history": {
                "d7_pct": round(((latest - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100, 2),
                "d30_pct": round(((latest - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100, 2)
            }
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def fetch_eia_v2(route, series_id, category, freq="weekly", label=""):
    if not EIA_KEY: return None
    url = f"https://api.eia.gov/v2/{route}/data/?api_key={EIA_KEY}&frequency={freq}&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&length=5"
    try:
        res = requests.get(url).json()
        data = res['response']['data']
        curr = float(data[0]['value'])
        past = float(data[1]['value'])
        
        as_of = datetime.strptime(data[0]['period'], '%Y-%m-%d').strftime('%b %d') + label
        change_pct = ((curr - past) / past) * 100
        
        return {
            "price": curr,
            "date": as_of,
            "change_1d": round(change_pct, 2),
            "source": f"US EIA{label}",
            "link": LINKS.get(category)
        }
    except Exception as e:
        print(f"Error fetching EIA {series_id}: {e}")
        return None

def get_days_ago(date_str):
    try:
        # Assumes date_str is 'YYYY-MM-DD' from your HTML5 date input
        past_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        delta = date.today() - past_date
        return delta.days
    except:
        return None

@prices_bp.route('/api/price/<category>')
def get_price(category):
    # --- 1. MANUAL GAS DATA ---
    if category in ['retail_gas_nat', 'retail_gas_ma']:
        manual = get_manual_prices()
        if manual and manual.get('date'):
            val = manual['national'] if category == 'retail_gas_nat' else manual['ma']
            days_ago = get_days_ago(manual['date'])
            
            return jsonify({
                "price": float(val),
                "date": manual['date'],
                "days_ago": days_ago if days_ago is not None else "N/A",
                "source": "Manual (Redis)",
                "link": LINKS.get(category),
                "history": None # Manual entry doesn't have 7d/30d history
            })

    # 2. Yahoo Finance Tickers
    yf_map = {"brent": "BZ=F", "wti": "CL=F", "natgas": "NG=F", "gasoline": "RB=F"}
    if category in yf_map:
        data = fetch_ticker_data(yf_map[category], category)
        return jsonify(data) if data else (jsonify({"error": "YF error"}), 500)
    
    # 3. EIA Hubs
    if category == "heating_oil": 
        data = fetch_eia_v2("petroleum/pri/wfr", "W_EPD2F_PRS_SMA_DPG", category, "weekly", " (Weekly)")
        return jsonify(data) if data else (jsonify({"error": "EIA error"}), 500)
    if category == "jetfuel": 
        data = fetch_eia_v2("petroleum/pri/spt", "EER_EPJK_PF4_RGC_DPG", category, "daily", " (Spot)")
        return jsonify(data) if data else (jsonify({"error": "EIA error"}), 500)
    # if category == "algonquin": 
    #     data = fetch_eia_v2("natural-gas/pri/fut", "NG_PRI_FUT_S1_D", category, "daily", " (Spot)")
    #     return jsonify(data) if data else (jsonify({"error": "EIA error"}), 500)
    
    return jsonify({"error": "Invalid category"}), 400