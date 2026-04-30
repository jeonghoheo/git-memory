"""
git-memory — Automatic AI Session Memory Storage

A lightweight tool that automatically saves AI assistant conversations
to a Git repository with category-based organization.

Example:
    from git_memory.auto_commit import main
    main()
"""

__version__ = "0.1.0"
__author__ = "Iskra Contributors"

from .auto_commit import main

__all__ = ["main"]
