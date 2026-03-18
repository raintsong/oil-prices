from flask import Blueprint, jsonify
import yfinance as yf
import requests
from datetime import datetime, date
from api.utils import get_deduplicated_history, EIA_KEY, LINKS

prices_bp = Blueprint('prices', __name__)

# Corrected: .year is a property, not a function
# Also converting to string immediately to help startswith() logic
CURRENT_YEAR_STR = str(datetime.now().year)

def get_days_ago(date_str):
    try:
        # Standard HTML5 date input is YYYY-MM-DD
        past_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        delta = date.today() - past_date
        return int(delta.days)
    except Exception as e:
        print(f"Date Parsing Error: {e} for string {date_str}")
        return 0

def fetch_ticker_data(symbol, category):
    try:
        ticker = yf.Ticker(symbol)
        # Dynamic start year
        ytd = ticker.history(start=f"{CURRENT_YEAR_STR}-01-01").dropna()
        
        if ytd.empty: return None

        peak_val = float(ytd['High'].max())
        peak_date = ytd['High'].idxmax().strftime('%b %d')
        latest = float(ytd['Close'].iloc[-1])
        
        def get_delta(days_back):
            # Guard against short dataframes
            if len(ytd) < days_back: return {"abs": 0, "pct": 0}
            past = float(ytd['Close'].iloc[-days_back])
            abs_diff = latest - past
            pct_diff = (abs_diff / past) * 100 if past != 0 else 0
            return {"abs": round(abs_diff, 2), "pct": round(pct_diff, 2)}

        d1 = get_delta(2)
        d7 = get_delta(7)
        d30 = get_delta(30)

        return {
            "price": latest,
            "date": ytd.index[-1].strftime('%b %d'),
            "peak_cy": {"val": round(peak_val, 2), "date": peak_date}, # Front-end expects 'peak_cy'
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
        print(f"YF Error ({symbol}): {e}")
        return None


def fetch_eia_v2(route, series_id, category, freq="weekly", label=""):
    if not EIA_KEY: return None
    url = f"https://api.eia.gov/v2/{route}/data/?api_key={EIA_KEY}&frequency={freq}&data[0]=value&facets[series][]={series_id}&sort[0][column]=period&sort[0][direction]=desc&length=40"
    
    try:
        res = requests.get(url).json()
        data = res['response']['data']
        
        curr = float(data[0]['value'])
        past = float(data[1]['value'])
        as_of = datetime.strptime(data[0]['period'], '%Y-%m-%d').strftime('%b %d') + label
        
        abs_1d = curr - past
        pct_1d = (abs_1d / past) * 100 if past != 0 else 0

        peak_val = 0.0
        peak_date = "N/A"
        
        for entry in data:
            # Fixed: Ensure startswith uses the string version of the year
            if entry['period'].startswith(CURRENT_YEAR_STR):
                val = float(entry['value'])
                if val > peak_val:
                    peak_val = val
                    peak_date = datetime.strptime(entry['period'], '%Y-%m-%d').strftime('%b %d')

        is_weekly = freq == "weekly"
        
        d7_idx = 1 if is_weekly else 7
        d30_idx = 4 if is_weekly else 30

        def calc_eia_history(target_idx):
            if len(data) > target_idx:
                past_val = float(data[target_idx]['value'])
                abs_diff = curr - past_val
                pct_diff = (abs_diff / past_val) * 100 if past_val != 0 else 0
                return {"abs": round(abs_diff, 3), "pct": round(pct_diff, 2)}
            return {"abs": None, "pct": None}

        d7_data = calc_eia_history(d7_idx)
        d30_data = calc_eia_history(d30_idx)

        return {
            "price": curr,
            "date": as_of,
            "change_1d": round(pct_1d, 2),
            "abs_1d": round(abs_1d, 3),
            "peak_cy": { # Matches front-end key
                "val": round(peak_val, 3),
                "date": peak_date
            },
            "source": f"US EIA{label}",
            "link": LINKS.get(category),
            "history": {
                "d7_pct": d7_data['pct'], "d7_abs": d7_data['abs'],
                "d30_pct": d30_data['pct'], "d30_abs": d30_data['abs']
            }
        }
    except Exception as e:
        print(f"EIA Error ({category}): {e}")
        return None


def get_cy_peak(history, field):
    peak_val = 0.0
    peak_date = "N/A"
    
    for entry in history:
        # Fixed: Ensure startswith uses the string version
        if entry['date'].startswith(CURRENT_YEAR_STR):
            if entry[field] > peak_val:
                peak_val = entry[field]
                peak_date = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%b %d')
                
    return {"val": peak_val, "date": peak_date}

@prices_bp.route('/api/price/<category>')
def get_price(category):
    if category in ['retail_gas_nat', 'retail_gas_ma']:
        history = get_deduplicated_history()
        
        if not history:
            return jsonify({"error": "No data found"}), 404
            
        latest = history[0]
        days_ago = get_days_ago(latest['date'])
        field = 'nat' if category == 'retail_gas_nat' else 'ma'
        curr_val = latest[field]
        peak = get_cy_peak(history, field)

        def get_diff(days_back):
            if len(history) > days_back:
                past = history[days_back][field]
                if past == 0: return {"abs": 0, "pct": 0}
                abs_c = curr_val - past
                return {"abs": round(abs_c, 3), "pct": round((abs_c / past) * 100, 2)}
            return {"abs": None, "pct": None}

        d1 = get_diff(1)
        d7 = get_diff(7)
        d30 = get_diff(30)

        return jsonify({
            "price": curr_val,
            "date": latest['date'],
            "peak_cy": peak, # Front-end expects peak_cy
            "days_ago": days_ago,
            "change_1d": d1['pct'],
            "abs_1d": d1['abs'],
            "history": {
                "d7_pct": d7['pct'], "d7_abs": d7['abs'],
                "d30_pct": d30['pct'], "d30_abs": d30['abs']
            },
            "source": "Manual (Redis)",
            "link": LINKS.get(category)
        })

    yf_map = {"brent": "BZ=F", "wti": "CL=F", "natgas": "NG=F", "gasoline": "RB=F"}
    if category in yf_map:
        data = fetch_ticker_data(yf_map[category], category)
        return jsonify(data) if data else (jsonify({"error": "YF error"}), 500)
    
    if category == "heating_oil": 
        data = fetch_eia_v2("petroleum/pri/wfr", "W_EPD2F_PRS_SMA_DPG", category, "weekly", " (Weekly)")
        return jsonify(data) if data else (jsonify({"error": "EIA error"}), 500)
    if category == "jetfuel": 
        data = fetch_eia_v2("petroleum/pri/spt", "EER_EPJK_PF4_RGC_DPG", category, "daily", " (Spot)")
        return jsonify(data) if data else (jsonify({"error": "EIA error"}), 500)
    
    return jsonify({"error": "Invalid category"}), 400