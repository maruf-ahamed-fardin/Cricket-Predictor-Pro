"""
Tests for the real cricket data importer service.
"""
import os
import tempfile
import pytest
import pandas as pd

from app.services.data_importer import CricketDataImporter, OVER_COLUMNS


class TestCricketDataImporter:
    """Test CricketDataImporter functionality."""

    def test_importer_initialization(self):
        importer = CricketDataImporter()
        assert importer.data_dir is not None

    def test_export_sample_template(self):
        importer = CricketDataImporter()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "sample_template.csv")
            res = importer.export_sample_template(out_path)
            assert os.path.exists(res)
            df = pd.read_csv(res)
            assert "match_id" in df.columns
            assert "over" in df.columns
            assert "batsman_runs" in df.columns

    def test_import_valid_ball_by_ball_csv(self):
        importer = CricketDataImporter()
        with tempfile.TemporaryDirectory() as tmpdir:
            sample_file = os.path.join(tmpdir, "matches.csv")
            importer.export_sample_template(sample_file)

            df = importer.import_ball_by_ball_csv(sample_file, fmt="t20")
            assert df is not None
            assert isinstance(df, pd.DataFrame)
            for col in OVER_COLUMNS:
                assert col in df.columns

    def test_import_nonexistent_file_returns_none(self):
        importer = CricketDataImporter()
        df = importer.import_ball_by_ball_csv("nonexistent_path_xyz.csv", fmt="t20")
        assert df is None
