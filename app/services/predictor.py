"""
Cricket Predictor Pro — Prediction Service

Loads pre-trained models and runs predictions for incoming requests.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

from app.services.data_generator import FORMAT_CONFIG
from app.services.model_trainer import PREDICTION_TARGETS


class CricketPredictor:
    """Loads all trained models and provides prediction interface."""

    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.models = {}
        self.metrics = {}
        self._load_models()
        self._load_metrics()

    def _load_models(self):
        """Load all serialized models from disk."""
        for fmt in FORMAT_CONFIG:
            self.models[fmt] = {}
            fmt_dir = os.path.join(self.models_dir, fmt)
            if not os.path.exists(fmt_dir):
                continue

            for target_key in PREDICTION_TARGETS:
                self.models[fmt][target_key] = {}
                model_names = {
                    "Linear Regression": "linear_regression",
                    "Gradient Boosting": "gradient_boosting",
                    "Polynomial Regression": "polynomial_regression",
                }
                for display_name, file_name in model_names.items():
                    model_path = os.path.join(
                        fmt_dir, f"{target_key}__{file_name}.joblib"
                    )
                    if os.path.exists(model_path):
                        self.models[fmt][target_key][display_name] = joblib.load(
                            model_path
                        )

    def _load_metrics(self):
        """Load saved evaluation metrics."""
        metrics_path = os.path.join(self.models_dir, "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                self.metrics = json.load(f)

    def predict(
        self, fmt: str, target_key: str, features: dict
    ) -> dict:
        """
        Run prediction using all 3 models.

        Args:
            fmt: Cricket format (t10, t20, odi, test)
            target_key: Prediction target key
            features: Dict of input feature values

        Returns:
            {
                "format": "T20",
                "target": "Runs in Over",
                "predictions": {
                    "Linear Regression": {"value": 7.2, "mae": 2.1, "r2": 0.48},
                    ...
                },
                "best_model": "Gradient Boosting",
                "feature_names": [...],
                "feature_values": [...]
            }
        """
        if fmt not in self.models or target_key not in self.models[fmt]:
            return {"error": f"No models found for {fmt}/{target_key}"}

        target_info = PREDICTION_TARGETS[target_key]
        feature_cols = target_info["feature_cols"]

        # Build feature array
        feature_values = []
        for col in feature_cols:
            val = features.get(col, 0)
            try:
                feature_values.append(float(val))
            except (ValueError, TypeError):
                feature_values.append(0.0)

        X = pd.DataFrame([feature_values], columns=feature_cols)

        # Get predictions from all models
        predictions = {}
        for model_name, model in self.models[fmt][target_key].items():
            try:
                pred = model.predict(X)[0]
                pred = max(0, round(float(pred), 2))  # No negative predictions

                # Get stored metrics
                metrics = {}
                if (
                    fmt in self.metrics
                    and target_key in self.metrics[fmt]
                    and model_name in self.metrics[fmt][target_key]
                ):
                    metrics = self.metrics[fmt][target_key][model_name]

                predictions[model_name] = {
                    "value": pred,
                    "mae": metrics.get("mae", 0),
                    "r2": metrics.get("r2", 0),
                    "rmse": metrics.get("rmse", 0),
                }
            except Exception as e:
                predictions[model_name] = {
                    "value": 0,
                    "error": str(e),
                }

        # Determine best model (lowest MAE from training)
        best_model = ""
        if predictions:
            valid = {
                k: v for k, v in predictions.items() if "error" not in v and v.get("mae", float("inf")) > 0
            }
            if valid:
                best_model = min(valid, key=lambda k: valid[k]["mae"])

        return {
            "format": FORMAT_CONFIG[fmt]["name"],
            "format_key": fmt,
            "target": target_info["name"],
            "target_key": target_key,
            "target_icon": target_info["icon"],
            "predictions": predictions,
            "best_model": best_model,
            "feature_names": feature_cols,
            "feature_values": feature_values,
        }

    def get_comparison_data(self) -> dict:
        """Get model comparison data for all formats and targets."""
        return self.metrics

    def get_format_info(self) -> dict:
        """Get format configuration for the UI."""
        return FORMAT_CONFIG

    def get_target_info(self) -> dict:
        """Get prediction target info for the UI."""
        return PREDICTION_TARGETS

    def get_feature_defaults(self, fmt: str, target_key: str) -> dict:
        """Get sensible default values for input features."""
        cfg = FORMAT_CONFIG.get(fmt, FORMAT_CONFIG["t20"])
        target_info = PREDICTION_TARGETS.get(target_key, {})
        feature_cols = target_info.get("feature_cols", [])

        defaults = {
            "over_number": cfg["max_overs"] // 2,
            "wickets_fallen": 3,
            "batsman_avg": cfg["avg_batting_avg"],
            "bowler_econ": cfg["avg_economy"],
            "strike_rate": cfg["avg_strike_rate"],
            "match_phase": 1,
            "overs_played": int(cfg["max_overs"] * 0.8),
            "wickets_lost": 5,
            "avg_batting_avg": cfg["avg_batting_avg"],
            "avg_bowling_avg": cfg["avg_bowling_avg"],
            "avg_strike_rate": cfg["avg_strike_rate"],
            "avg_economy": cfg["avg_economy"],
            "powerplay_runs": int(cfg["avg_run_rate"] * cfg["powerplay_end"] * 1.1),
            "middle_overs_runs": int(
                cfg["avg_run_rate"]
                * (cfg["death_over_start"] - cfg["powerplay_end"])
                * 0.85
            ),
            "total_innings_runs": int(
                (cfg["total_score_range"][0] + cfg["total_score_range"][1]) / 2
            ),
        }

        return {col: defaults.get(col, 0) for col in feature_cols}

    def get_feature_labels(self) -> dict:
        """Human-readable labels for feature columns."""
        return {
            "over_number": "Over Number",
            "wickets_fallen": "Wickets Fallen",
            "batsman_avg": "Batsman Average",
            "bowler_econ": "Bowler Economy",
            "strike_rate": "Strike Rate",
            "match_phase": "Match Phase (0=PP, 1=Mid, 2=Death)",
            "overs_played": "Overs Played",
            "wickets_lost": "Wickets Lost",
            "avg_batting_avg": "Avg Batting Average",
            "avg_bowling_avg": "Avg Bowling Average",
            "avg_strike_rate": "Avg Strike Rate",
            "avg_economy": "Avg Economy Rate",
            "powerplay_runs": "Powerplay Runs",
            "middle_overs_runs": "Middle Overs Runs",
            "total_innings_runs": "Total Innings Runs",
        }

    def get_feature_ranges(self, fmt: str, target_key: str) -> dict:
        """
        Return per-feature min/max/step/unit hints for the prediction form.
        Used to power real-time input validation and range hints in the UI.
        """
        cfg = FORMAT_CONFIG.get(fmt, FORMAT_CONFIG["t20"])
        max_ov = cfg["max_overs"]
        sr = cfg["total_score_range"]

        base_ranges = {
            "over_number":        {"min": 1,   "max": max_ov,          "step": 1,    "unit": "over"},
            "wickets_fallen":     {"min": 0,   "max": 9,               "step": 1,    "unit": "wkts"},
            "batsman_avg":        {"min": 5,   "max": 80,              "step": 0.1,  "unit": "avg"},
            "bowler_econ":        {"min": 1.0, "max": 18.0,            "step": 0.1,  "unit": "rpo"},
            "strike_rate":        {"min": 20,  "max": 250,             "step": 0.1,  "unit": "sr"},
            "match_phase":        {"min": 0,   "max": 2,               "step": 1,    "unit": ""},
            "overs_played":       {"min": 1,   "max": max_ov,          "step": 1,    "unit": "ovs"},
            "wickets_lost":       {"min": 0,   "max": 10,              "step": 1,    "unit": "wkts"},
            "avg_batting_avg":    {"min": 10,  "max": 70,              "step": 0.1,  "unit": "avg"},
            "avg_bowling_avg":    {"min": 10,  "max": 70,              "step": 0.1,  "unit": "avg"},
            "avg_strike_rate":    {"min": 20,  "max": 220,             "step": 0.1,  "unit": "sr"},
            "avg_economy":        {"min": 1.0, "max": 16.0,            "step": 0.1,  "unit": "rpo"},
            "powerplay_runs":     {"min": 0,   "max": cfg["powerplay_end"] * 12, "step": 1, "unit": "runs"},
            "middle_overs_runs":  {"min": 0,   "max": (cfg["death_over_start"] - cfg["powerplay_end"]) * 10, "step": 1, "unit": "runs"},
            "total_innings_runs": {"min": sr[0] - 40, "max": sr[1] + 80, "step": 1, "unit": "runs"},
        }

        target_info = PREDICTION_TARGETS.get(target_key, {})
        feature_cols = target_info.get("feature_cols", [])
        return {col: base_ranges[col] for col in feature_cols if col in base_ranges}
