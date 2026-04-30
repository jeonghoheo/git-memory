"""Tests for git_memory.auto_commit core functions — corrected with mocking."""

import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from typing import Dict, List

from git_memory.auto_commit import (
    categorize,
    extract_insights,
    load_transcript,
    is_processed,
    mark_processed,
    should_process_session,
)


# ── categorize() ─────────────────────────────────────────────────────────────

class TestCategorize:
    def test_meeting_keyword(self):
        assert categorize("I have a meeting tomorrow") == ("personal", "memo")

    def test_study_keyword(self):
        assert categorize("I will study Python") == ("learning", "notes")

    def test_project_keyword(self):
        # "task" → projects with subcategory "tasks" (from config)
        cat, sub = categorize("Need to finish this task")
        assert cat == "projects"
        assert sub == "tasks"

    def test_fallback_default(self):
        assert categorize("xyz nonsense") == ("daily", "notes")

    def test_word_boundary(self):
        # "planning" is keyword; "planningly" should not match
        cat, sub = categorize("the planningly thing")
        assert sub != "memo"

    def test_case_insensitive(self):
        assert categorize("A MEETING") == ("personal", "memo")


# ── extract_insights() ────────────────────────────────────────────────────────

class TestExtractInsights:
    def _msg(self, role: str, content: str, ts: str = "") -> Dict:
        return {
            "role": role,
            "content": content,
            "timestamp": ts or datetime.now(timezone.utc).isoformat(),
        }

    def test_keyword_match(self):
        msg = self._msg("user", "I want to study Rust")
        insights = extract_insights([msg])
        assert len(insights) == 1
        assert insights[0]["reason"] == "keyword:study"

    def test_assistant_explanation(self):
        msg = self._msg("assistant", "Remember to review the PR")
        insights = extract_insights([msg])
        assert len(insights) == 1
        assert insights[0]["reason"] == "assistant_explanation"

    def test_empty_content(self):
        assert extract_insights([self._msg("user", "   ")]) == []

    def test_multiple_mixed(self):
        msgs = [
            self._msg("user", "I study Python"),
            self._msg("user", "just chatting"),
            self._msg("assistant", "Note: check the logs"),
        ]
        insights = extract_insights(msgs)
        assert len(insights) == 2


# ── load_transcript() ─────────────────────────────────────────────────────────

class TestLoadTranscript:
    def test_loads_json(self, tmp_path):
        f = tmp_path / "t.json"
        f.write_text(json.dumps({"messages": [{"role": "user", "content": "hi"}]}))
        assert load_transcript(f) == [{"role": "user", "content": "hi"}]

    def test_missing_returns_empty(self, tmp_path):
        assert load_transcript(tmp_path / "nope.json") == []

    def test_malformed_returns_empty(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("invalid")
        assert load_transcript(f) == []


# ── is_processed / mark_processed ─────────────────────────────────────────────

class TestProcessedFlag:
    @patch("git_memory.auto_commit.PROCESSED_MARKER")
    def test_false_when_missing(self, mock_marker):
        mock_marker.exists.return_value = False
        assert is_processed(Path("x")) is False

    @patch("git_memory.auto_commit.PROCESSED_MARKER")
    def test_true_when_match(self, mock_marker):
        mock_marker.exists.return_value = True
        mock_marker.read_text.return_value = "x"
        assert is_processed(Path("x")) is True

    @patch("git_memory.auto_commit.PROCESSED_MARKER")
    def test_false_when_differs(self, mock_marker):
        mock_marker.exists.return_value = True
        mock_marker.read_text.return_value = "y"
        assert is_processed(Path("x")) is False

    @patch("git_memory.auto_commit.PROCESSED_MARKER")
    def test_mark_writes(self, mock_marker):
        mark_processed(Path("sess"))
        mock_marker.write_text.assert_called_once_with("sess")


# ── already_committed() ───────────────────────────────────────────────────────

class TestAlreadyCommitted:
    @patch("git_memory.auto_commit.run_git_command")
    def test_false_when_no_commit(self, mock_git):
        mock_git.return_value = (False, "")
        from git_memory.auto_commit import already_committed
        assert already_committed("sess") is False

    @patch("git_memory.auto_commit.run_git_command")
    def test_true_when_commit_found(self, mock_git):
        mock_git.return_value = (True, "feat: session sess")
        from git_memory.auto_commit import already_committed
        assert already_committed("sess") is True


# ── should_process_session() ──────────────────────────────────────────────────

class TestShouldProcessSession:
    def test_rejects_too_few_messages(self, tmp_path):
        ok, reason = should_process_session(tmp_path / "s.json", [])
        assert (ok, reason) == (False, "too_few_messages")

    def test_rejects_too_short_duration(self, tmp_path):
        base = datetime(2025, 1, 1, 12, 0, 0)
        msgs = [
            {"role": "user", "content": "a", "timestamp": base.isoformat()},
            {"role": "user", "content": "b", "timestamp": (base.replace(second=10)).isoformat()},
        ]
        ok, reason = should_process_session(tmp_path / "s.json", msgs)
        assert (ok, reason) == (False, "too_short")

    @patch("git_memory.auto_commit.already_committed", return_value=True)
    @patch("git_memory.auto_commit.is_processed", return_value=False)
    def test_skips_already_committed(self, mock_is, mock_ac, tmp_path):
        base = datetime(2025, 1, 1, 12, 0, 0)
        msgs = [
            {"role": "user", "content": "a", "timestamp": base.isoformat()},
            {"role": "user", "content": "b", "timestamp": (base.replace(minute=1)).isoformat()},
        ]
        ok, reason = should_process_session(tmp_path / "s.json", msgs)
        assert (ok, reason) == (False, "already_processed")

    @patch("git_memory.auto_commit.already_committed", return_value=False)
    @patch("git_memory.auto_commit.is_processed", return_value=False)
    def test_accepts_when_all_ok(self, mock_is, mock_ac, tmp_path):
        base = datetime(2025, 1, 1, 12, 0, 0)
        msgs = [
            {"role": "user", "content": "a", "timestamp": base.isoformat()},
            {"role": "user", "content": "b", "timestamp": (base.replace(minute=1)).isoformat()},
        ]
        ok, reason = should_process_session(tmp_path / "s.json", msgs)
        assert (ok, reason) == (True, "ok")
