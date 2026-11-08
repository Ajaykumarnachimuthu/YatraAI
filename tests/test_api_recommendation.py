"""
Test Suite: Yatra AI API & Recommendation Engine (Standard library unittest)
Tests:
1. Health check endpoint & model metadata
2. Supported corridors endpoint
3. Personas archetype definitions & Travel DNA vectors
4. Hard constraint enforcement (origin==destination, invalid city)
5. Time-Sensitive vs Cost-Sensitive traveller recommendation response
6. Continuous ML probability score ranking & tau=0.30 preference threshold
7. Determinism under fixed seed
8. Non-empty, grounded feature explanations
"""

import os
import sys

# Silence joblib/loky Windows CPU count warning
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

import unittest
from fastapi.testclient import TestClient

# Ensure repository root is on Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.api import app


class TestYatraRecommendationAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        """Verifies that /api/health responds with healthy status and champion model details."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["model_family"], "HistGradientBoostingClassifier")
        self.assertEqual(data["feature_configuration"].lower(), "core")
        self.assertEqual(data["decision_threshold"], 0.30)
        self.assertEqual(data["supported_metro_hubs"], 6)

    def test_web_index_and_static(self):
        """Verifies that the web frontend UI and static assets are served properly."""
        index_res = self.client.get("/")
        self.assertEqual(index_res.status_code, 200)
        self.assertIn("YĀTRĀ", index_res.text)
        self.assertIn("Travel DNA", index_res.text)

        css_res = self.client.get("/static/styles.css")
        self.assertEqual(css_res.status_code, 200)
        self.assertIn("--bg-primary", css_res.text)

        js_res = self.client.get("/static/app.js")
        self.assertEqual(js_res.status_code, 200)
        self.assertIn("DOMContentLoaded", js_res.text)

    def test_corridors_endpoint(self):
        """Verifies that /api/corridors returns the 6 metro hubs and 30 directed corridors."""
        response = self.client.get("/api/corridors")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["metro_cities"]), 6)
        self.assertEqual(data["corridors_count"], 30)
        self.assertIn({"origin": "Delhi", "destination": "Mumbai"}, data["corridors"])

    def test_personas_endpoint(self):
        """Verifies that /api/personas returns 6 archetypes with 7-D Travel DNA vectors."""
        response = self.client.get("/api/personas")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        personas = data["personas"]
        self.assertEqual(len(personas), 6)
        for p in personas:
            self.assertIn("persona_name", p)
            dna = p["travel_dna"]
            self.assertEqual(len(dna), 7)
            for dim, val in dna.items():
                self.assertTrue(0.0 <= val <= 1.0)

    def test_hard_constraint_same_city(self):
        """Verifies that queries with identical origin and destination are rejected before ML scoring."""
        payload = {
            "origin_city": "Delhi",
            "destination_city": "Delhi",
            "departure_window": "Morning",
        }
        response = self.client.post("/api/recommend", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Origin and destination cannot be the same city", response.json()["detail"])

    def test_hard_constraint_invalid_city(self):
        """Verifies that queries with unsupported city names are rejected before ML scoring."""
        payload = {
            "origin_city": "London",
            "destination_city": "Mumbai",
        }
        response = self.client.post("/api/recommend", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid origin city", response.json()["detail"])

    def test_recommendation_time_sensitive(self):
        """Verifies end-to-end recommendation workflow for a time-sensitive traveller."""
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
        response = self.client.post("/api/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["total_candidates"], 2)

        itineraries = data["itineraries"]
        self.assertEqual(len(itineraries), data["total_candidates"])

        probs = [it["ml_personalization_score"] for it in itineraries]
        self.assertEqual(probs, sorted(probs, reverse=True))

        top = data["recommended_journey"]
        self.assertEqual(top["rank"], 1)
        self.assertTrue(top["is_recommended"])
        self.assertEqual(top["ml_personalization_score"], probs[0])
        self.assertGreater(len(top["feature_reasons"]), 0)

    def test_recommendation_cost_sensitive_shifts_preferences(self):
        """Verifies that changing Travel DNA from Time-Sensitive to Cost-Sensitive alters candidate scores."""
        seed = 42

        req_time = {
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "departure_window": "Morning",
            "trip_purpose": "Business",
            "party_size": 1,
            "lead_days": 10,
            "travel_dna": {
                "cost_sensitivity": 0.05,
                "time_sensitivity": 0.95,
                "reliability_sensitivity": 0.90,
                "comfort_preference": 0.80,
                "transfer_tolerance": 0.10,
                "departure_time_flexibility": 0.20,
                "sustainability_preference": 0.10,
            },
            "seed": seed,
        }
        res_time = self.client.post("/api/recommend", json=req_time).json()

        req_cost = {
            "origin_city": "Delhi",
            "destination_city": "Mumbai",
            "departure_window": "Morning",
            "trip_purpose": "Commute",
            "party_size": 1,
            "lead_days": 10,
            "travel_dna": {
                "cost_sensitivity": 0.95,
                "time_sensitivity": 0.05,
                "reliability_sensitivity": 0.50,
                "comfort_preference": 0.10,
                "transfer_tolerance": 0.80,
                "departure_time_flexibility": 0.80,
                "sustainability_preference": 0.50,
            },
            "seed": seed,
        }
        res_cost = self.client.post("/api/recommend", json=req_cost).json()

        top_time = res_time["recommended_journey"]
        top_cost = res_cost["recommended_journey"]

        self.assertNotEqual(top_time["ml_personalization_score"], top_cost["ml_personalization_score"])

        expensive_flight_cost_prob = next(
            (it["ml_personalization_score"] for it in res_cost["itineraries"] if it["mode"] == "Flight"), None
        )
        expensive_flight_time_prob = next(
            (it["ml_personalization_score"] for it in res_time["itineraries"] if it["mode"] == "Flight"), None
        )
        if expensive_flight_cost_prob is not None and expensive_flight_time_prob is not None:
            self.assertLess(expensive_flight_cost_prob, expensive_flight_time_prob)

    def test_recommendation_determinism(self):
        """Verifies that calling the recommendation engine with identical inputs yields identical scores."""
        payload = {
            "origin_city": "Bangalore",
            "destination_city": "Chennai",
            "departure_window": "Evening",
            "trip_purpose": "Leisure",
            "party_size": 2,
            "lead_days": 5,
            "travel_dna": {
                "cost_sensitivity": 0.6,
                "time_sensitivity": 0.6,
                "reliability_sensitivity": 0.7,
                "comfort_preference": 0.5,
                "transfer_tolerance": 0.4,
                "departure_time_flexibility": 0.5,
                "sustainability_preference": 0.8,
            },
            "seed": 99,
        }
        res1 = self.client.post("/api/recommend", json=payload).json()
        res2 = self.client.post("/api/recommend", json=payload).json()

        self.assertEqual(res1["recommended_journey"]["service_identifier"], res2["recommended_journey"]["service_identifier"])
        self.assertEqual(res1["recommended_journey"]["ml_personalization_score"], res2["recommended_journey"]["ml_personalization_score"])


if __name__ == "__main__":
    unittest.main()
