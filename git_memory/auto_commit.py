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
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import yaml
from logging.handlers import RotatingFileHandler

# ── Config ─────────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(
    os.environ.get("git-memory_CONFIG",
                   Path.home() / "git-memory" / "config.yaml")
)

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {
        "hermes_sessions": Path.cwd() / "sessions",
        "git_memory_repo": Path.home() / "git-memory",
        "log_file": Path.home() / "logs" / "git_memory.log",
        "processed_marker": Path.home() / ".git-memory" / "last_processed.txt",
        "git": {"auto_add": True, "commit_prefix": "Auto-save:"},
        "logging": {"level": "INFO", "max_bytes": 10485760, "backup_count": 5},
    }

CONFIG = load_config()

HERMES_SESSIONS = Path(CONFIG.get("hermes_sessions", Path.cwd() / "sessions")).expanduser()
GIT_MEMORY = Path(CONFIG.get("git_memory_repo", Path.home() / "git-memory")).expanduser()
LOG_FILE = Path(CONFIG.get("log_file", Path.home() / "logs" / "git_memory.log")).expanduser()
PROCESSED_MARKER = Path(CONFIG.get("processed_marker", Path.home() / ".git-memory" / "last_processed.txt")).expanduser()

# Keywords from config
PERSONAL_KEYWORDS = [kw.lower() for kw in CONFIG.get("keywords", {}).get("personal", ["meeting", "planning", "decision"])]
LEARNING_KEYWORDS = [kw.lower() for kw in CONFIG.get("keywords", {}).get("learning", ["study", "learn", "concept"])]
IMPORTANT_KEYWORDS = PERSONAL_KEYWORDS + LEARNING_KEYWORDS

CATEGORY_RULES = CONFIG.get("category_rules", [
    {"keywords": PERSONAL_KEYWORDS, "category": "personal", "subcategory": "memo"},
    {"keywords": LEARNING_KEYWORDS, "category": "learning", "subcategory": "notes"},
])

# ── 로깅 설정 ─────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
log_level = getattr(logging, CONFIG["logging"].get("level", "INFO"))
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=CONFIG["logging"].get("max_bytes", 10485760),
            backupCount=CONFIG["logging"].get("backup_count", 5)
        )
    ]
)
logger = logging.getLogger(__name__)

# ── 헬퍼 함수 ─────────────────────────────────────────────────────────────────
def run_git_command(args: List[str], cwd: Path = GIT_MEMORY) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd)] + args,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            logger.error(f"Git command failed: git {' '.join(args)}\n{result.stderr}")
            return False  # operation failed, result.stderr
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

def should_process_session(session_file: Path, messages: List[Dict]) -> Tuple[bool, str]:
    msgs = len(messages)
    duration = 0
    if messages:
        try:
            start = datetime.fromisoformat(messages[0].get("timestamp", ""))
            end = datetime.fromisoformat(messages[-1].get("timestamp", ""))
            duration = (end - start).total_seconds()
        except:
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
        if any(kw in cl for kw in rule.get("keywords", [])):
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
            if re.search(r'\b' + re.escape(kw) + r'\b', cl):
                is_important = True
                reason = f"keyword:{kw}"
                break
        
                
        # Assistant explanations
        if role == "assistant" and any(w in cl for w in ["remember", "note", "key"]):
            is_important = True
            reason = "assistant_explanation"
        
        if is_important:
            insights.append({
                "role": role,
                "content": content,
                "reason": reason,
                "timestamp": msg.get("timestamp", ""),
            })
    return insights

def already_committed(session_id: str) -> bool:
    success, output = run_git_command(
        ["log", "--oneline", "--grep", f"session {session_id}"],
        GIT_MEMORY
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
    except:
        return False

def write_to_git_memory(session_file: Path, insights: List[Dict]) -> bool:
    try:
        data = json.loads(session_file.read_text())
        session_id = data["session_id"]
        session_date = datetime.fromisoformat(data["session_start"]).strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"Failed to parse session metadata: {e}")
        return False
    
    # Prevent duplicate commits
    if already_committed(session_id):
        logger.info(f"⏭️  Skipping already-committed session: {session_id}")
        return True   # already_committed -> skip but True (not an error)
    
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
        
        if CONFIG.get("git", {}).get("auto_add", True):
            success, _ = run_git_command(["add", str(filepath.relative_to(GIT_MEMORY))])
            if not success:
                logger.error(f"Failed to add {filepath} to git index")
                # Rollback any previously staged files
                for f in files_written[:-1]:  # All except current
                    run_git_command(["reset", "HEAD", str(f)])
                return False  # operation failed
    
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
                    insights_list.append(f"[{cat_key}] {preview}..." if len(content_text) > 100 else preview)
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
        
        success, output = run_git_command(["commit", "-m", msg])
        if success:
            logger.info(f"✅ Committed {len(files_written)} files: {', '.join(Path(f).name for f in files_written)}")
            mark_processed(session_file)
            return True   # successfully committed
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
def main() -> int:
    logger.info("=== Git Memory Auto-Commit Started ===")
    
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
        mark_processed(session_file)
        return 0
    
    should_p, reason = should_process_session(session_file, messages)
    if not should_p:
        if reason == "already_processed":
            logger.debug(f"Already processed: {session_file.name}")
        else:
            logger.info(f"Skipped: {reason}")
            mark_processed(session_file)
        return 0
    
    insights = extract_insights(messages)
    logger.info(f"💡 Extracted {len(insights)} insights from {len(messages)} messages")

    if write_to_git_memory(session_file, insights):
        logger.info("✅ Git memory updated successfully")
        return 0
    else:
        logger.error("❌ Failed to write to git memory")
        return 1

if __name__ == "__main__":
    force_mode = "--force" in sys.argv
    
    if force_mode:
        logger.info("🔧 Force mode activated")
        session_file = get_latest_session_file()
        if not session_file:
            logger.info("ℹ️  No sessions found")
            sys.exit(0)
        messages = load_transcript(session_file)
        if not messages:
            logger.warning(f"Empty transcript: {session_file.name}")
            sys.exit(0)
        
        insights = extract_insights(messages)
        logger.info(f"💡 Extracted {len(insights)} insights (force mode)")
        
        result = write_to_git_memory(session_file, insights)
        if result:
            logger.info("✅ Force mode completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Force commit failed")
            sys.exit(1)
    else:
        sys.exit(main())
