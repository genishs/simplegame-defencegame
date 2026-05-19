# 안시성 디펜스 (Ansiseong Defense)

> 645년 안시성 전투를 모티브로 한 한국사 디펜스 게임. Python 3.11 + tkinter로 제작.

![ci](https://github.com/genishs/simplegame-defencegame/actions/workflows/ci.yml/badge.svg)
![build-windows](https://github.com/genishs/simplegame-defencegame/actions/workflows/build-windows.yml/badge.svg)
![release-windows](https://github.com/genishs/simplegame-defencegame/actions/workflows/release-windows.yml/badge.svg)

---

## 스크린샷
*(Phase 3 이후 게임플레이 스크린샷 추가 예정)*

---

## 개요

고구려가 당나라 대군을 막아낸 **안시성 전투(645년)** 를 소재로 한 타워 디펜스 장르 게임입니다.
플레이어는 안시성주의 입장에서 성벽을 보강하고 병력을 배치하여 침공해오는 적의 파상공세를 막아냅니다.

- 한국사 소재의 전략 디펜스 게임
- 총 5개 스테이지 (역사 흐름 기반)
- 가벼운 실행 환경 (Python 표준 라이브러리 중심: tkinter)
- Windows 64bit 단일 실행파일(.exe) 배포 (PyInstaller)

---

## 현재 진행 상태

**Phase 3 완료 — `v0.3.0-rc.1` 사전 릴리즈 (2026-05-19). Phase 4 R1 첫 구현 라운드 머지 완료 (2026-05-19, develop@5c26653).**

| Phase | 내용 | 상태 |
|---|---|---|
| 1 | 사전 기획 — 역사 검토, 컨셉, 디자인 문서, 기술 아키텍처, SCM/CI 구축 | ✅ 완료 (v0.1.0, 2026-05-17) |
| 2 | 기본 로직/엔진 구현 + 스토리 작성 (메인 루프, 타워, 적 이동, 웨이브) | ✅ 완료 (v0.2.0, 2026-05-19) |
| 3 | 기능 통합 검토 + 디자인/스토리 적용 + 프로토타입 + 수직 슬라이스 + 회귀 매트릭스 | ✅ 완료 (`v0.3.0-rc.1`, 2026-05-19) |
| 4 | 기능 테스트 + 디버깅 + 버그픽스 + 튜토리얼/난이도/QA v2 (사용자 검수 CAT-01~07 통과 시 `v0.3.0` GA 승격) | 🚧 진행 중 (R1 완료: #26 튜토리얼, #27 난이도) |
| 5 | 전체 스토리 적용 + 최종 완성 + 패키징/릴리즈 | ⏳ 예정 |

### Phase 3 세부 진행
- **3.1 통합 하드닝 — 완료**: `reward.grain` 데이터 패치(#2), `src/systems/` tkinter import 금지 CI 가드(#8), stdlib-only stage JSON schema validator(#10), prerelease 감지 워크플로(#9)
- **3.2 스테이지 데이터 — 완료**: `stage_02` 요동 ~ `stage_05` 토산 JSON 5종 + 스키마 검증 테스트 40건(#11)
- **3.3 프로토타입 통합 — 완료**: `BattleScene._spawn_enemy` waypoint 결선(#1), M키 영웅 수동 모드(#4), Phase 2 잠재 결함(Enemy 생성자 시그니처 + waypoints 미설정) 동반 수정
- **3.4 디자인/스토리 적용 + 폰트 번들 — 완료**: `docs/story/08_ui_strings.md` SSOT v1.1 격상(#5), 캐릭터 플레이스홀더 5종(#6), Noto Sans KR(OFL 1.1) PyInstaller 번들링(#7)
- **3.5 수직 슬라이스 데모 — 완료**(#12): 메뉴 → 스테이지 선택 → 배틀 → 엔딩 풀 사이클 결선, BattleScene 진입 시 영웅(Hero) 자동 등록, stage_05 클리어 시 엔딩 라우팅, 통합 테스트 18건 + 회귀 매트릭스 자동 가드 21건 추가 (총 **334 passed**), PyInstaller `--onefile` .exe 로컬 빌드 검증 (24.9MB, Noto Sans KR 번들 확인), 사용자 검수 카탈로그 CAT-01~04 정의. SCM finalize: `v0.3.0-rc.1` 태깅 + main 머지.

### 다음 단계
- **사용자 시각 검수 (CAT-01~07)**: `docs/qa/scenario_catalog.md` 카탈로그 기반. 통과 시 `v0.3.0` 정식 GA 승격 (DECISION-SCM-P4-004 — 사용자 복귀 후 별도 라운드에서 main 머지·태깅).
- **Phase 4 R1 — 완료 (2026-05-19)**:
  - 튜토리얼 8단계 구현 + save_slot (#26 / PR #36, DECISION-DT2-P4-*)
  - 초반 3스테이지 난이도 하향 (#27 / PR #34, DECISION-DT1-P4-001~004) + 스키마 `night_vision_radius_multiplier` 옵션 필드
  - ui_strings §20 한국어 35건 확정 (#26 / PR #35, DECISION-DESIGN-P4-001~005)
  - 회귀 매트릭스 v2 + 시나리오 카탈로그 확장 + 자동 테스트 보강 (PR #37, DECISION-QA-P4-001~006)
- **Phase 4 R2 (후속)**: 사용자 검수 CAT-01~07 + 결함 수렴 + 1920×1080 / 100%·125% DPI 매트릭스 + BL-07 클리어율 시뮬레이션 자동화.

상세 변경 내역은 [CHANGELOG.md](./CHANGELOG.md) 참조.

---

## 기술 스택

- 언어: **Python 3.11**
- UI/렌더링: **tkinter** (표준 라이브러리)
- 빌드/패키징: **PyInstaller**
- 테스트: **pytest** (Phase 2부터)
- 린트/포맷: **ruff**, **black**
- CI/CD: **GitHub Actions**

상세 설계는 [docs/](./docs/) 폴더 참조.

---

## 요구사항 (실행 환경)

- OS: **Windows 10 / Windows 11 (64bit)**
- (소스 실행 시) Python **3.11**
- (배포 .exe 사용 시) 별도 런타임 설치 불필요

---

## 폴더 구조 (Phase 2 시점)

```
defensegame/
├── .github/
│   ├── workflows/           # GitHub Actions (CI/빌드/릴리즈)
│   ├── ISSUE_TEMPLATE/
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── docs/                    # 기획/설계 문서
│   ├── 01_history_research.md
│   ├── 02_concept_brief.md
│   ├── 03_game_design_document.md
│   ├── 04_technical_architecture.md
│   ├── 05_branching_release_strategy.md
│   ├── 06_ci_release_workflow.md
│   ├── 07_wireframes_visuals.md
│   ├── 08_asset_inventory.md
│   ├── 09_animation_state_diagrams.md
│   ├── story/               # 스토리 산출물 (00 bible / 01 intro / 02~06 stages / 07 ending / 08 ui_strings / 09 codex)
│   └── qa/                  # Phase 2 QA 리뷰·의사결정
├── src/                     # 게임 소스 코드
│   ├── core/                # app, game_loop, scaler, assets, events, settings, logger, sound
│   ├── entities/            # entity(ObjectPool), hero, ally, enemy, projectile, effect
│   ├── systems/             # combat, pathing, wave, economy, input (tk-independent)
│   ├── scenes/              # menu, stage_select, battle, ending
│   ├── ui/                  # widgets, hud, dialog
│   ├── data/                # 데이터 로더 + units/enemies/stages JSON
│   └── main.py
├── tests/                   # pytest 단위·통합 테스트 (139 passed)
├── assets/                  # (Phase 3 이후 일러스트/사운드 자산 투입 예정)
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── CHANGELOG.md
└── README.md
```

---

## 개발 가이드

### 로컬 실행
> Phase 2부터 소스 코드가 포함되며 실행 가능합니다.

```bash
# 1. 저장소 복제
git clone https://github.com/genishs/simplegame-defencegame.git
cd simplegame-defencegame

# 2. 가상환경
python -m venv .venv
.\.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux (참고)

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 실행
python src/main.py
```

### Windows 실행파일 직접 빌드 (Phase 2 이후)
```bash
pip install pyinstaller
pyinstaller --onefile --name AnsiseongDefense src/main.py
# dist/AnsiseongDefense.exe 생성
```

---

## 브랜치 전략 요약

| 브랜치 | 목적 |
|---|---|
| `main` | 정제/테스트 완료된 안정 코드. SCM이 develop에서 머지. |
| `develop` | 개발 통합 브랜치. 모든 PR의 기본 타깃. |
| `release/win64/dev` | Windows 빌드 검증 (GitHub Actions로 artifact 생성). |
| `release/win64/prd` | 정식 릴리즈. push 시 GitHub Release 자동 생성. |
| `feature/*`, `bugfix/*`, `docs/*` | 작업 브랜치. PR로 develop에 머지. |

상세는 [docs/05_branching_release_strategy.md](./docs/05_branching_release_strategy.md) 참조.

---

## 기여 방법 (Contribution)

1. 이슈를 먼저 생성하거나 기존 이슈를 확인합니다.
2. `develop`에서 브랜치를 분기합니다: `feature/<slug>`, `bugfix/<slug>`, `docs/<slug>`.
3. [Conventional Commits](https://www.conventionalcommits.org/) 규약으로 커밋합니다.
4. PR을 생성하고(base: `develop`), PR 템플릿을 채웁니다.
5. CI(`ci.yml`)가 통과해야 합니다.
6. SCM(@genishs)의 승인 후 머지됩니다.

자세한 PR 워크플로 및 보호 규칙은 [docs/05_branching_release_strategy.md](./docs/05_branching_release_strategy.md) 참조.

---

## CI / 릴리즈 워크플로

| 워크플로 | 트리거 | 동작 |
|---|---|---|
| `ci.yml` | develop/main/release/** push·PR | lint + 단위 테스트 (Ubuntu + Windows 매트릭스) |
| `build-windows.yml` | `release/win64/dev` push | Windows .exe 빌드 + artifact 업로드 |
| `release-windows.yml` | `release/win64/prd` push, `v*` tag | .exe 빌드 + GitHub Release 자동 생성 |

상세는 [docs/06_ci_release_workflow.md](./docs/06_ci_release_workflow.md) 참조.

---

## 라이선스

### 본 저장소 (코드/콘텐츠)
**미정 (To be decided)** — 추후 결정 예정입니다.
현재 시점에서 본 저장소의 코드/콘텐츠는 모든 권리가 저작자에게 유보됩니다(All rights reserved by default).

### 동봉 자산 (assets/)
| 자산 | 라이선스 | 출처 |
|---|---|---|
| `assets/fonts/NotoSansKR-Regular.otf` | **SIL Open Font License 1.1** | [notofonts/noto-cjk](https://github.com/notofonts/noto-cjk) |
| `assets/fonts/NotoSansKR-Bold.otf` | **SIL Open Font License 1.1** | [notofonts/noto-cjk](https://github.com/notofonts/noto-cjk) |

라이선스 전문은 [`assets/fonts/OFL.txt`](./assets/fonts/OFL.txt) 또는 [scripts.sil.org/OFL](https://scripts.sil.org/OFL) 참고.
SIL OFL 1.1은 폰트 파일의 **자유로운 사용·복제·재배포·임베딩**을 허용하며, 본 프로젝트는 빌드된 .exe 내부에 폰트를 임베드하는 형태로 사용합니다(DECISION-Q-007, Issue #7).

---

## 크레딧 / 연락처

- 기획·개발: **genishs**
- 형상관리(SCM): genishs
- 문의: GitHub Issues 사용 권장

> 본 프로젝트는 한국사 학습 목적의 비영리 학습 프로젝트입니다.
> 역사 자료는 정사(『삼국사기』 등) 및 학술 자료에 기반하되, 게임 연출상 일부 각색이 포함될 수 있습니다.
