import os
from upstash_redis import Redis
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.local"))

# --- REDIS CONFIGURATION ---
raw_url = os.environ.get("KV_URL", "")
kv_token = os.environ.get("KV_REST_API_TOKEN", "")

# Sanitize Vercel's rediss:// URL for the Upstash REST client
clean_url = raw_url
if "@" in raw_url:
    clean_url = "https://" + raw_url.split("@")[1]

redis = Redis(url=clean_url, token=kv_token)

EIA_KEY = os.environ.get("EIA_API_KEY")
ADMIN_PW = "crude" # In production, use os.environ.get("ADMIN_PW")

# Source links for the frontend cards
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