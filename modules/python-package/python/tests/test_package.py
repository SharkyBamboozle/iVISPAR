"""Smoke test: the architecture decomposition is an executable contract.

Every subpackage seam must import; renaming or deleting a seam breaks CI,
which forces the docs/ADR conversation instead of silent drift.
"""

import importlib

PACKAGE = "{{PACKAGE_NAME}}"

# BLUEPRINT: one entry per architecture seam (docstring-stub subpackages).
SUBPACKAGES: list[str] = [
    # "schemas",
    # "core",
]


def test_package_imports():
    importlib.import_module(PACKAGE)


def test_version():
    pkg = importlib.import_module(PACKAGE)
    assert isinstance(pkg.__version__, str) and pkg.__version__


def test_subpackage_seams():
    for sub in SUBPACKAGES:
        importlib.import_module(f"{PACKAGE}.{sub}")
