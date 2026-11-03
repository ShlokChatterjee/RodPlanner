"""Smoke test: verifies the package is importable (src layout is wired correctly)."""


def test_package_importable() -> None:
    import rodplanner  # noqa: F401
