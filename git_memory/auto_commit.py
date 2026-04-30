#!/usr/bin/env python3
"""
Git Memory Auto-Commit Hook

Monitors AI assistant sessions and auto-commits important insights
to ~/git-memory Git repository.

Features:
- Config-driven paths and keywords
- Duplicate commit prevention (git history check via already_committed())
- Word boundary keyword matching
- Transactional git operations with rollback
- Log rotation (RotatingFileHandler, 10MB limit, 5 backups)
"""

from __future__ import annotations
import os
import re
import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, cast
from . import __version__  # package version
import yaml
from logging.handlers import RotatingFileHandler

# ── Config ─────────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(
    os.environ.get("git-memory_CONFIG", Path.home() / "git-memory" / "config.yaml")
)


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return cast(Dict[str, Any], yaml.safe_load(f))
    return {
        "hermes_sessions": Path.cwd() / "sessions",
        "git_memory_repo": Path.home() / "git-memory",
        "log_file": Path.home() / "logs" / "git_memory.log",
        "processed_marker": Path.home() / ".git-memory" / "last_processed.txt",
        "git": {"auto_add": True, "commit_prefix": "Auto-save:"},
        "logging": {"level": "INFO", "max_bytes": 10485760, "backup_count": 5},
    }


CONFIG: Dict[str, Any] = load_config()

HERMES_SESSIONS: Path = Path(
    CONFIG.get("hermes_sessions", Path.cwd() / "sessions")
).expanduser()
GIT_MEMORY: Path = Path(
    CONFIG.get("git_memory_repo", Path.home() / "git-memory")
).expanduser()
LOG_FILE: Path = Path(
    CONFIG.get("log_file", Path.home() / "logs" / "git_memory.log")
).expanduser()
PROCESSED_MARKER: Path = Path(
    CONFIG.get("processed_marker", Path.home() / ".git-memory" / "last_processed.txt")
).expanduser()

# Keywords from config — aggregate ALL categories for importance detection
PERSONAL_KEYWORDS = [
    kw.lower() for kw in CONFIG.get("keywords", {}).get("personal", [])
]
LEARNING_KEYWORDS = [
    kw.lower() for kw in CONFIG.get("keywords", {}).get("learning", [])
]
# Include all remaining categories (projects, wedding, etc.)
ALL_KEYWORDS = []
for cat_name, kw_list in CONFIG.get("keywords", {}).items():
    if cat_name not in ("personal", "learning"):
        ALL_KEYWORDS.extend([kw.lower() for kw in kw_list])
IMPORTANT_KEYWORDS = PERSONAL_KEYWORDS + LEARNING_KEYWORDS + ALL_KEYWORDS

CATEGORY_RULES = CONFIG.get(
    "category_rules",
    [
        {"keywords": PERSONAL_KEYWORDS, "category": "personal", "subcategory": "memo"},
        {"keywords": LEARNING_KEYWORDS, "category": "learning", "subcategory": "notes"},
    ],
)

# ── 로깅 설정 ─────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
log_level = getattr(logging, CONFIG.get("logging", {}).get("level", "INFO"))
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=CONFIG.get("logging", {}).get("max_bytes", 10485760),
            backupCount=CONFIG.get("logging", {}).get("backup_count", 5),
        )
    ],
)
logger = logging.getLogger(__name__)


# ── 헬퍼 함수 ─────────────────────────────────────────────────────────────────
def run_git_command(args: List[str], cwd: Path = GIT_MEMORY) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd)] + args, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            logger.error(f"Git command failed: git {' '.join(args)}\n{result.stderr}")
            return False, ""  # operation failed, empty stderr
        return True, result.stdout.strip()
    except Exception as e:
        logger.error(f"Git command exception: {e}")
        return False, str(e)


def ensure_git_config() -> None:
    """Ensure git user.name and user.email are set"""
    success, _ = run_git_command(["config", "user.name"], GIT_MEMORY)
    if not success:
        logger.info("Setting git config in Git Memory repo")
        run_git_command(["config", "user.name", "Iskra Agent"], GIT_MEMORY)
        run_git_command(["config", "user.email", "hermes@localhost"], GIT_MEMORY)


def get_latest_session_file() -> Optional[Path]:
    files = list(HERMES_SESSIONS.glob("session_*.json"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def load_transcript(session_file: Path) -> List[Dict]:
    try:
        data = json.loads(session_file.read_text())
        return data.get("messages", [])
    except Exception as e:
        logger.error(f"Failed to load transcript {session_file.name}: {e}")
        return []


def should_process_session(
    session_file: Path, messages: List[Dict]
) -> Tuple[bool, str]:
    msgs = len(messages)
    duration = 0
    if messages:
        try:
            start = datetime.fromisoformat(messages[0].get("timestamp", ""))
            end = datetime.fromisoformat(messages[-1].get("timestamp", ""))
            duration = int(
                (end - start).total_seconds()
            )  # Convert to int for type compatibility
        except Exception:
            pass

    if msgs < 2:
        return False, "too_few_messages"
    if duration < 30:
        return False, "too_short"

    session_id = session_file.stem
    if session_id.startswith("session_"):
        session_id = session_id[8:]
    if already_committed(session_id):
        return False, "already_processed"

    return True, "ok"


def categorize(content: str) -> Tuple[str, str]:
    cl = content.lower()
    for rule in CATEGORY_RULES:
        keywords = rule.get("keywords", [])
        if any(re.search(r"\b" + re.escape(kw) + r"\b", cl) for kw in keywords):
            return rule.get("category", "daily"), rule.get("subcategory", "notes")
    return "daily", "notes"


def extract_insights(messages: List[Dict]) -> List[Dict]:
    insights = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not content.strip():
            continue

        is_important = False
        reason = None

        # Keyword matching with word boundaries
        cl = content.lower()
        for kw in IMPORTANT_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", cl):
                is_important = True
                reason = f"keyword:{kw}"
                break

        # Assistant explanations
        if role == "assistant" and any(w in cl for w in ["remember", "note", "key"]):
            is_important = True
            reason = "assistant_explanation"

        if is_important:
            insights.append(
                {
                    "role": role,
                    "content": content,
                    "reason": reason,
                    "timestamp": msg.get("timestamp", ""),
                }
            )
    return insights


def already_committed(session_id: str) -> bool:
    success, output = run_git_command(
        ["log", "--oneline", "--grep", f"session {session_id}"], GIT_MEMORY
    )
    return success and output.strip() != ""


def mark_processed(session_file: Path) -> bool:
    try:
        PROCESSED_MARKER.parent.mkdir(parents=True, exist_ok=True)
        PROCESSED_MARKER.write_text(session_file.name)
        return True
    except Exception as e:
        logger.error(f"Failed to mark processed: {e}")
        return False


def is_processed(session_file: Path) -> bool:
    if not PROCESSED_MARKER.exists():
        return False
    try:
        return PROCESSED_MARKER.read_text().strip() == session_file.name
    except Exception:
        return False


def write_to_git_memory(
    session_file: Path, insights: List[Dict], dry_run: bool = False
) -> bool:
    try:
        data = json.loads(session_file.read_text())
        session_id = data["session_id"]
        session_date = datetime.fromisoformat(data["session_start"]).strftime(
            "%Y-%m-%d"
        )
    except Exception as e:
        logger.error(f"Failed to parse session metadata: {e}")
        return False

    if dry_run:
        logger.info("🌊 DRY-RUN mode: no git operations will be performed")

    # Prevent duplicate commits
    if already_committed(session_id):
        logger.info(f"⏭️  Skipping already-committed session: {session_id}")
        return True  # already_committed -> skip but True (not an error)

    categories: Dict[str, List[Dict]] = {}
    for insight in insights:
        cat, subcat = categorize(insight["content"])
        key = f"{cat}/{subcat}"
        categories.setdefault(key, []).append(insight)

    files_written = []
    for cat_key, items in categories.items():
        cat, subcat = cat_key.split("/")
        cat_dir = GIT_MEMORY / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{session_date}_{subcat}.md"
        filepath = cat_dir / filename

        lines_content = [
            f"# {cat.title()} - {session_date}",
            f"**Source:** AI assistant session `{session_id}`",
            f"**Date:** {session_date}",
            "",
        ]

        for item in items:
            icon = "👤" if item["role"] == "user" else "🤖"
            lines_content.append(f"### {icon} {item['role'].title()}")
            lines_content.append(f"> {item['content']}")
            lines_content.append("")

        content = "\n".join(lines_content)

        if filepath.exists():
            existing = filepath.read_text()
            if f"session: {session_id}" not in existing:
                content = existing + "\n" + content

        filepath.write_text(content)
        files_written.append(str(filepath))

        if not dry_run and CONFIG.get("git", {}).get("auto_add", True):
            success, _ = run_git_command(["add", str(filepath.relative_to(GIT_MEMORY))])
            if not success:
                logger.error(f"Failed to add {filepath} to git index")
                # Rollback any previously staged files
                for f in files_written[:-1]:  # All except current
                    run_git_command(["reset", "HEAD", str(f)])
                return False  # operation failed
        elif dry_run:
            logger.info(
                f"  [DRY-RUN] Would run: git add {filepath.relative_to(GIT_MEMORY)}"
            )

    if files_written:
        prefix = CONFIG.get("git", {}).get("commit_prefix", "Auto-save:")
        msg = f"{prefix} session {session_id} ({session_date})\n\n"
        # Add insights preview (extracted from categories)
        insights_list = []
        for cat_key, items in categories.items():
            for item in items[:3]:  # Top 3 items per category
                content_text = item.get("content", "")
                preview = content_text[:100].strip()
                if preview:
                    insights_list.append(
                        f"[{cat_key}] {preview}..."
                        if len(content_text) > 100
                        else preview
                    )
                else:
                    insights_list.append(f"[{cat_key}] (empty)")

        if insights_list:
            msg += f"Categories: {', '.join(categories.keys())} ({len(insights_list)} insights)\n\n"
            msg += "Insights preview:\n"
            for insight in insights_list[:5]:  # Max 5 total
                msg += f"  • {insight}\n"
        else:
            msg += f"Categories: {', '.join(categories.keys())}\n"

        msg += f"Files: {', '.join(Path(f).name for f in files_written)}"

        if dry_run:
            logger.info(f"  [DRY-RUN] Would commit with message:\n{msg}")
            logger.info(
                f"  [DRY-RUN] Would commit {len(files_written)} files: {', '.join(Path(f).name for f in files_written)}"
            )
            # In dry-run, don't actually commit or mark processed
            return True
        else:
            success, output = run_git_command(["commit", "-m", msg])
            if success:
                logger.info(
                    f"✅ Committed {len(files_written)} files: {', '.join(Path(f).name for f in files_written)}"
                )
                mark_processed(session_file)
                return True  # successfully committed
            else:
                logger.error(f"Git commit failed: {output}")
                # Rollback
                for f in files_written:
                    run_git_command(["reset", "HEAD", str(f)])
                return False  # operation failed
    else:
        logger.info("ℹ️  No insights to commit")
        return True


# ── 메인 루프 ─────────────────────────────────────────────────────────────────
def main(dry_run: bool = False, force: bool = False) -> int:
    """Main entry point for git-memory auto-commit.

    Args:
        dry_run: If True, only print what would be done without touching git.
        force: If True, process the latest session even if already processed.

    Returns:
        0 on success, 1 on error.
    """
    logger.info("=== Git Memory Auto-Commit Started ===")

    if dry_run:
        logger.info("🌊 DRY-RUN mode: simulating operations without changes")

    if not HERMES_SESSIONS.exists():
        logger.error(f"AI assistant sessions directory missing: {HERMES_SESSIONS}")
        return 1
    if not GIT_MEMORY.exists():
        logger.error(f"Git memory repo missing: {GIT_MEMORY}")
        return 1
    if not GIT_MEMORY.joinpath(".git").exists():
        logger.error(f"Not a git repository: {GIT_MEMORY}")
        return 1

    ensure_git_config()

    session_file = get_latest_session_file()
    if not session_file:
        logger.info("ℹ️  No sessions found")
        return 0

    messages = load_transcript(session_file)
    if not messages:
        logger.warning(f"Empty or invalid transcript: {session_file.name}")
        if not dry_run:
            mark_processed(session_file)
        return 0

    # Force mode bypasses already_processed check
    if force:
        logger.info("🔧 Force mode activated — processing anyway")
        should_p = True
        reason = "forced"
    else:
        should_p, reason = should_process_session(session_file, messages)

    if not should_p:
        if reason == "already_processed":
            logger.debug(f"Already processed: {session_file.name}")
        else:
            logger.info(f"Skipped: {reason}")
            if not dry_run:
                mark_processed(session_file)
        return 0

    insights = extract_insights(messages)
    logger.info(f"💡 Extracted {len(insights)} insights from {len(messages)} messages")

    if write_to_git_memory(session_file, insights, dry_run=dry_run):
        if dry_run:
            logger.info("✅ Dry-run simulation completed successfully")
        else:
            logger.info("✅ Git memory updated successfully")
        return 0
    else:
        logger.error("❌ Failed to write to git memory")
        return 1


def cli_main() -> int:
    """Command-line interface entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        prog="git-memory",
        description="Automatic AI session memory storage with Git integration",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be committed without making any changes",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Process the latest session even if already committed",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable DEBUG level logging"
    )
    parser.add_argument(
        "--version", action="version", version=f"git-memory {__version__}"
    )

    args = parser.parse_args()

    # Set up console handler for CLI output
    console_handler = logging.StreamHandler(sys.stdout)
    console_level = logging.DEBUG if args.verbose else logging.INFO
    console_handler.setLevel(console_level)
    console_fmt = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    return main(dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    sys.exit(cli_main())
