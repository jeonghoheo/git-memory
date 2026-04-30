"""Tests for git_memory.auto_commit module."""

from git_memory.auto_commit import load_config


def test_load_config_returns_dict():
    """load_config() should return a dictionary."""
    config = load_config()
    assert isinstance(config, dict)


def test_config_has_required_keys():
    """Config should have at least one expected key."""
    config = load_config()
    expected_keys = ["hermes_sessions", "git_memory_repo", "log_file"]
    assert any(key in config for key in expected_keys)


def test_config_git_section():
    """Config should have a 'git' section with expected keys."""
    config = load_config()
    assert "git" in config
    assert "auto_add" in config["git"]
    assert "commit_prefix" in config["git"]


def test_config_logging_section():
    """Config should have a 'logging' section."""
    config = load_config()
    assert "logging" in config
    assert "level" in config["logging"]
