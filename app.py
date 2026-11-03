import os
from functools import wraps
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db, close_db
from validators import validate_registration, validate_event

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-development-secret")
app.teardown_appcontext(close_db)

with app.app_context():
    init_db()

def organizer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "organizer_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Organizer login required."}), 401
            return redirect(url_for("organizer_login"))
        return view(*args, **kwargs)
    return wrapped

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/event/<int:event_id>")
def event_detail_page(event_id):
    return render_template("event.html", event_id=event_id)

@app.get("/register/<int:event_id>")
def register_page(event_id):
    return render_template("register.html", event_id=event_id)

@app.get("/confirmation")
def confirmation_page():
    return render_template("confirmation.html")

@app.get("/organizer/login")
def organizer_login():
    return render_template("login.html")

@app.post("/organizer/login")
def organizer_login_submit():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    organizer = get_db().execute("SELECT * FROM organizers WHERE LOWER(email)=?", (email,)).fetchone()
    if organizer and check_password_hash(organizer["password_hash"], password):
        session.clear()
        session["organizer_id"] = organizer["id"]
        session["organizer_name"] = organizer["name"]
        return redirect(url_for("organizer_dashboard"))
    flash("Invalid email or password.", "error")
    return redirect(url_for("organizer_login"))

@app.get("/organizer/logout")
def organizer_logout():
    session.clear()
    return redirect(url_for("home"))

@app.get("/organizer/dashboard")
@organizer_required
def organizer_dashboard():
    return render_template("dashboard.html")

@app.get("/api/events")
def api_events():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    date = request.args.get("date", "").strip()
    query = """
        SELECT e.*, (e.capacity - COUNT(r.id)) AS seats_left
        FROM events e LEFT JOIN registrations r ON r.event_id=e.id
        WHERE e.status='Open'
    """
    params = []
    if search:
        query += " AND (LOWER(e.title) LIKE ? OR LOWER(e.description) LIKE ? OR LOWER(e.organizer_name) LIKE ?)"
        term = f"%{search.lower()}%"
        params += [term, term, term]
    if category:
        query += " AND LOWER(e.category)=?"
        params.append(category.lower())
    if location:
        query += " AND LOWER(e.location) LIKE ?"
        params.append(f"%{location.lower()}%")
    if date:
        query += " AND e.event_date=?"
        params.append(date)
    query += " GROUP BY e.id ORDER BY e.event_date ASC"
    rows = get_db().execute(query, params).fetchall()
    return jsonify([dict(row) for row in rows])

@app.get("/api/events/<int:event_id>")
def api_event_detail(event_id):
    row = get_db().execute("""
        SELECT e.*, (e.capacity - COUNT(r.id)) AS seats_left
        FROM events e LEFT JOIN registrations r ON r.event_id=e.id
        WHERE e.id=? GROUP BY e.id
    """, (event_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Event not found."}), 404
    return jsonify(dict(row))

@app.post("/api/register")
def api_register():
    data = request.get_json(silent=True) or request.form.to_dict()
    error = validate_registration(data)
    if error:
        return jsonify({"error": error}), 400
    db = get_db()
    event = db.execute("SELECT id, capacity, status FROM events WHERE id=?", (int(data["event_id"]),)).fetchone()
    if event is None:
        return jsonify({"error": "Event not found."}), 404
    if event["status"] != "Open":
        return jsonify({"error": "Registration for this event is closed."}), 400
    duplicate = db.execute(
        "SELECT id FROM registrations WHERE event_id=? AND LOWER(email)=LOWER(?)",
        (int(data["event_id"]), data["email"].strip())
    ).fetchone()
    if duplicate:
        return jsonify({"error": "You have already registered for this event with this email."}), 409
    count = db.execute("SELECT COUNT(*) FROM registrations WHERE event_id=?", (int(data["event_id"]),)).fetchone()[0]
    if count >= event["capacity"]:
        return jsonify({"error": "Sorry, this event is full."}), 409
    cursor = db.execute("""
        INSERT INTO registrations (event_id, full_name, email, phone)
        VALUES (?, ?, ?, ?)
    """, (int(data["event_id"]), data["full_name"].strip(), data["email"].strip(), data["phone"].strip()))
    db.commit()
    return jsonify({"message": "Registration successful!", "registration_id": cursor.lastrowid}), 201

@app.get("/api/organizer/events")
@organizer_required
def api_organizer_events():
    rows = get_db().execute("""
        SELECT e.*, COUNT(r.id) AS registered_count, (e.capacity-COUNT(r.id)) AS seats_left
        FROM events e LEFT JOIN registrations r ON r.event_id=e.id
        WHERE e.organizer_id=? GROUP BY e.id ORDER BY e.event_date
    """, (session["organizer_id"],)).fetchall()
    return jsonify([dict(row) for row in rows])

@app.get("/api/organizer/events/<int:event_id>/registrations")
@organizer_required
def api_event_registrations(event_id):
    event = get_db().execute(
        "SELECT id FROM events WHERE id=? AND organizer_id=?",
        (event_id, session["organizer_id"])
    ).fetchone()
    if not event:
        return jsonify({"error": "Event not found."}), 404
    rows = get_db().execute("""
        SELECT id, full_name, email, phone, registered_at
        FROM registrations WHERE event_id=? ORDER BY registered_at DESC
    """, (event_id,)).fetchall()
    return jsonify([dict(row) for row in rows])

@app.post("/api/organizer/events")
@organizer_required
def api_create_event():
    data = request.get_json(silent=True) or request.form.to_dict()
    error = validate_event(data)
    if error:
        return jsonify({"error": error}), 400
    db = get_db()
    organizer = db.execute("SELECT name FROM organizers WHERE id=?", (session["organizer_id"],)).fetchone()
    cursor = db.execute("""
        INSERT INTO events (title, category, description, event_date, event_time, location,
                            venue, capacity, organizer_id, organizer_name, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
    """, (data["title"].strip(), data["category"].strip(), data["description"].strip(),
          data["event_date"], data["event_time"], data["location"].strip(), data["venue"].strip(),
          int(data["capacity"]), session["organizer_id"], organizer["name"]))
    db.commit()
    return jsonify({"message": "Event created successfully.", "event_id": cursor.lastrowid}), 201

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
