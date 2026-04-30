# Git Memory

> Automatic AI Session Memory Storage — Git 기반 AI 대화 자동 저장

Git Memory는 AI 어시스턴트와의 대화를 자동으로 Git 저장소에 저장하고,
카테고리별로 분류하여 검색 가능하게 하는 경량 도구입니다.

## Features

- **자동 커밋**: 세션 종료 후 중요 인사이트 자동 저장
- **카테고리 분류**: `personal/`, `learning/`, `projects/` 등 주제별 디렉토리 생성
- **검색 가능**: `git grep`으로 전체 히스토리 검색
- **Git 기반**: 전체 내역 추적, 브랜치, merge, 충돌 해결 가능
- **무료**: 별도 서비스 비용 없음, 로컬 저장

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/git-memory.git
cd git-memory

# Install
pip install -e .
```

### Configuration

기본 설정 파일: `~/.config/git-memory/config.yaml`

```yaml
hermes_sessions: ~/hermes/sessions  # 세션 파일 경로
git_memory_repo: ~/git-memory        # 저장소 경로
log_file: ~/logs/git_memory.log      # 로그 파일

keywords:
  personal: ["meeting", "planning", "decision", "todo"]
  learning: ["study", "learn", "concept", "example"]
  projects: ["project", "task", "milestone"]

logging:
  level: INFO
  max_bytes: 10485760
  backup_count: 5

git:
  auto_add: true
  commit_prefix: "Auto-save:"
```

### Usage

```bash
# 수동 실행 (테스트)
git-memory

# 자동 실행 (launchd/cron으로 설정)
# 5분 간격 실행 권장
```

저장소는 자동으로 `personal/`, `learning/`, `projects/` 디렉토리를 생성하고
세션에서 추출한 인사이트를 Markdown 파일로 저장합니다.

## How It Works

1. **세션 감지**: `~/hermes/sessions/` 디렉토리의 최신 세션 파일 모니터링
2. **필터링**: 최소 2개 메시지, 30초 이상 대화만 처리
3. **인사이트 추출**: 키워드 매칭으로 중요 메시지 선별
4. **카테고리화**: 키워드 기반으로 `personal/`, `learning/`, `projects/` 중 하나 결정
5. **Git 저장**: `YYYY-MM-DD_<subcategory>.md` 파일명으로 커밋

## Documentation

자세한 문서는 `docs/` 디렉토리를 참고하세요:

- [README](docs/README.md) — 개요 및 설치 가이드
- [ARCHITECTURE](docs/ARCHITECTURE.md) — 시스템 아키텍처
- [OPERATIONS](docs/OPERATIONS.md) — 운영 및 모니터링
- [CONTRIBUTING](docs/CONTRIBUTING.md) — 기여 가이드
- [CHANGELOG](docs/CHANGELOG.md) — 변경 이력
- [TODO](docs/TODO.md) — 향후 계획

## Requirements

- Python 3.11+
- Git 2.30+
- macOS / Linux / Windows

## License

MIT License — 자유롭게 사용/수정/배포 가능.

## Contributing

기여는 언제나 환영합니다! [CONTRIBUTING.md](docs/CONTRIBUTING.md)를 참고하세요.

---

Made with 🧡 by the Iskra community
