"""
Cricket Predictor Pro — Admin Routes

Protected admin endpoints for model retraining and monitoring.
Access requires ADMIN_KEY environment variable.
"""

import os
import time
import json
import threading
from flask import Blueprint, render_template, request, jsonify, current_app, Response, abort, stream_with_context

from app.services.data_generator import FORMAT_CONFIG
from app.services.model_trainer import PREDICTION_TARGETS

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Thread-safe training state
_train_state = {"running": False, "log": [], "last_trained": None}
_train_lock = threading.Lock()


def _require_admin_key():
    """Abort 403 if ADMIN_KEY header or query param doesn't match config."""
    expected = current_app.config.get("ADMIN_KEY", "")
    provided = request.headers.get("X-Admin-Key") or request.args.get("key", "")
    if not expected or provided != expected:
        abort(403)


@admin_bp.route("/")
def admin_index():
    """Admin dashboard page."""
    _require_admin_key()
    return render_template(
        "admin.html",
        formats=FORMAT_CONFIG,
        targets=PREDICTION_TARGETS,
        state=_train_state,
    )


@admin_bp.route("/retrain", methods=["POST"])
def retrain():
    """Trigger model retraining in a background thread."""
    _require_admin_key()

    with _train_lock:
        if _train_state["running"]:
            return jsonify({"error": "Training already in progress"}), 409
        _train_state["running"] = True
        _train_state["log"] = []

    def _do_train():
        from app.services.data_generator import get_all_format_data
        from app.services.model_trainer import train_all_models

        models_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models"
        )
        try:
            _train_state["log"].append("📊 Generating synthetic cricket data...")
            data = get_all_format_data()
            _train_state["log"].append("✓ Data generated")

            _train_state["log"].append("🤖 Training 72 models...")
            results = train_all_models(data, models_dir)
            total = sum(len(m) for t in results.values() for m in t.values())
            _train_state["log"].append(f"✅ Training complete — {total} models saved")
            _train_state["last_trained"] = time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            _train_state["log"].append(f"❌ Error: {e}")
        finally:
            with _train_lock:
                _train_state["running"] = False

    thread = threading.Thread(target=_do_train, daemon=True)
    thread.start()
    return jsonify({"status": "started"})


@admin_bp.route("/status")
def status():
    """Return current training state as JSON."""
    _require_admin_key()
    return jsonify(_train_state)


@admin_bp.route("/stream")
def stream():
    """Server-Sent Events stream of training log lines."""
    _require_admin_key()
    seen = 0

    def generate():
        nonlocal seen
        while True:
            log = _train_state["log"]
            while seen < len(log):
                yield f"data: {json.dumps(log[seen])}\n\n"
                seen += 1
            if not _train_state["running"] and seen >= len(log):
                yield "data: __done__\n\n"
                break
            time.sleep(0.5)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")
