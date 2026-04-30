# Architecture

**Git Memory 시스템의 내부 구조와 데이터 흐름을 설명합니다.**

---

## 🏗️ 시스템 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    Hermes Agent                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ 세션 파일   │  │ 메시지      │  │ 인사이트 추출       │ │
│  │ *.json     │→ │ 필터링     │→ │ extract_insights()  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│           git_memory_auto_commit.py (자동 커밋)              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1. load_config()                                        │ │
│  │ 2. get_latest_session_file()                            │ │
│  │ 3. should_process_session() — 필터링                     │ │
│  │ 4. extract_insights() — 메시지 → 인사이트 변환          │ │
│  │ 5. categorize() — 카테고리 결정                         │ │
│  │ 6. write_to_git_memory() — Git 저장                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               ~/git-memory (Git 저장소)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ personal/    │  │ learning/    │  │ projects/         │ │
│  │ *.md         │  │ *.md         │  │ *.md              │ │
│  └──────────────┘  └──────────────┘  └───────────────────┘ │
│  └─────────────────────────────────────────────────────────┘ │
│                  Git history (전체 추적)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 데이터 흐름

### **Phase 1: 세션 감지**

```python
# 1. 최신 세션 파일 찾기
session_file = get_latest_session_file()  # ~/hermes/sessions/*.json

# 2. JSON 파싱
data = json.loads(session_file.read_text())
messages = data["messages"]  # List[Dict[role, content, timestamp]]
```

### **Phase 2: 필터링**

```python
# should_process_session() 조건
if len(messages) < 2:
    return False, "too_few_messages"  # 최소 2메시지

duration = (last_ts - first_ts).total_seconds()
if duration < 30:
    return False, "too_short"  # 최소 30초

if already_committed(session_id):
    return False, "already_processed"

if is_processed(session_file):
    return False, "already_marked"
```

### **Phase 3: 인사이트 추출**

```python
# extract_insights() — 중요 메시지만 선별
IMPORTANT_KEYWORDS = ["meeting", "decision", "study", "learn", "project", "remember", "note", "key", ...]

for msg in messages:
    role = msg["role"]  # "user" or "assistant"
    content = msg["content"]

    # 키워드 매칭 (단어 경계)
    if any(re.search(r'\b'+kw+r'\b', content.lower()) for kw in IMPORTANT_KEYWORDS):
        is_important = True

    # Assistant의 설명성 메시지
    if role == "assistant" and any(w in content for w in ["remember", "note", "key"]):
        is_important = True

    if is_important:
        insights.append({
            "role": role,
            "content": content,
            "reason": reason,
            "timestamp": msg["timestamp"]
        })
```

### **Phase 4: 카테고리화**

```python
# categorize() — 카테고리 결정
content_lower = ' '.join([insight['content'] for insight in insights]).lower()

if any(kw in content_lower for kw in PERSONAL_KEYWORDS):
    category = "personal"
elif any(kw in content_lower for kw in LEARNING_KEYWORDS):
    category = "learning"
elif any(kw in content_lower for kw in PROJECTS_KEYWORDS):
    category = "projects"
else:
    category = "uncategorized"  # 필요시 수동 분류
```

### **Phase 5: Git 저장**

```python
# 파일명: YYYY-MM-DD_<first-8 chars of first insight>.md
session_date = datetime.fromisoformat(messages[0]["timestamp"]).strftime("%Y-%m-%d")
first_insight = insights[0]["content"][:40].replace(" ", "-")
filename = f"{session_date}_{first_insight}.md"

# Markdown 형식
md_content = f"""# {category.title()} - {session_date}
**Source:** Hermes session `{session_id}`
**Date:** {session_date}

"""

for insight in insights:
    role_emoji = "👤" if insight["role"] == "user" else "🤖"
    md_content += f"\n### {role_emoji} {insight['role'].title()}\n> {insight['content']}\n"

# Git add & commit
(GIT_MEMORY / category / filename).write_text(md_content)
subprocess.run(["git", "add", str(GIT_MEMORY / category / filename)])
subprocess.run(["git", "commit", "-m", f"{PREFIX} session {session_id}"])
```

---

## 📁 파일 구조

```
git-memory/
├── .git/
│   ├── HEAD
│   ├── config
│   ├── objects/        # Git 객체 저장소
│   ├── refs/
│   │   └── heads/
│   │       └── main    # 기본 브랜치
│   └── logs/
│       └── HEAD        # 커밋 로그
│
├── personal/           # 카테고리 디렉토리 (자동 생성)
│   ├── 2024-01-15_meeting.md
│   └── ...
│
├── learning/           # 카테고리 디렉토리 (자동 생성)
│   └── ...
│
├── projects/           # 카테고리 디렉토리 (자동 생성)
│   └── ...
│
├── config.yaml         # 설정 파일 (선택)
└── README.md           # 이 파일
```

---

## 🔧 컴포넌트 상세

### **1. git_memory_auto_commit.py**

| 함수 | 역할 | 입력 | 출력 |
|------|------|------|------|
| `load_config()` | YAML 설정 로드 | - | Dict |
| `get_latest_session_file()` | 최신 세션 파일 찾기 | - | Path \| None |
| `load_transcript()` | JSON 파싱 | session_file | List[Dict] |
| `should_process_session()` | 처리 여부 결정 | session_file, messages | (bool, reason) |
| `extract_insights()` | 중요 메시지 추출 | messages | List[Dict] |
| `categorize()` | 카테고리 결정 | content | (category, filename_hint) |
| `already_committed()` | 커밋 중복 방지 | session_id | bool |
| `mark_processed()` | processed marker 작성 | session_file | bool |
| `is_processed()` | processed 상태 확인 | session_file | bool |
| `write_to_git_memory()` | Git에 저장 | session_file, insights | bool |
| `main()` | 진입점 | - | int (0=성공) |

### **2. launchd 플러시인**

```
~/Library/LaunchAgents/hermes.git-memory-auto-commit.plist
```

- **실행 주기**: 5분 (`StartInterval: 300`)
- **환경변수**: `PYTHONPATH=~/hermes` (또는 Hermes Agent 설치 경로)
- **실행 경로**: 시스템 Python 경로 (예: `/usr/bin/python3` 또는 `python3`)
- **실행 인자**: `python3 ~/hermes/scripts/git_memory_auto_commit.py`

---

## 🔐 보안

- **로컬 저장**: 모든 데이터는 `~/git-memory`에 저장 (클라우드 아님)
- **Git 추적**: 전체 이력 보존, 브랜치/머지 가능
- **No credentials**: API 키, 토큰 등 민감정보는 저장하지 않음 (필터링 규칙 추가 가능)

---

## 🐛 알려진 제한사항

1. **세션 필터링 조건**
   - 최소 2개 메시지
   - 최소 30초 대화 시간
   - 짧은 대화(`/search`, `/help`)는 저장되지 않음

3. **일관성 없음**
   - 카테고리 결정은 키워드 기반, 정확도 100% 아님
   - 수동 수정 가능 (`mv`로 디렉토리 이동)

3. **Git 충돌**
   - 동시 커밋 발생 시 수동 해결 필요
   - `git pull --rebase` 권장

---

## 📈 향후 개선

- [ ] **실시간 감시**: `inotify`/`fswatch`로 즉시 커밋
- [ ] **ML 카테고리 분류**: 키워드 기반 → NLP 모델
- [ ] **충돌 해결**: 자동 merge 도구
- [ ] **remote sync**: GitHub/GitLab 원격 저장소 자동 push
- [ ] **태그 시스템**: `#topic` 태그 자동 부여
- [ ] **중요도 점수**: 인사이트에 우선순위 부여

---

*Last updated: 2026-04-30*
