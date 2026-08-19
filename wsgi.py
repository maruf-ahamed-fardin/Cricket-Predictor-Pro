"""
Cricket Predictor Pro — Production WSGI Entry Point

For production deployment with gunicorn:
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

For development:
    python -m app.main
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
