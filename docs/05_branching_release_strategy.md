# 05. 브랜칭 및 릴리즈 전략 (Branching & Release Strategy)

- 문서 버전: 1.0 (Phase 1)
- 작성: SCM (Configuration/Release Manager)
- 최종 수정: 2026-05-17
- 적용 프로젝트: 안시성 디펜스 게임 (Python 3.11 + tkinter)
- 원격 저장소: https://github.com/genishs/simplegame-defencegame.git

## 1. 목적
이 문서는 본 프로젝트의 형상관리(Configuration Management) 정책을 정의한다.
- 누가 어떤 브랜치에 무엇을 푸시할 수 있는가
- 어떤 절차로 코드가 통합되고 릴리즈되는가
- 어떤 이력(커밋/태그/릴리즈노트)을 남기는가

추적가능성(Traceability)과 회귀가능성(Revertability)을 최우선 가치로 삼는다.

## 2. 브랜치 다이어그램

```
                       (PR)                 (SCM merge)
   feature/* ─────────────────▶  develop ─────────────────▶  main
   bugfix/*  ─────────────────▶     │                          │
   docs/*    ─────────────────▶     │                          │
                                    │                          │
                                    │ (SCM cherry-pick/merge) │
                                    ▼                          │
                         release/win64/dev                     │
                         (Windows 빌드 시험)                   │
                                    │                          │
                                    │ (검증 OK)               │
                                    ▼                          │
                         release/win64/prd ◀───────────────────┘
                         (GitHub Actions 자동 릴리즈, tag v*)
```

머지 방향 요약:
- feature/bugfix/docs → develop (PR, SCM 승인 후 squash merge)
- develop → main (SCM 단독 권한, merge commit, 안정화 시점)
- develop → release/win64/dev (SCM, 빌드 검증용)
- release/win64/dev → release/win64/prd (SCM, 검증 통과 후)
- v* 태그는 main 또는 release/win64/prd 머지 커밋에 부여

## 3. 브랜치 정의

| 브랜치 | 목적 | 푸시 권한 | 보호 |
|---|---|---|---|
| `main` | 정제·테스트 완료된 안정 코드. 사용자 노출 기준. | SCM only (PR merge) | 직접 push 금지, PR 필수, SCM 승인 필수, status check 통과 필수 |
| `develop` | 개발 코드 통합 브랜치. 모든 feature PR의 타깃. | SCM (PR merge), 일부 자동화 | 직접 push 금지, PR 필수, status check 통과 필수 |
| `release/win64/dev` | Windows 64bit PyInstaller 빌드 검증용. | SCM only | 직접 push 금지(SCM 제외), 빌드 워크플로 트리거 |
| `release/win64/prd` | 최종 사용자 릴리즈. push 시 GitHub Release 자동 생성. | SCM only | 직접 push 금지(SCM 제외), 릴리즈 워크플로 트리거, force-push 금지 |
| `feature/<slug>` | 신규 기능 개발 | 개발자 누구나 | - |
| `bugfix/<slug>` | 버그 수정 | 개발자 누구나 | - |
| `docs/<slug>` | 문서 변경 | 개발자 누구나 | - |
| `chore/<slug>` | 빌드/툴/잡일 | 개발자 누구나 | - |

피쳐 브랜치 네이밍: `feature/phase2-tower-basic`, `bugfix/arrow-collision`, `docs/update-readme`.

## 4. PR(Pull Request) 워크플로

1. 개발자가 `develop`에서 분기 → `feature/<slug>` 작업
2. 푸시 후 GitHub UI에서 `develop`을 base로 PR 생성
3. PR 템플릿 채워넣기(아래 7항 참조)
4. CI(`ci.yml`)가 자동 실행 → lint + 테스트 통과
5. SCM이 코드 리뷰 후 `Approve`
6. SCM이 squash merge로 통합 (커밋 메시지는 Conventional Commits 규약)
7. SCM은 일정 시점에 develop을 main으로 머지(merge commit, no fast-forward)
8. SCM은 빌드가 필요한 시점에 develop 또는 main을 release/win64/dev로 푸시
9. 빌드 검증 후 release/win64/prd로 푸시 → GitHub Release 자동 생성

긴급 수정(hotfix): `bugfix/hotfix-<slug>`를 main에서 분기 → main과 develop 양쪽으로 머지(SCM이 직접 수행).

## 5. 커밋 컨벤션 (Conventional Commits)

형식:
```
<type>(<scope>): <subject>

<body, optional>

<footer, optional, BREAKING CHANGE / Refs / Co-Authored-By>
```

type:
- `feat`: 신규 기능
- `fix`: 버그 수정
- `docs`: 문서만 변경
- `chore`: 빌드/툴/잡일(코드/테스트 영향 없음)
- `test`: 테스트 추가/수정
- `build`: 빌드 시스템 변경(PyInstaller 옵션 등)
- `ci`: CI 설정 변경
- `refactor`: 기능 변화 없는 리팩토링
- `perf`: 성능 개선
- `style`: 포매팅 (코드 동작 변화 없음)

scope 예시: `tower`, `enemy`, `wave`, `ui`, `audio`, `build`, `docs`, `ci`.

좋은 예:
- `feat(tower): add ballista tower with splash damage`
- `fix(wave): correct spawn interval at stage 3`
- `docs(readme): add Phase 2 progress`
- `ci(release): pin pyinstaller to 6.10`

나쁜 예:
- `update` / `wip` / `fix bug`

## 6. 버저닝 정책 (Semantic Versioning)

`MAJOR.MINOR.PATCH` 규칙을 따른다.
- `0.x.0` = Phase x 완료 시점 (x = 1..5)
  - `0.1.0`: Phase 1 (역사 검토 + 기획 + 기술 검토 + SCM 초기화) — 본 시점
  - `0.2.0`: Phase 2 (코어 게임플레이 프로토타입)
  - `0.3.0`: Phase 3 (스테이지/밸런싱)
  - `0.4.0`: Phase 4 (그래픽/사운드/QA)
  - `0.5.0`: Phase 5 (패키징/배포 베타)
- `1.0.0` = 정식 릴리즈 (Phase 5 완료 + 외부 QA OK)
- `MINOR`(Phase 내 작은 단위): `0.1.1`, `0.1.2` ... 와 같이 핫픽스에 한해 사용
- `MAJOR` 증가: 호환 불가능한 저장 포맷 변경 등(현재로선 1.0 이후로 보류)

## 7. PR 템플릿 (`.github/pull_request_template.md` 본문안)

```markdown
## 변경 요약 (Summary)
- 

## 동기 (Why)
- 

## 변경 유형
- [ ] feat / [ ] fix / [ ] docs / [ ] chore / [ ] test / [ ] build / [ ] ci / [ ] refactor

## 테스트 방법 (How to test)
1. 

## 영향 범위
- 영향 모듈: 
- 회귀 가능성: 낮음 / 중간 / 높음

## 체크리스트
- [ ] Conventional Commits 규약 준수
- [ ] 관련 문서(README/CHANGELOG/docs/) 갱신
- [ ] CI 통과
- [ ] 시크릿/개인정보 포함 없음
- [ ] base 브랜치: `develop`

## SCM 승인 (SCM only)
- [ ] 리뷰 완료
- [ ] CHANGELOG.md [Unreleased] 반영 확인
- [ ] 머지 전략: squash / merge / rebase 중 선택
```

## 8. 태깅 및 릴리즈 노트

- 태그는 SCM만 생성/푸시. 형식 `vMAJOR.MINOR.PATCH`.
- 태그 생성 위치: `main` 머지 커밋(또는 release/win64/prd 머지 커밋).
- 태그 메시지에는 해당 Phase 핵심 산출물 요약을 포함.
- `v*` 태그가 푸시되면 `release-windows.yml`이 트리거되어 자동으로 GitHub Release를 생성하고 .exe를 첨부한다.
- 릴리즈 노트는 CHANGELOG.md의 해당 버전 섹션을 본문으로 사용.

## 9. CHANGELOG 정책

- 포맷: [Keep a Changelog 1.1.0](https://keepachangelog.com/ko/1.1.0/)
- 섹션: `Added` / `Changed` / `Deprecated` / `Removed` / `Fixed` / `Security`
- 모든 PR은 `[Unreleased]` 섹션에 한 줄 추가 (SCM이 머지 시 확인)
- 릴리즈 시 SCM이 `[Unreleased]` → `[x.y.z] - YYYY-MM-DD` 로 승격

## 10. 보안 정책

- 시크릿(.env, *.local, credentials.json, *.key, *.pem 등)은 `.gitignore`에 반드시 등록
- 커밋 전 `git status`로 의도치 않은 파일 확인
- `git add -A` 대신 명시적 add 권장
- 만약 시크릿이 푸시된 경우:
  1. 즉시 해당 시크릿 폐기/회전
  2. `git filter-repo`로 히스토리 제거
  3. 강제 푸시(SCM 단독 수행)
- GitHub Actions의 비밀은 Repository Settings → Secrets에만 보관
  - `GITHUB_TOKEN`: GitHub 제공 기본 토큰 (Release 생성에 사용, 별도 설정 불필요)
  - 추가 비밀이 필요해지면 SCM이 명시적으로 추가

## 11. `.gitignore` 정책 (요약)

다음 카테고리는 항상 제외:
- Python: `__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- 빌드: `build/`, `dist/`, `*.spec`, `*.exe`, `*.zip`
- IDE: `.vscode/`, `.idea/`, `*.swp`
- OS: `Thumbs.db`, `.DS_Store`, `desktop.ini`
- 환경: `.env`, `*.local`, `*.secret`
- 로그/임시: `*.log`, `tmp/`, `temp/`

실제 파일은 `/.gitignore` 참조.

## 12. 책임 (RACI 요약)

| 활동 | SCM | 개발자 |
|---|---|---|
| 브랜치 보호 설정 | R, A | I |
| PR 승인/머지 | R, A | C |
| develop→main 머지 | R, A | I |
| 릴리즈 브랜치 푸시 | R, A | I |
| 태그/릴리즈 생성 | R, A | I |
| CHANGELOG 갱신 검수 | R, A | R |
| 시크릿 관리 | R, A | I |

R=Responsible, A=Accountable, C=Consulted, I=Informed.

## 13. 변경 이력
- 1.0 (2026-05-17): 초안 작성 (Phase 1).
