# Evently – Event Registration System (Week 4)

A full-stack event discovery and registration application built with HTML, CSS, JavaScript, Python Flask and SQLite.

## Features
- Event listing cards with date, time, category, venue and available seats.
- Search events by title, description and organizer.
- Filters for category, location and event date.
- Event details and participant registration.
- Backend validation for name, email and phone.
- Duplicate registration prevention for the same event and email.
- Seat-limit enforcement; full events cannot accept more registrations.
- Organizer login and dashboard.
- Organizer can create events and view participant details.
- SQLite database and JSON REST API.
- Responsive desktop and mobile interface.

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows PowerShell
1. Extract the ZIP and open the `Event_Registration_System_Week4` folder in VS Code.
2. Open the integrated terminal and run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

3. Open `http://127.0.0.1:5000`.

The database and sample events are created automatically on first run.

## Demo organizer login
- Email: `organizer@example.com`
- Password: `Organizer@123`

Change the demo password and set a strong `SECRET_KEY` before deploying publicly. This starter app uses a development secret by default.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/events` | List/search/filter open events |
| GET | `/api/events/<id>` | Event details and available seats |
| POST | `/api/register` | Register a participant |
| GET | `/api/organizer/events` | Organizer's events (login required) |
| GET | `/api/organizer/events/<id>/registrations` | Participants for an owned event (login required) |
| POST | `/api/organizer/events` | Create an event (login required) |
| GET | `/health` | Health check |

## Run tests
```powershell
python -m unittest discover -s tests -v
```

## Project structure
```text
Event_Registration_System_Week4/
├── app.py
├── database.py
├── validators.py
├── requirements.txt
├── README.md
├── test_cases.md
├── templates/
├── static/
├── database/
│   └── .gitkeep
└── tests/
    └── test_app.py
```

## Notes
- Sample events and organizer credentials are demo data.
- This is an educational starter project. Before public production deployment, add CSRF protection, rate limiting, stronger session configuration, email verification and deployment secrets.
