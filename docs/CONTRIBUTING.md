# Contributing

**Git Memory 시스템 개선을 위한 기여 가이드라인.**

---

## 👋 시작하기

### **환경 요구사항**

- macOS 11+ (Big Sur 이상)
- Python 3.11+
- Git 2.30+
- Hermes Agent 설치 완료

### **개발 환경 설정**

```bash
# 1. 저장소 클론 (이미 있음)
cd ~/git-memory

# 2. git user 설정
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 3. 의존성 설치
# (표준 라이브러리만 사용, 추가 의존성 없음)

# 4. 스크립트 실행 권한
chmod +x ~/hermes/scripts/git_memory_auto_commit.py
```

---

## 🧪 테스트

### **수동 테스트**

```bash
# 1. 테스트 세션 생성
python3 <<EOF
import json, time
from datetime import datetime

session = {
    "session_id": "test_manual_contrib",
    "session_start": datetime.now().isoformat(),
    "messages": [
        {"role": "user", "content": "안녕!", "timestamp": datetime.now().isoformat()},
        {"role": "assistant", "content": "안녕하세요! 학습 관련 표현 알려드릴까요?", "timestamp": datetime.now().isoformat()},
    ]
}
with open("~/hermes/sessions/session_test_manual_contrib.json", "w") as f:
    json.dump(session, f, ensure_ascii=False, indent=2)
EOF

# 2. processed marker 제거 (강제 재처리)
rm -f ~/.hermes/last_git_memory_processed

# 3. 스크립트 직접 실행
python3 -B ~/hermes/scripts/git_memory_auto_commit.py

# 4. 결과 확인
git -C ~/git-memory status
git -C ~/git-memory log --oneline -3
```

**기대 결과:** `personal/`, `learning/`, 또는 `projects/`에 새 파일 생성 후 커밋.

### **통합 테스트 (자동)**

```bash
# P1~P7 테스트 스크립트 실행
# (별도 테스트 스크립트 필요시 작성)
```

---

## 📐 코드 컨벤션

### **파일 구조**

```
hermes/
├── scripts/
│   ├── git_memory_auto_commit.py   # 메인 스크립트
│   ├── healthcheck.py              # 헬스체크
│   └── ...
├── logs/                           # 로그 디렉토리
├── sessions/                       # Hermes 세션 JSON
└── config.yaml                     # 설정

git-memory/
├── personal/                       # 카테고리 자동 생성
├── learning/
├── projects/
└── docs/                           # 문서
    ├── README.md
    ├── ARCHITECTURE.md
    └── ...
```

### **커밋 메시지 컨벤션**

자동 커밋 형식:
```
Auto-save: session <session_id> (YYYY-MM-DD)
```

수동 커밋 형식:
```
<type>: <description>

[optional body]

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

**타입:**
- `feat` — 새로운 기능
- `fix` — 버그 수정
- `docs` — 문서 업데이트
- `refactor` — 코드 리팩토링
- `test` — 테스트 추가/수정
- `chore` — 빌드/유지보수

---

## 🔍 코드 검토 (Review)

변경사항을 제출하기 전에 자체 검토:

1. **파일명/위치**: `git_memory_auto_commit.py`는 `~/hermes/scripts/`에 유지
2. **import**: 표준 라이브러리만 사용 (PyYAML 제외)
3. **에러 핸들링**: 예외 처리 확인
4. **로깅**: `logger.info()`, `logger.error()` 사용
5. **Git 작업**: `run_git_command()` 헬퍼 함수 사용
6. **설정**: `config.yaml`에 설정 추가/수정

---

## 🐛 버그 리포트

### **버그 템플릿**

```
**증상:**
[무슨 일이 발생했는지]

**재현 방법:**
1. ...
2. ...
3. ...

**기대 결과:**
[어떻게 되어야 하는지]

**환경:**
- macOS: [버전]
- Python: [버전]
- Hermes Agent: [버전]

**로그:**
[git_memory.log 관련 부분]
```

---

## 💡 기능 요청

기능 요청 전 확인:
1. **기존 문제 해결**: 이미 해결된 이슈 검색
2. **철학 부합**: Git 기반, 무료, 로컬 저장 원칙 준수
3. **간결성**: 작고 단일 책임 유지

**템플릿:**

```
**문제:**
[어떤 문제가 있는지]

**제안:**
[어떤 기능으로 해결할지]

**대안:**
[다른 방법 검토]

**우선순위:** 낮음/중간/높음
```

---

## 📦 릴리스 프로세스

1. 기능 완성 확인
2. `docs/` 문서 업데이트
3. `CHANGELOG.md` 업데이트
4. 버전 결정 (`PATCH`/`MINOR`)
5. `git commit -m "chore: release vX.Y.Z"`
6. `git tag vX.Y.Z`
7. `git push --tags`

---

## 🎯 기여 영역

| 영역 | 상태 | 담당 |
|------|------|------|
| **자동 커밋 로직** | ✅ 안정 | @hermes-core |
| **launchd 통합** | ✅ 완료 | @hermes-core |
| **카테고리 분류** | 🔄 개선 필요 | 도움 환영 |
| **ML 분류** | ⏳ 백로그 | 아이디어 제안 가능 |
| **성능 최적화** | ⏳ 백로그 | 도움 환영 |
| **문서화** | ✅ 진행 중 | @hermes-docs |
| **테스트 자동화** | ⏳ 백로그 | 도움 환영 |

---

## 📞 문의
지원:
- **GitHub**: [repository URL]
- **이메일**: support@git-memory.dev
- **Hermes 내**: `/help` 명령어

---

**감사합니다!** 🧡

*Every contribution matters — no matter how small.*
