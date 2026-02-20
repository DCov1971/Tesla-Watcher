import requests

URL = "https://www.tesla.com/inventory/api/v1/inventory-results?query={%22query%22:{%22model%22:%22my%22,%22condition%22:%22used%22,%22options%22:{%22AUTOPILOT%22:%22AUTOPILOT_FULL_SELF_DRIVING%22,%22CABIN_CONFIG%22:%22FIVE%22,%22INTERIOR%22:%22PREMIUM_BLACK%22,%22PAINT%22:[%22SILVER%22,%22BLUE%22]},%22arrangeby%22:%22plh%22,%22zip%22:%2285201%22,%22range%22:200},%22offset%22:0,%22count%22:50,%22outsideOffset%22:0,%22outsideSearch%22:false}"

def main():
response = requests.get(URL, timeout=30)
print("HTTP:", response.status_code)

if response.status_code != 200:
    print("Failed to reach Tesla")
    return

data = response.json()
cars = data.get("results", [])

print("Vehicles found:", len(cars))

for car in cars[:5]:
    print(car.get("VIN"), car.get("Price"))

if name == "main":
main()
