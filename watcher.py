import os
import json
import requests

# Your Tesla query (ZIP 85201, colors, FSD, etc.)
API_URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query={%22query%22:{%22model%22:%22my%22,%22condition%22:%22used%22,%22options%22:{%22AUTOPILOT%22:%22AUTOPILOT_FULL_SELF_DRIVING%22,%22CABIN_CONFIG%22:%22FIVE%22,%22INTERIOR%22:%22PREMIUM_BLACK%22,%22PAINT%22:[%22SILVER%22,%22BLUE%22]},%22arrangeby%22:%22plh%22,%22zip%22:%2285201%22,%22range%22:200},%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false}"

WARMUP_URL = "https://www.tesla.com/inventory/used/my?zip=85201&range=200"

PUSHOVER_USER = os.getenv("PUSHOVER_USER", "")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")

STATE_DIR = "state"
SEEN_FILE = os.path.join(STATE_DIR, "seen_vins.json")

HEADERS_PAGE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

HEADERS_API = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tesla.com/inventory/used/my",
    "Origin": "https://www.tesla.com",
}

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(vins):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(list(vins)), f)

def pushover(message):
    if not PUSHOVER_USER or not PUSHOVER_TOKEN:
        print("Missing pushover secrets; cannot notify.")
        return

    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": PUSHOVER_TOKEN, "user": PUSHOVER_USER, "message": message},
        timeout=20,
    )
    print("Pushover HTTP:", r.status_code, r.text[:120])

def fetch_inventory():
    s = requests.Session()

    # Warm-up request to get cookies / bot checks
    warm = s.get(WARMUP_URL, headers=HEADERS_PAGE, timeout=30)
    print("Warmup HTTP:", warm.status_code)

    # Now call the API with the same session/cookies
    r = s.get(API_URL, headers=HEADERS_API, timeout=30)
    print("Tesla API HTTP:", r.status_code)

    if r.status_code != 200:
        print("Tesla API body (first 300 chars):")
        print(r.text[:300])
        return None

    return r.json()

def main():
    data = fetch_inventory()
    if not data:
        # If Tesla blocks GitHub, you'll see 403 here. We won't error the job.
        return

    cars = data.get("results", [])
    print("Vehicles returned:", len(cars))

    current_vins = {c.get("VIN") for c in cars if c.get("VIN")}
    seen = load_seen()
    new_vins = current_vins - seen
    print("New VINs:", len(new_vins))

    for c in cars:
        vin = c.get("VIN")
        if vin in new_vins:
            price = c.get("Price")
            miles = c.get("Odometer")
            trim = c.get("TrimName") or c.get("Trim") or ""
            order_url = f"https://www.tesla.com/my/order/{vin}"
            pushover(f"NEW MATCHING MODEL Y\n{trim}\n${price} | {miles} miles\n{order_url}")

    save_seen(current_vins)

if __name__ == "__main__":
    main()
