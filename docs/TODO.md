# TODO — 향후 개선 계획

**Git Memory 시스템의 개발 로드맵 및 개선 아이템.**

---

## 🎯 우선순위 높음 (Next 1-2 releases)

### 🚀 **성능 & 안정성**

- [ ] **실시간 감시 (Real-time Watch)**
  - `fswatch`/`inotify`로 세션 파일 변경 즉시 감지
  - 5분 주기 → 즉시 실행으로 개선
  - 대기 시간 80% 감소

- [ ] **Python 캐시 문제 근본 해결**
  - `__pycache__` 자동 정리 스크립트 추가
  - launchd 환경 PYTHONPATH 보장 메커니즘
  - `importlib.reload()` 사용 검토

- [ ] **충돌 자동 해결**
  - Git merge conflict 발생 시 자동 병합 시도
  - `git pull --rebase` 전략
  - 충돌 파일 알림 (Slack/Email)

### 📊 **카테고리 분류 정확도**

- [ ] **키워드 dictionary 확장**
  - `personal`: meeting, planning, decision, todo, vacation, birthday...
  - `learning`: study, learn, concept, example, tutorial, exercise...
  - `projects`: project, task, milestone, deadline, deliverable...
  - `uncategorized`: 일반 대화 필터링 방지

- [ ] **ML 기반 분류 (선택사항)**
  - TF-IDF 또는 word2vec 기반 간단한 분류기
  - `scikit-learn` 없이 순수 Python 구현 시도
  - Accuracy 90%+ 목표

- [ ] **다중 카테고리 지원**
  - 하나의 세션이 여러 카테고리에 속할 수 있도록
  - 파일명: `YYYY-MM-DD_category1-category2_...md`
  - cross-link 생성

### 🔍 **검색 & 발견성**

- [ ] **태그 시스템**
  - 내용 분석 → `#해시태그` 자동 추출
  - `#meeting-notes`, `#learning-topic` 등
  - 검색: `git grep "#meeting"`

- [ ] **전체 텍스트 인덱싱**
  - `git grep` 대신 faster search 도구
  - `ripgrep` (`rg`) 기반 검색
  - fuzzy matching 지원

- [ ] **검색 UI (선택)**
  - 간단한 Flask/FastAPI 웹 인터페이스
  - `/search?q=meeting&category=all`
  - 결과를 HTML로 예쁘게 표시

---

## 🎨 중간 우선순위 (3-6개월)

### 📈 **사용성**

- [ ] **설정 UI**
  - `config.yaml` 대신 CLI 설정 도구
  - `git-memory config --add-keyword personal meeting`
  - `git-memory status`로 상태 확인

- [ ] **세션picker**
  - 어떤 세션이 저장될지 미리보기
  - `--dry-run` 모드
  - `git-memory simulate <session_file>`

- [ ] **중요도 점수**
  - 각 인사이트에 점수 부여 (0-100)
  - 점수 기준: 키워드 수, 내용 길이, assistant 설명 등
  - 높은 점수만 저장하는 필터 옵션

### 🛠️ **관리자 도구**

- [ ] **CLI 도구**
  ```bash
  git-memory status          # 저장소 상태
  git-memory list            # 최근 커밋 목록
  git-memory search <kw>     # 검색 (git grep 래퍼)
  git-memory fix-category    # 수동 카테고리 수정
  git-memory cleanup         # 오래된 파일 정리
  git-memory stats           # 통계 (카테고리별 파일 수, 커밋 수)
  ```

- [ ] **백업/복원**
  - `git bundle create backup.bundle --all`
  - 자동 백업 (cron: 매일 새벽 2시)
  - 백업 파일 정책 (30일 보관)

### 📚 **문서 & 가이드**

### **FAQ**
- Q: personal 카테고리가 안 생겨요
- Q: learning 카테고리는 어떻게 저장되나요
- Q: 중복 커밋이 생겨요
- Q: git 충돌 해결 방법

- [ ] **비디오 튜토리얼**
  - 5분 빠른 시작
  - 15분 심화 가이드
  - 트러블슈팅 케이스 스터디

- [ ] **국제화 (i18n)**
  - 영어, 한국어 문서
  - 키워드 예제 제공

---

## 🌟 장기 비전 (6개월 이상)

### 🔮 **AI 통합**

- [ ] **OpenAI/ChatGPT 연동**
  - 인사이트 요약 자동 생성
  - learning expressions 영어 번역 추가
  - 카테고리 추천 AI

- [ ] **벡터 DB & 임베딩**
  - `sentence-transformers`로 임베딩 생성
  - `chromadb` 검색 엔진
  - semantic search (예: "학습 관련 개념" → 관련 파일 모두)

- [ ] **RAG (Retrieval-Augmented Generation)**
  - Iskra Agent가 git_memory 자동 참조
  - `/ask` 명령어: "학습 관련 표현 저장한 거 보여줘"
  - 자동 검색 + 답변 생성

### 🌐 **공유 & 협업**

- [ ] **원격 저장소 sync**
  - GitHub/GitLab/Bitbucket 자동 push
  - private repo 권한 관리
  - CI/CD 파이프라인 통합

- [ ] **멀티유저 지원**
  - 여러 Iskra Agent가 같은 저장소 공유
  - user_id 태그 제공
  - 충돌 해결 전략 개선

- [ ] **API & SDK**
  - Python SDK: `import git_memory; git_memory.save(insights)`
  - Webhook: 저장 시 외부 시스템 알림
  - GraphQL API

### 🏗️ **아키텍처 리팩토링**

- [ ] **모듈화**
  ```
  git_memory/
  ├── core/
  │   ├── processor.py   # 세션 처리
  │   ├── categorizer.py # 카테고리 분류
  │   ├── git_writer.py  # Git 작업
  │   └── config.py      # 설정 관리
  ├── cli/
  │   └── git-memory     # CLI entry point
  ├── watch/
  │   └── observer.py    # 실시간 감시
  └── api/
      └── server.py      # REST API
  ```

- [ ] **테스트 커버리지 90%+**
  - pytest 사용
  - fixtures로 mock session
  - continuous integration (GitHub Actions)

- [ ] **Docker 컨테이너**
  - `Dockerfile` 제공
  - `docker-compose.yml` (postgres + git_memory)
  - Kubernetes helm chart

---

## 🐛 알려진 버그

| ID | 설명 | 상태 | 우선순위 |
|----|------|------|----------|
| BUG-001 | `analyze_session()` 함수 미구현으로 NameError | ✅ 고침 | 낮음 |
| BUG-002 | launchd 로그 파일 비어있음 (PYTHONPATH 문제) | ✅ 고침 | 중간 |
| BUG-003 | 카테고리가 `uncategorized`로만 분류되는 경우 | 🔄 조사중 | 중간 |
| BUG-004 | processed marker가 세션 파일명만 저장 | ⏳ 개선 필요 | 낮음 |
| BUG-005 | Git 충돌 시 자동 해결 불가 | ⏳ 백로그 | 중간 |

---

## 📊 진행 현황

| 영역 | 완료 | 진행중 | 대기 | 합계 |
|------|------|--------|------|------|
| **핵심 기능** | 8 | 1 | 0 | 9 |
| **성능/안정성** | 2 | 2 | 2 | 6 |
| **사용성** | 1 | 2 | 1 | 4 |
| **관리 도구** | 0 | 1 | 1 | 2 |
| **문서** | 4 | 0 | 1 | 5 |
| **AI 통합** | 0 | 0 | 3 | 3 |
| **공유/협업** | 0 | 0 | 3 | 3 |
| **아키텍처** | 0 | 0 | 3 | 3 |
| **테스트** | 0 | 0 | 1 | 1 |
| **컨테이너** | 0 | 0 | 2 | 2 |

**총 진행률: 15/38 (39%)**

---

## 🎯 다음 마일스톤 (v0.2.0)

**목표:** 카테고리 분류 정확도 80%+ , CLI 도구 완성

### Sprint 1 (2주)
- [ ] 키워드 dictionary 확장 (200+ 키워드)
- [ ] `git-memory` CLI 기본 명령어 5개 구현
- [ ] `--dry-run` 모드 추가

### Sprint 2 (2주)
- [ ] 테스트 커버리지 50%+
- [ ] FAQ 문서 작성
- [ ] major bug 3개 수정

### Sprint 3 (1주)
- [ ] 버그 수정 및 안정화
- [ ] 문서 검토
- [ ] v0.2.0 릴리스

---

## 💬 아이디어 제안

아이디어가 있으시면 자유롭게 제안해 주세요!

```markdown
**아이디어 제목:**

**문제:**
[어떤 문제를 해결하나요]

**해결책:**
[어떻게 구현할지]

**영향:**
[이 변경으로 누가/무엇이 이득인가요]

**우선순위:** 낮음/중간/높음
```

---

*Todo 버전: 1.0 — April 2026*  
*Last updated: 2026-04-30*
