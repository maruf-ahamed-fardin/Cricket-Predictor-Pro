"""
Tests for the data generator service.
"""
import pytest
import pandas as pd
import numpy as np

from app.services.data_generator import (
    FORMAT_CONFIG,
    generate_over_data,
    generate_innings_data,
    clean_data,
    get_all_format_data,
)


class TestFormatConfig:
    """Test FORMAT_CONFIG structure."""

    def test_all_formats_present(self):
        assert set(FORMAT_CONFIG.keys()) == {"t10", "t20", "odi", "test"}

    def test_required_keys_in_each_format(self):
        required = [
            "name", "max_overs", "total_score_range", "avg_run_rate",
            "avg_batting_avg", "avg_bowling_avg", "avg_economy",
            "avg_strike_rate", "death_over_start", "powerplay_end", "samples",
        ]
        for fmt, cfg in FORMAT_CONFIG.items():
            for key in required:
                assert key in cfg, f"Missing key '{key}' in format '{fmt}'"

    def test_max_overs_order(self):
        """T10 < T20 < ODI < Test."""
        assert FORMAT_CONFIG["t10"]["max_overs"] < FORMAT_CONFIG["t20"]["max_overs"]
        assert FORMAT_CONFIG["t20"]["max_overs"] < FORMAT_CONFIG["odi"]["max_overs"]
        assert FORMAT_CONFIG["odi"]["max_overs"] < FORMAT_CONFIG["test"]["max_overs"]

    def test_score_ranges_are_tuples_of_two(self):
        for fmt, cfg in FORMAT_CONFIG.items():
            sr = cfg["total_score_range"]
            assert len(sr) == 2
            assert sr[0] < sr[1], f"Invalid score range in {fmt}"


class TestGenerateOverData:
    """Test over-level synthetic data generation."""

    EXPECTED_COLS = {
        "over_number", "wickets_fallen", "batsman_avg",
        "bowler_econ", "strike_rate", "match_phase", "runs_in_over",
    }

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_returns_dataframe(self, fmt):
        df = generate_over_data(fmt)
        assert isinstance(df, pd.DataFrame)

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_expected_columns(self, fmt):
        df = generate_over_data(fmt)
        assert self.EXPECTED_COLS.issubset(set(df.columns))

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_row_count(self, fmt):
        df = generate_over_data(fmt)
        assert len(df) == FORMAT_CONFIG[fmt]["samples"]

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_over_number_in_range(self, fmt):
        df = generate_over_data(fmt)
        max_ov = FORMAT_CONFIG[fmt]["max_overs"]
        assert df["over_number"].min() >= 1
        assert df["over_number"].max() <= max_ov

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_wickets_non_negative(self, fmt):
        df = generate_over_data(fmt)
        assert (df["wickets_fallen"] >= 0).all()

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_runs_in_over_non_negative(self, fmt):
        df = generate_over_data(fmt)
        assert (df["runs_in_over"] >= 0).all()

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_match_phase_valid_values(self, fmt):
        df = generate_over_data(fmt)
        assert set(df["match_phase"].unique()).issubset({0, 1, 2})

    def test_deterministic_with_same_seed(self):
        df1 = generate_over_data("t20", seed=7)
        df2 = generate_over_data("t20", seed=7)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_results_different_seed(self):
        df1 = generate_over_data("t20", seed=1)
        df2 = generate_over_data("t20", seed=2)
        assert not df1.equals(df2)


class TestGenerateInningsData:
    """Test innings-level synthetic data generation."""

    EXPECTED_COLS = {
        "overs_played", "wickets_lost", "avg_batting_avg", "avg_bowling_avg",
        "avg_strike_rate", "avg_economy", "powerplay_runs", "middle_overs_runs",
        "total_innings_runs", "team_batting_avg", "team_bowling_avg",
        "total_run_avg", "overs_batted",
    }

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_returns_dataframe(self, fmt):
        df = generate_innings_data(fmt)
        assert isinstance(df, pd.DataFrame)

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_expected_columns(self, fmt):
        df = generate_innings_data(fmt)
        assert self.EXPECTED_COLS.issubset(set(df.columns))

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_total_runs_positive(self, fmt):
        df = generate_innings_data(fmt)
        assert (df["total_innings_runs"] > 0).all()

    @pytest.mark.parametrize("fmt", ["t10", "t20", "odi", "test"])
    def test_wickets_between_0_and_10(self, fmt):
        df = generate_innings_data(fmt)
        assert df["wickets_lost"].between(0, 10).all()


class TestCleanData:
    """Test data cleaning logic."""

    def test_zeros_replaced_in_float_cols(self):
        df = generate_over_data("t20", seed=42)
        # Inject known zeros
        df.loc[0, "batsman_avg"] = 0
        df.loc[1, "bowler_econ"] = 0
        cleaned = clean_data(df)
        assert cleaned.loc[0, "batsman_avg"] != 0
        assert cleaned.loc[1, "bowler_econ"] != 0

    def test_zero_valid_in_match_phase(self):
        df = generate_over_data("t20", seed=42)
        cleaned = clean_data(df)
        # match_phase 0 (powerplay) should still be present
        assert (cleaned["match_phase"] == 0).any()

    def test_no_nulls_after_clean(self):
        df = generate_over_data("t20", seed=42)
        cleaned = clean_data(df)
        assert not cleaned.isnull().any().any()


class TestGetAllFormatData:
    """Test the combined data factory."""

    def test_returns_all_formats(self):
        data = get_all_format_data()
        assert set(data.keys()) == {"t10", "t20", "odi", "test"}

    def test_each_format_has_over_and_innings(self):
        data = get_all_format_data()
        for fmt, fdata in data.items():
            assert "over" in fdata
            assert "innings" in fdata

    def test_both_are_dataframes(self):
        data = get_all_format_data()
        for fmt, fdata in data.items():
            assert isinstance(fdata["over"], pd.DataFrame)
            assert isinstance(fdata["innings"], pd.DataFrame)
