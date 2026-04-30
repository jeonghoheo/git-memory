# Git Memory 사용 가이드

실제 사용 시나리오와 예제를 통해 Git Memory를 어떻게 활용하는지 보여드립니다.

---

## 📦 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/git-memory.git
cd git-memory

# 개발 모드 설치 (Editable)
pip install -e .

# 또는 PyPI에서 설치 (배포 후)
pip install git-memory
```


---

## 🔧 설정

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

---

## 🚀 사용법

### 기본 명령어

```bash
# 도움말
git-memory --help

# 수동 실행 (가장 최신 세션 처리)
git-memory

# 상세 로그 출력
git-memory --verbose

# 이미 커밋된 세션 강제 재처리
git-memory --force

# 실제 Git 커밋 없이 시뮬레이션 (테스트용)
git-memory --dry-run
```

---

## ⚙️ 옵션 상세 설명

### `--dry-run`
실제 Git 커밋을 생성하지 않고, 어떤 파일이 생성될지, 어떤 메시지가 출력될지 미리 확인합니다.

```bash
$ git-memory --dry-run --verbose
[DRY-RUN] Would write to: personal/2026-04-30_memo.md
[DRY-RUN] Would commit: "Auto-save: session test_123"
[DRY-RUN] DRY RUN — no changes made
```

**사용 사례**:
- 설정이 올바른지 확인할 때
- 처음 사용 시 결과 미리보기
- CI/CD 파이프라인에서 테스트

### `--verbose`
각 단계(세션 감지, 필터링, 인사이트 추출, 카테고리 분류, Git 작업)의 상세 로그를 출력합니다.

```bash
$ git-memory --verbose
[INFO] Scanning ~/hermes/sessions/ for session files...
[INFO] Latest session: session_20260430_112058.json
[INFO] Session has 42 messages, duration 125s
[INFO] Extracted 3 insights from session
[INFO] Category: personal/memo (matched keywords: meeting, planning)
[INFO] Writing to: personal/2026-04-30_memo.md
[INFO] Committed: Auto-save: session 20260430_112058
```

### `--force`
`already_committed()` 체크를 우회하여 이미 Git에 커밋된 세션도 강제 재처리합니다.

```bash
# 이미 커밋된 세션을 다시 처리
git-memory --force
```

**주의**: 동일 세션을 중복 저장할 수 있으므로, `--dry-run`으로 먼저 테스트하세요.

---

## 📁 저장 구조

```
git-memory/
├── personal/              # 개인 메모 (회의, 아이디어, 결정)
│   ├── 2026-04-04_memo.md
│   └── 2026-04-30_meeting.md
├── learning/              # 언어 학습, 기술 학습
│   ├── 2026-04-10_russian.md
│   └── 2026-04-15_grammar.md
├── projects/              # 프로젝트 작업
│   ├── 2026-04-20_design.md
│   └── 2026-04-25_review.md
├── wedding/               # 웨딩 플래닝
│   └── 2026-04-30_plans.md
├── daily/                 # 날짜별 묶음 (선택적)
└── index.md               # 메타데이터 및 검색 인덱스 (향후)
```

파일명 형식: `YYYY-MM-DD_<subcategory>.md`

---

## 🔍 작동 원리

1. **세션 감지**: `~/hermes/sessions/` 디렉토리의 최신 세션 파일 찾기
2. **필터링**: 최소 요구사항 확인
   - 메시지 2개 이상
   - 대화 시간 30초 이상 (duration 필드)
   - 아직 Git에 커밋되지 않은 세션 (`already_committed()` 체크)
3. **인사이트 추출**: `keywords` 목록 기반으로 중요 메시지 선별
4. **카테고리 분류**: `category_rules` 순서대로 word boundary 매칭 → 첫 번째 매칭된 카테고리 사용
5. **Git 저장**: Markdown 파일 생성 및 커밋 (`Auto-save: session <id>`)

---

## 🛠️ 고급 활용

### launchd/cron 자동 실행

```bash
# 5분 간격 실행 (cron)
*/5 * * * * cd ~/hermes_git_memory && git-memory --verbose >> ~/logs/git_memory.log 2>&1

# launchd (macOS)
# ~/Library/LaunchAgents/git-memory-auto-commit.plist 생성
```

### 검색 예제

```bash
# 특정 키워드가 포함된 모든 파일 찾기
git grep -i "aspect" learning/

# 오늘 학습 내용만
git log --since="today" --oneline -- learning/

# 카테고리별 커밋 통계
git log --oneline -- personal/ | wc -l
git log --since="1 week" --oneline

# 특정 날짜 범위
git log --since="2026-04-01" --until="2026-04-30" --oneline
```

### 이미 커밋된 세션 확인

```bash
# 어떤 세션이 이미 처리되었는지 확인
git log --grep="Auto-save:" --oneline | head -20

# 특정 세션 ID로 검색
git log --grep="session_20260430" --oneline
```

**필요 조건**: Python 3.11+, Git

---

## 🔧 설정

기본 설정 파일: `~/.config/git-memory/config.yaml`

```yaml
hermes_sessions: ~/hermes/sessions      # Hermes 세션 파일 경로
git_memory_repo: ~/git-memory            # Git 저장소 경로
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

logging:
  level: INFO
  max_bytes: 10485760
  backup_count: 5

git:
  auto_add: true
  commit_prefix: "Auto-save:"
```

> ⚠️ **config.yaml 경로 확인**: 기본값은 `~/.config/git-memory/config.yaml`입니다.
> 환경변수 `git-memory_CONFIG`로 오버라이드 가능하나, 하이픈 포함 환경변수는
> shell에서 export가 불가능하므로 Python 코드에서 직접 설정해야 합니다.

---

## 🚀 사용법

### 기본 명령어

```bash
# 도움말
git-memory --help

# 수동 실행 (가장 최신 세션 처리)
git-memory

# 상세 로그 출력
git-memory --verbose

# 이미 커밋된 세션 강제 재처리
git-memory --force

# 실제 Git 커밋 없이 시뮬레이션 (테스트용)
git-memory --dry-run
```

---

## ⚙️ 옵션 상세 설명

### `--dry-run`
실제 Git 커밋을 생성하지 않고, 어떤 파일이 생성될지, 어떤 메시지가 출력될지 미리 확인합니다.

```bash
$ git-memory --dry-run --verbose
[DRY-RUN] Would write to: personal/2026-04-30_memo.md
[DRY-RUN] Would commit: "Auto-save: session test_123"
[DRY-RUN] DRY RUN — no changes made
```

**사용 사례**:
- 설정이 올바른지 확인할 때
- 처음 사용 시 결과 미리보기
- CI/CD 파이프라인에서 테스트

### `--verbose`
각 단계(세션 감지, 필터링, 인사이트 추출, 카테고리 분류, Git 작업)의 상세 로그를 출력합니다.

```bash
$ git-memory --verbose
[INFO] Scanning ~/hermes/sessions/ for session files...
[INFO] Latest session: session_20260430_112058.json
[INFO] Session has 42 messages, duration 125s
[INFO] Extracted 3 insights from session
[INFO] Category: personal/memo (matched keywords: meeting, planning)
[INFO] Writing to: personal/2026-04-30_memo.md
[INFO] Committed: Auto-save: session 20260430_112058
```

### `--force`
`already_committed()` 체크를 우회하여 이미 Git에 커밋된 세션도 강제로 재처리합니다.

```bash
# 이미 커밋된 세션을 다시 처리
git-memory --force
```

**주의**: 동일 세션을 중복 저장할 수 있으므로, `--dry-run`으로 먼저 테스트하세요.

---

## 📁 저장 구조

```
git-memory/
├── personal/              # 개인 메모 (회의, 아이디어, 결정)
│   ├── 2026-04-04_memo.md
│   └── 2026-04-30_meeting.md
├── learning/              # 언어 학습, 기술 학습
│   ├── 2026-04-10_russian.md
│   └── 2026-04-15_grammar.md
├── projects/              # 프로젝트 작업
│   ├── 2026-04-20_design.md
│   └── 2026-04-25_review.md
├── wedding/               # 웨딩 플래닝
│   └── 2026-04-30_plans.md
├── daily/                 # 날짜별 묶음 (선택적)
└── index.md               # 메타데이터 및 검색 인덱스 (향후)
```

파일명 형식: `YYYY-MM-DD_<subcategory>.md`

---

## 🔍 작동 원리

1. **세션 감지**: `~/hermes/sessions/` 디렉토리의 최신 세션 파일 찾기
2. **필터링**: 최소 요구사항 확인
   - 메시지 2개 이상
   - 대화 시간 30초 이상 (duration 필드)
   - 아직 Git에 커밋되지 않은 세션 (`already_committed()` 체크)
3. **인사이트 추출**: `keywords` 목록 기반으로 중요 메시지 선별
4. **카테고리 분류**: `category_rules` 순서대로 매칭 → 첫 번째 매칭된 카테고리 사용
5. **Git 저장**: Markdown 파일 생성 및 커밋 (`Auto-save: session <id>`)

---

## 🛠️ 고급 활용

### launchd/cron 자동 실행

```bash
# 5분 간격 실행 (cron)
*/5 * * * * cd ~/hermes_git_memory && git-memory --verbose >> ~/logs/git_memory.log 2>&1

# launchd (macOS)
# ~/Library/LaunchAgents/git-memory-auto-commit.plist 생성
```

### 검색 예제

```bash
# 특정 키워드가 포함된 모든 파일 찾기
git grep -i "aspect" learning/

# 오늘 학습 내용만
git log --since="today" --oneline -- learning/

# 카테고리별 커밋 통계
git log --oneline -- personal/ | wc -l
git log --since="1 week" --oneline

# 특정 날짜 범위
git log --since="2026-04-01" --until="2026-04-30" --oneline
```

### 이미 커밋된 세션 확인

```bash
# 어떤 세션이 이미 처리되었는지 확인
git log --grep="Auto-save:" --oneline | head -20

# 특정 세션 ID로 검색
git log --grep="session_20260430" --oneline
```

---

## ❓ FAQ

**Q: `git-memory` 명령어를 찾을 수 없다고 나옵니다.**
→ `pip install -e .`이 성공했는지 확인하세요. `which git-memory`로 경로 확인.

**Q: 설정 파일을 어디에 둬야 하나요?**
→ 기본값: `~/.config/git-memory/config.yaml`. 환경변수로 오버라이드 가능.

**Q: 카테고리가 `uncategorized`로만 나옵니다.**
→ `config.yaml`의 `keywords`가 올바른지, YAML syntax에 오류가 없는지 확인하세요.
BUG-003 수정으로 word boundary 매칭이 적용되었습니다.

**Q: `--dry-run` 실행 시 출력이 안 보입니다.**
→ `--verbose`와 함께 사용하세요: `git-memory --dry-run --verbose`.
로그 핸들러 구성이 올바른지 확인하세요.

**Q: 짧은 세션(7개 메시지)이 처리되지 않습니다.**
→ 기본 필터: 2개 메시지 이상, 30초 이상 대화.
`--force` 플래그로 우회 가능하나, 너무 짧은 세션은 정보 가치가 낮을 수 있습니다.

**Q: 이미 커밋된 세션을 다시 처리하면 어떻게 되나요?**
→ `--force` 없이는 건너뜁니다. `--force` 시 동일 파일이 덮어쓰기되고
새 커밋이 생성됩니다. 중복 위험이 있으므로 주의하세요.

---

## 📊 troubleshoting

| 증상 | 원인 | 해결 |
|------|------|------|
| 명령어 not found | pip安装 안됨 | `pip install -e .` |
| YAML syntax error | config 파일 형식 오류 | `yamllint`로 검증 |
| 세션 거절 | too_short (30초 미만) | `--force` 또는 duration 체크 완화 논의 |
| 카테고리 wrong | keyword 누락/순서 문제 | `config.yaml` keywords 확장 |
| Git 커밋 안됨 | GIT_MEMORY 경로 권한 문제 | `chmod -R u+w ~/git-memory` |

자세한 내용은 `docs/OPERATIONS.md`를 참고하세요.

---

*Happy Git-Memory! 🧡*