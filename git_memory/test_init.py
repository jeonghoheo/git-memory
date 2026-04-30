"""Tests for git_memory package initialization."""

import git_memory
from git_memory import __version__, main


def test_version():
    """Package should have a version string."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_main_importable():
    """main should be importable and callable."""
    assert callable(main)


def test_package_all():
    """Package __all__ should contain 'main'."""
    assert "main" in git_memory.__all__
