# Security Policy

**Git Memory — Automatic AI Session Memory Storage**

이 문서는 Git Memory 프로젝트의 보안 정책과 권장 보안 조치를 설명합니다.

---

## 📋 개요

Git Memory는 AI 대화를 자동으로 Git 저장소에 저장하는 도구입니다.  
대화 내용에 개인정보, API 키, 프로젝트 기밀 등 민감한 데이터가 포함될 수 있으므로, **보안에 각별한 주의가 필요합니다**.

현재 이 프로젝트는 **보안 관련 기능이 전혀 구현되어 있지 않습니다**.  
본 문서는 단계별로 적용 가능한 보안 강화 방안을 제시합니다.

---

## ⚠️ 현재의 보안 위험

### 1. **평문 저장 (Plain Text Storage)**
- 모든 대화가 Markdown 파일로 평문 저장됨
- Git 히스토리에 영구 보관 (삭제해도 과거 커밋에서 복구 가능)
- 저장소 복제 시 모든 데이터가 노출됨

### 2. **자동 커밋 위험**
- AI 세션에서 실수로 민감 정보가 포함된 경우 자동 커밋됨
- 사용자 확인 없이 바로 Git에 저장됨

### 3. **저장소 유출 위험**
- 로컬 디스크 도난/유출 시 데이터 그대로 노출
- remote(GitHub 등)에 push할 경우 인터넷 통해 접근 가능
- 백업 파일에도 동일한 평문 데이터 포함

### 4. **접근 제어 부재**
- 단일 저장소 구조: 모든 세션/카테고리/사용자가 동일 저장소 사용
- 세분화된 권한 관리 없음 (읽기/쓰기 제어 불가)

### 5. **과거 데이터 영구 보존**
- 민감 정보가 한 번 커밋되면 영구히 히스토리에 남음
- `git filter-repo`로 제거해도 과거 커밋에서 복구 가능성 있음

---

## 🎯 **보안 강화 우선순위**

### **P0 - 즉시 적용 (필수)**

| 번호 | 조치 | 설명 | 소요시간 |
|------|------|------|----------|
| 1 | **Private Repository** | GitHub/GitLab 저장소를 Private으로 전환 | 1분 |
| 2 | **`.gitignore` 강화** | 민감 파일/디렉토리 제외 규칙 추가 | 2분 |
| 3 | **SSH + 2FA** | Git remote 접근 시 SSH 키 + 2FA 활성화 | 3분 |

### **P1 - 단기 (1주 이내)**

| 번호 | 조치 | 도구/방법 | 설명 |
|------|------|----------|------|
| 4 | **부분 암호화** | `git-crypt` | `personal/` 폴더만 AES-256 암호화 |
| 5 | **자동 검사** | 정규식 기반 필터 | API 키, 비밀번호 패턴 감지 |
| 6 | **사용자 확인** | CLI prompt | 민감 키워드 감지 시 수동 승인 요청 |

### **P2 - 중기 (1-3개월)**

| 번호 | 조치 | 설명 |
|------|------|------|
| 7 | **PII Scanner** | `presidio`나 `scrubadub`로 개인정보 자동 탐지 |
| 8 | **분리 저장소** | `personal/`과 `projects/`를 별도 저장소로 분리 |
| 9 | **Audit Log** | 누가 언제 접근/변경했는지 기록 |
| 10 | **TTL 정책** | 오래된 메모리 자동 삭제/압축 (예: 1년) |

### **P3 - 장기 (3-6개월)**

| 번호 | 조치 | 설명 |
|------|------|------|
| 11 | **키 관리 시스템** | OS 키체인(Keychain) 또는 Vault 연동 |
| 12 | **E2E 암호화** | 저장 전/후 모두 암호화 (클라이언트 측) |
| 13 | **RBAC** | 역할 기반 접근 제어 (관리자/사용자/읽기전용) |
| 14 | **자동 삭제** | 민감 정보 감지 시 자동 제거 정책 |

---

## 🔐 **보안 도구 비교표**

### **암호화 도구**

| 도구 | 암호화 방식 | 장점 | 단점 | 추천도 |
|------|------------|------|------|--------|
| **git-crypt** | AES-256 (투명 암호화) | Git과 완벽 통합, 자동 암호화/복호화 | GPG 키 관리 필요 | ⭐⭐⭐⭐⭐ |
| **git-secret** | GPG 기반 파일 암호화 | 선택적 암호화, GPG 생태계 활용 | 설정 복잡 | ⭐⭐⭐⭐ |
| **SOPS** | AES-GCM + KMS 지원 | YAML/JSON/ENV 파일 전용, AWS KMS 연동 | MS Office 파일 미지원 | ⭐⭐⭐⭐⭐ |
| **BlackBox** | GPG 기반, Ansible 연동 | Ansible Vault 대체 가능 | 특정 도메인 | ⭐⭐⭐ |

**👉 추천: `git-crypt`**  
가장 무난하고 Git 워크플로우에 녹아들며, 폴더 단위로 암호화 가능.

---

## 📝 **단기 구현 가이드 (P0 + P1)**

### **Step 1: 저장소 Private로 전환**

```bash
# GitHub에서
1. Settings → General → Visibility → Private
2. Remove all external collaborators if any
3. Enable "Require pull request reviews" ( Protection)

# GitLab에서
Settings → General → Visibility, project features, permissions → Private
```

### **Step 2: .gitignore 강화**

```bash
# ~/.config/git-memory/ 디렉토리 전체 제외
# .gitignore에 추가:
*.key
*.pem
*.secret
*.env
secrets/
credentials/
config.local.yaml  # 로컬 override 파일
*.log
logs/
```

### **Step 3: git-crypt 도입 (선택적 부분 암호화)**

**설치:**
```bash
# macOS
brew install git-crypt

# Ubuntu
sudo apt-get install git-crypt

# 또는 GitHub Release에서 다운로드
```

**초기화:**
```bash
cd ~/git-memory  # 또는 프로젝트 저장소
git-crypt init
```

**암호화할 파일/폴더 지정 (.gitattributes):**
```bash
# .gitattributes 생성
personal/** filter=git-crypt diff=git-crypt
learning/** filter=git-crypt diff=git-crypt
projects/** filter=git-crypt diff=git-crypt
```

**GPG 키로 권한 부여:**
```bash
# 본인 GPG 키ID 확인
gpg --list-secret-keys --keyid-format=long

# 키 추가
git-crypt add-gpg-user YOUR_KEY_ID

# 커밋
git add .gitattributes
git commit -m "Enable git-crypt encryption for personal/learning/projects"
```

**암호화 해제 (다른 사용자에게 권한 부여 시):**
```bash
# 다른 사람의 GPG 공개키 가져오기
gpg --import their_public_key.asc

# 권한 부여
git-crypt add-gpg-user THEIR_KEY_ID
git push
```

**암호화된 파일 식별:**
```bash
# 암호화된 파일만 목록
git-crypt status

# 특정 파일 복호화 필요시
git-crypt unlock
```

---

## 🔍 **민감 정보 필터링 (Python)**

`git_memory/` 모듈에 `security_filter.py` 추가 권장:

```python
"""Security filter for detecting and masking sensitive information."""

import re
from typing import Optional, Tuple

# 민감 정보 패턴 (정규식)
SENSITIVE_PATTERNS = {
    "api_key": r"(?:api[_-]?key|access[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{20,})['\"]?",
    "password": r"(?:password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\"<>]{8,})['\"]?",
    "private_key": r"-----BEGIN [A-Z ]+ PRIVATE KEY-----",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone_kr": r"(\+82|0)\-?\d{2,3}\-?\d{3,4}\-?\d{4}",
    "ssn": r"\d{6}\-?\d{7}",  # 한국 주민등록번호
    "token": r"(?:bearer|token)\s+([A-Za-z0-9_\-]{10,})",
}

def detect_sensitive(text: str) -> Tuple[bool, list]:
    """텍스트에서 민감 정보 탐지."""
    findings = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            findings.append({"type": label, "matches": matches})
    return (len(findings) > 0, findings)

def mask_sensitive(text: str) -> str:
    """민감 정보 마스킹."""
    masked = text
    for label, pattern in SENSITIVE_PATTERNS.items():
        masked = re.sub(
            pattern,
            f"[REDACTED-{label.upper()}]",
            masked,
            flags=re.IGNORECASE
        )
    return masked

def should_commit_sensitive(text: str, auto_approve: bool = False) -> bool:
    """민감 정보 감지 시 커밋 승인 요청."""
    is_sensitive, findings = detect_sensitive(text)
    if is_sensitive:
        print(f"\n⚠️  민감 정보 감지됨:")
        for f in findings:
            print(f"   - {f['type']}: {f['matches']}")
        if auto_approve:
            print("   → auto-approve로 인해 그대로 커밋됨")
            return True
        response = input("\n커밋하시겠습니까? (y/N): ").strip().lower()
        return response == 'y'
    return True
```

**적용 위치:**
- `auto_commit.py`의 `main()` 함수 내 커밋 전에 `should_commit_sensitive()` 호출

---

## 🏗️ **중장기 아키텍처 개선안**

### **옵션 A: 저장소 분리 (추천)**

```
~/git-memory/
├── personal/          ← 암호화 (git-crypt)
│   └── .gitattributes
├── learning/          ← 평문
│   └── ...
├── projects-public/   ← 평문 (공유 가능)
│   └── ...
└── projects-secret/   ← 암호화 (git-crypt)
    └── ...

# 별도 저장소로 분리
~/git-memory-personal/   (Private, 암호화)
~/git-memory-public/     (Public 또는 Internal)
```

**장점:**
- 기본 저장소는 항상 Public/Internal로 안전
- 민감 저장소만 추가 보안 조치
- 실수로 민감 데이터를 Public 저장소에 저장하는 실수 방지

**단점:**
- 여러 저장소 관리 필요
- 검색이 불편해짐 (`git grep`가 저장소마다 필요)

---

### **옵션 B: 파일 단위 암호화 (git-secret)**

```bash
# 개별 파일 암호화 (personal/ 내 .md 파일만)
git secret init
git secret add personal/2024-04-30_meeting.md
git secret hide  # 암호화
git commit -m "Add encrypted meeting notes"
git push

# 복호화
git secret reveal
```

---

## 📊 **보안 수준矩阵**

| 수준 | 대상 | 방법 | 비용 | 추천 시나리오 |
|------|------|------|------|--------------|
| **L1** | 전체 저장소 | Private repo | 무료 | 개인용, 혼자 쓸 때 |
| **L2** | 카테고리별 분리 | 저장소 분리 | 무료 | 개인+공유 혼용할 때 |
| **L3** | 폴더 암호화 | git-crypt | 무료 | 민감 데이터 포함 시 |
| **L4** | 파일 암호화 | git-secret/SOPS | 무료 | 완전 비밀 정보 |
| **L5** | E2E加密 | 전단계 암호화 | 개발 필요 | 다중 사용자 공유 |

**현재 프로젝트 수준: L1 (Private만 하면 충분)**

**권장 수준:** L2 (저장소 분리) + L3 (git-crypt) 조합

---

## 🔐 **즉시 적용 체크리스트 (오늘 내)**

- [ ] GitHub 저장소 Private으로 전환
- [ ] `.gitignore`에 `secrets/`, `*.key`, `*.pem` 추가
- [ ] SSH 키 사용 + 2FA 활성화
- [ ] GPG 키 생성 (없으면) `gpg --full-generate-key`
- [ ] `git-crypt` 설치 및 초기화
- [ ] `.gitattributes`로 `personal/` 폴더 암호화 설정
- [ ] `security_filter.py` 파일 생성 ( implicilty )
- [ ] `auto_commit.py`에 `should_commit_sensitive()` 호출 추가

---

## 🚨 **민감 정보 이미 노출됐다면?**

```bash
# 1. BFG Repo-Cleaner로 키워드 삭제 (가장 쉬움)
# https://rtyley.github.io/bfg-repo-cleaner/
bfg --replace-text passwords.txt ~/git-memory

# passwords.txt 내용:
월드패스워드==>XXX
API_KEY==>[REDACTED]

# 2. 또는 git-filter-repo
pip install git-filter-repo
git filter-repo --replace-text <(echo "API_KEY==>REDACTED")

# 3. 강제 푸시 (협업자에게 공지!)
git push origin --force --all
git push origin --force --tags

# 4. 모든 협업자에게 새 clone 요청
```

**주의:** 이미 퍼진 복제본은 완전히 삭제 불가능합니다. 가능한 빨리 조치하세요.

---

## 📞 **보안 취약점 신고**

보안 취약점을 발견했을 경우:

1. **공개적으로 Issue/PR를 만들지 마세요**
2. 이메일: `jeonghoheo+(security)@gmail.com` (가상)
3. GitHub Security Advisory 사용 (Private repo에서만)

**포함 내용:**
- 발견 방법
- 영향 받는 버전
- 재현 절차
- 제안 수정 방안

---

## 📚 **추가 참고 자료**

| 주제 | 링크 |
|------|------|
| git-crypt 공식 문서 | https://github.com/AGWA/git-crypt |
| git-secret 공식 문서 | https://git-secret.io/ |
| SOPS 공식 문서 | https://github.com/mozilla/sops |
| BFG Repo-Cleaner | https://rtyley.github.io/bfg-repo-cleaner/ |
| presidio (PII detection) | https://github.com/microsoft/presidio |
| GitHub Security Best Practices | https://docs.github.com/en/actions/security-guides |

---

## 🤝 **기여**

보안 강화 관련 기여를 환영합니다:
- 더 정교한 필터 패턴 추가
- 암호화 모듈 구현
- 감사 로깅 기능
- 보안 테스트 코드

---

*Last updated: 2026-04-30 | Version: 0.1.1-dev*  
*Maintainers: Git Memory Security Team*
