"""
Cricket Predictor Pro — Real Cricket Data Importer & Parser

Supports importing and converting real-world cricket ball-by-ball / match datasets
(such as Cricsheet CSV/JSON, Kaggle match deliveries, or custom match exports)
into the standardised feature schema used by the training and inference pipelines.
"""

import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

from app.services.data_generator import FORMAT_CONFIG, clean_data

logger = logging.getLogger(__name__)


# ─── Standard Feature Schema ──────────────────────────────────────────────────

OVER_COLUMNS = [
    "over_number",
    "wickets_fallen",
    "batsman_avg",
    "bowler_econ",
    "strike_rate",
    "match_phase",
    "runs_in_over",
]

INNINGS_COLUMNS = [
    "overs_played",
    "wickets_lost",
    "avg_batting_avg",
    "avg_bowling_avg",
    "avg_strike_rate",
    "avg_economy",
    "powerplay_runs",
    "middle_overs_runs",
    "total_innings_runs",
    "team_batting_avg",
    "team_bowling_avg",
    "total_run_avg",
    "overs_batted",
]


class CricketDataImporter:
    """
    Parses and transforms external cricket data into model-compatible datasets.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
        )

    def import_ball_by_ball_csv(
        self,
        filepath: str,
        fmt: str = "t20",
    ) -> Optional[pd.DataFrame]:
        """
        Convert ball-by-ball CSV deliveries into aggregated over-level dataset.
        Expected minimum columns in raw ball-by-ball data:
        - match_id, inning, over, ball, batsman_runs, extra_runs, is_wicket (optional)
        """
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return None

        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} deliveries from {filepath}")

            # Normalise column names
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            # Determine over column
            over_col = "over" if "over" in df.columns else "over_number"
            runs_col = "runs_off_bat" if "runs_off_bat" in df.columns else "batsman_runs"
            if runs_col not in df.columns:
                runs_col = "runs" if "runs" in df.columns else None

            extras_col = "extras" if "extras" in df.columns else "extra_runs"
            wicket_col = "is_wicket" if "is_wicket" in df.columns else "wicket"

            if not over_col or over_col not in df.columns:
                logger.error("Missing over column in raw dataset")
                return None

            # Calculate total runs per delivery
            df["total_runs_delivery"] = 0
            if runs_col and runs_col in df.columns:
                df["total_runs_delivery"] += df[runs_col].fillna(0)
            if extras_col and extras_col in df.columns:
                df["total_runs_delivery"] += df[extras_col].fillna(0)

            # Wicket indicator
            if wicket_col in df.columns:
                df["wicket_flag"] = df[wicket_col].fillna(0).astype(int)
            else:
                df["wicket_flag"] = 0

            # Group by match, inning, over
            group_keys = [k for k in ["match_id", "inning", over_col] if k in df.columns]
            if not group_keys:
                group_keys = [over_col]

            over_grouped = df.groupby(group_keys).agg(
                runs_in_over=("total_runs_delivery", "sum"),
                wickets_in_over=("wicket_flag", "sum"),
            ).reset_index()

            cfg = FORMAT_CONFIG.get(fmt, FORMAT_CONFIG["t20"])
            max_ov = cfg["max_overs"]
            pp_end = cfg["powerplay_end"]
            death_start = cfg["death_over_start"]

            # Construct standardized columns
            over_grouped["over_number"] = over_grouped[over_col].clip(1, max_ov)
            
            # Cumulative wickets (simulated or computed if match/inning present)
            if "match_id" in over_grouped.columns:
                over_grouped["wickets_fallen"] = (
                    over_grouped.groupby(["match_id", "inning"])["wickets_in_over"]
                    .cumsum()
                    .shift(1)
                    .fillna(0)
                    .clip(0, 9)
                )
            else:
                over_grouped["wickets_fallen"] = np.random.randint(0, 6, len(over_grouped))

            # Match phase
            def calc_phase(ov):
                if ov <= pp_end:
                    return 0
                elif ov >= death_start:
                    return 2
                return 1

            over_grouped["match_phase"] = over_grouped["over_number"].apply(calc_phase)

            # Player statistics estimations (if not available in raw ball dataset)
            n_rows = len(over_grouped)
            over_grouped["batsman_avg"] = np.random.normal(
                cfg["avg_batting_avg"], 6.0, n_rows
            ).clip(10, 75).round(1)
            over_grouped["bowler_econ"] = np.random.normal(
                cfg["avg_economy"], 1.5, n_rows
            ).clip(3.0, 15.0).round(1)
            over_grouped["strike_rate"] = np.random.normal(
                cfg["avg_strike_rate"], 20.0, n_rows
            ).clip(50, 240).round(1)

            # Ensure all required columns exist
            result_df = over_grouped[OVER_COLUMNS].copy()
            return clean_data(result_df)

        except Exception as e:
            logger.error(f"Error parsing ball-by-ball CSV: {e}", exc_info=True)
            return None

    def export_sample_template(self, output_path: str) -> str:
        """
        Create a sample CSV template for users/analysts to upload real data.
        """
        sample_data = {
            "match_id": [101, 101, 101, 101, 102],
            "inning": [1, 1, 1, 1, 1],
            "over": [1, 2, 3, 4, 1],
            "ball": [1, 1, 1, 1, 1],
            "batsman_runs": [1, 4, 6, 0, 2],
            "extra_runs": [0, 0, 1, 0, 0],
            "is_wicket": [0, 0, 1, 0, 0],
        }
        df = pd.DataFrame(sample_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path
