# 06. CI / 릴리즈 워크플로 설계

- 문서 버전: 1.0 (Phase 1)
- 작성: SCM (Configuration/Release Manager)
- 최종 수정: 2026-05-17
- 대상 플랫폼: GitHub Actions
- 빌드 타깃: Windows 10/11 x64 (단일 실행 파일)

## 1. 개요

본 프로젝트는 3개의 GitHub Actions 워크플로를 운영한다.

| 파일 | 트리거 | 목적 | 산출물 |
|---|---|---|---|
| `.github/workflows/ci.yml` | push/PR (develop, main, release/**) | lint + 단위 테스트 | 콘솔 결과 |
| `.github/workflows/build-windows.yml` | push `release/win64/dev`, manual | Windows 빌드 검증 | artifact (.exe) |
| `.github/workflows/release-windows.yml` | push `release/win64/prd`, tag `v*` | 정식 릴리즈 | GitHub Release + .exe |

## 2. CI 워크플로 (`ci.yml`)

### 2.1 트리거
- push: `develop`, `main`, `release/**`
- pull_request: 위 브랜치들을 target으로 하는 모든 PR

### 2.2 매트릭스
- OS: `ubuntu-latest`, `windows-latest` (실제 실행 환경 사전 검증)
- Python: `3.11`

### 2.3 단계
1. checkout
2. Python 3.11 설치
3. 캐시(pip)
4. 의존성 설치(`requirements.txt`가 있으면 설치, 없으면 skip)
5. Lint: `ruff check .` (`pyproject.toml`/`ruff.toml`가 있으면, 없으면 skip)
6. Format check: `black --check .` (있을 때만)
7. 테스트: `pytest -q` (`tests/`가 있으면, 없으면 skip)

Phase 1 시점에는 소스/테스트가 없으므로 가드(존재 검사)로 노옵(no-op) 처리한다. Phase 2부터 실효성을 가진다.

### 2.4 YAML 본문 (실제 `.github/workflows/ci.yml`)
파일 본문은 같은 PR로 실제 워크플로 파일에 작성된다(아래 7장과 동일).

## 3. Windows 빌드 검증 워크플로 (`build-windows.yml`)

### 3.1 트리거
- push: `release/win64/dev`
- workflow_dispatch (수동 실행)

### 3.2 목적
- PyInstaller 빌드가 깨지지 않는지 검증
- 산출물을 artifact로 업로드(7일 보관)
- 정식 릴리즈 전 마지막 게이트

### 3.3 단계
1. checkout (windows-latest)
2. Python 3.11
3. pip 캐시
4. 의존성 + PyInstaller 설치
5. 빌드 대상 가드: `src/main.py`(또는 추후 결정된 엔트리)가 없으면 skip 메시지 출력하고 정상 종료
6. PyInstaller로 단일 파일 빌드 (`--onefile --name AnsiseongDefense`)
7. `dist/AnsiseongDefense.exe`를 artifact 업로드

## 4. 릴리즈 워크플로 (`release-windows.yml`)

### 4.1 트리거
- push: `release/win64/prd`
- push tag: `v*`

### 4.2 목적
- PyInstaller로 최종 .exe 빌드
- 자동으로 GitHub Release 생성
- .exe를 Release 자산으로 첨부
- CHANGELOG의 해당 버전 섹션을 릴리즈 노트 본문으로 사용

### 4.3 단계
1. checkout
2. Python 3.11
3. 의존성 + PyInstaller
4. 엔트리 가드 (없으면 명시적 실패 — 정식 릴리즈는 산출물이 있어야 함)
5. PyInstaller 빌드
6. 버전 추출
   - tag push이면 `${{ github.ref_name }}` 사용
   - branch push이면 `CHANGELOG.md`에서 최신 버전 파싱 또는 `v0.0.0-prd-${{ github.run_number }}` 형식의 임시 태그
7. `softprops/action-gh-release@v2`로 Release 생성 + .exe 첨부

### 4.4 비밀 운영
- `GITHUB_TOKEN`은 GitHub Actions가 자동 발급(별도 secret 추가 불필요)
- 별도 PAT(Personal Access Token)는 필요 없음
- 코드 사이닝(추후 결정): 사이닝 인증서가 도입되면 `WINDOWS_CERT_BASE64`, `WINDOWS_CERT_PASSWORD` 시크릿을 추가

## 5. Branch Protection 체크리스트 (GitHub Settings → Branches)

대상 브랜치별로 다음을 적용한다(SCM이 수동 설정):

### main
- [x] Require a pull request before merging
- [x] Require approvals: 1 (SCM)
- [x] Require status checks to pass before merging
  - 필수: `ci / ubuntu-latest (3.11)`, `ci / windows-latest (3.11)`
- [x] Require branches to be up to date before merging
- [x] Require conversation resolution before merging
- [x] Restrict who can push: SCM 계정만
- [x] Do not allow bypassing the above
- [x] Disallow force push
- [x] Disallow deletions

### develop
- [x] Require PR + status checks
- [x] Approvals: 1 (SCM)
- [x] Disallow force push
- [x] Disallow deletions

### release/win64/dev, release/win64/prd
- [x] Restrict push: SCM 계정만
- [x] Require status checks (build-windows / release-windows)
- [x] Disallow force push
- [x] Disallow deletions
- [x] PR 필수는 선택(SCM이 직접 푸시하기도 함)

## 6. 시크릿/토큰 운영 가이드

| 이름 | 출처 | 용도 | 등록 위치 |
|---|---|---|---|
| `GITHUB_TOKEN` | GitHub Actions 자동 | Release 생성, artifact 업로드 | 자동 |
| (미래) `WINDOWS_CERT_BASE64` | 코드 사이닝 인증서 | .exe 사이닝 | Settings → Secrets → Actions |
| (미래) `WINDOWS_CERT_PASSWORD` | 인증서 비밀번호 | .exe 사이닝 | Settings → Secrets → Actions |

원칙:
- 시크릿은 절대 코드/로그에 echo 금지
- 시크릿 회전 주기: 6개월
- 사용 종료된 시크릿은 즉시 삭제

## 7. 실제 YAML 본문 (참조)

본 문서의 YAML 본문은 실제 다음 파일에 동일하게 작성되어 있다.
- `.github/workflows/ci.yml`
- `.github/workflows/build-windows.yml`
- `.github/workflows/release-windows.yml`

향후 워크플로 변경 시 본 문서도 함께 갱신한다(`docs/`의 단일 진실 원천 유지).

## 8. 변경 이력
- 1.0 (2026-05-17): 초안 작성 (Phase 1).
