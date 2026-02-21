import os
import json
import requests

# Your Tesla search (ZIP 85201, colors, FSD, etc.)
URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query={%22query%22:{%22model%22:%22my%22,%22condition%22:%22used%22,%22options%22:{%22AUTOPILOT%22:%22AUTOPILOT_FULL_SELF_DRIVING%22,%22CABIN_CONFIG%22:%22FIVE%22,%22INTERIOR%22:%22PREMIUM_BLACK%22,%22PAINT%22:[%22SILVER%22,%22BLUE%22]},%22arrangeby%22:%22plh%22,%22zip%22:%2285201%22,%22range%22:200},%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false}"

PUSHOVER_USER = os.getenv("PUSHOVER_USER", "")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")

STATE_DIR = "state"
SEEN_FILE = os.path.join(STATE_DIR, "seen_vins.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.tesla.com/",
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
        print("Pushover secrets not set; printing instead:")
        print(message)
        return

    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": PUSHOVER_TOKEN, "user": PUSHOVER_USER, "message": message},
        timeout=20,
    )
    print("Pushover status:", r.status_code)

def main():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    print("Tesla HTTP:", r.status_code)
    if r.status_code != 200:
        print(r.text[:300])
        return

    data = r.json()
    cars = data.get("results", [])
    print("Vehicles returned:", len(cars))

    current_vins = set()
    for car in cars:
        vin = car.get("VIN")
        if vin:
            current_vins.add(vin)

    seen = load_seen()
    new_vins = current_vins - seen
    print("New VINs:", len(new_vins))

    # Alert once per new car
    for car in cars:
        vin = car.get("VIN")
        if vin in new_vins:
            price = car.get("Price")
            miles = car.get("Odometer")
            trim = car.get("TrimName") or car.get("Trim") or ""
            order_url = f"https://www.tesla.com/my/order/{vin}"
            pushover(f"NEW MATCHING MODEL Y\n{trim}\n${price} | {miles} miles\n{order_url}")

    save_seen(current_vins)

if __name__ == "__main__":
    main()

Commit the change.

Step 3 — Update run.yml to (a) pass secrets and (b) remember state

Go to .github/workflows/run.yml → ✏️ Edit and replace with this:

name: Tesla Watcher

on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install requests

      - name: Restore state cache
        uses: actions/cache@v4
        with:
          path: state
          key: tesla-watcher-state

      - name: Run watcher
        env:
          PUSHOVER_USER: ${{ secrets.PUSHOVER_USER }}
          PUSHOVER_TOKEN: ${{ secrets.PUSHOVER_TOKEN }}
        run: python watcher.py

      - name: Save state cache
        uses: actions/cache@v4
        with:
          path: state
          key: tesla-watcher-state

Commit.

Step 4 — Test it now

Go to Actions → Tesla Watcher → Run workflow.

What you should expect:

First run after adding cache may alert on anything currently in the list (because “seen” is empty the first time).

After that, it will only alert when a new VIN appears.

If you don’t want the first-run burst, tell me and I’ll change it so the first run “primes” the cache without notifying.

Quick optional improvement (recommended)

If you want faster than 10 minutes, we can go to every 5 minutes. (GitHub may occasionally throttle if too frequent, but 5 is usually fine.)

When you run the workflow after these changes, tell me:

Did you get a Pushover notification?

Did it alert on multiple cars right away (expected on first run)?
