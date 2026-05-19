# Changelog

이 문서는 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)을 따르며, 버전 관리는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)을 따릅니다.

## [Unreleased]

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
