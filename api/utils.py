import os
import logging
from upstash_redis import Redis
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
    """Saves manual gas price overrides to Upstash Redis."""
    if not redis:
        logger.error("Redis client not initialized.")
        return False
    try:
        redis.set("manual_date", str(date_str))
        redis.set("manual_price_nat", str(national))
        redis.set("manual_price_ma", str(ma))
        logger.info(f"Updated Redis: {date_str}, {national}, {ma}")
        return True
    except Exception as e:
        logger.error(f"Redis Push Failed: {e}")
        return False

def get_manual_prices():
    """Retrieves current manual overrides from Redis."""
    if not redis:
        return None
    try:
        return {
            "date": redis.get("manual_date"),
            "national": redis.get("manual_price_nat"),
            "ma": redis.get("manual_price_ma")
        }
    except Exception as e:
        logger.error(f"Redis Get Failed: {e}")
        return None