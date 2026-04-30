# Git Memory 사용 가이드

실제 사용 시나리오와 예제를 통해 Git Memory를 어떻게 활용하는지 보여드립니다.

---

## 시나리오 1: 개인 메모

### 🎯 목표
회의, 아이디어, 개인적인 생각들을 자동으로 저장하고 나중에 검색

### 설정

```yaml
# ~/.config/git-memory/config.yaml
keywords:
  personal: ["meeting", "회의", "아이디어", "결정", "할일", "todo", "planning"]
```

### 예상 저장 구조

```
git-memory/personal/
├── 2024-01-15_meeting.md      # 회의 관련 대화
├── 2024-01-20_ideas.md        # 아이디어 브레인스토밍
└── 2024-02-01_decision.md     # 결정사항
```

### 예제Markdown 파일

```markdown
# personal - 2024-01-15

**Source:** AI session session_abc123
**Date:** 2024-01-15

### 👤 User
> 다음 주 월요일 오후 3시에 팀미팅 잡아줘

### 🤖 Assistant
> ✅ 2024-01-15 15:00에 팀 미팅이 예약되었습니다.

### 👤 User
> 아, 아직 결정 안 했으니까 할 일에만 메모해줘
```

---

## 시나리오 2: 언어 학습

### 🎯 목표
러시아어, 영어 등 언어 학습 관련 대화를 자동 수집

### 설정

```yaml
keywords:
  learning:
    - "러시아어"
    - "russian"
    - "문법"
    - "grammar"
    - "단어"
    - "vocabulary"
    - "발음"
    - "pronunciation"
    - "aspect"
    - "격"
  personal: []  # 언어 학습은 별도 카테고리
```

**참고:** category_rules로 더 정교한 분류 가능
```yaml
category_rules:
  - keywords: ["러시아어", "russian", "grammar"]
    category: learning
    subcategory: russian
  - keywords: ["英語", "english", "vocabulary"]
    category: learning
    subcategory: english
```

### 예상 저장 구조

```
git-memory/learning/
├── 2024-01-10_russian.md
├── 2024-01-12_english.md
└── 2024-01-15_grammar.md
```

### 검색 예제

```bash
# "aspect"라는 단어가 포함된 모든 파일 찾기
git grep -i "aspect" learning/

# 오늘 학습 내용만
git log --since="today" --oneline -- learning/

# 특정 단어가 언급된 위치
git grep -n "instrumental" learning/russian/
```

---

## 시나리오 3: 프로젝트 작업

### 🎯 목표
프로젝트 결정사항, 할 일, 마일스톤을 Git으로 관리

### 설정

```yaml
keywords:
  projects:
    - "프로젝트"
    - "project"
    - "태스크"
    - "task"
    - "마일스톤"
    - "milestone"
    - "데드라인"
    - "deadline"
    - "결정"
    - "decision"
```

### 예상 저장 구조

```
git-memory/projects/
├── 2024-01-20_meeting.md      # 프로젝트 kick-off
├── 2024-02-01_milestone.md    # 마일스톤 달성
├── 2024-02-15_decision.md     # 기술 결정
└── 2024-03-01_review.md       # 회고
```

### 활용법

1. **주간 회고 작성:**
```bash
# 이번 주 프로젝트 관련 모든 커밋 보기
git log --since="1 week ago" --oneline -- projects/

# 마일스톤별로 정리
git log --grep="milestone" --oneline
```

2. **결정사항 추적:**
```bash
# "결정"이 포함된 파일만
git grep -l "결정" projects/
```

3. **템플릿 활용:**
`projects/` 디렉토리에 `TEMPLATE.md`를 두고 새 프로젝트 시작 시 참고

---

## 시나리오 4: 워드프레스 블로그 연동

### 🎯 목표
AI가 작성한 블로그 초안을 자동 저장

### 설정

```yaml
keywords:
  projects:
    - "blog"
    - "블로그"
    - "포스트"
    - "post"
    - "article"
    - "기사"
```

### workflow

1. AI에게 블로그 글 초안 작성 요청
2. 대화가 끝나면 자동으로 `projects/`에 저장
3. 나중에 `git grep`으로 과거 글 검색
4. 필요한 부분만 복사해서 워드프레스에 올리기

---

## 시나리오 5: 리서치 노트

### 🎯 목표
인터넷 리서치, 기술 조사 내용 저장

### 설정

```yaml
keywords:
  learning:
    - "리서치"
    - "research"
    - "조사"
    - "기술"
    - "technology"
    - "트렌드"
    - "trend"
```

---

## 고급 활용

### 🔗 Cross-referencing

저장된 파일들끼리 서로 참조하려면:

```markdown
# 2024-01-15_meeting.md

## 참고 자료
- [[2024-01-10_russian]]  # Obsidian-style link ( vydav )
- 관련 결정: `projects/2024-01-20_decision.md`
```

### 🏷️ 태그 시스템 (수동)

파일 내용에 태그 추가:
```markdown
#personal #meeting #important #q1-2024
```

검색:
```bash
git grep "#important" personal/
```

### 📊 통계

```bash
# 카테고리별 파일 수
ls personal/ | wc -l
ls learning/ | wc -l
ls projects/ | wc -l

# 월별 커밋 수
git log --since="1 month" --oneline | wc -l

# 가장 활발한 달
git log --format="%ad" --date=format:"%Y-%m" | sort | uniq -c | sort -nr
```

---

## 자동화 팁

### 1. launchd/cron으로 5분 간격 실행 권장

```bash
# 수동 테스트 먼저
git-memory

# 문제없으면 자동 등록
launchctl load ~/Library/LaunchAgents/git-memory-auto-commit.plist
```

### 2. 로그 모니터링

```bash
tail -f ~/logs/git_memory.log
```

### 3. 저장소 백업 (주기적)

```bash
# 매주 백업
0 2 * * 0 git -C ~/git-memory bundle create ~/backups/git-memory-$(date +%Y%m%d).bundle --all
```

---

## 팁 & 트릭

1. **키워드 충분히 넣기**: 너무 짧은 대화는 저장되지 않음 (30초/2메시지 조건)
2. **config.yaml 자주 업데이트**: 새로운 주제 생길 때마다 키워드 추가
3. **수동 분류**: 잘못 분류된 파일은 `mv`로 이동 후 `git commit`
4. **Obsidian 연동**: `git-memory` 디렉토리를 Obsidian Vault로 열면 그래프 뷰 가능
5. **검색 최적화**: `git grep --color=always "키워드" | less -R`

---

## 워크플로우 예시: 하루 일과

```
09:00  아침 회의 → AI에게 요약 요청 → 자동 저장 (personal)
10:30  러시아어 공부 → AI와 대화 → 자동 저장 (learning)
14:00  프로젝트 설계 → AI 피드백 → 자동 저장 (projects)
18:00  하루 마무리 → git log로 오늘 작업 리뷰
```

---

## 문제가 있나요?

- **HELP.md** — 명령어, 설정, FAQ
- **OPERATIONS.md** — 트러블슈팅, 모니터링
- **GitHub Issues** — 버그 리포트

---

*Happy Git-Memory! 🧡*
