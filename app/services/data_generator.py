"""
Cricket Predictor Pro — Synthetic Data Generator

Generates realistic cricket data for T10, T20, ODI, and Test formats.
Each format has tuned parameters to reflect real-world scoring patterns.
"""

import pandas as pd
import numpy as np


# ─── Format-specific configuration ───────────────────────────────────────────

FORMAT_CONFIG = {
    "t10": {
        "name": "T10",
        "max_overs": 10,
        "total_score_range": (80, 130),
        "avg_run_rate": 10.5,
        "avg_batting_avg": 28,
        "avg_bowling_avg": 22,
        "avg_economy": 9.5,
        "avg_strike_rate": 145,
        "death_over_start": 8,
        "powerplay_end": 3,
        "samples": 3000,
    },
    "t20": {
        "name": "T20",
        "max_overs": 20,
        "total_score_range": (130, 220),
        "avg_run_rate": 8.5,
        "avg_batting_avg": 32,
        "avg_bowling_avg": 26,
        "avg_economy": 8.0,
        "avg_strike_rate": 130,
        "death_over_start": 16,
        "powerplay_end": 6,
        "samples": 5000,
    },
    "odi": {
        "name": "ODI",
        "max_overs": 50,
        "total_score_range": (220, 350),
        "avg_run_rate": 5.8,
        "avg_batting_avg": 38,
        "avg_bowling_avg": 32,
        "avg_economy": 5.5,
        "avg_strike_rate": 90,
        "death_over_start": 40,
        "powerplay_end": 10,
        "samples": 5000,
    },
    "test": {
        "name": "Test",
        "max_overs": 90,
        "total_score_range": (200, 600),
        "avg_run_rate": 3.2,
        "avg_batting_avg": 42,
        "avg_bowling_avg": 35,
        "avg_economy": 3.0,
        "avg_strike_rate": 52,
        "death_over_start": 80,
        "powerplay_end": 1,  # No powerplay in Test
        "samples": 5000,
    },
}


def generate_over_data(fmt: str, seed: int = 42) -> pd.DataFrame:
    """
    Generate per-over data for a given cricket format.

    Returns DataFrame with columns:
        over_number, wickets_fallen, batsman_avg, bowler_econ,
        strike_rate, match_phase, runs_in_over
    """
    cfg = FORMAT_CONFIG[fmt]
    rng = np.random.default_rng(seed)
    N = cfg["samples"]

    over = rng.integers(1, cfg["max_overs"] + 1, N)

    # Wickets scale with over number
    wkt = np.clip(rng.poisson(over * (0.3 if fmt != "test" else 0.08)), 0, 9)

    # Batting average centered on format average
    bat_avg = np.round(
        rng.normal(cfg["avg_batting_avg"], 8, N).clip(10, 65), 1
    )

    # Bowler economy centered on format average
    bowler_econ = np.round(
        rng.normal(cfg["avg_economy"], 1.2, N).clip(2, 14), 2
    )

    # Strike rate centered on format average
    strike_rate = np.round(
        rng.normal(cfg["avg_strike_rate"], 20, N).clip(30, 220), 1
    )

    # Match phase: 0 = powerplay, 1 = middle, 2 = death
    phase = np.where(
        over <= cfg["powerplay_end"],
        0,
        np.where(over >= cfg["death_over_start"], 2, 1),
    )

    # Runs per over — realistic formula per format
    base_runs = cfg["avg_run_rate"]
    runs = (
        base_runs
        + 0.25 * (over / cfg["max_overs"] * 10)  # Acceleration
        - 0.5 * wkt  # Wickets slow scoring
        + 0.15 * (bat_avg - cfg["avg_batting_avg"])  # Better batter
        + 1.1 * (bowler_econ - cfg["avg_economy"])  # Weaker bowler
        + 0.02 * (strike_rate - cfg["avg_strike_rate"])  # Aggressive batter
        + 3.5 * (phase == 2)  # Death-over surge
        + 1.0 * (phase == 0)  # Powerplay boost
    )

    # Add noise and clip to reasonable range
    runs_in_over = np.clip(rng.poisson(np.clip(runs, 1, 30)), 0, 36)

    df = pd.DataFrame(
        {
            "over_number": over,
            "wickets_fallen": wkt,
            "batsman_avg": bat_avg,
            "bowler_econ": bowler_econ,
            "strike_rate": strike_rate,
            "match_phase": phase,
            "runs_in_over": runs_in_over,
        }
    )

    # Inject ~5% missing values as zeros
    n_missing = int(N * 0.05)
    for col in ["batsman_avg", "bowler_econ", "strike_rate"]:
        idx = rng.choice(N, n_missing, replace=False)
        df.loc[idx, col] = 0

    return df


def generate_innings_data(fmt: str, seed: int = 42) -> pd.DataFrame:
    """
    Generate per-innings data for total runs, batting avg, bowling avg, etc.

    Returns DataFrame with columns:
        overs_played, wickets_lost, avg_batting_avg, avg_bowling_avg,
        avg_strike_rate, avg_economy, powerplay_runs, middle_overs_runs,
        total_innings_runs, team_batting_avg, team_bowling_avg,
        total_run_avg, overs_batted
    """
    cfg = FORMAT_CONFIG[fmt]
    rng = np.random.default_rng(seed + 100)
    N = cfg["samples"]
    max_ov = cfg["max_overs"]

    # How many overs the team actually batted (might be all out early)
    overs_batted = np.clip(
        rng.normal(max_ov * 0.85, max_ov * 0.15, N).astype(int),
        max_ov // 3,
        max_ov,
    )

    wickets_lost = np.clip(rng.poisson(4.5, N), 0, 10)

    avg_bat = np.round(
        rng.normal(cfg["avg_batting_avg"], 6, N).clip(15, 60), 1
    )
    avg_bowl = np.round(
        rng.normal(cfg["avg_bowling_avg"], 5, N).clip(15, 55), 1
    )
    avg_sr = np.round(
        rng.normal(cfg["avg_strike_rate"], 15, N).clip(35, 200), 1
    )
    avg_econ = np.round(
        rng.normal(cfg["avg_economy"], 1.0, N).clip(2, 14), 2
    )

    # Powerplay runs
    pp_overs = cfg["powerplay_end"]
    pp_runs = np.round(
        rng.normal(cfg["avg_run_rate"] * pp_overs * 1.1, pp_overs * 1.5, N).clip(
            pp_overs, pp_overs * 6
        )
    ).astype(int)

    # Middle overs runs
    mid_overs = cfg["death_over_start"] - pp_overs
    mid_runs = np.round(
        rng.normal(cfg["avg_run_rate"] * mid_overs * 0.85, mid_overs * 1.2, N).clip(
            mid_overs, mid_overs * 5
        )
    ).astype(int)

    # Total innings runs
    total_runs = (
        cfg["avg_run_rate"] * overs_batted
        + 0.8 * (avg_bat - cfg["avg_batting_avg"])
        - 0.6 * (avg_bowl - cfg["avg_bowling_avg"])
        + 0.3 * (avg_sr - cfg["avg_strike_rate"])
        - 3 * wickets_lost
        + rng.normal(0, 12, N)
    )
    total_runs = np.clip(total_runs.astype(int), 30, cfg["total_score_range"][1] + 80)

    # Team-level averages (targets)
    team_bat_avg = np.round(
        (total_runs / np.maximum(wickets_lost, 1)) * 0.6
        + avg_bat * 0.4
        + rng.normal(0, 3, N),
        1,
    ).clip(10, 80)

    team_bowl_avg = np.round(
        avg_bowl + rng.normal(0, 4, N) + 0.1 * wickets_lost, 1
    ).clip(12, 70)

    total_run_avg = np.round(total_runs / np.maximum(overs_batted, 1), 2)

    df = pd.DataFrame(
        {
            "overs_played": overs_batted,
            "wickets_lost": wickets_lost,
            "avg_batting_avg": avg_bat,
            "avg_bowling_avg": avg_bowl,
            "avg_strike_rate": avg_sr,
            "avg_economy": avg_econ,
            "powerplay_runs": pp_runs,
            "middle_overs_runs": mid_runs,
            "total_innings_runs": total_runs,
            "team_batting_avg": team_bat_avg,
            "team_bowling_avg": team_bowl_avg,
            "total_run_avg": total_run_avg,
            "overs_batted": overs_batted,
        }
    )

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Replace hidden zeros (impossible values) with column medians."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_clean = df.copy()
    for col in numeric_cols:
        if col in ("match_phase", "wickets_fallen", "wickets_lost", "over_number"):
            continue  # Zero is valid for these
        mask = df_clean[col] == 0
        if mask.any():
            df_clean.loc[mask, col] = np.nan
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    return df_clean


def get_all_format_data(seed: int = 42) -> dict:
    """
    Generate and clean data for all formats and both data types.

    Returns:
        {
            "t10": {"over": DataFrame, "innings": DataFrame},
            "t20": {"over": DataFrame, "innings": DataFrame},
            ...
        }
    """
    data = {}
    for fmt in FORMAT_CONFIG:
        over_df = clean_data(generate_over_data(fmt, seed))
        innings_df = clean_data(generate_innings_data(fmt, seed))
        data[fmt] = {"over": over_df, "innings": innings_df}
    return data
