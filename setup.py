"""
Git Memory — 자동 AI 세션 메모리 저장소

Hermes Agent와 연동하여 AI 대화를 자동으로 Git 저장소에 저장합니다.
카테고리별 분류, git grep 검색, 전체 이력 추적을 제공합니다.
"""

from setuptools import setup, find_packages

setup(
    name="git-memory",
    version="0.1.0",
    author="Iskra Contributors",
    author_email="support@git-memory.dev",
    description="Automatic session memory storage with Git integration",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/git-memory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.11",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "git-memory=git_memory.auto_commit:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.md"],
    },
)
