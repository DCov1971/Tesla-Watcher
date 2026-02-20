import os
import json
import requests

URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query={%22query%22:{%22model%22:%22my%22,%22condition%22:%22used%22,%22options%22:{%22AUTOPILOT%22:%22AUTOPILOT_FULL_SELF_DRIVING%22,%22CABIN_CONFIG%22:%22FIVE%22,%22INTERIOR%22:%22PREMIUM_BLACK%22,%22PAINT%22:[%22SILVER%22,%22BLUE%22]},%22arrangeby%22:%22plh%22,%22zip%22:%2285201%22,%22range%22:200},%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false}"

PUSHOVER_USER = os.getenv("PUSHOVER_USER", "")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")

DATA_FILE = "seen_vins.json"

HEADERS = {
"User-Agent": "Mozilla/5.0",
"Accept": "application/json,text/plain,/",
"Referer": "https://www.tesla.com/",
}

def load_seen():
try:
with open(DATA_FILE, "r") as f:
return set(json.load(f))
except:
return set()

def save_seen(vins):
with open(DATA_FILE, "w") as f:
json.dump(list(vins), f)

def notify(message):
if not PUSHOVER_USER or not PUSHOVER_TOKEN:
print("No pushover keys set")
print(message)
return

requests.post(
    "https://api.pushover.net/1/messages.json",
    data={
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": message
    }
)

def main():
r = requests.get(URL, headers=HEADERS, timeout=30)
print("Tesla status:", r.status_code)

if r.status_code != 200:
    print("Bad response")
    return

data = r.json()
cars = data.get("results", [])

current_vins = set(c["VIN"] for c in cars if "VIN" in c)
seen = load_seen()
new = current_vins - seen

print("Cars found:", len(cars))
print("New cars:", len(new))

for car in cars:
    if car.get("VIN") in new:
        price = car.get("Price")
        miles = car.get("Odometer")
        link = f"https://www.tesla.com/my/order/{car['VIN']}"
        notify(f"NEW MODEL Y FOUND\n${price} | {miles} miles\n{link}")

save_seen(current_vins)

if name == "main":
main()
