"""
Cricket Predictor Pro — Model Trainer

Trains 3 ML models for each prediction target across all cricket formats.
Models: Linear Regression, Gradient Boosting, Polynomial Regression (degree=2)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

from app.services.data_generator import FORMAT_CONFIG


# ─── Prediction target definitions ───────────────────────────────────────────

PREDICTION_TARGETS = {
    "runs_in_over": {
        "name": "Runs in Over",
        "description": "Predict runs scored in a specific over",
        "data_type": "over",
        "target_col": "runs_in_over",
        "feature_cols": [
            "over_number",
            "wickets_fallen",
            "batsman_avg",
            "bowler_econ",
            "strike_rate",
            "match_phase",
        ],
        "icon": "🏏",
    },
    "total_innings_runs": {
        "name": "Total Innings Runs",
        "description": "Predict total team score for an innings",
        "data_type": "innings",
        "target_col": "total_innings_runs",
        "feature_cols": [
            "overs_played",
            "wickets_lost",
            "avg_batting_avg",
            "avg_bowling_avg",
            "avg_strike_rate",
            "avg_economy",
            "powerplay_runs",
            "middle_overs_runs",
        ],
        "icon": "📊",
    },
    "batting_avg": {
        "name": "Batting Average",
        "description": "Predict batting average for a player profile",
        "data_type": "innings",
        "target_col": "team_batting_avg",
        "feature_cols": [
            "overs_played",
            "wickets_lost",
            "total_innings_runs",
            "avg_strike_rate",
            "avg_economy",
            "powerplay_runs",
        ],
        "icon": "🏆",
    },
    "bowling_avg": {
        "name": "Bowling Average",
        "description": "Predict bowling average for a bowler profile",
        "data_type": "innings",
        "target_col": "team_bowling_avg",
        "feature_cols": [
            "overs_played",
            "wickets_lost",
            "total_innings_runs",
            "avg_batting_avg",
            "avg_economy",
            "middle_overs_runs",
        ],
        "icon": "🎳",
    },
    "total_run_avg": {
        "name": "Total Run Average",
        "description": "Average runs per over for a team/format",
        "data_type": "innings",
        "target_col": "total_run_avg",
        "feature_cols": [
            "overs_played",
            "wickets_lost",
            "avg_batting_avg",
            "avg_bowling_avg",
            "avg_strike_rate",
            "avg_economy",
        ],
        "icon": "📈",
    },
    "overs_batted": {
        "name": "Overs Played",
        "description": "Predict how many overs a team bats before all-out",
        "data_type": "innings",
        "target_col": "overs_batted",
        "feature_cols": [
            "wickets_lost",
            "avg_batting_avg",
            "avg_bowling_avg",
            "avg_strike_rate",
            "avg_economy",
            "powerplay_runs",
        ],
        "icon": "⏱️",
    },
}


def get_models() -> dict:
    """Return a dictionary of the 3 ML model instances."""
    return {
        "Linear Regression": make_pipeline(
            StandardScaler(), LinearRegression()
        ),
        "Gradient Boosting": make_pipeline(
            StandardScaler(),
            GradientBoostingRegressor(
                n_estimators=150,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
            ),
        ),
        "Polynomial Regression": make_pipeline(
            StandardScaler(),
            PolynomialFeatures(degree=2, include_bias=False),
            LinearRegression(),
        ),
    }


def train_single_target(
    df: pd.DataFrame,
    target_key: str,
    fmt: str,
    models_dir: str,
) -> dict:
    """
    Train all 3 models for a single prediction target + format combination.

    Returns evaluation metrics for each model.
    """
    target_info = PREDICTION_TARGETS[target_key]
    feature_cols = target_info["feature_cols"]
    target_col = target_info["target_col"]

    # Ensure all feature columns exist
    available_cols = [c for c in feature_cols if c in df.columns]
    if not available_cols or target_col not in df.columns:
        return {}

    X = df[available_cols].copy()
    y = df[target_col].copy()

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = get_models()
    results = {}

    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Evaluation metrics
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)

        # Save the model
        safe_model_name = model_name.lower().replace(" ", "_")
        model_path = os.path.join(models_dir, fmt, f"{target_key}__{safe_model_name}.joblib")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)

        results[model_name] = {
            "mae": round(mae, 3),
            "r2": round(r2, 4),
            "rmse": round(rmse, 3),
            "model_path": model_path,
        }

    return results


def train_all_models(data: dict, models_dir: str) -> dict:
    """
    Train all models for all targets across all formats.

    Args:
        data: Output of get_all_format_data()
        models_dir: Path to save model files

    Returns:
        Nested dict: {format: {target: {model: metrics}}}
    """
    all_results = {}

    for fmt in FORMAT_CONFIG:
        all_results[fmt] = {}
        fmt_data = data[fmt]

        for target_key, target_info in PREDICTION_TARGETS.items():
            data_type = target_info["data_type"]
            df = fmt_data[data_type]

            print(f"  Training {FORMAT_CONFIG[fmt]['name']:>4} | {target_info['name']:<22}", end="")
            results = train_single_target(df, target_key, fmt, models_dir)

            if results:
                # Find best model
                best = min(results.items(), key=lambda x: x[1]["mae"])
                print(f" ✓  Best: {best[0]} (MAE: {best[1]['mae']:.3f})")
                all_results[fmt][target_key] = results
            else:
                print(" ✗  Skipped (missing columns)")

    # Save metrics summary
    metrics_path = os.path.join(models_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(all_results, f, indent=2)

    return all_results
