# Phase 3 진행 체크리스트

본 체크리스트는 `docs/10_phase3_plan.md` 의 sub-phase 별 진행을 1줄 단위로 추적한다. 각 페르소나가 작업 완료 시 체크를 채우고, PR/커밋 해시를 옆에 기록한다.

> 갱신 규칙: 체크 박스 옆에 `(#PR번호 / commit-hash)` 또는 `(N/A — 해당 작업이 별도 PR 없이 본 plan 내 처리)` 형태로 추적.

---

## Phase 3.1 — Hardening

- [ ] Issue #8 — `src/systems/*`, `src/entities/*` tkinter import 금지 CI grep 가드 (`.github/workflows/ci.yml`)  — 담당: Dev Team1 + Configuration Manager
- [ ] Issue #2 — `src/data/stages/stage_01.json reward.grain` 추가  — 담당: Dev Team1
- [ ] (신규) release-windows.yml prerelease 자동 판단 로직 — tag suffix `-alpha`/`-beta`/`-rc` 감지  — 담당: Configuration Manager
- [ ] (신규) `src/data/loader.py` stage JSON 스키마 검증 (표준 라이브러리만, DECISION-P3-005)  — 담당: Dev Lead
- [ ] DoD 체크 — ruff/black/pytest 0 에러, 가드 검증 시뮬레이션 통과
- [ ] CHANGELOG `[Unreleased]` 항목 추가

## Phase 3.2 — Data Patch

- [ ] `src/data/stages/stage_02.json` 작성 (백암성, 평화 항복 분기 플래그)  — 담당: Dev Team1
- [ ] `src/data/stages/stage_03.json` 작성 (개모성)  — 담당: Dev Team1
- [ ] `src/data/stages/stage_04.json` 작성 (안시성 외곽)  — 담당: Dev Team1
- [ ] `src/data/stages/stage_05.json` 작성 (안시성 토산 — placeholder 메커닉)  — 담당: Dev Team1
- [ ] `src/data/loader.py` `list_stage_ids()` 함수 추가  — 담당: Dev Lead
- [ ] `tests/test_stage_data_set.py` 신규 — 5건 stage 모두 스키마 통과  — 담당: Dev Lead
- [ ] DoD 체크 — pytest 통과, 5 stage 로드 OK

## Phase 3.3 — Gameplay Integration

- [ ] Issue #1 — `BattleScene._spawn_enemy()` waypoints[0] 참조  — 담당: Dev Team1
- [ ] `tests/test_spawn_waypoint.py` 추가
- [ ] Issue #4 — `docs/phase3/hero_manual_mode.md` 명세 작성  — 담당: Dev Team2
- [ ] Issue #4 — M키 토글 + 방향키 이동 구현 (`src/systems/input.py`, `src/entities/hero.py`)
- [ ] `tests/test_hero_manual_input.py` 추가
- [ ] `tests/test_battle_scene_multistage.py` — 5 stage 통합 동작
- [ ] 영웅 4페이즈/궁극기 시각 이펙트 적용
- [ ] DoD 체크 — 신규 테스트 그린, 통합 시연 가능

## Phase 3.4 — UI/Asset Polish

- [ ] Issue #5 — ui_strings.md SSOT 일관화 (`src/ui/`, `src/scenes/` 하드코딩 검색·치환)  — 담당: Design Member
- [ ] `tests/test_no_korean_literal_in_ui.py` 신규 (정규식 grep 가드)
- [ ] Issue #6 — 픽션 캐릭터 5종 placeholder 자산 (`assets/characters/`)  — 담당: Design Lead
- [ ] `docs/08_asset_inventory.md` 픽션 캐릭터 행 갱신
- [ ] Issue #7 — `assets/fonts/NotoSansKR-Regular.ttf` + `OFL.txt` 동봉  — 담당: Dev Lead
- [ ] Issue #7 — PyInstaller spec 또는 `--add-data` 구성
- [ ] 와이어프레임 SCN-01/SCN-03/SCN-04/SCN-08 코드 반영  — 담당: Dev Team2 + Design Lead
- [ ] DoD 체크 — UI 한국어 리터럴 0건, 자산 18장 lookup OK

## Phase 3.5 — Vertical Slice & Demo

- [ ] Stage 1 수직 슬라이스 시나리오 시연 가능 (메뉴 → battle → result → menu)
- [ ] `tests/test_vertical_slice_stage01.py` 통합 테스트 신규
- [ ] pytest 200+ passed 달성
- [ ] `docs/qa/phase3_review.md` Test Lead 리뷰 작성
- [ ] v0.3.0-rc.1 태그 푸시 → release-windows.yml prerelease Release 자동 게시
- [ ] CHANGELOG `[0.3.0-rc.1]` 섹션 추가
- [ ] Phase 3 회고 `docs/phase3/retrospective.md` 작성  — 담당: Planning Lead