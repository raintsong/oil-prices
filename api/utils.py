import os
import logging
import json
import time
from upstash_redis import Redis
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env.local
load_dotenv(find_dotenv(".env.local"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 1. REDIS CONFIGURATION (VERCEL/UPSTASH INTEGRATION) ---
# Mapping to your specific UPSTASH_KV_KV_... keys
rest_url = os.environ.get("UPSTASH_KV_KV_REST_API_URL")
rest_token = os.environ.get("UPSTASH_KV_KV_REST_API_TOKEN")

# SANITIZATION: Force the https:// protocol for the Upstash REST client
if rest_url and not rest_url.startswith("http"):
    rest_url = f"https://{rest_url}"

# Initialize the client
if rest_url and rest_token:
    redis = Redis(url=rest_url, token=rest_token)
    print(f"✅ REDIS INITIALIZED: {rest_url}")
else:
    print("❌ REDIS ERROR: Missing UPSTASH_KV_KV_... env variables")
    redis = None

# --- 2. EIA & ADMIN CONFIG ---
EIA_KEY = os.environ.get("EIA_API_KEY")
ADMIN_PW = os.environ.get("ADMIN_PW", "crude")

# --- 3. SOURCE LINKS ---
LINKS = {
    "brent": "https://finance.yahoo.com/quote/BZ=F",
    "wti": "https://finance.yahoo.com/quote/CL=F",
    "natgas": "https://finance.yahoo.com/quote/NG=F",
    "gasoline": "https://finance.yahoo.com/quote/RB=F",
    "retail_gas_nat": "https://www.eia.gov/todayinenergy/prices.php",
    "retail_gas_ma": "https://www.eia.gov/todayinenergy/prices.php",
    "heating_oil": "https://www.eia.gov/petroleum/heatingoilpropane/",
    "jetfuel": "https://www.eia.gov/dnav/pet/hist/eer_epjk_pf4_rgc_dpgD.htm",
    # "algonquin": "https://www.eia.gov/todayinenergy/prices.php"
}

# --- 4. DATA HELPERS ---
def set_manual_prices(date_str, national, ma):
    if not redis: return False
    try:
        # 1. Create the 'Row' with a precise timestamp
        # This is your "timestamp column"
        data_point = {
            "date": date_str,      # e.g., "2026-03-17"
            "nat": float(national),
            "ma": float(ma),
            "created_at": time.time() # Unix timestamp for precise ordering
        }
        
        # 2. Append to the history log
        redis.lpush("price_history_log", json.dumps(data_point))
        return True
    except Exception as e:
        print(f"Error saving to Redis: {e}")
        return False

def get_deduplicated_history():
    """
    Simulates: SELECT * FROM (SELECT *, ROW_NUMBER() OVER 
    (PARTITION BY date ORDER BY created_at DESC) as rn FROM log) 
    WHERE rn = 1
    """
    if not redis: return []
    try:
        # Pull the last 100 entries to ensure we have enough history
        raw_data = redis.lrange("price_history_log", 0, 100)
        all_entries = [json.loads(item) for item in raw_data]
        
        # Deduplicate by date, keeping the first (most recent) one found
        seen_dates = set()
        unique_history = []
        
        for entry in all_entries:
            if entry['date'] not in seen_dates:
                unique_history.append(entry)
                seen_dates.add(entry['date'])
        
        # Now we have a clean history: [Today, Yesterday, 2 days ago...]
        return unique_history
    except Exception as e:
        print(f"Error processing history: {e}")
        return []