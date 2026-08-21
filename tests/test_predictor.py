"""
Tests for the CricketPredictor inference service.
"""
import os
import pytest

from app.services.predictor import CricketPredictor
from app.services.data_generator import FORMAT_CONFIG
from app.services.model_trainer import PREDICTION_TARGETS


@pytest.fixture
def predictor(models_dir):
    return CricketPredictor(models_dir)


class TestCricketPredictorLoad:
    def test_models_loaded(self, predictor):
        assert bool(predictor.models)

    def test_all_formats_loaded(self, predictor):
        for fmt in FORMAT_CONFIG:
            assert fmt in predictor.models

    def test_all_targets_loaded_for_t20(self, predictor):
        for target in PREDICTION_TARGETS:
            assert target in predictor.models["t20"]

    def test_metrics_loaded(self, predictor):
        assert bool(predictor.metrics)


class TestCricketPredictorPredict:
    """Test prediction output contract."""

    def _sample_features(self, fmt="t20", target="runs_in_over"):
        return predictor_defaults(fmt, target)

    def test_predict_returns_dict(self, predictor):
        feats = {"over_number": 10, "wickets_fallen": 3,
                 "batsman_avg": 35, "bowler_econ": 8.0,
                 "strike_rate": 130, "match_phase": 1}
        result = predictor.predict("t20", "runs_in_over", feats)
        assert isinstance(result, dict)

    def test_predict_has_required_keys(self, predictor):
        feats = {"over_number": 10, "wickets_fallen": 3,
                 "batsman_avg": 35, "bowler_econ": 8.0,
                 "strike_rate": 130, "match_phase": 1}
        result = predictor.predict("t20", "runs_in_over", feats)
        for key in ("format", "target", "predictions", "best_model"):
            assert key in result

    def test_predictions_non_negative(self, predictor):
        feats = {"over_number": 10, "wickets_fallen": 3,
                 "batsman_avg": 35, "bowler_econ": 8.0,
                 "strike_rate": 130, "match_phase": 1}
        result = predictor.predict("t20", "runs_in_over", feats)
        for model_name, pred in result["predictions"].items():
            if "error" not in pred:
                assert pred["value"] >= 0

    def test_predict_invalid_format_returns_error(self, predictor):
        result = predictor.predict("invalid_fmt", "runs_in_over", {})
        assert "error" in result

    def test_predict_all_formats(self, predictor):
        feats = {"over_number": 5, "wickets_fallen": 2,
                 "batsman_avg": 32, "bowler_econ": 7.5,
                 "strike_rate": 125, "match_phase": 0}
        for fmt in FORMAT_CONFIG:
            result = predictor.predict(fmt, "runs_in_over", feats)
            assert "predictions" in result

    def test_three_predictions_returned(self, predictor):
        feats = {"over_number": 10, "wickets_fallen": 3,
                 "batsman_avg": 35, "bowler_econ": 8.0,
                 "strike_rate": 130, "match_phase": 1}
        result = predictor.predict("t20", "runs_in_over", feats)
        assert len(result["predictions"]) == 3

    def test_best_model_is_one_of_predictions(self, predictor):
        feats = {"over_number": 10, "wickets_fallen": 3,
                 "batsman_avg": 35, "bowler_econ": 8.0,
                 "strike_rate": 130, "match_phase": 1}
        result = predictor.predict("t20", "runs_in_over", feats)
        if result["best_model"]:
            assert result["best_model"] in result["predictions"]


class TestFeatureHelpers:
    def test_get_feature_defaults_returns_dict(self, predictor):
        defaults = predictor.get_feature_defaults("t20", "runs_in_over")
        assert isinstance(defaults, dict)
        assert len(defaults) > 0

    def test_get_feature_defaults_all_formats(self, predictor):
        for fmt in FORMAT_CONFIG:
            defaults = predictor.get_feature_defaults(fmt, "runs_in_over")
            assert isinstance(defaults, dict)

    def test_get_feature_labels_returns_dict(self, predictor):
        labels = predictor.get_feature_labels()
        assert isinstance(labels, dict)
        assert "over_number" in labels

    def test_get_feature_ranges_returns_dict(self, predictor):
        """Ranges must exist for all feature columns."""
        ranges = predictor.get_feature_ranges("t20", "runs_in_over")
        assert isinstance(ranges, dict)
        for col in PREDICTION_TARGETS["runs_in_over"]["feature_cols"]:
            assert col in ranges
            assert "min" in ranges[col]
            assert "max" in ranges[col]
