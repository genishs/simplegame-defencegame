# v0.3.0 GA 진입 체크리스트

작성: QA Lead (DECISION-QA-P4M-001)
작성일: 2026-05-19
기준 커밋: `020d0cf` (develop HEAD, Phase 4 R2)

---

## 개요

v0.3.0 정식 출시(GA)를 위한 최종 점검 체크리스트입니다.
사용자 검수(CAT-01~07) 및 DPI 매트릭스 2건이 완료되면
SCM 라운드에서 `develop → main` 머지 + `v0.3.0` 태그를 실행합니다.

---

## 자동 가드 (SCM/CI 완료)

| 항목 | 상태 | 근거 |
|------|------|------|
| pytest 전체 424건 통과 | ✓ | `pytest -q` 424 passed, 0 failed |
| pytest -m regression_p4 71건 통과 | ✓ | Phase 4 회귀 가드 선택 실행 확인 |
| pytest -m audio 18건 통과 | ✓ | 오디오 시스템 가드 확인 |
| ruff lint 오류 0건 | ✓ | `ruff check .` All checks passed |
| black 포맷 이상 0건 | ✓ | `black --check .` unchanged |
| CI ubuntu-latest 통과 | ✓ | GitHub Actions (develop, PR #40/#41/#42) |
| CI windows-latest 통과 | ✓ | GitHub Actions (develop, PR #40/#41/#42) |
| Domain layer tk-free guard 통과 | ✓ | grep + AST 2단계 검증 |

---

## 사용자 검수 (수동)

> 아래 항목은 사용자가 직접 실행 후 ☐ → ✓ 로 변경하세요.

| 항목 | 상태 | 기준 |
|------|------|------|
| CAT-01 게임 첫 실행 ~ 메인 메뉴 응답성 | ☐ 대기 중 | 3초 이내, 한글 정상 표시 |
| CAT-02 Stage 1 전 구간 손맛 | ☐ 대기 중 | 영웅 M키, 배치, UI 반응성 |
| CAT-03 .exe 더블클릭 실행 (Windows 11) | ☐ 대기 중 | PyInstaller 빌드, 오류 없음 |
| CAT-04 폰트 한글 렌더링 검증 | ☐ 대기 중 | 깨짐 없음, DPI 100%/125% |
| CAT-05 튜토리얼 첫 실행 자동 진입 손맛 | ☐ 대기 중 | 8단계 UX, skip 동작 |
| CAT-06 난이도 하향 stage 01~03 클리어율 | ☐ 대기 중 | 체감 난이도 적정 |
| CAT-07 M키 수동 모드 + 튜토리얼 6단계 | ☐ 대기 중 | 일시정지 UX |

---

## DPI 매트릭스 (수동)

| 항목 | 상태 |
|------|------|
| 1920×1080 + 100% DPI 전체 씬 | ☐ 대기 중 |
| 1920×1080 + 125% DPI 전체 씬 | ☐ 대기 중 |

---

## GA 진입 조건

**조건**: 위 자동 가드 ✓ 전체 + 사용자 검수 ☐ 0건

현재 상태: **자동 가드 완료 / 사용자 검수 7건 + DPI 2건 대기 중**

GA 게이트가 열리면 SCM 라운드에서 다음을 실행합니다:
1. `git merge develop → main`
2. `git tag v0.3.0`
3. GitHub Release 초안 생성
4. CHANGELOG v0.3.0 GA 마무리

---

## 참조

- 회귀 매트릭스: `docs/qa/regression_matrix.md` (v2.2)
- 시나리오 카탈로그: `docs/qa/scenario_catalog.md` (CAT-01~07)
- Phase 4 종료 보고서: `docs/qa/phase4_completion_report.md`
- DECISION: DECISION-QA-P4M-001~004
