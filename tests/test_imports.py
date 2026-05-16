import importlib


def test_riskops_package_imports() -> None:
    package = importlib.import_module("riskops")
    assert package.__version__ == "0.0.0"
