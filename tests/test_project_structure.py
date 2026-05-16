from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_core_directories_exist() -> None:
    required_directories = [
        "riskops",
        "riskops/data",
        "riskops/data/generators",
        "riskops/data/warehouse",
        "riskops/data/quality",
        "riskops/metrics",
        "riskops/metrics/calculators",
        "riskops/engines",
        "riskops/engines/anomaly",
        "riskops/engines/attribution",
        "riskops/engines/visualization",
        "riskops/engines/report",
        "riskops/engines/qc",
        "riskops/engines/script",
        "riskops/agents",
        "riskops/agents/prompts",
        "riskops/tui",
        "synthetic_data/raw_secure",
        "synthetic_data/dim",
        "synthetic_data/ods",
        "synthetic_data/dwd",
        "synthetic_data/dws",
        "synthetic_data/ads",
        "metadata",
        "schemas",
        "templates/html",
        "templates/ppt",
        "templates/word",
        "templates/excel",
        "configs",
        "docs/prd",
        "docs/prd/history",
        "docs/prd/en",
        "docs/decisions",
        "docs/screenshots",
        "reports",
        "exports",
        "tests",
        "scripts",
    ]

    missing = [path for path in required_directories if not (ROOT / path).is_dir()]
    assert missing == []


def test_script_files_exist() -> None:
    scripts = [
        "scripts/generate_synthetic_data.py",
        "scripts/build_warehouse.py",
        "scripts/render_docs.py",
        "scripts/validate_data_quality.py",
        "scripts/validate_metric_quality.py",
    ]

    missing = [path for path in scripts if not (ROOT / path).is_file()]
    assert missing == []


def test_metadata_and_schemas_directories_exist() -> None:
    assert (ROOT / "metadata").is_dir()
    assert (ROOT / "schemas").is_dir()
