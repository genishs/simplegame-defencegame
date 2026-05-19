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

**Phase 4 자동 가드 완결 — `v0.4.0-rc.1` 사전 릴리즈 (2026-05-19, SCM 발급, develop@8e9c3de). Phase 5 진입 (kickoff PR #47/#48 머지). `v0.4.0` GA는 사용자 검수(CAT-01~07 + DPI 매트릭스) 대기 — 통과 시 별도 SCM 라운드에서 main 머지·태깅 (DECISION-SCM-P5K-001).**

> **버전 매핑(메모리 규칙 정합)**: Phase 1 = v0.1.0, Phase 2 = v0.2.0, Phase 3 = v0.3.0, **Phase 4 = v0.4.0** (RC 발급, GA 대기), Phase 5 = v1.0.0 (RC→GA 직행, 중간 마이너 도입 여부 OPEN-PL-P5-006).
> 이전: `v0.3.0-rc.1` 사전 릴리즈는 별도 검수 대기 — `v0.3.0` 정식 승격 단계는 Phase 4 자동 가드 완결과 분리, 사용자 검수 후 별도 SCM 라운드.

| Phase | 내용 | 상태 |
|---|---|---|
| 1 | 사전 기획 — 역사 검토, 컨셉, 디자인 문서, 기술 아키텍처, SCM/CI 구축 | ✅ 완료 (v0.1.0, 2026-05-17) |
| 2 | 기본 로직/엔진 구현 + 스토리 작성 (메인 루프, 타워, 적 이동, 웨이브) | ✅ 완료 (v0.2.0, 2026-05-19) |
| 3 | 기능 통합 검토 + 디자인/스토리 적용 + 프로토타입 + 수직 슬라이스 + 회귀 매트릭스 | ✅ 완료 (`v0.3.0-rc.1`, 2026-05-19) |
| 4 | 기능 테스트 + 디버깅 + 버그픽스 + 튜토리얼/난이도/QA v2 + SFX 백엔드 + 클리어율 자동화 + 잠재 결함 해결 (자동 가드 완료, 사용자 검수 CAT-01~07 통과 시 `v0.3.0` GA 승격) | ✅ 자동 가드 완료 (R1+R2+R3: #26 #27 #29 #38 #39 #43 #44, 사용자 검수 대기) |
| 5 | 전체 스토리 적용 + 최종 완성 + 패키징/릴리즈 | 🚧 진행 중 (kickoff 2026-05-19, `docs/14_phase5_plan.md`, 4 sub-phase 분할, 대상: v1.0.0-rc.1→v1.0.0 — SCM 정정 2026-05-19) |

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
- **Phase 4 R2 — 완료 (2026-05-19)**:
  - BL-07 클리어율 시뮬레이션 자동화 (#39 / PR #41, DECISION-DT1-P4B-001~005) — tkinter-free 헤드리스 시뮬레이터, 15/15 (100%) 클리어
  - simpleaudio SFX 백엔드 시범 도입 (#29 / PR #42, DECISION-AUDIO-012) — 8 placeholder WAV + AU-07 자동화, ubuntu CI `libasound2-dev` step 추가
  - pytest markers 4종(`regression_p4`, `slow`, `audio`, `network`) 정식 등록, 경고 0건
  - pytest 누적 **424 passed** (Phase 4 R1 종료 시점 396 → +28, 회귀 0)
- **Phase 4 R3 — 완료 (2026-05-19)**:
  - WaveSystem 보스 path 다단 fallback (#43 / PR #46, DECISION-DL-P5P-001)
  - Projectile swept-circle 충돌 (#44 / PR #46, DECISION-DL-P5P-002) — BL-07 시뮬레이터 workaround 정식 코드화
  - pytest markers 5+2 파일 일관 적용 + `ci.yml` 3-step 분리 (PR #45, DECISION-QA-P4M-001~003)
  - 회귀 매트릭스 v2.2→v2.3 (55→64 시나리오, WV/CB 신규 10건)
  - **`docs/qa/v0_3_0_ga_checklist.md`** 발행 — 자동 가드 8/8 ✓ / 사용자 검수 0/7 ☐ / DPI 0/2 ☐
  - **`docs/qa/phase4_completion_report.md`** Phase 4 종료 보고서
  - pytest 누적 **448 passed** (Phase 4 종료 시점, slow 별도 시 BL-07 5/5)
- **GA 진입 (사용자 의존)**: CAT-01~07 + DPI 매트릭스 통과 후 별도 SCM 라운드에서 develop → main 머지 + `v0.3.0` 태그 + GitHub Release prerelease=false 갱신.
- **Phase 4 종료 — `v0.4.0-rc.1` 사전 릴리즈 (2026-05-19, SCM 발급)**: Phase 4 R1+R2+R3 자동 가드 완결 시점에 발급. 사용자 검수(CAT-01~07 + DPI 매트릭스) 통과 시 별도 SCM 라운드에서 `v0.4.0` 정식 GA 승격.
- **Phase 5 진입 (2026-05-19, DECISION-PL-P5-001~006 + SCM 정정 DECISION-SCM-P5K-001)**: `docs/14_phase5_plan.md` 발행 — 전체 스토리 통합 + 최종 완성 + 패키징/릴리즈(1.0.0). 4 sub-phase 분할 (메모리 규칙 정합: 1.0.0 = Phase 5 완료):
  - **Phase 5.1 BGM 통합**: Issue #30 정식 클로즈, OGG Vorbis 백엔드 도입 (OPEN-AUDIO-001 마감 예정) — develop 누적
  - **Phase 5.2 전체 스토리 통합**: `docs/story/01~07` 산출물을 인게임 intro/outro/엔딩 컷씬으로 실 통합, 5인 픽션 캐릭터 대사 SSOT 60~80건 추가 — develop 누적
  - **Phase 5.3 자산 실수급 / 최종 완성**: BGM 8곡 + SFX 20개 실 라이선스 자산 교체, 픽션 캐릭터 일러스트 옵션 B(강화 placeholder) 우선
  - **Phase 5.4 1.0.0 패키징 / 릴리즈** → v1.0.0-rc.1 → v1.0.0: 자동 릴리즈 노트 + Linux 빌드 CI 추가(DECISION-PL-P5-005), Windows 코드 서명 미적용 유지(DECISION-PL-P5-004), macOS 보류(OPEN-PL-P5-002)
  - 페르소나 거버넌스: Localization Engineer / Release Engineer 신설은 보류, Steering 후속 라운드 표결 위임 (OPEN-PL-P5-001~002)
  - 자율 결정 6건 DECISION-PL-P5-001~006 기록, 6건 OPEN-PL-P5-001~006 후속 위임 (SCM 정정 시 OPEN-PL-P5-006 신설)
  - 중간 마이너 태그(v0.5.0/v0.6.0) 도입 여부는 OPEN-PL-P5-006 Steering 표결 위임

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
