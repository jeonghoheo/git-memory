# Changelog

Git Memory 변경 이력.
모든 중요한 변경사항은 이 파일에 기록됩니다.

---

## [Unreleased]

### Added
- gstack/document-release 스킬 기반 문서화 시스템
- OPERATIONS.md 운영 가이드 추가
- CONTRIBUTING.md 기여 가이드 추가

### Changed
- `analyze_session()` 호출 제거 (NameError 버그 패치)
- launchd plist: `LimitLoadToSessionType` 제거, PYTHONPATH 명시적 설정
- Hermes 저장소 Git으로 초기화

### Fixed
- `is_processed` NameError (analyze_session 미구현 버그)
- launchd에서 Python 모듈 import 실패 (PYTHONPATH 설정)
- cron job 실행 안 됨 (macOS launchd로 마이그레이션)

---

## [0.1.0] — 2026-04-30

### Added
- 최초 공개 릴리스
- 자동 커밋 시스템 (`git_memory_auto_commit.py`)
- launchd 통합 (5분 주기 실행)
- 카테고리 분류: `personal/`, `learning/`, `projects/`
- Git 기반 저장 및 검색 (`git grep`)
- `~/.hermes/last_git_memory_processed` 중복 방지 marker
- `~/.config/git-memory/config.yaml` 설정 파일

### Documentation
- README.md
- ARCHITECTURE.md
- OPERATIONS.md
- CONTRIBUTING.md
- CHANGELOG.md
- TODO.md

---

## [0.0.1] — Pre-release

### Added
- 초기 프로토타입 (P1~P3 테스트)
- cron 기반 자동 커밋 (레거시)
- 기본 카테고리 테스트

### Known Issues
- cron이 macOS에서 비활성화됨 → launchd로 대체
- `analyze_session()` 함수 미구현으로 NameError
- 세션 필터링 조건 엄격 (30초/2메시지)

---

## 📌 버전 관리 방식

**SemVer** (Semantic Versioning) 사용:

```
MAJOR . MINOR . PATCH
  ↑       ↑      ↑
  │       │      └─ 버그 수정, 후방 호환
  │       └─ 기능 추가, 후방 호환
  └─ 호환성 변경 (주요 릴리스)
```

**예시:**
- `0.1.0` — 초기 안정 릴리스
- `1.0.0` — 프로덕션 준비 완료
- `1.2.3` — 기능 2.X, 버그 수정 3

---

## 🔄 업그레이드 경로

### 0.1.0 → 1.0.0 (예정)

**주요 목표:**
- [ ] remote sync (GitHub/GitLab 자동 push)
- [ ] 실시간 감시 (fswatch/inotify)
- [ ] ML 카테고리 분류
- [ ] 충돌 자동 해결
- [ ] 태그 시스템 (#해시태그)
- [ ] 중요도 점수 부여

### 0.1.0 → 0.2.0 (다음 마이너)

**우선순위:**
1. `uncategorized/` 카테고리 분류 정확도 향상
2. 키워드 기반 분류 정확도 개선
3. 테스트 커버리지 80%+

---

*Last generated: 2026-04-30*  \n*Maintainers: Git Memory Contributors*
