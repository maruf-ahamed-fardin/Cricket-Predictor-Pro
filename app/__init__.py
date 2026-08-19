"""
Cricket Predictor Pro — Flask Application Factory
Production-ready with logging, error handlers, and env config.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template

from app.services.predictor import CricketPredictor
from app.services.data_generator import FORMAT_CONFIG
from app.services.model_trainer import PREDICTION_TARGETS


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    # ── Config ────────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cricket-predictor-pro-dev-key")
    app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # ── Logging ───────────────────────────────────────────────────────────────
    _configure_logging(app)

    # ── Load ML models ────────────────────────────────────────────────────────
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    predictor = CricketPredictor(models_dir)
    app.config["PREDICTOR"] = predictor
    app.logger.info(f"Loaded models from: {models_dir}")

    # ── Register blueprints ───────────────────────────────────────────────────
    from app.routes.predict import predict_bp
    app.register_blueprint(predict_bp)

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template(
            "error.html",
            formats=FORMAT_CONFIG,
            targets=PREDICTION_TARGETS,
            code=404,
            title="Page Not Found",
            message="The page you're looking for doesn't exist.",
            emoji="🏏",
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {e}")
        return render_template(
            "error.html",
            formats=FORMAT_CONFIG,
            targets=PREDICTION_TARGETS,
            code=500,
            title="Something Went Wrong",
            message="An internal error occurred. Please try again.",
            emoji="🚨",
        ), 500

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        from flask import jsonify
        return jsonify({"status": "ok", "models_loaded": bool(predictor.models)})

    app.logger.info("🏏 Cricket Predictor Pro app ready.")
    return app


def _configure_logging(app: Flask):
    """Set up rotating file logger + console logger."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

    # File handler (10 MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.config.get("DEBUG") else logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)
