"""Enforces the inward-only layer rules from CLAUDE.md."""

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[1] / "pawmatch"
FRAMEWORKS = {"fastapi", "pydantic", "psycopg", "starlette", "uvicorn"}
FORBIDDEN_LAYERS = {
    "domain": {"application", "infrastructure", "interface", "main"},
    "application": {"infrastructure", "interface", "main"},
    "infrastructure": {"interface", "main"},
    "interface": {"infrastructure", "main"},
}


def imported_modules(path: Path) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, f"{path}: use absolute imports"
            modules.add(node.module or "")
            modules.update(f"{node.module}.{alias.name}" for alias in node.names)
    return modules


@pytest.mark.parametrize("layer", FORBIDDEN_LAYERS)
def test_layer_does_not_import_outward(layer: str) -> None:
    files = list((PACKAGE / layer).rglob("*.py"))
    assert files, f"no source files found for {layer}"
    forbidden = {f"pawmatch.{name}" for name in FORBIDDEN_LAYERS[layer]}
    for path in files:
        for module in imported_modules(path):
            assert not any(module == f or module.startswith(f"{f}.") for f in forbidden), (
                f"{path} imports {module}"
            )


@pytest.mark.parametrize("layer", ["domain", "application"])
def test_inner_layers_import_no_framework_or_driver(layer: str) -> None:
    for path in (PACKAGE / layer).rglob("*.py"):
        roots = {module.split(".")[0] for module in imported_modules(path)}
        assert not roots & FRAMEWORKS, f"{path} imports {roots & FRAMEWORKS}"


def test_sql_driver_is_only_used_by_infrastructure() -> None:
    for path in PACKAGE.rglob("*.py"):
        if "infrastructure" in path.parts:
            continue
        roots = {module.split(".")[0] for module in imported_modules(path)}
        assert "psycopg" not in roots, f"{path} imports psycopg"
