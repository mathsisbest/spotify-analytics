"""Tests for dbt model queries and SQL schema contracts."""

from __future__ import annotations

import pathlib


def test_dbt_models_exist() -> None:
    transform_dir = pathlib.Path(__file__).parent.parent / "transform" / "models"
    staging_file = transform_dir / "staging" / "stg_streaming_history.sql"
    fct_listening = transform_dir / "marts" / "fct_listening.sql"
    fct_summary = transform_dir / "marts" / "fct_daily_summary.sql"
    schema_file = transform_dir / "schema.yml"

    assert staging_file.exists(), "stg_streaming_history.sql must exist"
    assert fct_listening.exists(), "fct_listening.sql must exist"
    assert fct_summary.exists(), "fct_daily_summary.sql must exist"
    assert schema_file.exists(), "schema.yml must exist"


def test_schema_yml_contains_models() -> None:
    schema_file = pathlib.Path(__file__).parent.parent / "transform" / "models" / "schema.yml"
    content = schema_file.read_text()
    assert "stg_streaming_history" in content
    assert "stg_track_features" in content
    assert "fct_listening" in content
    assert "fct_daily_summary" in content
