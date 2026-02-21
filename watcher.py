import os
import requests

PUSHOVER_USER = os.getenv("PUSHOVER_USER", "")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN", "")

print("Has PUSHOVER_USER:", bool(PUSHOVER_USER))
print("Has PUSHOVER_TOKEN:", bool(PUSHOVER_TOKEN))

r = requests.post(
    "https://api.pushover.net/1/messages.json",
    data={
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": "TEST ✅ Tesla-Watcher notification from GitHub Actions",
    },
    timeout=20,
)

print("Pushover HTTP:", r.status_code)
print("Pushover response:", r.text[:200])
