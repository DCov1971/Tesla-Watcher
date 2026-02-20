import requests
import json

URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query={%22query%22:{%22model%22:%22my%22,%22condition%22:%22used%22,%22options%22:{%22AUTOPILOT%22:%22AUTOPILOT_FULL_SELF_DRIVING%22,%22CABIN_CONFIG%22:%22FIVE%22,%22INTERIOR%22:%22PREMIUM_BLACK%22,%22PAINT%22:[%22SILVER%22,%22BLUE%22]},%22arrangeby%22:%22plh%22,%22zip%22:%2285201%22,%22range%22:200},%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false}"

PUSHOVER_USER = "uawhycbxu57y2rhx8q7armn6dosnhd"
PUSHOVER_TOKEN = "aeefrc6gfxbikr7k2z1uvd3hwtehhk"

DATA_FILE = "seen_vins.json"

def load_seen():
try:
with open(DATA_FILE, "r") as f:
return set(json.load(f))
except:
return set()

def save_seen(vins):
with open(DATA_FILE, "w") as f:
json.dump(list(vins), f)

def notify(msg):
requests.post("https://api.pushover.net/1/messages.json", data={
"token": PUSHOVER_TOKEN,
"user": PUSHOVER_USER,
"message": msg
})

def check_inventory():
r = requests.get(URL)
data = r.json()

cars = data["results"]
current_vins = set(car["VIN"] for car in cars)

seen = load_seen()
new = current_vins - seen

for car in cars:
    if car["VIN"] in new:
        price = car["Price"]
        miles = car["Odometer"]
        url = f"https://www.tesla.com/my/order/{car['VIN']}"
        notify(f"NEW MODEL Y FOUND\n${price} | {miles} miles\n{url}")

save_seen(current_vins)

check_inventory()ua
