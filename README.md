# Git Memory

> Automatic AI Session Memory Storage — Git 기반 AI 대화 자동 저장

[![pip install](https://img.shields.io/badge/pip%20install-git--memory-blue)](https://pypi.org/project/git-memory/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://pypi.org/project/git-memory/)
[![CI](https://img.shields.io/github/actions/workflow/status/jeonghoheo/git-memory/ci.yml?branch=main)](https://github.com/jeonghoheo/git-memory/actions)
[![Coverage](https://img.shields.io/badge/coverage-unknown-yellow)](https://github.com/jeonghoheo/git-memory/actions)
[![Quality](https://img.shields.io/badge/quality-mypy%2B%20black%2B%20ruff-blue)](https://github.com/jeonghoheo/git-memory/actions)

Git Memory는 AI 어시스턴트와의 대화를 자동으로 Git 저장소에 저장하고,
카테고리별로 분류하여 검색 가능하게 하는 경량 도구입니다.

## Features

### Continuous Integration

- **GitHub Actions**: Every push runs automated tests (pytest) and linting (ruff, black)
- **Free**: Unlimited minutes for public repositories
- **Badge**: See build status on the repository page
- **Coverage**: (optional) Code coverage reports can be added

See `.github/workflows/ci.yml` for the full configuration.

- **자동 커밋**: 세션 종료 후 중요 인사이트 자동 저장
- **카테고리 분류**: `personal/`, `learning/`, `projects/`, `wedding/` 주제별 디렉토리 생성
- **검색 가능**: `git grep`으로 전체 히스토리 검색
- **Git 기반**: 전체 내역 추적, 브랜치, merge, 충돌 해결 가능
- **무료**: 별도 서비스 비용 없음, 로컬 저장

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/git-memory.git
cd git-memory

# Install (Editable mode for development)
pip install -e .

# Verify installation
git-memory --help
```

**Requirements**: Python 3.11+, Git

### Configuration

기본 설정 파일: `~/.config/git-memory/config.yaml`

```yaml
hermes_sessions: ~/hermes/sessions      # 세션 파일 경로
git_memory_repo: ~/git-memory            # 저장소 경로
log_file: ~/logs/git_memory.log          # 로그 파일

keywords:
  personal:
    - "meeting"
    - "회의"
    - "아이디어"
    - "결정"
    - "planning"
    - "계획"
    # ... 200+ 키워드 확장 가능
  learning:
    - "study"
    - "학습"
    - "공부"
    - "russian"
    - "러시아어"
    # ...
  projects:
    - "project"
    - "프로젝트"
    - "task"
    - "태스크"
    # ...
  wedding:
    - "wedding"
    - "결혼"
    - "ceremony"
    - "식"
    # ...

category_rules:
  - keywords: ["러시아어", "russian", "grammar", "문법"]
    category: learning
    subcategory: russian
  - keywords: ["결혼", "wedding", "ceremony", "예식"]
    category: wedding
    subcategory: ceremony

logging:
  level: INFO
  max_bytes: 10485760
  backup_count: 5

git:
  auto_add: true
  commit_prefix: "Auto-save:"
```

> ⚠️ **환경변수 오버라이드**: `git-memory_CONFIG` 환경변수로 설정 파일 경로를 변경할 수 있으나,
> 하이픈(`-`) 포함 환경변수는 bash에서 `export`가 불가능하므로 Python 코드 내에서 설정해야 합니다.

### Usage

```bash
# 기본 실행 (가장 최신 세션 처리)
git-memory

# 상세 로그 출력
git-memory --verbose

# 이미 커밋된 세션 강제 재처리
git-memory --force

# 실제 Git 커밋 없이 시뮬레이션 (테스트용)
git-memory --dry-run
```

**CLI Options**

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--dry-run` | 실제 Git 커밋 없이 시뮬레이션 | `False` |
| `--verbose` | 상세 로그 출력 (DEBUG 레벨) | `False` |
| `--force` | 이미 커밋된 세션 강제 재처리 | `False` |
| `--help` | 도움말 출력 | - |

저장소는 자동으로 `personal/`, `learning/`, `projects/`, `wedding/` 디렉토리를 생성하고
세션에서 추출한 인사이트를 Markdown 파일로 저장합니다.

## How It Works

1. **세션 감지**: `~/hermes/sessions/` 디렉토리의 최신 세션 파일 모니터링
2. **필터링**: 최소 2개 메시지, 30초 이상 대화만 처리
3. **인사이트 추출**: 키워드 매칭(`IMPORTANT_KEYWORDS`)으로 중요 메시지 선별
4. **카테고리 분류**: `category_rules` 순서대로 word boundary 매칭 → 첫 번째 매칭된 카테고리 사용
5. **Git 저장**: `YYYY-MM-DD_<subcategory>.md` 파일명으로 커밋 (`Auto-save: session <id>`)

## CLI Options

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--dry-run` | 실제 Git 커밋 없이 시뮬레이션만 실행 | `False` |
| `--verbose` | 상세 로그 출력 (DEBUG 레벨) | `False` |
| `--force` | 이미 커밋된 세션도 강제 재처리 | `False` |
| `--help` | 도움말 출력 | - |

## Documentation

자세한 문서는 `docs/` 디렉토리를 참고하세요:

- [README](docs/README.md) — 개요 및 설치 가이드
- [USAGE](USAGE.md) — 시나리오별 사용법 및 CLI 옵션
- [ARCHITECTURE](docs/ARCHITECTURE.md) — 시스템 아키텍처
- [OPERATIONS](docs/OPERATIONS.md) — 운영 및 모니터링
- [CONTRIBUTING](docs/CONTRIBUTING.md) — 기여 가이드
- [CHANGELOG](docs/CHANGELOG.md) — 변경 이력
- [TODO](docs/TODO.md) — 향후 계획
- [HELP](HELP.md) — 명령어, 설정, FAQ

## Requirements

- Python 3.11+
- Git 2.30+
- macOS / Linux / Windows

## Project Structure

```
git-memory/
├── git_memory/
│   ├── __init__.py
│   ├── auto_commit.py      # 메인 로직 (세션 감지, 추출, 저장)
│   └── config.py           # 설정 로드
├── docs/                   # 상세 문서
├── tests/                  # 테스트 (향후)
├── USAGE.md               # 사용 시나리오 가이드
├── README.md              # 이 파일
├── HELP.md                # 명령어 도움말
├── setup.py               # 패키지 설정
├── config.yaml            # 기본 설정 샘플
└── requirements.txt       # 의존성
```

## License

MIT License — 자유롭게 사용/수정/배포 가능.

## Contributing

기여는 언제나 환영합니다! [CONTRIBUTING.md](docs/CONTRIBUTING.md)를 참고하세요.

---

Made with 🧡 by the Iskra community