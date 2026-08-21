"""
Pytest configuration and shared fixtures.
"""
import os
import sys
import pytest

# Make sure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture
def app():
    """Create a test Flask application."""
    application = create_app()
    application.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    yield application


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def models_dir():
    """Return the models directory path."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
