"""
Tests for the model trainer service.
"""
import os
import tempfile
import pytest

from app.services.data_generator import get_all_format_data
from app.services.model_trainer import (
    PREDICTION_TARGETS,
    get_models,
    train_single_target,
    train_all_models,
)


class TestPredictionTargets:
    """Test PREDICTION_TARGETS structure."""

    REQUIRED_TARGET_KEYS = {"name", "description", "data_type", "target_col", "feature_cols", "icon"}

    def test_six_targets_defined(self):
        assert len(PREDICTION_TARGETS) == 6

    def test_all_required_keys_present(self):
        for key, info in PREDICTION_TARGETS.items():
            for rk in self.REQUIRED_TARGET_KEYS:
                assert rk in info, f"Missing '{rk}' in target '{key}'"

    def test_feature_cols_non_empty(self):
        for key, info in PREDICTION_TARGETS.items():
            assert len(info["feature_cols"]) > 0, f"No feature_cols in '{key}'"

    def test_data_type_valid(self):
        valid_types = {"over", "innings"}
        for key, info in PREDICTION_TARGETS.items():
            assert info["data_type"] in valid_types, f"Bad data_type in '{key}'"


class TestGetModels:
    """Test the 3 ML model factory."""

    def test_returns_three_models(self):
        models = get_models()
        assert len(models) == 3

    def test_expected_model_names(self):
        models = get_models()
        assert "Linear Regression" in models
        assert "Gradient Boosting" in models
        assert "Polynomial Regression" in models

    def test_models_are_pipelines(self):
        from sklearn.pipeline import Pipeline
        models = get_models()
        for name, model in models.items():
            assert isinstance(model, Pipeline), f"{name} is not a Pipeline"


class TestTrainSingleTarget:
    """Test training for a single target."""

    def test_returns_dict_with_three_models(self):
        data = get_all_format_data()
        df = data["t20"]["over"]
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_single_target(df, "runs_in_over", "t20", tmpdir)
        assert len(result) == 3
        assert "Linear Regression" in result
        assert "Gradient Boosting" in result
        assert "Polynomial Regression" in result

    def test_metrics_keys_present(self):
        data = get_all_format_data()
        df = data["t20"]["over"]
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_single_target(df, "runs_in_over", "t20", tmpdir)
        for model_name, metrics in result.items():
            assert "mae" in metrics
            assert "r2" in metrics
            assert "rmse" in metrics

    def test_mae_positive(self):
        data = get_all_format_data()
        df = data["t20"]["over"]
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_single_target(df, "runs_in_over", "t20", tmpdir)
        for model_name, metrics in result.items():
            assert metrics["mae"] >= 0

    def test_model_files_saved(self):
        data = get_all_format_data()
        df = data["t20"]["over"]
        with tempfile.TemporaryDirectory() as tmpdir:
            train_single_target(df, "runs_in_over", "t20", tmpdir)
            t20_dir = os.path.join(tmpdir, "t20")
            saved = os.listdir(t20_dir)
            assert any("runs_in_over" in f for f in saved)

    def test_missing_columns_returns_empty(self):
        import pandas as pd
        df = pd.DataFrame({"col_a": [1, 2, 3]})
        with tempfile.TemporaryDirectory() as tmpdir:
            result = train_single_target(df, "runs_in_over", "t20", tmpdir)
        assert result == {}


class TestTrainAllModels:
    """Test the full training pipeline (light version using t20 only)."""

    def test_results_contain_all_formats(self):
        data = get_all_format_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            results = train_all_models(data, tmpdir)
        assert set(results.keys()) == {"t10", "t20", "odi", "test"}

    def test_metrics_json_created(self):
        data = get_all_format_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            train_all_models(data, tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "metrics.json"))
