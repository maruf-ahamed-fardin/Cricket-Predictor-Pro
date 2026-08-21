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
    abort,
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


@predict_bp.route("/about")
def about():
    """About / How It Works page."""
    return render_template(
        "about.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
    )


@predict_bp.route("/history")
def history():
    """Prediction history page (data stored client-side in localStorage)."""
    return render_template(
        "history.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
    )


@predict_bp.route("/simulate/<fmt>")
def simulate(fmt):
    """Over-by-over innings simulator."""
    if fmt not in FORMAT_CONFIG:
        fmt = "t20"
    return render_template(
        "simulate.html",
        fmt=fmt,
        fmt_config=FORMAT_CONFIG[fmt],
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
    )


@predict_bp.route("/compare/players")
def player_compare():
    """Side-by-side player prediction comparison."""
    predictor = get_predictor()
    fmt = request.args.get("fmt", "t20")
    if fmt not in FORMAT_CONFIG:
        fmt = "t20"
    target_key = request.args.get("target", "runs_in_over")
    if target_key not in PREDICTION_TARGETS:
        target_key = "runs_in_over"

    defaults = predictor.get_feature_defaults(fmt, target_key)
    labels = predictor.get_feature_labels()
    ranges = predictor.get_feature_ranges(fmt, target_key)
    target_info = PREDICTION_TARGETS[target_key]

    return render_template(
        "player_compare.html",
        fmt=fmt,
        fmt_config=FORMAT_CONFIG[fmt],
        formats=FORMAT_CONFIG,
        target_key=target_key,
        target_info=target_info,
        targets=PREDICTION_TARGETS,
        defaults=defaults,
        labels=labels,
        ranges=ranges,
        feature_cols=target_info["feature_cols"],
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
    ranges = predictor.get_feature_ranges(fmt, target_key)
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
        ranges=ranges,
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
    ranges = predictor.get_feature_ranges(fmt, target_key)

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
        ranges=ranges,
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


@predict_bp.route("/api/docs")
def api_docs():
    """Interactive API documentation page."""
    return render_template(
        "api_docs.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
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


@predict_bp.route("/api/ranges/<fmt>/<target_key>")
def api_ranges(fmt, target_key):
    """Get min/max/step/unit ranges for each feature in a format/target."""
    if fmt not in FORMAT_CONFIG:
        return jsonify({"error": f"Invalid format: {fmt}"}), 400
    if target_key not in PREDICTION_TARGETS:
        return jsonify({"error": f"Invalid target: {target_key}"}), 400

    predictor = get_predictor()
    ranges = predictor.get_feature_ranges(fmt, target_key)
    return jsonify({"ranges": ranges})
