import json
from api.utils import redis

def check_data():
    print("\n--- 🔍 REDIS FULL DATA AUDIT ---")
    
    try:
        # 1. Check Legacy Keys (Single latest values)
        legacy_date = redis.get("manual_date")
        print(f"Legacy Key [manual_date]: {legacy_date}")

        # 2. Check the History Log (The List)
        # 0 to -1 fetches EVERY item in the Redis List
        history_raw = redis.lrange("price_history_log", 0, -1)
        
        if not history_raw:
            print("\n⚠️  [price_history_log] is EMPTY.")
        else:
            print(f"\n📜 History Log Found: {len(history_raw)} entries")
            print(f"{'DATE':<12} | {'NAT':<8} | {'MA':<8} | {'TIMESTAMP'}")
            print("-" * 50)
            
            for item in history_raw:
                # Convert the JSON string back to a Python dict
                data = json.loads(item)
                
                date = data.get('date', 'N/A')
                nat = data.get('nat', 0.0)
                ma = data.get('ma', 0.0)
                ts = data.get('created_at', 0)
                
                # Highlight the Chaos Peak for easy spotting
                peak_marker = " 🔥 PEAK" if nat == 9.999 else ""
                dip_marker = " ❄️  DIP" if nat < 0 else ""
                
                print(f"{date:<12} | {nat:<8.3f} | {ma:<8.3f} | {ts}{peak_marker}{dip_marker}")
        
        print("\n" + "-" * 50)

    except Exception as e:
        print(f"\n❌ Error reading Redis: {e}")

if __name__ == "__main__":
    check_data()