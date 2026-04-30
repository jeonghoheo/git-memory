# Git Memory 도움말

## 명령어 참조

### `git-memory`
AI 세션을 자동 저장하는 메인 명령어.

```bash
# 수동 실행 (한 번만)
git-memory

# 설정 파일 경로 확인
git-memory --config

# 버전 확인
git-memory --version

# 도움말
git-memory --help
```

**환경변수:**
```bash
# 설정 파일 경로 오버라이드
export HERMES_GIT_MEMORY_CONFIG=~/.config/git-memory/custom.yaml
git-memory
```

---

## 설정 파일 상세

위치: `~/.config/git-memory/config.yaml`

```yaml
# 세션 파일 경로 (Hermes 또는 다른 AI 어시스턴트)
hermes_sessions: ~/hermes/sessions

# Git 저장소 경로
git_memory_repo: ~/git-memory

# 로그 파일
log_file: ~/logs/git_memory.log

# 처리된 세션 기록 (중복 방지)
processed_marker: ~/.git-memory/last_processed.txt

# 카테고리별 키워드 (소문자 저장됨)
keywords:
  personal: ["meeting", "planning", "decision", "todo", "discuss"]
  learning: ["study", "learn", "concept", "example", "tutorial"]
  projects: ["project", "task", "milestone", "deadline", "deliverable"]

# 카테고리 결정 규칙 (순서대로 평가)
category_rules:
  - keywords: ["결혼", "wedding", "예식"]  # personal로 분류
    category: personal
    subcategory: wedding
  - keywords: ["러시아어", "russian", "grammar"]
    category: learning
    subcategory: language

# Git 설정
git:
  auto_add: true           # 자동 git add
  commit_prefix: "Auto-save:"  # 커밋 메시지 접두사

# 로깅 설정
logging:
  level: INFO              # DEBUG, INFO, WARNING, ERROR
  max_bytes: 10485760      # 10MB
  backup_count: 5          # 백업 파일 수
```

---

## 저장소 구조

```
~/git-memory/
├── personal/              # 개인 메모
│   ├── 2024-01-15_meeting.md
│   └── 2024-01-20_plans.md
├── learning/              # 학습 기록
│   ├── 2024-02-10_python.md
│   └── 2024-02-15_russian.md
├── projects/              # 프로젝트 작업
│   ├── 2024-03-01_design.md
│   └── 2024-03-15_review.md
└── .git/                 # Git 이력
```

**파일명 형식:** `YYYY-MM-DD_<subcategory>.md`

---

## 자동 실행 설정

### macOS (launchd)

```bash
# plist 파일 위치
~/Library/LaunchAgents/git-memory-auto-commit.plist

# 시작
launchctl start git-memory-auto-commit

# 중지
launchctl stop git-memory-auto-commit

# 상태 확인
launchctl list | grep git-memory

# 재로드 (설정 변경 후)
launchctl unload ~/Library/LaunchAgents/git-memory-auto-commit.plist
launchctl load ~/Library/LaunchAgents/git-memory-auto-commit.plist
```

**plist 예시:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>git-memory-auto-commit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/usr/local/bin/git-memory</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>  <!-- 5분 -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_GIT_MEMORY_CONFIG</key>
        <string>~/.config/git-memory/config.yaml</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Linux (cron)

```bash
# crontab -e
*/5 * * * * /usr/bin/git-memory
```

### Windows (Task Scheduler)

```
작업 스케줄러 → 기본 작업 생성 → 5분마다 실행
프로그램: python.exe
인수: -m git_memory.auto_commit
```
---
## CI/CD 자동 테스트 (GitHub Actions)

저장소에 GitHub Actions workflow가设置되어 있어, 코드 변경 시 자동으로 테스트가 실행됩니다.

### workflow 확인

```bash
# GitHub Actions 대시보드
https://github.com/jeonghoheo/git-memory/actions

# 로컬에서 수동 실행
pytest -v

# linting 수동 실행
pip install ruff black
ruff check git_memory/
black --check git_memory/
```

### workflow 파일 위치

`.github/workflows/ci.yml`

### workflow 구성

1. **test job**
   - Python 3.11 설정
   - `pip install -r requirements.txt`
   - `pytest -v` 실행

2. **lint job** (선택적)
   - `ruff check` 실행
   - `black --check` 실행

### CI 실패 시 해결

```bash
# 로컬에서 동일 명령어 실행하여 문제 확인
pytest -v

# lint 에러 수정
black git_memory/
ruff check --fix git_memory/

# 다시 커밋 & 푸시
git add .
git commit -m "Fix lint errors"
git push origin main
```

---

지원

---

## 문제 해결 (빠른 참조)

| 문제 | 명령어 | 해결 |
|------|--------|------|
| 자동 커밋 안 됨 | `launchctl list \| grep git-memory` | launchd 실행 확인 |
| 로그 확인 | `tail -f ~/logs/git_memory.log` | 실시간 로그 |
| 저장소 초기화 | `rm -rf ~/git-memory && git-memory` | 처음부터 |
| 설정 테스트 | `git-memory --config` | 설정 파일 경로 확인 |
| 수동 실행 | `git-memory` | 즉시 실행 |

---

## 자주 묻는 질문 (FAQ)

**Q: 카테고리가 안 생겨요**  
→ `keywords` 설정 확인, config.yaml 파일 위치 확인

**Q: 중복 커밋이 발생해요**  
→ `~/.git-memory/last_processed.txt` 삭제

**Q: Git 충돌 났어요**  
```bash
cd ~/git-memory
git status  # 충돌 파일 확인
# 에디터로 수정 후
git add .
git commit -m "manual conflict resolution"
```

**Q: 특정 세션만 저장하고 싶어요**  
→ 현재는 전체 세션 처리만 지원, 수동으로 `git-memory` 실행

**Q: 다른 AI 도구와 연동 가능할까요?**  
→ `hermes_sessions` 경로를 다른 도구의 세션 경로로 설정

---

## 지원

- **GitHub Issues**: https://github.com/jeonghoheo/git-memory/issues
- **문서**: `docs/` 디렉토리 참고
- **기여**: `CONTRIBUTING.md`

---

*버전: 0.1.0 | 라이선스: MIT | Maintainers: Iskra Community*