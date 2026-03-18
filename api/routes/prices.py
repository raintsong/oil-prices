from flask import Blueprint, jsonify
import yfinance as yf
import requests
from datetime import datetime, date
from api.utils import get_deduplicated_history, EIA_KEY, LINKS

prices_bp = Blueprint('prices', __name__)

def fetch_ticker_data(symbol, category):
    try:
        ticker = yf.Ticker(symbol)
        ytd = ticker.history(start="2026-01-01").dropna()
        peak_val = float(ytd['High'].max())
        peak_date = ytd['High'].idxmax().strftime('%b %d')
        latest = float(ytd['Close'].iloc[-1])
        
        def get_delta(days_back):
            past = float(ytd['Close'].iloc[-days_back])
            abs_diff = latest - past
            pct_diff = (abs_diff / past) * 100
            return {"abs": round(abs_diff, 2), "pct": round(pct_diff, 2)}

        d1 = get_delta(2)
        d7 = get_delta(7)
        d30 = get_delta(30)

        return {
            "price": latest,
            "date": ytd.index[-1].strftime('%b %d'),
            "peak_2026": {"val": round(peak_val, 2), "date": peak_date},
            "change_1d": d1['pct'],
            "abs_1d": d1['abs'],
            "history": {
                "d7_pct": d7['pct'], "d7_abs": d7['abs'],
                "d30_pct": d30['pct'], "d30_abs": d30['abs']
            },
            "source": "Yahoo Finance",
            "link": LINKS.get(category)
        }
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_eia_v2(route, series_id, category, freq="weekly", label=""):
    if not EIA_KEY: return None
    # We fetch 40 units of length to ensure we cover all of 2026 so far
    url = f"https://api.eia.gov/v2/{route}/data/?api_key={EIA_KEY}&frequency={freq}&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&length=40"
    
    try:
        res = requests.get(url).json()
        data = res['response']['data']
        
        # 1. Latest Data
        curr = float(data[0]['value'])
        past = float(data[1]['value'])
        as_of = datetime.strptime(data[0]['period'], '%Y-%m-%d').strftime('%b %d') + label
        
        # 2. Calculate 1D/1W Change
        abs_1d = curr - past
        pct_1d = (abs_1d / past) * 100

        # 3. Calculate 2026 Peak
        peak_val = 0.0
        peak_date = "N/A"
        
        for entry in data:
            # Only check entries that fall within 2026
            if entry['period'].startswith("2026"):
                val = float(entry['value'])
                if val > peak_val:
                    peak_val = val
                    # Format date for the UI (e.g., "Mar 10")
                    peak_date = datetime.strptime(entry['period'], '%Y-%m-%d').strftime('%b %d')

        return {
            "price": curr,
            "date": as_of,
            "change_1d": round(pct_1d, 2),
            "abs_1d": round(abs_1d, 3),
            "peak_2026": {
                "val": round(peak_val, 3),
                "date": peak_date
            },
            "source": f"US EIA{label}",
            "link": LINKS.get(category),
            # Simplified history for EIA (using index 1 as 1-period back)
            "history": {
                "d7_pct": None, # EIA weekly data makes 7d/30d logic complex
                "d30_pct": None
            }
        }
    except Exception as e:
        print(f"EIA Error ({category}): {e}")
        return None


def get_2026_peak(history, field):
    """Finds the max value and date for the year 2026 in the history list."""
    peak_val = 0.0
    peak_date = "N/A"
    
    for entry in history:
        # Only look at 2026 dates
        if entry['date'].startswith("2026"):
            if entry[field] > peak_val:
                peak_val = entry[field]
                peak_date = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%b %d')
                
    return {"val": peak_val, "date": peak_date}

@prices_bp.route('/api/price/<category>')
def get_price(category):
    if category in ['retail_gas_nat', 'retail_gas_ma']:
        history = get_deduplicated_history() # Our "Partitioned" list
        
        if not history:
            return jsonify({"error": "No data found"}), 404
            
        latest = history[0]
        days_ago = get_days_ago(latest['date'])
        field = 'nat' if category == 'retail_gas_nat' else 'ma'
        curr_val = latest[field]
        peak = get_2026_peak(history, field) # Find peak from Redis

        def get_diff(days_back):
            # Attempt to find the entry exactly X days ago, 
            # or the closest one available in our unique list
            if len(history) > days_back:
                past = history[days_back][field]
                abs_c = curr_val - past
                return {"abs": round(abs_c, 3), "pct": round((abs_c / past) * 100, 2)}
            return {"abs": None, "pct": None}

        d1 = get_diff(1)
        d7 = get_diff(7)
        d30 = get_diff(30)

        return jsonify({
            "price": curr_val,
            "date": latest['date'],
            "peak_2026": peak,
            "days_ago": days_ago, # CRITICAL: Ensure this key exists
            "change_1d": d1['pct'],
            "abs_1d": d1['abs'],
            "history": {
                "d7_pct": d7['pct'], "d7_abs": d7['abs'],
                "d30_pct": d30['pct'], "d30_abs": d30['abs']
            },
            "source": "Manual (Redis)",
            "link": LINKS.get(category)
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