import os
import yfinance as yf
import requests
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
from dotenv import load_dotenv
from upstash_redis import Redis

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, '..', 'public')

load_dotenv()
app = Flask(__name__)

# --- REDIS CONFIGURATION ---
# Sanitize the Vercel rediss:// URL for the Upstash REST client
raw_url = os.environ.get("KV_URL", "")
kv_token = os.environ.get("KV_REST_API_TOKEN", "")

clean_url = raw_url
if "@" in raw_url:
    clean_url = "https://" + raw_url.split("@")[1]

redis = Redis(url=clean_url, token=kv_token)

EIA_KEY = os.environ.get("EIA_API_KEY")
ADMIN_PW = "your_secret_password" # Ensure this matches your admin.html

# Source Links for the Dashboard
LINKS = {
    "brent": "https://finance.yahoo.com/quote/BZ=F",
    "wti": "https://finance.yahoo.com/quote/CL=F",
    "natgas": "https://finance.yahoo.com/quote/NG=F",
    "gasoline": "https://finance.yahoo.com/quote/RB=F",
    "retail_gas_nat": "https://www.eia.gov/todayinenergy/prices.php",
    "retail_gas_ma": "https://www.eia.gov/todayinenergy/prices.php",
    "heating_oil": "https://www.eia.gov/petroleum/heatingoilpropane/",
    "jetfuel": "https://www.eia.gov/dnav/pet/hist/eer_epjk_pf4_rgc_dpgD.htm",
    "algonquin": "https://www.eia.gov/todayinenergy/prices.php"
}

# --- ADMIN LOGIC (Write to Redis) ---

@app.route('/api/admin/update', methods=['POST'])
def admin_update():
    try:
        data = request.json
        if not data or data.get('pw') != ADMIN_PW:
            return jsonify({"error": "Unauthorized"}), 401
        
        raw_date = data.get('date')
        # Format the date nicely for the UI (e.g., 'Mar 16')
        formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%b %d') if raw_date else datetime.now().strftime('%b %d')
        
        # Save to Upstash
        redis.set('manual_date', formatted_date)
        redis.set('manual_price_nat', data.get('nat_price'))
        redis.set('manual_price_ma', data.get('ma_price'))
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DATA FETCHING HELPERS ---

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

# --- PUBLIC API ROUTE ---

@app.route('/api/price/<category>')
def get_price(category):
    # 1. Check for Manual AAA Data
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

    # 2. Market Tickers (Yahoo Finance)
    yf_map = {"brent": "BZ=F", "wti": "CL=F", "natgas": "NG=F", "gasoline": "RB=F"}
    if category in yf_map:
        return jsonify(fetch_ticker_data(yf_map[category], category))
    
    # 3. Regional Hubs (EIA)
    if category == "heating_oil": 
        return jsonify(fetch_eia_v2("petroleum/pri/wfr", "W_EPD2F_PRS_SMA_DPG", category, "weekly", " (Weekly)"))
    if category == "jetfuel": 
        return jsonify(fetch_eia_v2("petroleum/pri/spt", "EER_EPJK_PF4_RGC_DPG", category, "daily", " (Spot)"))
    if category == "algonquin": 
        # Daily Futures proxy for Algonquin troubleshooting
        return jsonify(fetch_eia_v2("natural-gas/pri/fut", "NG_PRI_FUT_S1_D", category, "daily", " (Spot)"))
    
    return jsonify({"error": "Invalid category"}), 400


@app.route('/')
def serve_index():
    return send_from_directory(PUBLIC_DIR, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(PUBLIC_DIR, 'admin.html')

# 2. Add this to handle CSS or Images if you add them later
@app.route('/public/<path:path>')
def send_public(path):
    return send_from_directory(PUBLIC_DIR, path)

# ... (keep your /api/price and /api/admin/update routes here) ...

if __name__ == "__main__":
    app.run(debug=True, port=5000)