"""
Cricket Predictor Pro — Train All Models

Standalone script to generate data and train all models for all formats.
Run: python train_models.py
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_generator import get_all_format_data, FORMAT_CONFIG
from app.services.model_trainer import train_all_models, PREDICTION_TARGETS


def main():
    print("=" * 65)
    print("  🏏  Cricket Predictor Pro — Model Training Pipeline")
    print("=" * 65)

    models_dir = os.path.join(os.path.dirname(__file__), "models")
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    # Step 1: Generate data
    print("\n📊 Step 1: Generating synthetic cricket data...")
    start = time.time()
    data = get_all_format_data(seed=42)

    for fmt, fmt_data in data.items():
        name = FORMAT_CONFIG[fmt]["name"]
        over_rows = len(fmt_data["over"])
        inn_rows = len(fmt_data["innings"])
        print(f"  {name:>4}: {over_rows} over samples, {inn_rows} innings samples")

        # Save CSVs
        fmt_data["over"].to_csv(
            os.path.join(data_dir, f"{fmt}_over_data.csv"), index=False
        )
        fmt_data["innings"].to_csv(
            os.path.join(data_dir, f"{fmt}_innings_data.csv"), index=False
        )

    elapsed = time.time() - start
    print(f"  ✓ Data generated in {elapsed:.1f}s\n")

    # Step 2: Train models
    print("🤖 Step 2: Training models...")
    print(f"  {len(FORMAT_CONFIG)} formats × {len(PREDICTION_TARGETS)} targets × 3 models")
    print("-" * 65)

    start = time.time()
    results = train_all_models(data, models_dir)
    elapsed = time.time() - start

    # Step 3: Summary
    print("\n" + "=" * 65)
    print("  📋  Training Summary")
    print("=" * 65)

    total_models = 0
    for fmt, targets in results.items():
        for target, models in targets.items():
            total_models += len(models)

    print(f"  Total models trained: {total_models}")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print(f"  Models saved to: {os.path.abspath(models_dir)}")
    print(f"  Metrics saved to: {os.path.join(models_dir, 'metrics.json')}")

    # Best model per format
    print("\n  🏆 Best Model per Format (by lowest avg MAE):")
    print("  " + "-" * 50)
    for fmt in FORMAT_CONFIG:
        if fmt not in results:
            continue
        model_maes = {}
        for target, models in results[fmt].items():
            for model_name, metrics in models.items():
                if model_name not in model_maes:
                    model_maes[model_name] = []
                model_maes[model_name].append(metrics["mae"])

        if model_maes:
            best = min(model_maes, key=lambda k: sum(model_maes[k]) / len(model_maes[k]))
            avg_mae = sum(model_maes[best]) / len(model_maes[best])
            print(f"  {FORMAT_CONFIG[fmt]['name']:>4}: {best} (avg MAE: {avg_mae:.3f})")

    print("\n" + "=" * 65)
    print("  ✅  All models trained! Run 'python -m app.main' to start the server.")
    print("=" * 65)


if __name__ == "__main__":
    main()
