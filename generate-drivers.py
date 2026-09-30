# Generates drivers.json with 1000 sample drivers
import json
import random
from datetime import datetime, timedelta, timezone

random.seed(42)  # same output every run

FIRST = ["Jean", "Aline", "Eric", "Claudine", "Patrick", "Diane", "Emmanuel", "Grace", "Olivier", "Sandrine",
         "Innocent", "Josiane", "Fabrice", "Vestine", "Landry", "Immaculee", "Celestin", "Solange", "Yves", "Divine",
         "Theogene", "Beatrice", "Aimable", "Chantal", "Didier", "Marie", "Samuel", "Esperance", "Pacifique", "Alice"]
LAST = ["Uwase", "Habimana", "Mukamana", "Niyonzima", "Ndayisaba", "Uwimana", "Nkurunziza", "Mugisha", "Ishimwe",
        "Iradukunda", "Mutesi", "Hakizimana", "Nsengimana", "Uwizeye", "Munyaneza", "Byiringiro", "Kamanzi", "Niyigena",
        "Rukundo", "Twagirayezu"]

STATUS_CHOICES = ["available", "offline", "on_ride"]
STATUS_WEIGHTS = [45, 35, 20]

def random_phone(used):
    while True:
        phone = f"+2507{random.choice('2389')}{random.randint(0, 9999999):07d}"
        if phone not in used:
            used.add(phone)
            return phone

base_time = datetime(2026, 9, 1, tzinfo=timezone.utc)
used_phones, drivers = set(), []

for i in range(1, 1001):
    updated = base_time + timedelta(minutes=random.randint(0, 43200))
    drivers.append({
        "id": i,
        "name": f"{random.choice(FIRST)} {random.choice(LAST)}",
        "phone": random_phone(used_phones),
        "availability_status": random.choices(STATUS_CHOICES, STATUS_WEIGHTS)[0],
        "is_active": random.random() > 0.08,  # ~8% deactivated
        "updated_at": updated.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

# Deactivated drivers should be offline
for d in drivers:
    if not d["is_active"]:
        d["availability_status"] = "offline"

# Fixed drivers so the demo/curl tests always work
drivers[0].update(availability_status="available", is_active=True)   # id 1 -> 200 / 204
drivers[1].update(availability_status="on_ride", is_active=True)     # id 2 -> 409
drivers[2].update(availability_status="offline", is_active=False)    # id 3 -> 404

with open("drivers.json", "w") as f:
    json.dump(drivers, f, indent=2)

print(f"Wrote {len(drivers)} drivers")