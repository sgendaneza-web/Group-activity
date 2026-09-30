# Drivers resource: PUT (update) and DELETE (soft delete / deactivate)
# Run: pip install flask && python app.py

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---- Load the sample data from drivers.json (same folder as this file) ----
def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

DATA_FILE = Path(__file__).parent / "drivers.json"

with open(DATA_FILE, "r") as f:
    drivers = json.load(f)  # list of 1000 driver dictionaries

VALID_STATUSES = ["available", "offline", "on_ride"]
PHONE_REGEX = re.compile(r"^\+?[0-9]{10,15}$")


# ---- Helper: find an ACTIVE driver by id ----
def find_active_driver(driver_id):
    for driver in drivers:
        if driver["id"] == driver_id and driver["is_active"]:
            return driver
    return None


# ---- Helper: validate the PUT body, return a list of problems ----
def validate_driver_body(body):
    errors = []

    name = body.get("name")
    if not isinstance(name, str) or name.strip() == "":
        errors.append("name is required and must be a non-empty string")

    phone = body.get("phone")
    if not isinstance(phone, str) or not PHONE_REGEX.match(phone):
        errors.append("phone is required and must be 10-15 digits (optional leading +)")

    if body.get("availability_status") not in VALID_STATUSES:
        errors.append(f"availability_status is required and must be one of: {', '.join(VALID_STATUSES)}")

    return errors


# ---- 1. UPDATE: PUT /api/v1/drivers/<id> ----
@app.route("/api/v1/drivers/<int:driver_id>", methods=["PUT"])
def update_driver(driver_id):
    driver = find_active_driver(driver_id)
    if driver is None:
        return jsonify(error="Not Found", message="No active driver with that id"), 404

    body = request.get_json(silent=True) or {}
    errors = validate_driver_body(body)
    if errors:
        return jsonify(error="Bad Request", details=errors), 400

    driver["name"] = body["name"].strip()
    driver["phone"] = body["phone"]
    driver["availability_status"] = body["availability_status"]
    driver["updated_at"] = now()

    return jsonify(
        id=driver["id"],
        name=driver["name"],
        phone=driver["phone"],
        availability_status=driver["availability_status"],
        updated_at=driver["updated_at"],
    ), 200


# ---- 2. DELETE: DELETE /api/v1/drivers/<id> (soft delete) ----
@app.route("/api/v1/drivers/<int:driver_id>", methods=["DELETE"])
def delete_driver(driver_id):
    driver = find_active_driver(driver_id)
    if driver is None:
        return jsonify(error="Not Found", message="No active driver with that id"), 404

    # Business rule: can't deactivate a driver who is mid-ride
    if driver["availability_status"] == "on_ride":
        return jsonify(
            error="Conflict",
            message="Driver is currently on a ride and cannot be deactivated",
        ), 409

    driver["is_active"] = False
    driver["availability_status"] = "offline"
    driver["updated_at"] = now()

    return "", 204  # success, no body


# ---- JSON 404 for unknown routes (e.g. /api/v1/drivers/abc) ----
@app.errorhandler(404)
def not_found(_e):
    return jsonify(error="Not Found", message="Resource not found"), 404


if __name__ == "__main__":
    app.run(port=3000, debug=True)