# Changelog

이 문서는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)을 따르며, 버전 관리는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)을 따릅니다.

## [Unreleased]

> Phase 5 진입 라운드 누적. Phase 5.1 BGM 통합 본 작업(`src/core/sound.py` 백엔드 + `tests/test_sound_bgm.py`) 시작 시 본 섹션에 항목 누적. 중간 마이너 태그(v0.5.0/v0.6.0) 도입 여부는 OPEN-PL-P5-006 (Steering 후속). Phase 5 종료 시점에 `v1.0.0-rc.1` → `v1.0.0` 로 변환.

### Fixed (게임플레이 인터랙션 4건 종합 — Issue #55/#56/#57/#58, DECISION-DL-P4D-007/008/009)

v0.4.0-rc.4 사용자 검수에서 발견된 게임플레이 인터랙션 결함 4건을 한 PR 로 종합 fix. 모두 동일한 근본 원인 — BL-07 시뮬레이터(systems 직접 호출)는 통과하지만 실 BattleScene/UI 인터랙션이 결여되어 사용자가 게임을 진행할 수 없는 현상.

- **Issue #58 / DECISION-DL-P4D-007**: 영웅 양만춘 평타 자동 공격 미구현 — GDD §3.1 사양(atk 35 / range 380px / 1.0/s)이 정의만 되어 있고 실행 코드 없음. `Hero.auto_attack(enemies)` / `find_target_in_range` 신규 추가. BattleScene 이 매 틱 호출 → Projectile 스폰 → CombatSystem 명중 처리. 자동·수동 모드 모두에서 발사 트리거 (수동 모드도 적과 전투 가능, Issue #58 사용자 보고). 발사체 스폰은 BattleScene 책임으로 도메인 가드 (src/entities tkinter-free) 유지.
- **Issue #57 / DECISION-DL-P4D-007**: 영웅이 무반응 상태 — Hero.update 가 페이즈/궁극기 쿨다운만 처리하고 적 타겟팅·발사가 없었음. 위 #58 fix 가 본 결함도 동시 해결.
- **Issue #56 / DECISION-DL-P4D-008**: 아군 유닛 배치 UI 부재 — BattleScene 에 유닛 선택 패널·build_zone 클릭 핸들러·곡식 차감 로직 신규 추가. 좌하단 패널에 units.json 의 가용 유닛 표시(이름·곡식 비용), 선택 → build_zone 클릭 → Ally 가 world['allies'] 에 추가. 곡식 부족·zone 점유 시 안내 텍스트 갱신.
- **Issue #55 / DECISION-DL-P4D-009**: 튜토리얼 단계 2·3 spotlight 클릭 미반응 — mock placeholder/spotlight ring 에 클릭 핸들러가 binding 안 됐음. 단계 2(resource)·단계 3(buildzone) 의 mock content/ring 에 `trigger_step2_done`/`trigger_step3_done` binding. 단일 텍스트 클릭 좁은 hit area 우회용으로 spotlight 영역에 투명 hit-area 사각형 추가.

### Added

- `tests/test_gameplay_interaction_overhaul.py` (신규, 18 케이스):
  - Hero 평타 7케이스 (auto_attack/find_target_in_range/cooldown/empty list/manual mode 발사).
  - BattleScene 배치 UI 5케이스 (units_db 로드/토글/배치/점유/곡식 부족).
  - Tutorial spotlight 클릭 4케이스 (step 2/3 binding/handler 존재/step 5 핸들러 없음).
  - hero update tick 2케이스 (수동 모드 cooldown 유지 회귀).

### Changed

- `src/entities/hero.py`: `_atk_cooldown` / `target` 필드 + `auto_attack` / `find_target_in_range` / `atk_cooldown` 프로퍼티 신규.
- `src/scenes/battle_scene.py`: `_tick_hero_attack` / `_on_build_zone_click` / `_on_unit_button_click` / `_draw_unit_selection_panel` / `_draw_placement_hint` 헬퍼 + `_units_db`·`_selected_unit_id`·`_build_zone_occupants` state 신규. 수동 모드도 hero.update 호출 (평타 쿨다운 진행).
- `src/scenes/tutorial_scene.py`: `_bind_spotlight_click` + mock content 각 아이템에 클릭 binding. 단계 진입 시 `_spotlight_click_handler` 사전 설정.
- `tests/test_hero_manual_mode.py`: `test_manual_mode_skips_hero_auto_update` → `test_manual_mode_still_ticks_hero_cooldowns` (Issue #58 정책 갱신 반영).
- pytest 누적 **472 → 490** (+18 회귀 가드, 회귀 0).

### Decisions

- **DECISION-DL-P4D-007**: 영웅 평타 자동 공격을 Hero 도메인(tkinter-free) 으로 구현, 발사체 스폰은 BattleScene 가 위임 받음. 자동·수동 모드 모두 평타 트리거 (GDD §3.1 사양 일치).
- **DECISION-DL-P4D-008**: 유닛 배치 UI를 BattleScene 직접 구현 (별도 widget 클래스 미사용 — Phase 4 인지부하 최소 원칙 유지). units.json 의 cost 가 곡식 비용. 한 zone 당 1 유닛 정책.
- **DECISION-DL-P4D-009**: Tutorial spotlight 클릭 영역을 mock content + 투명 hit-area 사각형 + ring fill 3중으로 binding. 작은 텍스트 hit area 미스를 회피.

### Follow-up 권장 (별도 issue)

- BL-07 시뮬레이터에 BattleScene 의 영웅 평타 + 배치 UI 호출을 통합 (현재 시뮬레이터는 ally 자동 배치 + 영웅 비활성). Phase 5 cleanup 라운드 후보.
- 본 PR 의 영웅 평타는 GDD 의 S1/S2/S3 스킬 미구현 — 현재 평타와 궁극기만 작동. 스킬 시스템은 Phase 5 후속 작업.
- HUD 상단 곡식 아이콘과 좌하단 유닛 선택 패널을 SCN-05 디자인 와이어프레임과 통합 (DESIGN 라운드).

## [0.4.0-rc.4] - 2026-05-20 — v0.4.0-rc.3 검수 결함 fix RC (.exe 재검수 대기)

> 사용자 .exe 검수(Issue #53) 결함 fix RC. develop@d5b5797(PR #54 머지 시점). release-windows.yml prerelease=true 자동 트리거 + PyInstaller .exe 재빌드. 메인 세션이 rc.2/rc.3 패턴(DECISION-SCM-P5K-003/004) 재사용으로 처리.
>
> v0.4.0 정식 GA 진입 조건: CAT-01~07 + DPI 매트릭스 모두 통과 후 별도 SCM 라운드.

### Fixed
- **Issue #53 (PR #54, DECISION-DL-P4D-006)**: v0.4.0-rc.3 사용자 검수 결함 3호 fix — "stage1 진입은 하는데 전투시작이 안돼" (영웅·적 모두 안 보임). 충격적 원인: **`BattleScene.render()`가 Phase 3.5부터 `pass` 한 줄**이었음. systems(wave/pathing/combat)가 정상 동작해 메모리에서는 spawn·이동·전투가 진행됐지만 캔버스에 한 번도 그려진 적 없음. BL-07 시뮬레이터는 systems만 직접 호출하므로 자동 가드가 결함을 잡지 못했음 (실 게임 ↔ 자동 가드 정합 빈약):
  - `src/scenes/battle_scene.py`: `render()` 정식 구현 + 헬퍼 5개(`_render_hero/_ally/_enemy/_projectile/_effect`).
  - `_known_canvas_items` set으로 stale canvas 정리, churn 회피.
  - `scaler.to_screen` 좌표 변환으로 base↔screen 정합.
  - entity.draw()는 no-op 유지 (도메인 가드 src/entities tkinter-free 보존).

### Added
- `tests/test_battle_scene_entities_render.py` (신규, 8건): 영웅 렌더 / 적 렌더 / wave 진행+render 통합 / render 멱등성 / 사망 후 canvas 정리 / 좌표 정합 / 멀티 엔티티 / App._tick(update+render) 사슬 모사.

### Changed
- pytest 누적 **464 → 472** (+8 회귀 가드, 회귀 0).

### Decisions
- **DECISION-SCM-P5K-005**: v0.4.0-rc.4 발급 (rc.2/rc.3 패턴 재사용). 메인 세션이 PR #54 머지 + CHANGELOG/README 변환 + 태그 push + 로컬 .exe 재빌드까지 직접 처리.

### Follow-up 권장 (별도 issue)
- BL-07 시뮬레이터에 render 호출을 통합하면 동종 결함(render 누락)을 차후 자동 차단 가능. Phase 5 cleanup 라운드 후보.

## [0.4.0-rc.3] - 2026-05-20 — v0.4.0-rc.2 검수 결함 fix RC (.exe 재검수 대기)

> 사용자 .exe 검수(Issue #51) 결함 fix RC. 핵심 원인은 PyInstaller spec `datas` 에 `src/data/` 디렉터리 누락이라 **rc.1·rc.2 .exe 모두 동일 결함을 가졌음**(개발 모드는 정상). develop@9827245(PR #52 머지 시점). release-windows.yml prerelease=true 자동 트리거 + PyInstaller .exe 재빌드. 메인 세션이 rc.2 패턴(DECISION-SCM-P5K-003) 재사용으로 처리.
>
> v0.4.0 정식 GA 진입 조건: CAT-01~07 + DPI 매트릭스 모두 통과 후 별도 SCM 라운드.

### Fixed
- **Issue #51 (PR #52, DECISION-DL-P4D-003~005)**: v0.4.0-rc.2 사용자 검수 결함 2호 fix — "튜토리얼 끝나고 stage01에서 더이상 동작하지 않아" (frozen). 원인은 **PyInstaller spec 의 `datas` 에 `src/data/` JSON 자원이 누락**되어 .exe 실행 시 `load_stage("stage_01")` 가 FileNotFoundError → `BattleScene.stage = None` → `update()` 매 tick early return → 사용자에게 frozen 으로 보이는 현상. 3중 보강:
  - `AnsiseongDefense.spec`: `src/data` 디렉토리를 `datas` 에 추가 (stage_*.json, enemies.json, units.json 번들).
  - `src/core/settings.py`: `resolve_data_root()` 헬퍼 신규 — PyInstaller `sys._MEIPASS` 환경 우선 해석, 개발 모드 폴백.
  - `src/scenes/battle_scene.py`: stage 로드 실패 시 frozen 대신 사용자에게 시각적 에러 placeholder 표시.
  - `src/core/app.py`: `_tick()` silent catch 보강 — 동일 예외 연속 3회 이상 시 캔버스에 에러 배너 1회 표시, 정상 tick 복귀 시 자동 클리어 (DECISION-DL-P4D-005).

### Added
- `tests/test_tutorial_to_battle_routing.py` (신규, 11 케이스): 튜토리얼 종료 → stage_select → BattleScene 진입 사슬 회귀 가드.
- `tests/test_battle_scene_flow.py`: FakeCanvas 확장.

### Changed
- pytest 누적 **453 → 464** (+11 회귀 가드, 회귀 0).

### Decisions
- **DECISION-SCM-P5K-004**: v0.4.0-rc.3 발급 (rc.2 패턴 재사용). 메인 세션이 PR #52 squash 머지 + 태그 push + 로컬 .exe 재빌드까지 직접 처리. CHANGELOG/README 정합 commit은 태그 push 후 보강.

## [0.4.0-rc.2] - 2026-05-20 — v0.4.0-rc.1 검수 결함 fix RC (.exe 재검수 대기)

> 사용자 직접 요청("실행프로그램을 만들어줘")으로 v0.4.0-rc.2 발급. v0.4.0-rc.1 사용자 검수(CAT-05) 진행 중 발견된 튜토리얼 spotlight 결함 fix를 별도 RC로 출시하여 .exe 재검수 가능하도록 함. develop@18bb4a5(태그 시점 기준). release-windows.yml prerelease=true 자동 트리거 + PyInstaller .exe 재빌드.
>
> v0.4.0 정식 GA 진입 조건: CAT-01~07 + DPI 매트릭스 모두 통과 후 별도 SCM 라운드.

### Fixed
- **Issue #49 (PR #50, DECISION-DL-P4D-001~002)**: TutorialScene spotlight 동그라미가 가리키는 위치에 실제 HUD 콘텐츠 부재 → mock HUD placeholder 직접 렌더 (곡식 100 / buildzone "?" / hero "楊" / pause 아이콘). Canvas z-order 명시: mask → mock content → ring → arrow → label.

### Changed
- 회귀 매트릭스 v2.3 → v2.4 — TU-11 시나리오 신규 (총 69)
- pytest 누적 448 → 453 (+5 회귀 가드, 회귀 0)

### Decisions
- **DECISION-SCM-P5K-003**: v0.4.0-rc.2 발급 (옵션 A 정석 채택 — RC2 → .exe 재검수 → v0.4.0 GA). 메인 세션이 사용자 직접 요청 + 단일 태그 작업으로 처리, SCM 라운드 spawn 비용 절약. 비가역 작업 위임 사례 — 향후 동일 패턴(사용자 직접 명시 + 단순 태그) 시 메인 세션 처리 허용 (DECISION-SCM-P4F-002 정신과 정합).

## [0.4.0-rc.1] - 2026-05-19 — Phase 4 자동 가드 완결 (RC, 사용자 검수 대기)

> Phase 4 (기능 테스트 + 디버깅 + 버그픽스 + 튜토리얼/난이도/QA v2 + SFX 백엔드 + 클리어율 자동화 + 잠재 결함 해결) 자동 가드 완결 시점. 메모리 규칙(0.x.0 = Phase x 완료) 정합. 사용자 시각 검수(CAT-01~07) + DPI 매트릭스(1920×1080·100%/125%) 통과 시 별도 SCM 라운드에서 `v0.4.0` 정식 GA 승격 (DECISION-SCM-P5K-001).
>
> 본 RC는 Phase 4 R1+R2+R3 + Phase 5 kickoff(PR #47) + Phase 5.1 BGM prep(PR #48) 누적. develop@8e9c3de. pytest **448 passed**, ruff/black 0 에러.
>
> Phase 5 kickoff 산출물(PR #47/#48)은 Phase 5 본 작업 진입 직전 문서·placeholder만 포함 — 코드(.py) 도메인 영역 무변경. 따라서 RC에 안전하게 합산.

### Phase 5 Kickoff — Planning Lead 명세 + Audio Engineer BGM prep (PR #47/#48, 2026-05-19)

#### Added (Planning, PR #47)
- `docs/14_phase5_plan.md` (신규, 326줄): Phase 5 (전체 스토리 통합 + 최종 완성 + 패키징/릴리즈 1.0.0) 운영 계획서 — 4 sub-phase 분할 (5.1 BGM / 5.2 스토리 / 5.3 자산 / 5.4 패키징), acceptance criteria + DECISION-PL-P5-001~006 + OPEN-PL-P5-001~006
- `docs/phase5/checklist.md` (신규): 각 라운드별 1줄 체크박스 추적
- README "현재 진행 상태" + "다음 단계" 갱신: Phase 5 진행 중 (🚧) 표시

#### Added (Audio prep, PR #48)
- `docs/audio/02_bgm_candidates.md` (신규, 247줄): BGM 후보 8건 (CC0 ×4 + CC BY 4.0 ×4, 동양풍 우선, 번들 ~18.2MB)
- `docs/audio/03_bgm_backend_proposal.md` (신규, 188줄): pygame.mixer vs simpleaudio vs PyOgg 비교, **pygame.mixer 채택** (DECISION-AUDIO-013)
- `assets/audio/bgm/` 신규 — 무음 30초 WAV placeholder 8건 (bgm.intro/menu/tutorial/stage_01_02/stage_03_04/stage_05/victory/defeat) + 라이선스 정책 README
- `src/core/sound.py`: `play_bgm()` docstring 보강 — Phase 5.1 예정 시그니처 (`play_bgm(name, *, loop, fade_in)`, `stop_bgm(*, fade_out)`, `set_bgm_volume(v)`)
- `docs/audio/01_asset_inventory.md`: BGM 섹션 후보 8건 매핑 갱신 (dot-notation 통일, 저작자/우선순위 열 추가)
- `docs/qa/regression_matrix.md`: v2.3 갱신, BG-01~BG-04 시나리오 등록 (총 68건, 자동화 대기)

#### Changed (SCM 정정 라운드, DECISION-SCM-P5K-001)
- `docs/14_phase5_plan.md`: 버전 매핑을 메모리 규칙(0.x.0=Phase x 완료, 1.0.0=Phase 5 완료)에 정합하도록 정정. 초기 plan은 v0.4.0/v0.5.0을 Phase 5 sub-phase에 할당하여 규칙 위반 → Phase 4 = v0.4.0-rc.1, Phase 5 = v1.0.0-rc.1 → v1.0.0 직행으로 정정
- `docs/phase5/checklist.md`: sub-phase 헤더에서 마이너 태그 매핑 제거, develop 누적 명시. 중간 마이너 도입 여부는 OPEN-PL-P5-006 (신규)
- README "다음 단계": Phase 4 종료 v0.4.0-rc.1 발급 명시, Phase 5 매핑 정정

#### Decisions (PR #47 + SCM 정정)
- DECISION-PL-P5-001 (정정): Phase 4 종료 = v0.4.0-rc.1 → v0.4.0, Phase 5 종료 = v1.0.0-rc.1 → v1.0.0
- DECISION-PL-P5-002~006: 픽션 일러스트 옵션 B / Localization Engineer 보류 / Windows 코드 서명 미적용 / Linux CI 추가, macOS 보류 / Release Engineer 보류
- DECISION-AUDIO-013 (PR #48): BGM 백엔드 pygame.mixer 채택
- DECISION-AUDIO-014 (PR #48): 우선순위 '상' 5건 Phase 5.1 수급, '중' 3건 Phase 5.2 이후
- **DECISION-SCM-P5K-001 (본 RC 라운드)**: PR #47 버전 매핑 정정 commit을 PR #47 브랜치에 직접 push 후 squash 머지(별도 정정 PR 신설 회피). 메모리 규칙 정합 우선

#### Merged PRs (Phase 5 kickoff)
- #47 — docs(phase 5 kickoff): Phase 5 명세 + checklist + README 갱신 (squash → develop@8e9c3de)
- #48 — feat(audio): Phase 5.1 BGM prep — 후보 조사 + placeholder + 백엔드 제안 (Issue #30) (squash → develop@621ba21)

#### Open Issues (Phase 5 위임)
- #30 — Audio asset inventory (BGM 자산 발주 — Phase 5.1 본 작업)

### Phase 4 R3 — 정리 라운드 (2026-05-19, DECISION-SCM-P4F-001~002)

> Phase 4 종료 라운드. PR #45(QA cleanup) + PR #46(잠재 결함 #43/#44 정식 해결) 통합 머지 완료. develop@6e108a4.
> `v0.3.0` GA 승격은 여전히 보류 — 사용자 시각 검수(CAT-01~07) + DPI 매트릭스(1920×1080·100%/125%) 통과 후 별도 SCM 라운드(DECISION-SCM-P4-004 유지).

#### Added
- **WaveSystem boss path 다단 fallback (Issue #43, PR #46, DECISION-DL-P5P-001)**:
  - `WaveDef.boss_path` 옵션 필드 추가 + schema validator 갱신
  - `WaveSystem._resolve_boss_path()` 우선순위: `wave.boss_path` → `spawns[0].path` → `load(paths=)` 첫 path → `world['waypoints']` 첫 키 → `"p_main"` 호환 fallback
  - stage JSON 무변경 — stage_03/04/05 보스 wave 자동 해결
  - `tests/test_wave_boss_path.py` (13건): WV-01~05 회귀 매트릭스 자동 가드
- **Projectile swept-circle 충돌 (Issue #44, PR #46, DECISION-DL-P5P-002)**:
  - `Projectile.update`: 발사체 segment + 타겟 segment 동기 swept-circle 최단거리 판정
  - `PathingSystem.update`: enemy `_prev_x/_prev_y` 매 틱 갱신
  - hit_radius=12 유지 — 게임플레이 균형 영향 0
  - `tests/test_combat_sweep.py` (11건): CB-01~05 회귀 매트릭스 자동 가드
- **pytest markers 일관 적용 (PR #45, DECISION-QA-P4M-001~003)**:
  - `tests/test_regression_p4.py`, `tests/test_clear_rate_simulation.py`, `tests/test_sound_simpleaudio.py`, `tests/test_tutorial_scene.py`, `tests/test_stage_balance.py` 5건에 `regression_p4`/`slow`/`audio` 일관 적용
  - 신규 테스트 `tests/test_wave_boss_path.py`, `tests/test_combat_sweep.py`도 `regression_p4` 적용 (SCM 후속 보완)
  - `.github/workflows/ci.yml` 3-step 분리: fast(`-m "not slow"`) → audio(`-m audio`) → full
- **v0.3.0 GA 체크리스트 발행 (PR #45)**: `docs/qa/v0_3_0_ga_checklist.md` — 자동 가드 8/8 ✓ + 사용자 검수 0/7 ☐ + DPI 0/2 ☐. 사용자 복귀 시 검수 후 ☐→✓ 전환 절차 명시
- **Phase 4 종료 보고서**: `docs/qa/phase4_completion_report.md` — R1/R2/R3 산출물 종합

#### Changed
- 회귀 매트릭스 v2.2 → v2.3: WV-01~05 + CB-01~05 신규 등록 (55→64 시나리오), markers 표 갱신
- pytest 누적 **448 passed** (Phase 4 R2 종료 시점 424 → +24, 회귀 0). `-m slow` 별도 시 BL-07 5/5 통과

#### Fixed
- Issue #43: WaveSystem 보스 path_id `"p_main"` 하드코딩 → 다단 fallback (BL-07 시뮬레이터 workaround 정식 코드화)
- Issue #44: Projectile hit_radius 오버슈트 → swept-circle 판정 (시뮬레이터 DPS 모델과 게임플레이 정합)

#### Closed Issues
- #43 WaveSystem 보스 path 하드코딩 (PR #46)
- #44 Projectile hit_radius 오버슈트 (PR #46)

#### Merged PRs
- #45 — qa(phase4-cleanup): markers + 매트릭스 v2.2 + GA 체크리스트 (squash → develop@4c86ea6)
- #46 — fix(phase 5 준비): Issue #43 보스 path + Issue #44 swept-circle (squash → develop@6e108a4)

#### Decisions (DECISION-SCM-P4F-*)
- **001**: PR #45 → PR #46 머지 순서 — markers/체크리스트 baseline 안착 후 잠재 결함 해결 PR 적용
- **002**: SCM 페르소나 사용량 한도 도달로 R3 마무리(README/CHANGELOG/신규 테스트 markers 보완)를 메인 세션이 직접 develop에 commit. DECISION-SCM-P4B-003(사용자 부재 자율 권한 위임 범위)과 정합

### Phase 4 R2 — 후반 라운드 통합 머지 (2026-05-19, DECISION-SCM-P4B-001~003)

> Phase 4 후반 라운드. PR #41(BL-07 클리어율 자동화) + PR #42(simpleaudio SFX 백엔드) 통합 머지 완료. develop@b5b9f2c.
> `v0.3.0` GA 승격은 여전히 보류 — 사용자 시각 검수(CAT-01~07) 완료 후 별도 SCM 라운드(DECISION-SCM-P4-004 유지).

#### Added
- **BL-07 클리어율 시뮬레이션 자동화 (Issue #39, PR #41, DECISION-DT1-P4B-001~005)**:
  - `src/systems/auto_mode_simulator.py` (신규, 337줄): tkinter-free 헤드리스 BattleScene 시뮬레이터. WaveSystem + PathingSystem + 직접 DPS 모델 채택.
  - `tests/test_clear_rate_simulation.py` (신규, 9건/15 회 반복): 5 시드 × 3 스테이지 = 15/15 (100%) 클리어 확인, 실행시간 ≈1.4s (임계 5s 대비).
  - `pyproject.toml` pytest markers 4종 정식 등록: `regression_p4` / `slow` / `audio` / `network` — PytestUnknownMarkWarning 0건.
- **simpleaudio SFX 백엔드 시범 도입 (Issue #29, PR #42, DECISION-AUDIO-012)**:
  - `src/core/sound.py`: winsound no-op stub → simpleaudio 비동기 WAV 재생 + PCM 볼륨 스케일링 (`set_master_volume` 실제 구현, 미설치/헤드리스 graceful fallback 내장).
  - `assets/audio/sfx/` 8 placeholder WAV(무음, Python `wave` stdlib 생성, 게임플레이 영향 0) + `assets/audio/sfx/README.md`.
  - `tests/test_sound_simpleaudio.py` (신규, 18건): AU-01~08 자동화 — AU-07 다채널 동시 재생(`play_buffer` 2회 호출 mock 검증) + AU-08 PCM 볼륨/뮤트 풀 사이클.
  - `src/scenes/menu_scene.py` / `src/scenes/battle_scene.py`: SFX 통합 — 버튼 클릭(ui_click), 적 사망(enemy_die), 웨이브 시작(wave_start), 영웅 페이즈(hero_skill).

#### Changed
- `SoundManager` API 확장 — `play_ui`, `play_sfx` 신규 메서드 + 마스터 볼륨 PCM 스케일링.
- `.github/workflows/ci.yml`: ubuntu-latest 잡에 `libasound2-dev` apt 설치 step 추가 (simpleaudio 의존). windows 잡은 그대로(winsound + simpleaudio 휠 양립).
- `docs/qa/regression_matrix.md`: AU-01~07 + BL-07 ✗ → ✓ 자동 가드 전환.
- `requirements.txt`: `simpleaudio>=1.0.4` 추가.

#### Decisions (DECISION-SCM-P4B-*)
- **001**: 머지 순서 — PR #41(BL-07, systems/ 단독) → PR #42(simpleaudio, 자산·CI·SoundManager 확산) 선후 적용. 작은 변경 선행, 외부 패키지 의존 + CI 변경은 후행 검증 부담 분리.
- **002**: `pyproject.toml` markers 충돌 해결 — BL-07(develop)의 4종 마커 스켈레톤 + audio(PR #42) 메타데이터(`Issue #29, DECISION-AUDIO-012`) 통합본 채택. `regression_p4` 설명도 PR #42의 매트릭스 자동 테스트 표현 + develop의 DECISION 트레이스를 합성.
- **003**: README/CHANGELOG 갱신을 SCM 본인 명의로 develop에 직접 commit (별도 `docs(release): ...` PR 생략) — Phase 4 후반 라운드 종료 마무리, 사용자 부재 자율 권한 위임 범위 내. `v0.3.0` GA 승격(main 머지·태깅) 보류는 그대로 유지.

#### Merged PRs
- #41 — feat(phase4-bl07): BL-07 클리어율 자동화 + pytest mark 등록 (squash → develop@b5112ca)
- #42 — feat(audio): simpleaudio SFX 백엔드 시범 도입 (squash → develop@b5b9f2c)

#### Closed Issues
- #29 simpleaudio SFX 백엔드 (PR #42, 수동 close — squash 메시지 키워드 누락 보정)
- #38 AU-07 다채널 자동 테스트 (PR #42, 수동 close)
- #39 BL-07 클리어율 시뮬레이션 (PR #41, 수동 close)

#### Open Issues (Phase 5 위임)
- #30 — Audio asset inventory (BGM 자산 발주 — Phase 5)

#### pytest 누적
- 베이스라인: 396 passed (Phase 4 R1 종료) → **424 passed** (+15 BL-07 + 18 simpleaudio − 일부 중복 회귀 가드 흡수). 경고 0건. ruff/black 양쪽 ✓.

---

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

[Unreleased]: https://github.com/genishs/simplegame-defencegame/compare/v0.4.0-rc.1...HEAD
[0.4.0-rc.1]: https://github.com/genishs/simplegame-defencegame/compare/v0.3.0-rc.1...v0.4.0-rc.1
[0.3.0]: https://github.com/genishs/simplegame-defencegame/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/genishs/simplegame-defencegame/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/genishs/simplegame-defencegame/releases/tag/v0.1.0
