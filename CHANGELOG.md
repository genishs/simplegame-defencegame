# Changelog

이 문서는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)을 따르며, 버전 관리는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)을 따릅니다.

## [Unreleased]

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

### Closed Issues
- #2 reward.grain 데이터 패치
- #5 UI strings SSOT v1.1
- #6 캐릭터 플레이스홀더 5종
- #8 src/systems tkinter import 금지 CI 가드
- #9 prerelease 감지 정책
- #10 stage JSON schema validator

### Decisions (Phase 3)
- DECISION-T1-P3-001 (TYPE_CHECKING import 예외), DECISION-DL-P3-001 (stdlib-only validator), DECISION-D-P3-001 / 001a / 001b / 001c (UI strings SSOT + 컨벤션 + 신규 키 + 표 형식), DECISION-SCM-P3-001 (회수 4파일 한정 픽션 라벨 일괄 치환), DECISION-SCM-P3-002 (변경분 외 일괄 치환 보류)

### Notes
- 본 라운드는 Phase 3.1 통합 하드닝 종결 + Phase 3.4 디자인 일부. Phase 3.2(stages 02~05 데이터, #11) / 3.3(프로토타입 통합) / 3.5(사용자 검수) 다음 라운드 예정
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

[Unreleased]: https://github.com/genishs/simplegame-defencegame/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/genishs/simplegame-defencegame/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/genishs/simplegame-defencegame/releases/tag/v0.1.0
