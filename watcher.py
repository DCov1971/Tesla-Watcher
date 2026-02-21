import os
import json
import requests

URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query={%22query%22:{%22model%22:%22my%22,%22condition%22:%22used%22,%22options%22:{%22AUTOPILOT%22:%22AUTOPILOT_FULL_SELF_DRIVING%22,%22CABIN_CONFIG%22:%22FIVE%22,%22INTERIOR%22:%22PREMIUM_BLACK%22,%22PAINT%22:[%22SILVER%22,%22BLUE%22]},%22arrangeby%22:%22plh%22,%22zip%22:%2285201%22,%22range%22:200},%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false}"

PUSHOVER_USER = os.getenv("PUSHOVER_USER", "")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tesla.com/inventory/used/my",
    "Origin": "https://www.tesla.com"
}

def send_push(message):
    if not PUSHOVER_USER or not PUSHOVER_TOKEN:
        print("Missing pushover secrets")
        return
    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": PUSHOVER_TOKEN, "user": PUSHOVER_USER, "message": message},
        timeout=20,
    )
    print("Push status:", r.status_code)

def main():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    print("Tesla HTTP:", r.status_code)

    if r.status_code != 200:
        print(r.text[:300])
        return

    data = r.json()
    cars = data.get("results", [])
    print("Vehicles:", len(cars))

    for car in cars[:2]:
        send_push(f"TEST MATCH FOUND\n${car.get('Price')} | {car.get('Odometer')} miles\nhttps://www.tesla.com/my/order/{car.get('VIN')}")

if __name__ == "__main__":
    main()
