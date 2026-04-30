# Git Memory

**자동 세션 메모리 저장소** — AI 대화를 Git으로 자동 저장하고 카테고리별로 분류합니다.

---

## 📖 기능

| 기능          | 설명                                                     |
| ----------- | ------------------------------------------------------ |
| 기능          | 설명                                                     |
| **자동 커밋**   | 세션 종료 후 중요 인사이트를 `~/git-memory`에 자동 저장                 |
| **카테고리 분류** | `personal/`, `learning/`, `projects/` 등 주제별 디렉토리 자동 생성 |
| **검색 가능**   | `git grep`으로 전체 히스토리 검색                                |
| **Git 기반**  | 전체 내역 추적, 브랜치, merge, 충돌 해결 가능                         |
| **무료**      | 별도 서비스 비용 없음, 로컬 저장                                    |

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론 (이미 있음)
cd ~/git-memory

# 초기 설정 (자동 실행됨)
git config --local user.email "hermes@localhost"
git config --local user.name "Iskra Agent"
```

### 2. 실행

```bash
# 수동 실행 (테스트)
python3 ~/hermes/scripts/git_memory_auto_commit.py

# 자동 실행 (launchd)
launchctl start hermes.git-memory-auto-commit
```

자동 실행은 **5분 간격**으로 처리됩니다.

---

## 📂 저장소 구조

```
git-memory/
├── personal/              # 개인 메모 대화
│   └── 2024-01-15_meeting.md
├── learning/              # 학습 관련 대화 (언어, 기술 등)
│   └── ...
├── projects/              # 프로젝트 작업 대화
│   └── ...
├── .git/                 # Git 메타데이터
└── config.yaml           # 설정 파일 (선택사항)
```

파일명 형식: `YYYY-MM-DD_<description>.md` (자동 생성)

---

## 🔍 검색하기

```bash
# 모든 파일에서 키워드 검색
git grep -i "meeting"

# 특정 카테고리에서만
git grep -i "decision" -- personal/
```
# 최근 N일 동안
git log --since="7 days" --oneline
```

---

## ⚙️ 설정

`~/.config/git-memory/config.yaml` (선택):

```yaml
hermes_sessions: ~/hermes/sessions  # Iskra 세션 경로 (기본값)
git_memory_repo: ~/git-memory       # 저장소 경로
log_file: ~/logs/git_memory.log     # 로그 파일

keywords:
  personal: ["meeting", "planning", "decision", "todo"]
  learning: ["study", "learn", "concept", "example"]
  projects: ["project", "task", "milestone", "deadline"]

logging:
  level: INFO
  max_bytes: 10485760
  backup_count: 5

git:
  auto_add: true
  commit_prefix: "Auto-save:"
```

---

## 🛠️ 문제 해결

| 문제 | 해결책 |
|------|--------|
| **자동 커밋 안 됨** | `launchctl list \| grep hermes`로 실행 확인 |
| **파일이 안 생김** | `should_process_session` 조건 확인 (최소 2메시지, 30초) |
| **권한 오류** | `~/git-memory`에 쓰기 권한 확인 |
| **중복 커밋** | `~/.hermes/last_git_memory_processed` 파일 확인 |

---

## 📊 작동 원리

1. **세션 감시**: Iskra 세션 파일(`~/hermes/sessions/`) 모니터링
2. **필터링**: `should_process_session()` 조건 확인
   - 메시지 2개 이상
   - 대화 시간 30초 이상
   - 이미 처리된 세션 제외
3. **인사이트 추출**: `extract_insights()`로 중요 메시지 선별
4. **Git 저장**: `write_to_git_memory()`로 Markdown 파일 생성 및 커밋

---

## 🎯 사용 사례

- **언어 학습**: 학습 관련 표현 자동 수집
- **프로젝트 회의**: 결정사항 Git에 영구 보관
- **아이디어 개발**: 아이디어 히스토리 추적
- **기술 검색**: 과거 대화에서 코드/예제 즉시 검색

---

## 📄 라이선스

MIT License — 자유롭게 사용/수정/배포 가능.

---

## 🤝 기여

버그 리포트/기능 요청: [GitHub Issues]

---

*Made with 🧡 by Iskra*
