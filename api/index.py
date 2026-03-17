import os
import yfinance as yf
import requests
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
from dotenv import load_dotenv
from upstash_redis import Redis

load_dotenv()

# We set strict_slashes=False so that /admin and /admin/ both work
app = Flask(__name__)
app.url_map.strict_slashes = False

# --- REDIS CONFIGURATION ---
raw_url = os.environ.get("KV_URL", "")
kv_token = os.environ.get("KV_REST_API_TOKEN", "")
clean_url = "https://" + raw_url.split("@")[1] if "@" in raw_url else raw_url
redis = Redis(url=clean_url, token=kv_token)

EIA_KEY = os.environ.get("EIA_API_KEY")
ADMIN_PW = "your_secret_password" # Change this!

# Absolute pathing for Vercel environments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, '..', 'public')

# Links for the dashboard
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

# --- STATIC ROUTES ---

@app.route('/')
def serve_index():
    return send_from_directory(PUBLIC_DIR, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(PUBLIC_DIR, 'admin.html')

# --- ADMIN API ---

@app.route('/api/admin/update', methods=['POST'])
def admin_update():
    try:
        data = request.json
        if not data or data.get('pw') != ADMIN_PW:
            return jsonify({"error": "Unauthorized"}), 401
        
        raw_date = data.get('date')
        formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%b %d') if raw_date else datetime.now().strftime('%b %d')
        
        redis.set('manual_date', formatted_date)
        redis.set('manual_price_nat', data.get('nat_price'))
        redis.set('manual_price_ma', data.get('ma_price'))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- PRICE API ---

@app.route('/api/price/<category>')
def get_price(category):
    # Manual Override Logic
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

    # Yahoo Finance Logic
    yf_map = {"brent": "BZ=F", "wti": "CL=F", "natgas": "NG=F", "gasoline": "RB=F"}
    if category in yf_map:
        try:
            ticker = yf.Ticker(yf_map[category])
            hist = ticker.history(period="40d").dropna()
            live = ticker.history(period="1d", interval="1m").dropna()
            ytd = ticker.history(start="2026-01-01").dropna()
            latest = float(live['Close'].iloc[-1])
            def calc(past):
                abs_v = latest - past
                return {"abs": round(abs_v, 2), "pct": round((abs_v / past) * 100, 2)}
            return jsonify({
                "current": latest, "as_of": live.index[-1].strftime('%b %d, %I:%M %p'),
                "peak_2026": {"val": float(ytd['High'].max()), "date": ytd['High'].idxmax().strftime('%b %d')},
                "source_name": "Yahoo Finance", "source_url": LINKS.get(category),
                "d1": calc(hist['Close'].iloc[-2]), "d7": calc(hist['Close'].iloc[-6]), "d30": calc(hist['Close'].iloc[0])
            })
        except: return jsonify({"error": "Ticker error"}), 500
    
    # EIA Hubs (Placeholder - ensure your fetch_eia_v2 helper is included if needed)
    return jsonify({"error": "Invalid category"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)