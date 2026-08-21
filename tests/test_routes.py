"""
Integration tests for all Flask routes.
"""
import json
import pytest


class TestWebRoutes:
    """Test all HTML-rendering routes return 200."""

    def test_home_page(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Cricket Predictor Pro" in resp.data

    def test_predict_page_t20(self, client):
        resp = client.get("/predict/t20")
        assert resp.status_code == 200

    def test_predict_page_t10(self, client):
        resp = client.get("/predict/t10")
        assert resp.status_code == 200

    def test_predict_page_odi(self, client):
        resp = client.get("/predict/odi")
        assert resp.status_code == 200

    def test_predict_page_test(self, client):
        resp = client.get("/predict/test")
        assert resp.status_code == 200

    def test_predict_page_invalid_fmt_falls_back(self, client):
        resp = client.get("/predict/invalid_fmt")
        assert resp.status_code == 200  # falls back to t20

    def test_compare_page(self, client):
        resp = client.get("/compare")
        assert resp.status_code == 200

    def test_profile_page(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 200

    def test_about_page(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_history_page(self, client):
        resp = client.get("/history")
        assert resp.status_code == 200

    def test_simulate_page_t20(self, client):
        resp = client.get("/simulate/t20")
        assert resp.status_code == 200

    def test_player_compare_page(self, client):
        resp = client.get("/compare/players")
        assert resp.status_code == 200


class TestAPIRoutes:
    """Test all JSON API routes."""

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "status" in data
        assert data["status"] == "ok"

    def test_api_formats(self, client):
        resp = client.get("/api/formats")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert set(data.keys()) == {"t10", "t20", "odi", "test"}

    def test_api_targets(self, client):
        resp = client.get("/api/targets")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 6

    def test_api_defaults_t20_runs(self, client):
        resp = client.get("/api/defaults/t20/runs_in_over")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "defaults" in data
        assert "labels" in data

    def test_api_ranges(self, client):
        resp = client.get("/api/ranges/t20/runs_in_over")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "ranges" in data

    def test_api_predict_valid(self, client):
        payload = {
            "format": "t20",
            "target": "runs_in_over",
            "features": {
                "over_number": 15,
                "wickets_fallen": 3,
                "batsman_avg": 38,
                "bowler_econ": 8.5,
                "strike_rate": 135,
                "match_phase": 2,
            }
        }
        resp = client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "predictions" in data

    def test_api_predict_invalid_format(self, client):
        payload = {"format": "xyz", "target": "runs_in_over", "features": {}}
        resp = client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_api_predict_invalid_target(self, client):
        payload = {"format": "t20", "target": "fake_target", "features": {}}
        resp = client.post(
            "/api/predict",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_api_predict_missing_body(self, client):
        resp = client.post("/api/predict", content_type="application/json")
        assert resp.status_code == 400

    def test_api_docs_page(self, client):
        resp = client.get("/api/docs")
        assert resp.status_code == 200


class TestSecurityHeaders:
    """Verify security headers are present on every response."""

    def test_x_frame_options(self, client):
        resp = client.get("/")
        assert resp.headers.get("X-Frame-Options") == "SAMEORIGIN"

    def test_x_content_type_options(self, client):
        resp = client.get("/")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_xss_protection(self, client):
        resp = client.get("/")
        assert "X-XSS-Protection" in resp.headers

    def test_referrer_policy(self, client):
        resp = client.get("/")
        assert "Referrer-Policy" in resp.headers

    def test_permissions_policy(self, client):
        resp = client.get("/")
        assert "Permissions-Policy" in resp.headers


class TestErrorHandlers:
    """Test 404 and 500 error handlers."""

    def test_404_returns_error_page(self, client):
        resp = client.get("/nonexistent-page-xyz")
        assert resp.status_code == 404
        assert b"404" in resp.data

    def test_predict_post_with_form(self, client):
        resp = client.post(
            "/predict/t20",
            data={
                "target_key": "runs_in_over",
                "over_number": "12",
                "wickets_fallen": "3",
                "batsman_avg": "35",
                "bowler_econ": "8",
                "strike_rate": "130",
                "match_phase": "1",
            }
        )
        assert resp.status_code == 200
