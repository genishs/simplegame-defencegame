# 회귀 매트릭스 — Phase 3.5

**DECISION-TL-P3-5-001**: 매트릭스 열 구성은 현행 씬/시스템 아키텍처(Menu·StageSelect·Battle·Ending·Font·DPI·Persistence·Audio) 8개 모듈 기준으로 설정.  
**DECISION-TL-P3-5-002**: 자동 테스트 표기(✓)는 현재 `tests/` 디렉터리에 동작하는 케이스가 존재할 때만 표기. headless 불가 UI 테스트는 ✗ 로 표기.

마지막 갱신: 2026-05-19 | 기준 커밋: `3c8cf7f`

---

## 범례

| 기호 | 의미 |
|------|------|
| ✓ | 자동 테스트 케이스 존재 (pytest 포함) |
| ✗ | 자동 테스트 없음 (수동 검수 또는 headless 불가) |
| — | 해당 모듈과 무관 |

---

## 매트릭스

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|
| **[MN] 메뉴 진입·종료** | | | | | | | | | |
| MN-01 | 앱 시작 → 메인 메뉴 빌드 오류 없음 | ✗ | — | — | — | — | — | — | — |
| MN-02 | 메인 메뉴 버튼 8개 렌더링 확인 | ✗ | — | — | — | — | — | — | — |
| MN-03 | Enter 키로 포커스 버튼 활성화 | ✓ | — | — | — | — | — | — | — |
| MN-04 | Up/Down 키 포커스 이동 (0 ~ 7 인덱스) | ✓ | — | — | — | — | — | — | — |
| MN-05 | "종료" 버튼 클릭 시 app.quit() 호출 | ✓ | — | — | — | — | — | — | — |
| **[SS] 스테이지 선택·잠금 해제** | | | | | | | | | |
| SS-01 | StageSelectScene.build() 오류 없음 | — | ✗ | — | — | — | — | — | — |
| SS-02 | 초기 상태: stage_01만 해금 (나머지 잠금) | — | ✓ | — | — | — | — | ✓ | — |
| SS-03 | stage_01 카드 클릭 → battle 씬 전환 | — | ✗ | — | — | — | — | — | — |
| SS-04 | 잠금된 카드 클릭 시 화면 전환 없음 | — | ✗ | — | — | — | — | — | — |
| SS-05 | ESC 키 → 메뉴 복귀 | — | ✓ | — | — | — | — | — | — |
| **[BT] 배틀 시작·wave 진행·클리어·패배** | | | | | | | | | |
| BT-01 | BattleScene.build() 오류 없음 (stage_01) | — | — | ✓ | — | — | — | — | — |
| BT-02 | build() 후 WaveSystem에 웨이브 로드 | — | — | ✓ | — | — | — | — | — |
| BT-03 | update(dt) → WaveSystem.update 호출 순서 | — | — | ✓ | — | — | — | — | — |
| BT-04 | update(dt) → PathingSystem.update 호출 | — | — | ✓ | — | — | — | — | — |
| BT-05 | update(dt) → CombatSystem.update 호출 | — | — | ✓ | — | — | — | — | — |
| BT-06 | 시스템 호출 순서: wave → pathing → combat | — | — | ✓ | — | — | — | — | — |
| BT-07 | wave.all_clear + enemies=[] → 승리 판정 | — | — | ✓ | — | — | — | — | — |
| BT-08 | goals_reached >= lives → 패배 판정 | — | — | ✓ | — | — | — | — | — |
| BT-09 | _paused=True 시 시스템 update 스킵 | — | — | ✓ | — | — | — | — | — |
| BT-10 | ESC 키 → PauseDialog (_paused=True) | — | — | ✓ | — | — | — | — | — |
| **[HM] 영웅 자동/수동 M키 토글** | | | | | | | | | |
| HM-01 | M키 → _hero_direct_mode True/False 토글 | — | — | ✓ | — | — | — | — | — |
| HM-02 | M키 토글 시 hero.manual_mode.toggled 이벤트 | — | — | ✓ | — | — | — | — | — |
| HM-03 | M키 토글 시 캔버스 상태 라벨 갱신 | — | — | ✓ | — | — | — | — | — |
| HM-04 | 수동 모드에서 방향키/WASD 영웅 이동 | — | — | ✓ | — | — | — | — | — |
| HM-05 | 수동 모드에서 hero.update(AI) 호출 안 함 | — | — | ✓ | — | — | — | — | — |
| **[FD] 폰트 적용·DPI 변화** | | | | | | | | | |
| FD-01 | 번들 폰트 경로 해석 (dev 모드 vs _MEIPASS) | — | — | — | — | ✓ | — | — | — |
| FD-02 | 번들 폰트 없을 때 Malgun Gothic 폴백 | — | — | — | — | ✓ | — | — | — |
| FD-03 | 창 리사이즈 후 Scaler.font_pt 최솟값 >= 8 | — | — | — | — | — | ✓ | — | — |
| **[EN] 엔딩 분기** | | | | | | | | | |
| EN-01 | EndingScene 패널 순차 진행 (Space) | — | — | — | ✓ | — | — | — | — |
| EN-02 | ESC → 메인 메뉴 복귀 | — | — | — | ✓ | — | — | — | — |

---

## 자동화 우선순위 (✗ → ✓ 전환 후보)

다음 항목은 headless FakeApp/FakeCanvas 패턴으로 자동화 가능하다고 판단
(**DECISION-TL-P3-5-003**).

| # | 시나리오 | 자동화 방법 | 신규 파일 |
|---|----------|-------------|-----------|
| MN-03 | Enter 키 포커스 활성화 | FakeApp + `_on_enter_key` 직접 호출 | `test_regression_p3_5.py` |
| MN-04 | Up/Down 포커스 이동 | `_on_up_key`/`_on_down_key` 호출 후 `_focused_idx` 검증 | `test_regression_p3_5.py` |
| MN-05 | 종료 버튼 → app.quit() | FakeApp.quit 호출 여부 추적 | `test_regression_p3_5.py` |
| SS-02 | 잠금 상태 초기화 | player_data mock 주입 후 unlocked 집합 확인 | `test_regression_p3_5.py` |
| SS-05 | ESC → 메뉴 복귀 | `_on_escape` 호출 후 `app._goto_calls` 확인 | `test_regression_p3_5.py` |
| EN-01 | EndingScene 패널 진행 | FakeApp + `_on_space` 반복 호출 | `test_regression_p3_5.py` |
| EN-02 | ESC → 메뉴 복귀 | `_on_escape` 호출 후 `app._goto_calls` 확인 | `test_regression_p3_5.py` |

> headless 불가 항목 (MN-01·02, SS-01·03·04, SS-03 click tag_bind):
> tkinter 창 초기화 및 이벤트 루프가 필요한 씬 렌더링은 수동 검수(`scenario_catalog.md`) 의존.

---

## CI 커버리지 점검 결과

| 카테고리 | CI 커버 여부 | 비고 |
|----------|-------------|------|
| Menu | 부분 커버 (test_regression_p3_5.py 추가로 보완) | 키보드 네비게이션 신규 추가 |
| StageSelect | 부분 커버 (test_regression_p3_5.py 추가로 보완) | 잠금 로직 신규 추가 |
| Battle | 커버됨 (test_battle_scene_flow.py 등) | |
| Ending | 부분 커버 (test_regression_p3_5.py 추가로 보완) | 패널 진행 신규 추가 |
| Font | 커버됨 (test_fonts_runtime.py) | |
| DPI/Scaler | 커버됨 (test_scaler.py) | |
| Persistence | 미커버 | player_data 저장·로드 로직 미구현 상태 |
| Audio | 미구현 | Phase 4+ 예정 |

**권장 CI 추가 step** (DECISION-TL-P3-5-004):
pytest marker `regression_p3_5`를 신규 테스트에 적용해 선택 실행 가능하도록 함.
현재 CI `pytest -q` 명령이 tests/ 전체를 커버하므로 별도 step 없이도 신규 테스트가 포함됨.
