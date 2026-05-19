# Changelog

이 문서는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)을 따르며, 버전 관리는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)을 따릅니다.

## [Unreleased]

### Phase 4 R1 — 첫 구현 라운드 머지 (2026-05-19, DECISION-SCM-P4-001~004)

> Phase 4 첫 구현 라운드. PR #34/#35/#36/#37 4건 통합 머지 완료. develop@5c26653.
> `v0.3.0` GA 승격은 사용자 시각 검수(CAT-01~07) 완료 후 별도 SCM 라운드로 보류 (DECISION-SCM-P4-004).

#### Added
- **튜토리얼 8단계 인터랙티브 흐름 (Issue #26)**:
  - `src/scenes/tutorial_scene.py` (신규, 1011줄): 메뉴 진입 → 단계 1~8 → stage_select 라우팅. 스킵/ESC 확인 다이얼로그 + "다시 보지 않기" 영구 무시 지원.
  - `src/core/save_slot.py` (신규): `SaveSlot` 데이터 클래스 + `tutorial_dismissed` / `tutorial_completed` 영속 필드 + 슬롯 직렬화.
  - `tests/test_tutorial_scene.py` (신규, 23건): 튜토리얼 단계 진행/스킵 다이얼로그/save_slot 영속/자동 진입 정책 자동 가드.
- **ui_strings §20 한국어 35건 확정 (Issue #26 후속, DECISION-DESIGN-P4-001~005)**: `docs/story/08_ui_strings.md` §20 (`menu.tutorial.button` ~ `tutorial.step8.*`) — 가이드 화자 = 양만춘(`~하시오/~하오` 톤) + 도입부 모용손 [픽션] 카운터파트. 한자 글리프 = 명적(鳴鏑) + 요동성(遼東城) 최소 2건. `docs/characters/` 캐릭터 가이드 역할 추가.
- **회귀 매트릭스 v2 + 시나리오 카탈로그 확장 (DECISION-QA-P4-001~006)**:
  - `docs/qa/regression_matrix.md` v2: AU-01~08 / TU-01~10 / BL-01~07 신규 25건 + Tutorial 모듈 열(총 9 모듈) + 거부권 가이드.
  - `docs/qa/scenario_catalog.md` 확장: CAT-05~07 (튜토리얼 8단계 / 난이도 체감 / 한자 글리프) 추가.
  - `tests/test_regression_p4.py` (신규, 17건): AU-01~06 SoundManager + BL-04/05 무변경 가드 + import guard.
- **스키마 옵션 필드 `night_vision_radius_multiplier`**: `src/data/schema.py` validator 가 0.5~2.0 범위 옵션 필드 허용. stage_03 야간 시야 보정.
- **자동 테스트**:
  - `tests/test_stage_balance.py` (신규, 22건): BL-01~03 / BL-06 자동 가드 — wave 수, count, interval, reward.grain, schema 옵션 필드.
  - 총 `pytest` = **396 passed** (Phase 3.5 종료 시점 334 → +62, 회귀 0).

#### Changed
- **초반 3스테이지 난이도 하향 (Issue #27, DECISION-DT1-P4-001~004)**:
  - `src/data/stages/stage_01.json`: reward.grain 50 → 100 (체감 진입 보상 강화).
  - `src/data/stages/stage_02.json`: wave 6 → 4, W1 count -40%, interval +30%, reward.grain → 150.
  - `src/data/stages/stage_03.json`: wave 6 → 4, W1 단일 path=p_gorge, reward.grain → 220, `night_vision_radius_multiplier` 필드 추가.
  - stage_04~05 무변경 (영향 0 가드 — BL-04/05 ✓).
- `tests/test_stages_02_05.py` / `test_stage_reward_grain.py`: stage_02/03 wave 축소 + reward 조정 반영.
- `docs/story/08_ui_strings.md`: §20 "키 예약" 상태 → "한국어 확정"으로 격상.
- `docs/qa/regression_matrix.md` v2.1 (DECISION-SCM-P4-002): Phase 4 R1 머지 후 TU-01/02/03/05/09/10 + BL-01/02/03/06 시나리오를 ✗ → ✓ 자동 가드로 전환. headless 자동화 불가 항목(TU-04/06/07/08, BL-07) 은 ✗ 유지 + 수동 검수 의존.

#### Decisions (DECISION-SCM-P4-*)
- **001**: PR 머지 순서를 #34(독립) → #37(독립) → #36(튜토리얼 구현, placeholder §20) → #35(한국어 §20) 로 적용. PR #35 한국어 §20이 §20 placeholder 보다 후행 머지되어 한국어 본문 보존 보장.
- **002**: PR #34/#36 머지 후 자동 가드 가능한 시나리오(TU-01/02/03/05/09/10, BL-01~03/06) 를 본 라운드에서 ✓ 전환. 별도 후속 라운드로 분리하지 않음 — Phase 4 R1 종료 시점 매트릭스가 develop 코드 실태와 일치하도록 정합 보정.
- **003**: TU-04/06/07/08 은 tkinter 창·이벤트 루프 의존(headless 자동화 불가) 으로 ✗ 유지. 수동 검수 카탈로그(CAT-05~07) 의존.
- **004**: `v0.3.0` GA 승격(main 머지·태깅) 은 본 SCM 라운드에서 보류. 사용자 시각 검수(CAT-01~07) 완료 후 별도 SCM 라운드에서 수행 — 제약(main 직접 푸시 금지, 새 태그 생성 금지) 준수.

#### Merged PRs
- #34 — feat(balance): stage 01~03 난이도 하향 (squash → develop@0a5351e)
- #37 — qa(phase4): 회귀 매트릭스 v2 + 자동 테스트 보강 (squash → develop@58f482d)
- #36 — feat(phase 4): 인터랙티브 튜토리얼 8단계 구현 (squash → develop@3c5f594)
- #35 — docs(tutorial): §20 ui_strings 35건 한국어 확정 (squash → develop@5c26653)

#### Closed Issues
- #26 인터랙티브 튜토리얼 8단계 (PR #36 자동 close)
- #27 초반 3스테이지 난이도 하향 (PR #34 자동 close)

#### Open Issues (Phase 4 후반 / Phase 5)
- #29 — 오디오 다채널 동시 재생 백엔드 (AU-07 자동화 게이트)
- #30 — Audio asset inventory (오디오 자산 발주)
- #38 — (Phase 4 후반)
- #39 — (Phase 5)

## [0.3.0] - 2026-05-19 — Phase 3 완료

> Phase 3 라운드 (3.1 통합 하드닝 → 3.2 스테이지 데이터 → 3.3 프로토타입 통합 → 3.4 디자인/스토리 + 폰트 번들 → 3.5 수직 슬라이스 + 회귀 매트릭스) 전체 종료. `v0.3.0-rc.1` 사전 릴리즈 후 사용자 시각 검수(CAT-01~04) 통과 시 정식 `v0.3.0` GA 승격 예정 (DECISION-SCM-P3-006).

### Phase 3.5 회귀 매트릭스 + 시나리오 카탈로그 (2026-05-19)

#### Added
- `docs/qa/regression_matrix.md` (신규): Phase 3 누적 회귀 매트릭스 — 메뉴 / 스테이지 선택 / 배틀 / 결과 / 엔딩 5 씬별 자동 가드 매핑
- `docs/qa/scenario_catalog.md` (신규): 사용자 시각 검수 시나리오 카탈로그 CAT-01~04 (메뉴 네비게이션, 스테이지 풀 사이클, 영웅 M키 모드, 폰트 한글 렌더링)
- `tests/test_regression_p3_5.py` (신규, 21건): 회귀 매트릭스 자동 가드 — MN-03~05 메뉴 키보드, BT-01~03 배틀 진입/스폰, RD-01~02 ResultDialog 라우팅, ED-01 엔딩 검출, FT-01 폰트 SSOT, UI-01~02 ui_strings SSOT 키 등

#### Changed (Phase 3 finalize, DECISION-SCM-P3-001)
- `tests/test_regression_p3_5.py::test_menu_enter_key_triggers_goto_for_focused_button`: 회귀 가드 기준을 수직 슬라이스 흐름(메뉴 → 스테이지 선택 → 배틀, PR #24/DECISION-DL-P3-5-002) 에 맞춰 `battle` → `stage_select` 로 갱신. PR #23 작성 시점(수직 슬라이스 미적용)과 PR #24 머지 결과(라우팅 변경) 가 양립 불가하여 SCM finalize 단계에서 보정.


### Phase 3.5 수직 슬라이스 데모 (2026-05-19)

#### Added
- `tests/test_vertical_slice.py` (신규, 18건): 메뉴 → 스테이지 선택 → 배틀 → 결과 → 엔딩 풀 사이클 통합 회귀 가드 (Issue #12)
  - 메뉴 라우팅 (`menu.new_game` / `menu.continue` → `stage_select`) 가드
  - BattleScene 진입 시 영웅(Hero) 자동 등록 검증 (`world["hero"]`)
  - `stage_05` 클리어 시 `ResultDialog._on_next` → ending 라우팅, 그 외 stage → stage_select
  - 패배 시 ResultDialog 모든 콜백이 stage_select 로 회귀
  - UI 문자열 SSOT 키 존재 검증 (menu / stage_select / battle / ending)
  - `main._register_scenes` 4 씬 모두 등록 (회귀 가드)
  - stage_01 전 wave force_advance 무예외 통과
- `BattleScene._compute_hero_spawn_xy()`: build_zone 기반 영웅 스폰 좌표 헬퍼 (DECISION-DL-P3-5-003)
- `BattleScene._UI_STRINGS_DEFAULT["battle.placeholder.intro"]`: SSOT 진입 안내 텍스트 (DECISION-DL-P3-5-005)

#### Changed
- `src/scenes/menu_scene.py`: "새 게임" / "이어하기" 버튼 라우팅 `battle` → `stage_select` (수직 슬라이스 흐름, DECISION-DL-P3-5-002)
- `src/scenes/battle_scene.py`:
  - `build()` 에서 영웅(Hero) 인스턴스를 자동 생성하여 `world["hero"]` 에 등록 — 기존에는 외부에서 주입되지 않아 패배 조건 및 M키 모드가 사실상 비활성 (DECISION-DL-P3-5-003)
  - `_end_battle()`: 승리 + `stage_05` 인 경우 "다음" 버튼이 ending 으로 라우팅, 그 외에는 기존대로 stage_select (DECISION-DL-P3-5-004)
  - 좌하단 manual_mode 라벨 폰트 하드코딩 `"Malgun Gothic"` → `family_regular()` SSOT 적용
  - 전투 진입 안내 텍스트를 raw 한국어에서 `_UI_STRINGS_DEFAULT` 키로 분리

#### Verified
- PyInstaller `--onefile` 로컬 빌드 성공 (Windows, 24.9 MB, `dist/AnsiseongDefense.exe`)
- `pyi-archive_viewer` 로 `assets/fonts/NotoSansKR-Regular.otf` + `NotoSansKR-Bold.otf` 가 .exe 내부에 포함됨 확인
- 전체 회귀 `pytest`: 295 + 18 = **313 passed** (실패 0)

#### Decisions (DECISION-DL-P3-5-*)
- **001**: Stage 1 wave 수는 사양(3 wave) 그대로 유지. acceptance criteria 의 "6 wave" 문구는 stage_02 이후의 사양이므로 stage_01 검수에는 "모든 wave (3 wave) 완주" 로 적용.
- **002**: 메뉴의 "새 게임" / "이어하기" 도 `stage_select` 경유로 일관화 (수직 슬라이스 흐름).
- **003**: BattleScene 진입 시 영웅을 build_zone 첫 zone 중앙(없으면 화면 중앙) 에 자동 스폰.
- **004**: 승리 분기는 `stage_id == "stage_05"` 만 ending 으로, 그 외는 stage_select. 단일 stage 검수에서도 stage_05 직접 진입 시 엔딩 도달 가능.
- **005**: 배틀 placeholder 텍스트와 manual_mode 라벨을 SSOT 키 기반으로 정리.
- **006**: PyInstaller 빌드는 본 PR 에서 로컬 검증 완료, 정식 산출물 발행은 SCM 라운드 (`v0.3.0-rc.1` 태깅 + GitHub Actions `build-windows.yml` / `release-windows.yml`) 로 위임.

#### Closed Issues
- #12 수직 슬라이스 데모 + `v0.3.0-rc.1` 준비 (DECISION-DL-P3-5-002/003/004)

### Phase 3.3 프로토타입 통합 (2026-05-19)

#### Added
- `src/scenes/battle_scene.py`: `_spawn_enemy()` stage waypoint 첫 좌표 결선 — `path[0]` 사용 + 빈 path 가드 + 적 인스턴스에 전체 waypoints 주입 (Issue #1 / DECISION-Q-010)
- M키 영웅 수동 조작 모드 (toggle: M, WASD/방향키 이동, 자동 사거리 추격 일시 정지) (Issue #4 / DECISION-Q-009)
- `tests/test_battle_spawn.py` (신규, 7건): spawn 좌표·waypoint 주입 회귀 방지
- `tests/test_hero_manual_mode.py` (신규, 7건): toggle 멱등성, 이동 dt, 모드 라벨, 자동 사거리 중단 검증
- `docs/story/08_ui_strings.md` v1.2: M키 모드 UI 문자열 4건 (battle.hero_mode.{auto,manual,toggle,prompt})

#### Fixed
- **Phase 2 잠재 결함 동반 수정**: `Enemy` 생성자 시그니처 불일치(BattleScene이 보내던 인자 vs 실제 정의), `waypoints` 미설정으로 `pathing.update` 첫 프레임 실패 — 두 결함은 Phase 2 기본 path 한 종(stage_01) 환경에서는 노출되지 않다가 Phase 3.2 신규 stage 도입과 함께 재현됨

#### Closed Issues
- #1 BattleScene `_spawn_enemy` stage waypoint 첫 좌표 참조 (DECISION-Q-010)
- #4 영웅 M키 직접 조작 모드 상세 명세 (DECISION-Q-009)

### Phase 3.2 스테이지 데이터 (2026-05-19)

#### Added
- `src/data/stages/stage_02.json` 요동성 외곽 — 보병/궁수 혼합 6 wave (Issue #11)
- `src/data/stages/stage_03.json` 백암성 — 기병 돌격 도입 7 wave
- `src/data/stages/stage_04.json` 개모성 — 공성병기(투석거·충차) 도입 8 wave
- `src/data/stages/stage_05.json` 안시성 외곽 — 보스 wave + 다중 lane 9 wave (토산 스테이지는 6.x 결전용으로 잠정 분리)
- `tests/test_stages_02_05.py` (신규, 40건): 각 스테이지별 schema validity / wave 합산 / reward.grain / unlock chain / 적 type 사전조건

#### Closed Issues
- #11 stages 02~05 JSON 작성 (DECISION-DL-P3-001 스키마 가드)

### Phase 3.4 폰트 번들링 (2026-05-19)

#### Added
- `assets/fonts/NotoSansKR-Regular.otf` (~4.4MB), `NotoSansKR-Bold.otf` (~4.6MB), `OFL.txt` 동봉 (Issue #7 / DECISION-Q-007)
- `src/core/fonts.py` (신규): 런타임 폰트 해석 + Win32 `AddFontResourceExW` 프로세스-한정 등록 + Malgun Gothic 폴백. `family_regular() / family_bold() / font_tuple()` 공개 API
- `AnsiseongDefense.spec` (신규): PyInstaller spec — `datas=[("assets/fonts", "assets/fonts")]` SSOT 관리, `--onefile` 형식 유지 (DECISION-DESIGN-P3-4-001)
- `tests/test_fonts_runtime.py` (신규): 14건 — `_MEIPASS` 경로 분기, 폴백 정책, idempotent 등록 회귀 방지
- CI 워크플로 `build-windows.yml / release-windows.yml`: 빌드 후 `PyInstaller.utils.cliutils.archive_viewer` 로 .exe 내부 폰트 포함 검증 step
- README "라이선스" 섹션: 동봉 자산 목록 + SIL OFL 1.1 명시

#### Changed
- `src/core/app.py`: 부팅 시 `register_korean_fonts(root)` 호출 — 1회 등록·캐시
- `src/ui/{widgets,hud,dialog}.py`, `src/scenes/{menu,stage_select,battle,ending}_scene.py`: 하드코딩 `"Malgun Gothic"` → `family_regular()/family_bold()` 동적 해석으로 치환 (총 11개 위치)
- `.gitignore`: `*.spec` 무시는 유지하되 `!AnsiseongDefense.spec` 예외 추가

#### Closed Issues
- #7 Noto Sans KR(OFL) PyInstaller 번들링 구성

#### Decisions (Phase 3.4)
- DECISION-DESIGN-P3-4-001 — spec 파일 단일 SSOT, 워크플로는 spec 우선 + `--add-data` 폴백
- DECISION-DESIGN-P3-4-002 — `--onefile` 유지(콜드 스타트 ↑ 대신 운영 단순성). 자산 누적 시 onedir 재검토
- DECISION-DESIGN-P3-4-003 — Regular + Bold 둘 다 번들(시각 품질 우선, 디스크 +5MB는 허용 범위). 추가 weight(Light/Medium 등)는 보류

### Phase 3.1 통합 하드닝 (2026-05-19)

#### Added
- `stage_01.json` `reward.grain: 50` 데이터 패치 (Issue #2 / DECISION-Q-011)
- `StageReward` dataclass 도입 (`src/data/loader.py`): `gold/grain/unlock` 타입 필드, 기본값 0 비파괴
- `scripts/check_systems_no_tk.py` (신규, AST 기반): `src/systems/` 도메인 계층 tkinter import 금지 가드. `TYPE_CHECKING` 가드 내 import는 허용 (DECISION-T1-P3-001)
- CI `ci.yml`: grep + AST 이중 방어선 step 추가 (Issue #8 / DECISION-4.1)
- `src/data/schema.py` (신규, 427줄): stdlib-only stage JSON schema validator. `validate_stage / validate_units / validate_enemies` + `StageSchemaError` (Issue #10 / DECISION-DL-P3-001)
- 테스트 +62건: `test_stage_reward_grain` (11), `test_systems_no_tk` (18), `test_stage_schema` (33). pytest **195 passed**
- 문서: `docs/04_technical_architecture.md` §5.4 schema policy, CI tk-free 가드 현황 주석

#### Changed
- `src/data/loader.py`: schema validation 호출 추가 + `__all__` 정비. `StageDef.reward` 타입 `dict → StageReward`
- `src/scenes/battle_scene.py`: `stage.reward.grain` 직접 접근으로 단순화

### Phase 3.4 디자인/스토리 적용 — 일부 (2026-05-19)

#### Added
- `docs/assets/placeholders/character_placeholders.md` (신규, 374줄): 5개 주요 캐릭터 플레이스홀더 (양만춘/연개소문/이세민/이도종/유백영) (Issue #6)
- `docs/assets/placeholders/README.md` (신규): 플레이스홀더 운영 정책

#### Changed
- `docs/story/08_ui_strings.md` v1.0 → **v1.1 SSOT 격상** (Issue #5 / DECISION-D-P3-001 ~ 001c): 키 네이밍 컨벤션 `<scene>.<component>.<role>` 명문화, 신규 UI 키 10건 추가 (cavalry.sortie, dialog.next/skip, intro.skip_confirm, help.tut1~6.*)
- `docs/07_wireframes_visuals.md`: 픽션·승인대기 → 픽션 라벨 정리 (7건, DECISION-SCM-P3-001)

### CI / Workflow

#### Added
- `docs/06_ci_release_workflow.md`: prerelease 감지 정책 명문화 (Issue #9)
- prerelease 태그 regex 단위 테스트 23건
- `release-windows.yml`: SemVer pre-release suffix 기반 prerelease 자동 감지

### Closed Issues (누적)
- #1 BattleScene `_spawn_enemy` stage waypoint 첫 좌표 참조
- #2 reward.grain 데이터 패치
- #4 영웅 M키 직접 조작 모드 상세 명세
- #5 UI strings SSOT v1.1
- #6 캐릭터 플레이스홀더 5종
- #7 Noto Sans KR(OFL) PyInstaller 번들링
- #8 src/systems tkinter import 금지 CI 가드
- #9 prerelease 감지 정책
- #10 stage JSON schema validator
- #11 stages 02~05 JSON 작성

### Decisions (Phase 3)
- DECISION-T1-P3-001 (TYPE_CHECKING import 예외), DECISION-DL-P3-001 (stdlib-only validator), DECISION-D-P3-001 / 001a / 001b / 001c (UI strings SSOT + 컨벤션 + 신규 키 + 표 형식), DECISION-SCM-P3-001 (회수 4파일 한정 픽션 라벨 일괄 치환), DECISION-SCM-P3-002 (변경분 외 일괄 치환 보류)
- DECISION-Q-009 (M키 수동 모드 상세 명세 — toggle 멱등, 자동 모드 사거리 추격 일시 정지), DECISION-Q-010 (waypoint 첫 좌표 결선 + waypoints 주입)
- DECISION-SCM-P3-003 (Phase 3.2 → 3.3 → 3.4 순차 squash 머지, 데이터 우선 → 코드 결선 → 자산 독립 순), DECISION-SCM-P3-004 (Phase 3.5 종료 시까지 main/`v0.3.0` 태깅 금지)

### Notes
- Phase 3.1 / 3.2 / 3.3 / 3.4 통합 완료. 잔여는 Phase 3.5 수직 슬라이스 데모(Stage 1 전 구간 playable + 사용자 검수) + `v0.3.0-rc.1` (Issue #12)
- pytest 합계 **295 passed** (Phase 2 종료 시 139 → +156)
- main 브랜치 머지 및 `v0.3.0` 태깅은 Phase 3 전체 종료 시 수행

## [0.2.0] - 2026-05-19 — Phase 2 완료

### Added
- 스토리 산출물 `docs/story/00~09` (story bible / intro / 5 stage scripts / 2 endings / ui_strings / codex)
- 디자인 산출물 `docs/07_wireframes_visuals.md` (9 화면, 1757줄), `docs/08_asset_inventory.md` (759줄), `docs/09_animation_state_diagrams.md` (1176줄)
- 코어 엔진 `src/main.py`, `src/core/{app,game_loop,scaler,assets,events,settings,logger,sound}.py`
- 엔티티 본구현 `src/entities/{entity(ObjectPool, PoolExhausted), hero(4 페이즈+ultimate), ally(targeting), enemy(fade), projectile(swept-segment), effect}.py`
- 시스템 본구현 `src/systems/{combat.update, pathing.update, wave.update, economy, input}.py`
- UI/씬 `src/ui/{widgets, hud, dialog}.py`, `src/scenes/{menu, stage_select, battle, ending}_scene.py`
- 데이터 로더 + stage_01 `src/data/loader.py`, `src/data/{units.json, enemies.json, stages/stage_01.json}`
- 테스트 49건 추가(scaler/pathing/economy/object_pool/hero_phases/enemy_fade/projectile/combat_pathing_integration/wave_system/wave_schedule_load/hud_state_model/dialog_state/battle_scene_flow), pytest **139 passed / 0 failed**
- QA 리뷰 `docs/qa/phase2_review.md`, `docs/qa/phase2_decisions.md` (DECISION-Q-001~011)

### Changed
- `src/entities/entity.py` ObjectPool 스텁 → 본구현(capacity 가드 + PoolExhausted + headless 동작)

### Decisions (PM/Design/Dev/QA)
- DECISION-S03/5B/E03 (스토리), DECISION-D-001~210 (디자인 50+), DECISION-T1/T2 (구현), DECISION-Q-001~011 (OPEN 종결: 픽션 캐릭터 승인, ui_strings SSOT, 사운드 winsound, 폰트 Noto Sans KR(OFL) + Malgun Gothic 폴백)

### Notes
- tkinter 의존 없는 도메인 계층(`src/systems/*`, `src/entities/*`) 보장(CI 회귀 방지 권고)
- M키 영웅 직접 조작은 플래그만, 상세 명세 Phase 3 이슈로 분리

## [0.1.0] - 2026-05-17 — Phase 1 완료

### Added
- 역사 자료 조사 문서 (`docs/01_history_research.md`)
- 게임 컨셉 브리프 (`docs/02_concept_brief.md`)
- 게임 디자인 문서 (`docs/03_game_design_document.md`)
- 기술 아키텍처 문서 (`docs/04_technical_architecture.md`)
- 형상관리 / 브랜칭·릴리즈 전략 문서 (`docs/05_branching_release_strategy.md`)
- CI / 릴리즈 워크플로 설계 문서 (`docs/06_ci_release_workflow.md`)
- 프로젝트 루트 `README.md` (한국어, Phase 1 기준)
- `CHANGELOG.md` (Keep a Changelog 포맷)
- `.gitignore` (Python / 빌드 / IDE / OS / 시크릿 규칙)
- GitHub 협업 자산
  - `.github/pull_request_template.md`
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/CODEOWNERS` (전체 파일 SCM 승인 필요)
- GitHub Actions 워크플로
  - `.github/workflows/ci.yml` (Ubuntu + Windows 매트릭스, lint + pytest, 가드 포함)
  - `.github/workflows/build-windows.yml` (`release/win64/dev` 푸시 시 PyInstaller 빌드 + artifact)
  - `.github/workflows/release-windows.yml` (`release/win64/prd` 푸시 / `v*` 태그 시 빌드 + GitHub Release 자동 생성 + .exe 첨부)
- 브랜치 체계: `main`, `develop`, `release/win64/dev`, `release/win64/prd`

### Notes
- 본 버전은 사전 기획·인프라 단계로, 실행 가능한 게임 코드는 아직 포함하지 않습니다.
- 라이선스는 미정이며 추후 결정합니다.

[Unreleased]: https://github.com/genishs/simplegame-defencegame/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/genishs/simplegame-defencegame/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/genishs/simplegame-defencegame/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/genishs/simplegame-defencegame/releases/tag/v0.1.0
