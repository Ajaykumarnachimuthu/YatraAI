"""
Test Suite: Full-Stack Backend Services
Tests:
1. User registration & duplicate check
2. User authentication & JWT token issuance
3. Authenticated profile retrieval & Travel DNA updates
4. Search session persistence & session_id assignment
5. Closed-loop choice feedback logging & summary metrics
6. Saved trips lifecycle (Create, List, Delete)
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.db.session import init_db


class TestFullStackBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.test_email = "traveller@yatra-ai.org"
        cls.test_password = "SecurePassword123!"

    def test_01_user_registration_and_login_flow(self):
        """Tests complete user lifecycle: Registration -> Token Issuance -> Profile -> Update DNA."""
        # 1. Register user
        reg_payload = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": "Arjun Sharma",
            "travel_dna": {
                "cost_sensitivity": 0.30,
                "time_sensitivity": 0.85,
                "reliability_sensitivity": 0.90,
                "comfort_preference": 0.75,
                "transfer_tolerance": 0.20,
                "departure_time_flexibility": 0.40,
                "sustainability_preference": 0.60,
            },
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        if res_reg.status_code == 400:
            # User already exists from previous run, login instead
            pass
        else:
            self.assertEqual(res_reg.status_code, 201)
            reg_data = res_reg.json()
            self.assertIn("access_token", reg_data)
            self.assertEqual(reg_data["user"]["email"], self.test_email)

        # 2. Login user
        login_payload = {
            "email": self.test_email,
            "password": self.test_password,
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.json()
        self.assertIn("access_token", login_data)
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Retrieve authenticated profile
        res_me = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], self.test_email)

        # 4. Update Travel DNA
        dna_update = {
            "travel_dna": {
                "cost_sensitivity": 0.20,
                "time_sensitivity": 0.90,
                "reliability_sensitivity": 0.95,
                "comfort_preference": 0.80,
                "transfer_tolerance": 0.15,
                "departure_time_flexibility": 0.30,
                "sustainability_preference": 0.70,
            }
        }
        res_update = self.client.put("/api/auth/dna", json=dna_update, headers=headers)
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()["travel_dna"]["time_sensitivity"], 0.90)

    def test_02_recommendation_persistence_and_session_id(self):
        """Verifies that executing a recommendation saves a SearchSession with valid ID."""
        payload = {
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "departure_window": "Morning",
            "trip_purpose": "Business",
            "party_size": 1,
            "lead_days": 7,
            "travel_dna": {
                "cost_sensitivity": 0.10,
                "time_sensitivity": 0.95,
                "reliability_sensitivity": 0.90,
                "comfort_preference": 0.85,
                "transfer_tolerance": 0.10,
                "departure_time_flexibility": 0.20,
                "sustainability_preference": 0.20,
            },
            "seed": 42,
        }
        res = self.client.post("/api/recommend", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("session_id", data)
        self.assertIsNotNone(data["session_id"])
        self.assertGreater(data["session_id"], 0)

        # Store session_id for feedback test
        self.__class__.created_session_id = data["session_id"]

    def test_03_choice_feedback_recording(self):
        """Verifies that feedback tracking records choice decisions and updates summary metrics."""
        session_id = getattr(self.__class__, "created_session_id", 1)
        feedback_payload = {
            "session_id": session_id,
            "selected_rank": 1,
            "selected_mode": "Flight",
            "action_type": "selected",
            "user_comment": "Optimal balance of flight duration and departure schedule.",
        }
        res_fb = self.client.post("/api/feedback", json=feedback_payload)
        self.assertEqual(res_fb.status_code, 201)
        fb_data = res_fb.json()
        self.assertEqual(fb_data["session_id"], session_id)
        self.assertEqual(fb_data["selected_rank"], 1)

        # Verify summary
        res_sum = self.client.get("/api/feedback/summary")
        self.assertEqual(res_sum.status_code, 200)
        summary = res_sum.json()
        self.assertGreaterEqual(summary["total_feedback_events"], 1)
        self.assertGreaterEqual(summary["champion_rank_1_selections"], 1)

    def test_04_saved_trips_flow(self):
        """Verifies authenticated trip saving, retrieval, and deletion."""
        # 1. Login to get token
        login_payload = {
            "email": self.test_email,
            "password": self.test_password,
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Save trip
        trip_payload = {
            "session_id": 1,
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "mode": "Flight",
            "carrier": "Vistara",
            "service_identifier": "UK-815",
            "service_tier": "Business",
            "cost_inr": 53164.0,
            "duration_hours": 12.67,
            "departure_window": "Morning",
            "notes": "Booked for executive conference.",
        }
        res_save = self.client.post("/api/trips", json=trip_payload, headers=headers)
        self.assertEqual(res_save.status_code, 201)
        trip_id = res_save.json()["id"]

        # 3. List trips
        res_list = self.client.get("/api/trips", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        trips = res_list.json()
        self.assertTrue(any(t["id"] == trip_id for t in trips))

        # 4. Delete trip
        res_del = self.client.delete(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(res_del.status_code, 204)

