"""
Cricket Predictor Pro — Flask Application Factory
"""

import os
from flask import Flask

from app.services.predictor import CricketPredictor


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    app.config["SECRET_KEY"] = "cricket-predictor-pro-2024"

    # Initialize predictor with trained models
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    predictor = CricketPredictor(models_dir)

    # Store predictor in app config for route access
    app.config["PREDICTOR"] = predictor

    # Register blueprints
    from app.routes.predict import predict_bp

    app.register_blueprint(predict_bp)

    return app
