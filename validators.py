import re
from datetime import date

def validate_registration(data):
    for field in ("event_id", "full_name", "email", "phone"):
        if not str(data.get(field, "")).strip():
            return "Please complete all required fields."
    try:
        int(data["event_id"])
    except (TypeError, ValueError):
        return "Invalid event ID."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", str(data["email"]).strip()):
        return "Please enter a valid email address."
    phone = re.sub(r"[\s+\-()]", "", str(data["phone"]))
    if not phone.isdigit() or not 10 <= len(phone) <= 15:
        return "Please enter a valid phone number (10 to 15 digits)."
    if len(str(data["full_name"]).strip()) > 100:
        return "Name must be 100 characters or fewer."
    return None

def validate_event(data):
    required = ("title", "category", "description", "event_date", "event_time", "location", "venue", "capacity")
    if any(not str(data.get(field, "")).strip() for field in required):
        return "Please complete all event fields."
    try:
        capacity = int(data["capacity"])
        date.fromisoformat(data["event_date"])
        if capacity < 1 or capacity > 100000:
            return "Capacity must be between 1 and 100000."
    except (ValueError, TypeError):
        return "Please enter a valid date and positive capacity."
    return None
