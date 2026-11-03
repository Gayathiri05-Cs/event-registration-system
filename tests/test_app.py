import os
import tempfile
import unittest
import database
import app as app_module

class EventSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.original_db = database.DATABASE
        database.DATABASE = os.path.join(cls.temp_dir.name, "test.db")
        app_module.app.config["TESTING"] = True
        app_module.app.config["SECRET_KEY"] = "test-secret"
        with app_module.app.app_context():
            database.init_db()
        cls.client = app_module.app.test_client()

    @classmethod
    def tearDownClass(cls):
        database.DATABASE = cls.original_db
        cls.temp_dir.cleanup()

    def test_home(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_events_list(self):
        response = self.client.get("/api/events")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()), 0)

    def test_event_not_found(self):
        self.assertEqual(self.client.get("/api/events/9999").status_code, 404)

    def test_invalid_registration(self):
        response = self.client.post("/api/register", json={
            "event_id": 1, "full_name": "Test", "email": "bad", "phone": "123"
        })
        self.assertEqual(response.status_code, 400)

    def test_successful_registration(self):
        response = self.client.post("/api/register", json={
            "event_id": 1, "full_name": "Test Person",
            "email": "unique-test@example.com", "phone": "9876543210"
        })
        self.assertEqual(response.status_code, 201)

    def test_duplicate_registration(self):
        payload = {"event_id": 2, "full_name": "Test Person",
                   "email": "same@example.com", "phone": "9876543210"}
        self.assertEqual(self.client.post("/api/register", json=payload).status_code, 201)
        self.assertEqual(self.client.post("/api/register", json=payload).status_code, 409)

    def test_organizer_requires_login(self):
        self.assertEqual(self.client.get("/api/organizer/events").status_code, 401)

    def test_organizer_login(self):
        response = self.client.post("/organizer/login", data={
            "email": "organizer@example.com", "password": "Organizer@123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your event dashboard", response.data)

    def test_create_event(self):
        self.client.post("/organizer/login", data={
            "email": "organizer@example.com", "password": "Organizer@123"
        })
        response = self.client.post("/api/organizer/events", json={
            "title": "Test Event", "category": "Technology",
            "description": "A test event description.", "event_date": "2027-02-01",
            "event_time": "10:00 AM", "location": "Chennai",
            "venue": "Test Hall", "capacity": 20
        })
        self.assertEqual(response.status_code, 201)

    def test_health(self):
        self.assertEqual(self.client.get("/health").get_json()["status"], "ok")

if __name__ == "__main__":
    unittest.main()
