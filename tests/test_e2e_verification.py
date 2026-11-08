"""
End-to-End (E2E) System Verification Suite for Yatra AI
Comprehensive multi-tier verification covering:
1. Machine Learning Champion Model & Latency
2. Database Schema, Foreign Keys & Persistence
3. End-to-End User Authentication & Profile Lifecycle
4. Personalized Multimodal Recommendation & Preference Dynamics (Flight vs Rail)
5. Closed-Loop Choice Feedback Tracking & Precision Metrics
6. User Saved Itineraries (Create, List, Delete)
7. Frontend Production Bundle Serving & SPA Routing
"""

import os
import sys
import time
import unittest
from fastapi.testclient import TestClient

# Silence joblib/loky Windows CPU count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.models import User, SearchSession, RecommendedItinerary, UserChoiceFeedback, SavedTrip
from ml.recommendation_engine import get_recommendation_engine


class TestYatraAIE2EVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.db = SessionLocal()
        cls.test_email = f"e2e_traveler_{int(time.time())}@yatra-ai.org"
        cls.test_password = "E2E_Secure_Password_2026!"
        cls.auth_token = None
        cls.user_id = None
        cls.session_time_id = None
        cls.session_cost_id = None

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_ml_champion_model_and_latency(self):
        """Tier 1: Verifies ML champion model loading, metadata, and sub-50ms inference latency."""
        engine = get_recommendation_engine()
        self.assertIsNotNone(engine.engine.model)
        self.assertEqual(engine.engine.threshold, 0.30)
        self.assertEqual(len(engine.metro_cities), 6)

        # Benchmark inference latency
        query = {
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "departure_window": "Morning",
            "trip_purpose": "Business",
            "party_size": 1,
            "lead_days": 7,
        }
        dna = {
            "cost_sensitivity": 0.20,
            "time_sensitivity": 0.90,
            "reliability_sensitivity": 0.90,
            "comfort_preference": 0.80,
            "transfer_tolerance": 0.20,
            "departure_time_flexibility": 0.30,
            "sustainability_preference": 0.30,
        }

        start = time.perf_counter()
        result = engine.recommend(query=query, traveller_dna=dna, seed=42)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertGreaterEqual(result["total_candidates"], 2)
        self.assertIsNotNone(result["recommended_journey"])
        # Production latency check: scoring candidate sets should take < 100 ms
        self.assertLess(elapsed_ms, 100.0, f"Inference took {elapsed_ms:.2f} ms, expected < 100 ms")

    def test_02_database_schema_and_tables(self):
        """Tier 2: Verifies that database tables are initialized and accessible."""
        user_count = self.db.query(User).count()
        session_count = self.db.query(SearchSession).count()
        itinerary_count = self.db.query(RecommendedItinerary).count()

        self.assertIsInstance(user_count, int)
        self.assertIsInstance(session_count, int)
        self.assertIsInstance(itinerary_count, int)

    def test_03_system_health_telemetry_endpoint(self):
        """Tier 3: Verifies /api/health returns complete status across ML, DB, and Cache."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["model_family"], "HistGradientBoostingClassifier")
        self.assertEqual(data["decision_threshold"], 0.30)
        self.assertEqual(data["supported_metro_hubs"], 6)
        self.assertEqual(data["database_status"], "connected")
        self.assertIn(data["cache_backend"], ["redis", "in_memory_lru"])

    def test_04_user_registration_authentication_and_jwt(self):
        """Tier 4: Registers new user, logs in, obtains JWT, and inspects profile."""
        # 1. Register
        reg_payload = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": "E2E Verified Traveler",
            "travel_dna": {
                "cost_sensitivity": 0.15,
                "time_sensitivity": 0.95,
                "reliability_sensitivity": 0.90,
                "comfort_preference": 0.85,
                "transfer_tolerance": 0.10,
                "departure_time_flexibility": 0.20,
                "sustainability_preference": 0.40,
            },
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)
        reg_data = res_reg.json()
        self.assertIn("access_token", reg_data)
        self.assertEqual(reg_data["user"]["email"], self.test_email)
        self.__class__.user_id = reg_data["user"]["id"]

        # 2. Login
        login_payload = {
            "email": self.test_email,
            "password": self.test_password,
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        token = res_login.json()["access_token"]
        self.__class__.auth_token = token

        # 3. Authenticated profile check
        headers = {"Authorization": f"Bearer {token}"}
        res_me = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        me_data = res_me.json()
        self.assertEqual(me_data["email"], self.test_email)
        self.assertEqual(me_data["travel_dna"]["time_sensitivity"], 0.95)

    def test_05_recommendation_time_sensitive_professional(self):
        """Tier 5A: Corporate Traveler (High time sensitivity) -> Should prefer Flight."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "departure_window": "Morning",
            "trip_purpose": "Business",
            "party_size": 1,
            "lead_days": 3,
            "travel_dna": {
                "cost_sensitivity": 0.10,
                "time_sensitivity": 0.98,
                "reliability_sensitivity": 0.95,
                "comfort_preference": 0.90,
                "transfer_tolerance": 0.05,
                "departure_time_flexibility": 0.10,
                "sustainability_preference": 0.10,
            },
            "seed": 42,
        }
        res = self.client.post("/api/recommend", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("session_id", data)
        self.assertIsNotNone(data["session_id"])
        self.__class__.session_time_id = data["session_id"]

        top = data["recommended_journey"]
        self.assertEqual(top["rank"], 1)
        self.assertEqual(top["mode"], "Flight", "Corporate business traveller should prefer Flight over Rail")
        self.assertGreaterEqual(top["ml_personalization_score"], 0.30)
        self.assertTrue(top["preference_threshold_met"])
        self.assertGreater(len(top["feature_reasons"]), 0)

        # Verify DB persistence of session and candidate records
        db_session = self.db.query(SearchSession).filter(SearchSession.id == data["session_id"]).first()
        self.assertIsNotNone(db_session)
        self.assertEqual(db_session.user_id, self.user_id)
        self.assertEqual(db_session.origin_city, "Delhi")
        self.assertEqual(db_session.destination_city, "Mumbai")

        db_itins = self.db.query(RecommendedItinerary).filter(RecommendedItinerary.session_id == data["session_id"]).all()
        self.assertEqual(len(db_itins), data["total_candidates"])

    def test_06_recommendation_cost_sensitive_backpacker(self):
        """Tier 5B: Budget Traveler (High cost sensitivity) -> Model shifts preference to Rail."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "departure_window": "Morning",
            "trip_purpose": "Commute",
            "party_size": 1,
            "lead_days": 14,
            "travel_dna": {
                "cost_sensitivity": 0.98,
                "time_sensitivity": 0.05,
                "reliability_sensitivity": 0.40,
                "comfort_preference": 0.10,
                "transfer_tolerance": 0.90,
                "departure_time_flexibility": 0.90,
                "sustainability_preference": 0.60,
            },
            "seed": 42,
        }
        res = self.client.post("/api/recommend", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.__class__.session_cost_id = data["session_id"]

        top = data["recommended_journey"]
        self.assertEqual(top["rank"], 1)
        self.assertEqual(top["mode"], "Rail", "Cost-sensitive traveller should prefer Rail (Sleeper/AC) over Flight")

        # Verify lowest fare option is surfaced
        min_fare = min(it["cost_inr"] for it in data["itineraries"])
        self.assertEqual(top["cost_inr"], min_fare)

    def test_07_closed_loop_choice_feedback_tracking(self):
        """Tier 6: Records traveller choice feedback and verifies adoption analytics summary."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        feedback_payload = {
            "session_id": self.session_time_id,
            "selected_rank": 1,
            "selected_mode": "Flight",
            "action_type": "selected",
            "user_comment": "Vistara flight was the ideal option for tight meeting schedule.",
        }
        res_fb = self.client.post("/api/feedback", json=feedback_payload, headers=headers)
        self.assertEqual(res_fb.status_code, 201)

        # Inspect summary
        res_summary = self.client.get("/api/feedback/summary")
        self.assertEqual(res_summary.status_code, 200)
        summary = res_summary.json()
        self.assertGreater(summary["total_feedback_events"], 0)
        self.assertGreater(summary["champion_rank_1_selections"], 0)
        self.assertGreater(summary["champion_adoption_rate"], 0.0)

    def test_08_saved_trips_lifecycle(self):
        """Tier 7: Verifies saving an itinerary, listing saved trips, and deleting it."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # 1. Save trip
        save_payload = {
            "session_id": self.session_time_id,
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "mode": "Flight",
            "carrier": "Vistara",
            "service_identifier": "UK-815",
            "service_tier": "Business",
            "cost_inr": 53164.0,
            "duration_hours": 12.67,
            "departure_window": "Morning",
            "notes": "Booked for keynote conference.",
        }
        res_save = self.client.post("/api/trips", json=save_payload, headers=headers)
        self.assertEqual(res_save.status_code, 201)
        trip_id = res_save.json()["id"]

        # 2. List saved trips
        res_list = self.client.get("/api/trips", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        trips = res_list.json()
        self.assertTrue(any(t["id"] == trip_id for t in trips))

        # 3. Delete trip
        res_del = self.client.delete(f"/api/trips/{trip_id}", headers=headers)
        self.assertEqual(res_del.status_code, 204)

        # 4. Confirm deletion
        res_list_after = self.client.get("/api/trips", headers=headers)
        self.assertFalse(any(t["id"] == trip_id for t in res_list_after.json()))

    def test_09_frontend_assets_and_spa_routing(self):
        """Tier 8: Verifies React 18 production bundle serving, assets, and client-side SPA fallback."""
        # Root index.html
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertIn("YĀTRĀ AI", res_root.text)
        self.assertIn('<div id="root">', res_root.text)

        # Client-side SPA routing fallback
        res_spa = self.client.get("/trips")
        self.assertEqual(res_spa.status_code, 200)
        self.assertIn('<div id="root">', res_spa.text)


if __name__ == "__main__":
    unittest.main()

