import os
import sqlite3
from flask import g

DATABASE = "database/events.db"

SAMPLE_EVENTS = [
    ("AI & Innovation Workshop", "Technology", "A beginner-friendly workshop covering practical AI concepts, responsible AI and hands-on demonstrations.", "2026-12-12", "10:00 AM", "Chennai", "Main Auditorium", 100, "Campus Events Team", "Open"),
    ("Web Development Bootcamp", "Technology", "Build a responsive website and learn the basics of HTML, CSS and JavaScript with guided activities.", "2026-12-18", "09:30 AM", "Chennai", "Computer Lab 2", 60, "Tech Club", "Open"),
    ("Startup Pitch Day", "Entrepreneurship", "Present ideas, receive mentor feedback and connect with student founders and local entrepreneurs.", "2026-12-20", "11:00 AM", "Coimbatore", "Innovation Hall", 80, "E-Cell", "Open"),
    ("Career Readiness Seminar", "Career", "Learn resume writing, interview preparation, networking and internship search strategies.", "2026-12-22", "02:00 PM", "Bengaluru", "Seminar Hall A", 120, "Placement Cell", "Open"),
    ("Design Thinking Challenge", "Design", "A collaborative design sprint focused on identifying user problems and creating simple prototypes.", "2026-12-28", "10:00 AM", "Chennai", "Innovation Lab", 45, "Design Society", "Open"),
    ("Python Coding Contest", "Competition", "Solve beginner and intermediate Python problems in a friendly timed coding contest.", "2027-01-05", "09:00 AM", "Online", "Virtual Event", 200, "Coding Club", "Open")
]

def get_db():
    if "db" not in g:
        os.makedirs("database", exist_ok=True)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs("database", exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("""CREATE TABLE IF NOT EXISTS organizers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        event_date TEXT NOT NULL,
        event_time TEXT NOT NULL,
        location TEXT NOT NULL,
        venue TEXT NOT NULL,
        capacity INTEGER NOT NULL CHECK(capacity > 0),
        organizer_id INTEGER NOT NULL,
        organizer_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open',
        FOREIGN KEY (organizer_id) REFERENCES organizers(id)
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events(id)
    )""")
    organizer = db.execute("SELECT id FROM organizers WHERE email=?", ("organizer@example.com",)).fetchone()
    if not organizer:
        from werkzeug.security import generate_password_hash
        cursor = db.execute("INSERT INTO organizers (name,email,password_hash) VALUES (?,?,?)",
                            ("Demo Organizer", "organizer@example.com", generate_password_hash("Organizer@123")))
        organizer_id = cursor.lastrowid
    else:
        organizer_id = organizer[0]
    count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if count == 0:
        db.executemany("""INSERT INTO events
            (title,category,description,event_date,event_time,location,venue,capacity,organizer_id,organizer_name,status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            [(*event[:8], organizer_id, event[8], event[9]) for event in SAMPLE_EVENTS])
    db.commit()
    db.close()
