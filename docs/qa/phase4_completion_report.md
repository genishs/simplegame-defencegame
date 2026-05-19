# Phase 4 종료 보고서

작성: QA Lead (DECISION-QA-P4M-001~004)
작성일: 2026-05-19
기준 커밋: `020d0cf` (develop HEAD)
대상 Phase: Phase 4 (R1, R2, cleanup)

---

## 개요

안시성 디펜스 Phase 4 는 다음 3개 라운드로 구성되었습니다:

| 라운드 | 주요 산출물 | 자동 테스트 |
|--------|-----------|------------|
| Phase 4 R1 | 튜토리얼 씬 (PR #36), 난이도 하향 (PR #34), 회귀 매트릭스 v2.0→v2.1 | 334 → 382 (+48) |
| Phase 4 R2 | BL-07 클리어율 시뮬레이터 (PR #41), simpleaudio SFX (PR #42), SCM finalize (PR #40) | 382 → 424 (+42) |
| Phase 4 cleanup | pytest markers 일관 적용, 회귀 매트릭스 v2.1→v2.2, GA 체크리스트 | 424 (markers는 metadata) |

---

## pytest 테스트 증가 내역

| 기준 | 수량 | 변화 |
|------|------|------|
| Phase 3.5 완료 (v0.3.0-rc.1) | 334건 | — |
| Phase 4 R1 완료 | 382건 | +48 |
| Phase 4 R2 완료 | 424건 | +42 |
| Phase 4 cleanup 완료 | 424건 | 0 (markers metadata만) |

**총 증가: 334 → 424 (+90건)**

---

## 회귀 매트릭스 시나리오 증가 내역

| 버전 | 시나리오 수 | 변화 |
|------|-----------|------|
| v2.0 (Phase 4 초기) | 30건 (v1) | — |
| v2.0 (Phase 4 신규 추가) | 55건 (+25) | AU/TU/BL 카테고리 신설 |
| v2.1 (R1 완료 후) | 55건 (✓ 전환) | TU/BL 자동화 전환 |
| v2.2 (cleanup 완료) | 55건 (✓ 전환) | BL-07/AU-01~07 자동화 완료 |

---

## Phase 4 주요 산출물

### R1 산출물
- `src/scenes/tutorial_scene.py` — 8단계 튜토리얼 씬 (PR #36, Dev Lead)
- `src/core/save_slot.py` — tutorial_dismissed/completed 필드 (PR #36)
- `src/data/stages/stage_01~03.json` — 난이도 하향 (PR #34, Dev Team1)
- `tests/test_tutorial_scene.py` — 23건 자동 테스트 (PR #36)
- `tests/test_stage_balance.py` — 22건 자동 테스트 (PR #34)
- `tests/test_regression_p4.py` — 17건 자동 테스트 (R1)
- `docs/qa/regression_matrix.md` — v2.1 갱신 (PR #40, SCM)

### R2 산출물
- `src/systems/auto_mode_simulator.py` — mock 시뮬레이터 (PR #41, Dev Team1)
- `src/core/sound.py` — simpleaudio SFX 백엔드 (PR #42, Dev Team2)
- `assets/audio/sfx/*.wav` — SFX placeholder 8건 (PR #42)
- `tests/test_clear_rate_simulation.py` — 9건 자동 테스트 (PR #41)
- `tests/test_sound_simpleaudio.py` — 18건 자동 테스트 (PR #42)

### cleanup 산출물
- `tests/test_clear_rate_simulation.py` — `pytestmark = regression_p4` 추가
- `tests/test_tutorial_scene.py` — `pytestmark = regression_p4` 추가
- `tests/test_stage_balance.py` — `pytestmark = regression_p4` 추가
- `.github/workflows/ci.yml` — pytest 3-step 분리 (fast/audio/full)
- `docs/qa/regression_matrix.md` — v2.2 갱신 (markers 체계 표, BL-07/AU ✓ 전환)
- `docs/qa/scenario_catalog.md` — 검수 현황 섹션 추가
- `docs/qa/v0_3_0_ga_checklist.md` — GA 체크리스트 신규 (본 파일)
- `docs/qa/phase4_completion_report.md` — 본 보고서

---

## pytest markers 적용 현황

| 파일 | markers | 적용 방식 |
|------|---------|----------|
| `tests/test_regression_p4.py` | `regression_p4` | 모듈 수준 `pytestmark` (기존) |
| `tests/test_clear_rate_simulation.py` | `regression_p4` (모듈), `slow` (클래스+함수) | cleanup 적용 |
| `tests/test_sound_simpleaudio.py` | `audio` | 모듈 수준 `pytestmark` (기존) |
| `tests/test_tutorial_scene.py` | `regression_p4` | cleanup 적용 |
| `tests/test_stage_balance.py` | `regression_p4` | cleanup 적용 |

**선택 실행 결과**:
- `pytest -m regression_p4`: 71건 선택, 353 deselected
- `pytest -m slow`: 5건 선택 (BL-07 클리어율 + 성능)
- `pytest -m audio`: 18건 선택 (AU-01~08)

---

## 자율 결정 이력 (DECISION-QA-P4M-###)

| ID | 결정 내용 |
|----|----------|
| DECISION-QA-P4M-001 | cleanup 작업 범위 확정: markers 5개 파일, CI 3-step, 매트릭스 v2.2, GA 체크리스트, 종료 보고서 |
| DECISION-QA-P4M-002 | CI 3-step 채택: fast(not slow) → audio → full. 별도 step 추가로 디버깅 가시성 향상 |
| DECISION-QA-P4M-003 | BL-07 ✗→✓ 전환 확정 (PR #41 머지, test_clear_rate_simulation.py 9건). AU-01~07 ✓ 재확인 (PR #42) |
| DECISION-QA-P4M-004 | pytest markers 체계 표 regression_matrix.md에 추가. pyproject.toml markers 기존 등록 상태 유지 (변경 없음) |

---

## 사용자 의존 잔여 항목

Phase 4 자동화 가드는 모두 통과 상태입니다. 아래 항목은 사용자 직접 검수가 필요합니다:

1. **CAT-01~07** (7건): `docs/qa/scenario_catalog.md` 수동 검수
2. **DPI 매트릭스** (2건): 1920×1080 + 100%/125% DPI 환경 확인

상세 진행 방법: `docs/qa/v0_3_0_ga_checklist.md` 참조

---

## Phase 5 인수 사항

Phase 5 (Dev Lead: feature/phase5-prep-bug-fixes)에서 신규 테스트 파일
(`test_wave_boss_path.py`, `test_combat_sweep.py`)이 추가될 예정입니다.
해당 파일에는 markers가 미적용 상태로 머지될 수 있으며,
Phase 5 첫 cleanup 라운드 또는 Dev Lead가 자율 적용 예정입니다.
