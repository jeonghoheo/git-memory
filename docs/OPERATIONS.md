# Operations Guide

**Git Memory 시스템의 운영, 모니터링, 트러블슈팅 가이드.**

---

## 🚨 모니터링

### **로그 파일 위치**

| 로그 | 경로 | 설명 |
|------|------|------|
| **자동 커밋 로그** | `~/logs/git_memory.log` | 주요 실행 로그 |
| **launchd stdout** | `~/logs/git_memory_launchd.log` | launchd 표준 출력 |
| **launchd stderr** | `~/logs/git_memory_launchd.err` | launchd 에러 |
| **cron 로그** | `~/logs/git_memory_cron.log` | (레거시) cron 실행 로그 |
| **Git 저장소 로그** | `~/git-memory/.git/logs/` | Git 내부 로그 |

### **실시간 모니터링**

```bash
# tail -f로 실시간 로그 확인
tail -f ~/logs/git_memory.log

# 최근 50줄만
tail -n 50 ~/logs/git_memory.log

# 에러만 필터링
tail -f ~/logs/git_memory.log | grep -i error

# launchd 상태 확인
launchctl list | grep git-memory
```

### **로그 레벨**

```
[INFO] === Git Memory Auto-Commit Started ===
[INFO] 💡 Extracted 3 insights from 10 messages
[INFO] ✅ Committed 1 files: 2024-01-15_meeting.md
[INFO] Skipped: too_short          ← 조건 불만족
[ERROR] Failed to write to git memory
```

---

## 🔧 일반 운영 작업

### **1. launchd 서비스 관리 (macOS)**

```bash
# 상태 확인
launchctl list | grep git-memory-auto-commit

# 즉시 실행 (수동 트리거)
launchctl start git-memory-auto-commit

# 중지
launchctl stop git-memory-auto-commit

# 언로드 (비활성화)
launchctl unload ~/Library/LaunchAgents/git-memory-auto-commit.plist

# 재로드 (설정 변경 후)
launchctl unload ~/Library/LaunchAgents/git-memory-auto-commit.plist
launchctl load ~/Library/LaunchAgents/git-memory-auto-commit.plist

# plist 위치
~/Library/LaunchAgents/git-memory-auto-commit.plist
```

### **2. cron 관리 (레거시)**

```bash
# crontab 확인
crontab -l

# crontab 편집
crontab -e

# cron 재시작 (시스템 서비스)
sudo launchctl unload /System/Library/LaunchDaemons/com.vix.cron.plist
sudo launchctl load -w /System/Library/LaunchDaemons/com.vix.cron.plist
```

> **Note**: macOS는 `launchd`를 기본으로 사용합니다. cron은 비활성화되어 있을 수 있음.

### **3. Git 저장소 상태 확인**

```bash
# 저장소 상태
cd ~/git-memory && git status

# 최근 커밋
git log --oneline -10

# 세션별 커밋 확인
git log --oneline --grep="session" -20

# 카테고리별 파일 목록
ls -la personal/ learning/ projects/
```

### **4. 처리된 세션 확인**

```bash
# Processed marker 파일
cat ~/.hermes/last_git_memory_processed
# 출력 예: session_test_gitmemory_20260430_100337.json

# marker 삭제 (다시 처리하려면)
rm ~/.hermes/last_git_memory_processed
```

---

## 🚨 문제 해결 (Troubleshooting)

### **문제 1: 자동 커밋이 안 됨**

**증상:** 시간이 지나도 `git_memory.log`에 새 로그 없음, 커밋 없음

**진단:**

```bash
# 1. launchd 실행 확인
launchctl list | grep git-memory
# PID가 있으면 실행 중

# 2. 최근 로그 확인
tail -n 20 ~/logs/git_memory.log
# "Skipped: too_short" 나오면 조건 미달
```

**해결:**

| 원인 | 해결책 |
|------|--------|
| **launchd 비활성** | `launchctl load ~/Library/LaunchAgents/git-memory-auto-commit.plist` |
| **PYTHONPATH 없음** | plist 파일의 `EnvironmentVariables` 확인 (기본값: `~/hermes`) |
| **세션 조건 미달** | 30초 이상, 2메시지 이상 대화 필요 |
| **이미 처리됨** | `~/.hermes/last_git_memory_processed` 삭제 |
| **스크립트 에러** | 직접 실행해보기: `python3 ~/hermes/scripts/git_memory_auto_commit.py` |

---

### **문제 2: NameError: name 'is_processed' is not defined**

**원인:** 스크립트가 예전 버전으로 캐시됨 (git tracking 안 되던 시절 파일)

**해결:**

```bash
# 1. hermes 디렉토리를 git repo로 초기화
cd ~/hermes
git init
git add scripts/git_memory_auto_commit.py
git commit -m "init hermes scripts"

# 2. launchd 재로드
launchctl unload ~/Library/LaunchAgents/git-memory-auto-commit.plist
launchctl load ~/Library/LaunchAgents/git-memory-auto-commit.plist
```

---

### **문제 3: 카테고리가 잘못 분류됨**

**증상:** personal 관련 대화가 `uncategorized/`에 저장됨 (또는 잘못된 카테고리)

**해결:**

```bash
# 1. config.yaml 키워드 확인/추가
cat ~/.config/git-memory/config.yaml | grep -A5 "keywords:"

# 예시:
# keywords:
#   personal: ["meeting", "planning", "decision", "todo"]
#   learning: ["study", "learn", "concept", "example"]
#   projects: ["project", "task", "milestone", "deadline"]

# 2. 키워드 추가 후 저장
# (자동으로 다음 실행부터 적용)
```

**수동 이동:**

```bash
# 파일을 올바른 카테고리로 이동
mv ~/git-memory/uncategorized/YYYY-MM-DD_file.md ~/git-memory/personal/
git -C ~/git-memory add -A
git -C ~/git-memory commit -m "move to personal category"
```

---

### **문제 4: Git 충돌 발생**

**증상:** 커밋 실패, `git status`에 충돌 표시

**해결:**

```bash
# 1. 충돌 상태 확인
git -C ~/git-memory status

# 2. 충돌 파일 수동 병합
# (에디터로 <<<<<<< markers 해결)

# 3. staging 후 커밋
git -C ~/git-memory add .
git -C ~/git-memory commit -m "manual merge"

# 4. 이후 자동 커밋 재개
launchctl start git-memory-auto-commit
```

---

### **문제 5: launchd 로그 파일 크기 0 bytes**

**원인:** PYTHONPATH, LimitLoadToSessionType 설정 문제

**해결:**

```bash
# 1. plist 파일 확인
cat ~/Library/LaunchAgents/git-memory-auto-commit.plist

# 필수 항목:
# - EnvironmentVariables > PYTHONPATH: ~/hermes (또는 Hermes 설치 경로)
# - ProgramArguments에 python3 절대경로
# - LimitLoadToSessionType 없어야 함

# 2. job 재로드
launchctl unload ~/Library/LaunchAgents/git-memory-auto-commit.plist
launchctl load ~/Library/LaunchAgents/git-memory-auto-commit.plist

# 3. 즉시 실행 테스트
launchctl start git-memory-auto-commit
tail -f ~/logs/git_memory.log
```

---

### **문제 6: 세션 파일이 감지되지 않음**

**진단:**

```bash
# 1. 세션 디렉토리 파일 확인
ls -la ~/hermes/sessions/ | head -20

# 2. 가장 최근 세션 확인
latest=$(ls -t ~/hermes/sessions/*.json 2>/dev/null | head -1)
echo "Latest: $latest"

# 3. 세션 내용 검증 (JSON 유효성)
python3 -c "import json; json.load(open('$latest'))" && echo "VALID" || echo "INVALID"

# 4. 메시지 수/시간 확인
python3 -c "
import json, sys
from datetime import datetime
data = json.load(open('$latest'))
msgs = len(data['messages'])
if msgs >= 2:
    start = datetime.fromisoformat(data['messages'][0]['timestamp'])
    end = datetime.fromisoformat(data['messages'][-1]['timestamp'])
    dur = (end-start).total_seconds()
    print(f'Messages: {msgs}, Duration: {dur:.1f}s')
else:
    print(f'Too few messages: {msgs}')
"
```

---

## 📊 성능/용량 관리

### **저장소 크기 확인**

```bash
# 전체 저장소 크기
du -sh ~/git-memory

# 카테고리별 크기
du -sh ~/git-memory/personal/
du -sh ~/git-memory/learning/
du -sh ~/git-memory/projects/

# .git 객체 정리 (오래된 객체 prune)
git -C ~/git-memory gc --prune=now
```

### **로그 로테이션**

`~/.config/git-memory/config.yaml`:

```yaml
logging:
  max_bytes: 10485760   # 10MB
  backup_count: 5       # 최대 5개 백업
```

로그 파일 자동 순환 (RotatingFileHandler).

---

## 🔄 유지보수

### **주기적 작업**

| 주기 | 작업 | 명령어 |
|------|------|--------|
| 매일 | 로그 로테이션 확인 | `ls -lh ~/logs/*.log` |
| 매주 | 저장소 백업 | `git -C ~/git-memory bundle create backup.bundle --all` |
| 매월 | 오래된 세션 정리 | `find ~/hermes/sessions -mtime +90 -delete` |
| 분기 | Git GC 실행 | `git -C ~/git-memory gc` |

---

## 🆘 긴급 복구

### **자동 커밋 완전 중지**

```bash
# 1. launchd 언로드
launchctl unload ~/Library/LaunchAgents/git-memory-auto-commit.plist

# 2. crontab 제거 (있으면)
crontab -e  # git_memory_auto_commit 줄 삭제

# 3. 프로세스 kill
pkill -f git_memory_auto_commit
```

### **저장소 초기화 (전체 삭제)**

```bash
# WARNING: 모든 기록 삭제됨!
rm -rf ~/git-memory
mkdir -p ~/git-memory
cd ~/git-memory
git init
git config user.email "hermes@localhost"
git config user.name "Iskra Agent"
```

---

## 📞 지원

문제 발생 시:
1. 이 문서의 Troubleshooting 섹션 참고
2. `~/logs/git_memory.log` 로그 확인
3. `launchctl list` 상태 확인
4. GitHub Issues에 버그 리포트

---

*Operations version: 1.0 — April 2026*

---

## 🔄 CI/CD (GitHub Actions)

### workflow 실행 확인

```bash
# GitHub Actions 대시보드
open https://github.com/jeonghoheo/git-memory/actions

# CLI로 최근 실행 확인
gh run list --workflow=ci.yml
```

### workflow 수동 트리거

```bash
# workflow_dispatch가 설정된 경우
gh workflow run ci.yml

# 또는 커밋으로 트리거
git commit --allow-empty -m "Trigger CI"
git push origin main
```

### 테스트 실패 시 로컬 검증

```bash
# 1. 동일 명령어 로컬 실행
pytest -v

# 2. lint 문제 수정
pip install black ruff
black git_memory/
ruff check git_memory/ --fix

# 3. 다시 커밋
git add .
git commit -m "Fix CI errors"
git push origin main
```

### workflow 파일 편집

`.github/workflows/ci.yml`을 수정한 후:
```bash
git add .github/workflows/ci.yml
git commit -m "Update CI: add coverage"
git push origin main
```

변경사항은 다음 push부터 적용됩니다.

### GitHub CLI 설치 (선택)

```bash
# macOS
brew install gh

# 인증
gh auth login
```

---

## 📊 메트릭스

| 지표 | 명령어 | 설명 |
|------|--------|------|
| 저장소 크기 | `du -sh ~/git-memory` | 디스크 사용량 |
| 커밋 수 | `git rev-list --count HEAD` | 전체 커밋 수 |
| 최근 활동 | `git log --since="1 day" --oneline` | 오늘 커밋 |

---

*Last updated: 2026-04-30 | 버전: 0.1.1*
