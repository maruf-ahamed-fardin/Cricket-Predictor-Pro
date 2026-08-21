# 🏏 Cricket Predictor Pro

> **AI-Powered Cricket Match Analytics & Statistics Prediction Platform**
> Predict match outcomes, over-by-over scoring dynamics, and player milestones across **T10, T20, ODI, and Test** formats using multiple machine learning algorithms simultaneously.

---

## 💡 The Core Idea

Cricket is an evolving, data-intensive sport where match situations fluctuate ball-by-ball. Traditional statistical averages often fail to capture dynamic factors such as match phase (Powerplay vs Death overs), bowler economy pressure, and collapsing wickets.

**Cricket Predictor Pro** solves this by providing:
1. **Multi-Model Inference**: Instead of relying on a single black-box algorithm, every prediction runs across **Linear Regression**, **Gradient Boosting**, and **Polynomial Regression** in parallel, comparing outputs with real-time confidence intervals ($\pm\text{MAE}$).
2. **Format-Aware Intelligence**: Calibrated models tailored specifically for the statistical distributions of **T10**, **T20**, **ODI**, and **Test** cricket.
3. **Interactive Simulation & Comparison**: Live over-by-over innings progression simulator, side-by-side player/scenario comparisons, and complete REST API accessibility.

---

## 🌟 Key Capabilities

- **🤖 72 Pre-Trained ML Models**: 3 algorithms × 6 targets × 4 formats with automated evaluation metrics (MAE, R², RMSE).
- **⚙️ Over-by-Over Match Simulator**: Simulates full innings progression ball-by-ball with dynamic wickets and live run-rate tracking.
- **⚔️ Player / Scenario Comparison**: Compare two distinct match situations simultaneously with grouped visual diffs.
- **📊 Model Analytics Dashboard**: Interactive Bar and Radar performance charts with instant filtering and algorithm leaderboards.
- **📋 Persistent Prediction History**: Locally saved prediction records with single-click re-runs and CSV export.
- **🔌 OpenAPI REST API**: Fully documented endpoints with live browser-testing capabilities for external integrations.
- **🛡️ Enterprise Security**: Hardened with strict Content Security Policy (CSP), anti-clickjacking, XSS protections, and permissions policies.
- **🌐 Localization & PWA**: Bilingual support (**English** & **বাংলা**) and installable Progressive Web App with offline caching.

---

## 🏗️ Architecture Overview

```
User Input / API Request
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Flask Web & REST API Layer                 │
│    (Security Middleware, Validation, Error Handlers)     │
└──────────────────────────┬──────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌──────────────────────────────┐   ┌───────────────────────┐
│     Inference Engine         │   │   Simulator & Compare │
│  (CricketPredictor Service)  │   │  (Multi-Scenario Run) │
└──────────────┬───────────────┘   └───────────┬───────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────────────────────────────────┐
│              72 Machine Learning Pipelines               │
│  • Linear Regression    • Gradient Boosting              │
│  • Polynomial Regression                                 │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│               Interactive Visual Results                 │
│  (Confidence ±MAE, Chart.js Visuals, History, Exports)   │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/maruf-ahamed-fardin/Cricket-Predictor-Pro.git
cd Cricket-Predictor-Pro

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Run Application

```bash
# Start the Flask development server
python wsgi.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### 3. Run Test Suite

```bash
python -m pytest -v
```

---

## 📖 API Reference

Interactive API documentation with live testing is available at `/api/docs` or via the `openapi.yaml` specification file.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Application & model health check |
| `GET` | `/api/formats` | List supported cricket formats |
| `GET` | `/api/targets` | List available prediction targets |
| `GET` | `/api/ranges/<fmt>/<target>` | Get feature bounds & units |
| `POST` | `/api/predict` | Execute 3-model prediction |

---

## 📄 License

This project is licensed under the MIT License.