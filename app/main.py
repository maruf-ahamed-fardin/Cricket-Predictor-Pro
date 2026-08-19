"""
Cricket Predictor Pro — Entry Point

Run: python -m app.main
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n🏏 Cricket Predictor Pro is running!")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
