from api.utils import redis

def check_data():
    try:
        date = redis.get("manual_date")
        nat = redis.get("manual_price_nat")
        ma = redis.get("manual_price_ma")
        
        print("--- REDIS DATA CHECK ---")
        print(f"Date: {date}")
        print(f"National: {nat}")
        print(f"MA: {ma}")
        print("------------------------")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()