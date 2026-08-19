"""
Cricket Predictor Pro — Routes

All web and API routes for prediction, comparison, and landing pages.
"""

import os
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
    send_from_directory,
)

from app.services.data_generator import FORMAT_CONFIG
from app.services.model_trainer import PREDICTION_TARGETS

predict_bp = Blueprint("predict", __name__)


def get_predictor():
    """Get the predictor instance from app config."""
    return current_app.config["PREDICTOR"]


# ─── Web Routes ──────────────────────────────────────────────────────────────


@predict_bp.route("/favicon.ico")
def favicon():
    """Serve official logo as the site favicon."""
    static_dir = os.path.join(current_app.root_path, "static")
    return send_from_directory(
        static_dir,
        "favicon.svg",
        mimetype="image/svg+xml",
    )


@predict_bp.route("/")
def index():
    """Landing page with format and target selection."""
    return render_template(
        "index.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
    )


@predict_bp.route("/profile")
def profile():
    """User profile page."""
    return render_template(
        "profile.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
    )



@predict_bp.route("/predict/<fmt>")
def predict_page(fmt):
    """Prediction form page for a specific format."""
    if fmt not in FORMAT_CONFIG:
        fmt = "t20"

    target_key = request.args.get("target", "runs_in_over")
    if target_key not in PREDICTION_TARGETS:
        target_key = "runs_in_over"

    predictor = get_predictor()
    defaults = predictor.get_feature_defaults(fmt, target_key)
    labels = predictor.get_feature_labels()
    target_info = PREDICTION_TARGETS[target_key]

    return render_template(
        "predict.html",
        fmt=fmt,
        fmt_config=FORMAT_CONFIG[fmt],
        formats=FORMAT_CONFIG,
        target_key=target_key,
        target_info=target_info,
        targets=PREDICTION_TARGETS,
        defaults=defaults,
        labels=labels,
        feature_cols=target_info["feature_cols"],
        result=None,
    )


@predict_bp.route("/predict/<fmt>", methods=["POST"])
def predict_submit(fmt):
    """Handle prediction form submission."""
    if fmt not in FORMAT_CONFIG:
        fmt = "t20"

    target_key = request.form.get("target_key", "runs_in_over")
    if target_key not in PREDICTION_TARGETS:
        target_key = "runs_in_over"

    predictor = get_predictor()
    target_info = PREDICTION_TARGETS[target_key]
    labels = predictor.get_feature_labels()

    # Collect feature values from form
    features = {}
    for col in target_info["feature_cols"]:
        val = request.form.get(col, 0)
        try:
            features[col] = float(val)
        except (ValueError, TypeError):
            features[col] = 0.0

    # Run prediction
    result = predictor.predict(fmt, target_key, features)

    return render_template(
        "predict.html",
        fmt=fmt,
        fmt_config=FORMAT_CONFIG[fmt],
        formats=FORMAT_CONFIG,
        target_key=target_key,
        target_info=target_info,
        targets=PREDICTION_TARGETS,
        defaults=features,
        labels=labels,
        feature_cols=target_info["feature_cols"],
        result=result,
    )


@predict_bp.route("/compare")
def compare():
    """Model comparison dashboard."""
    predictor = get_predictor()
    metrics = predictor.get_comparison_data()

    return render_template(
        "compare.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
        metrics=metrics,
    )


# ─── API Routes ──────────────────────────────────────────────────────────────


@predict_bp.route("/api/predict", methods=["POST"])
def api_predict():
    """
    JSON API endpoint for predictions.

    POST /api/predict
    Body: {"format": "t20", "target": "runs_in_over", "features": {...}}
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    fmt = data.get("format", "t20")
    target_key = data.get("target", "runs_in_over")
    features = data.get("features", {})

    if fmt not in FORMAT_CONFIG:
        return jsonify({"error": f"Invalid format: {fmt}"}), 400
    if target_key not in PREDICTION_TARGETS:
        return jsonify({"error": f"Invalid target: {target_key}"}), 400

    predictor = get_predictor()
    result = predictor.predict(fmt, target_key, features)

    return jsonify(result)


@predict_bp.route("/api/formats")
def api_formats():
    """List available formats."""
    return jsonify(
        {k: {"name": v["name"], "max_overs": v["max_overs"]} for k, v in FORMAT_CONFIG.items()}
    )


@predict_bp.route("/api/targets")
def api_targets():
    """List available prediction targets."""
    return jsonify(
        {
            k: {"name": v["name"], "description": v["description"], "icon": v["icon"]}
            for k, v in PREDICTION_TARGETS.items()
        }
    )


@predict_bp.route("/api/defaults/<fmt>/<target_key>")
def api_defaults(fmt, target_key):
    """Get default feature values for a format/target combination."""
    predictor = get_predictor()
    defaults = predictor.get_feature_defaults(fmt, target_key)
    labels = predictor.get_feature_labels()
    return jsonify({"defaults": defaults, "labels": labels})
