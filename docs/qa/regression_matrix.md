# 회귀 매트릭스 — Phase 4 (v2, 누적 모드)

> v1 → v2 갱신: QA Lead (DECISION-PERSONA-002 활성화, 2026-05-19)
> v1 30 시나리오 전체 유지 + Phase 4 신규 25건 추가 = **총 55 시나리오**

**DECISION-TL-P3-5-001**: 매트릭스 열 구성은 현행 씬/시스템 아키텍처(Menu·StageSelect·Battle·Ending·Font·DPI·Persistence·Audio) 8개 모듈 기준으로 설정. *(v1 유지)*
**DECISION-TL-P3-5-002**: 자동 테스트 표기(✓)는 현재 `tests/` 디렉터리에 동작하는 케이스가 존재할 때만 표기. headless 불가 UI 테스트는 ✗ 로 표기. *(v1 유지)*
**DECISION-QA-P4-001**: v2부터 Tutorial 모듈 열 추가 — 총 **9 모듈** 기준.
**DECISION-QA-P4-002**: 자동화 불가 판정 기준 추가 — tkinter 이벤트 루프 필요·음원 파일 필요·실제 백엔드 미구현 항목은 ✗.
**DECISION-QA-P4-003**: Phase 게이트 거부권 임계값 — green path 시나리오(BT-01~10, MN-03~05, SS-02/05, HM-01~05) 중 1건이라도 ✗ 전환, 또는 `pytest -q` 자동 테스트 합격률 < 99% 시 발동.

마지막 갱신: 2026-05-19 | 기준 커밋: `f338c8d` | 작성: QA Lead (DECISION-PERSONA-002)

---

## 범례

| 기호 | 의미 |
|------|------|
| ✓ | 자동 테스트 케이스 존재 (pytest 포함) |
| ✗ | 자동 테스트 없음 (수동 검수 또는 headless 불가) |
| — | 해당 모듈과 무관 |

---

## 매트릭스 (v1 유지 30건)

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| **[MN] 메뉴 진입·종료** | | | | | | | | | | |
| MN-01 | 앱 시작 → 메인 메뉴 빌드 오류 없음 | ✗ | — | — | — | — | — | — | — | — |
| MN-02 | 메인 메뉴 버튼 8개 렌더링 확인 | ✗ | — | — | — | — | — | — | — | — |
| MN-03 | Enter 키로 포커스 버튼 활성화 | ✓ | — | — | — | — | — | — | — | — |
| MN-04 | Up/Down 키 포커스 이동 (0 ~ 7 인덱스) | ✓ | — | — | — | — | — | — | — | — |
| MN-05 | "종료" 버튼 클릭 시 app.quit() 호출 | ✓ | — | — | — | — | — | — | — | — |
| **[SS] 스테이지 선택·잠금 해제** | | | | | | | | | | |
| SS-01 | StageSelectScene.build() 오류 없음 | — | ✗ | — | — | — | — | — | — | — |
| SS-02 | 초기 상태: stage_01만 해금 (나머지 잠금) | — | ✓ | — | — | — | — | ✓ | — | — |
| SS-03 | stage_01 카드 클릭 → battle 씬 전환 | — | ✗ | — | — | — | — | — | — | — |
| SS-04 | 잠금된 카드 클릭 시 화면 전환 없음 | — | ✗ | — | — | — | — | — | — | — |
| SS-05 | ESC 키 → 메뉴 복귀 | — | ✓ | — | — | — | — | — | — | — |
| **[BT] 배틀 시작·wave 진행·클리어·패배** | | | | | | | | | | |
| BT-01 | BattleScene.build() 오류 없음 (stage_01) | — | — | ✓ | — | — | — | — | — | — |
| BT-02 | build() 후 WaveSystem에 웨이브 로드 | — | — | ✓ | — | — | — | — | — | — |
| BT-03 | update(dt) → WaveSystem.update 호출 순서 | — | — | ✓ | — | — | — | — | — | — |
| BT-04 | update(dt) → PathingSystem.update 호출 | — | — | ✓ | — | — | — | — | — | — |
| BT-05 | update(dt) → CombatSystem.update 호출 | — | — | ✓ | — | — | — | — | — | — |
| BT-06 | 시스템 호출 순서: wave → pathing → combat | — | — | ✓ | — | — | — | — | — | — |
| BT-07 | wave.all_clear + enemies=[] → 승리 판정 | — | — | ✓ | — | — | — | — | — | — |
| BT-08 | goals_reached >= lives → 패배 판정 | — | — | ✓ | — | — | — | — | — | — |
| BT-09 | _paused=True 시 시스템 update 스킵 | — | — | ✓ | — | — | — | — | — | — |
| BT-10 | ESC 키 → PauseDialog (_paused=True) | — | — | ✓ | — | — | — | — | — | — |
| **[HM] 영웅 자동/수동 M키 토글** | | | | | | | | | | |
| HM-01 | M키 → _hero_direct_mode True/False 토글 | — | — | ✓ | — | — | — | — | — | — |
| HM-02 | M키 토글 시 hero.manual_mode.toggled 이벤트 | — | — | ✓ | — | — | — | — | — | — |
| HM-03 | M키 토글 시 캔버스 상태 라벨 갱신 | — | — | ✓ | — | — | — | — | — | — |
| HM-04 | 수동 모드에서 방향키/WASD 영웅 이동 | — | — | ✓ | — | — | — | — | — | — |
| HM-05 | 수동 모드에서 hero.update(AI) 호출 안 함 | — | — | ✓ | — | — | — | — | — | — |
| **[FD] 폰트 적용·DPI 변화** | | | | | | | | | | |
| FD-01 | 번들 폰트 경로 해석 (dev 모드 vs _MEIPASS) | — | — | — | — | ✓ | — | — | — | — |
| FD-02 | 번들 폰트 없을 때 Malgun Gothic 폴백 | — | — | — | — | ✓ | — | — | — | — |
| FD-03 | 창 리사이즈 후 Scaler.font_pt 최솟값 >= 8 | — | — | — | — | — | ✓ | — | — | — |
| **[EN] 엔딩 분기** | | | | | | | | | | |
| EN-01 | EndingScene 패널 순차 진행 (Space) | — | — | — | ✓ | — | — | — | — | — |
| EN-02 | ESC → 메인 메뉴 복귀 | — | — | — | ✓ | — | — | — | — | — |

---

## Phase 4 신규 시나리오 (25건)

### [AU] 오디오 정책 회귀 (DECISION-AUDIO-011 연동)

> AU-01~AU-06: no-op 스텁 상태에서 현재 pytest 자동화 가능. `tests/test_regression_p4.py` 에 케이스 추가.
> AU-07~AU-08: 실제 다채널 백엔드(simpleaudio/pygame.mixer) 도입 후 전환 예정.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| AU-01 | SoundManager.play_bgm("main_menu") 호출 시 예외 없음 (no-op 포함) | — | — | — | — | — | — | — | ✓ | — |
| AU-02 | SoundManager.play_sfx("sfx_arrow_shoot") 호출 시 예외 없음 | — | — | — | — | — | — | — | ✓ | — |
| AU-03 | SoundManager.play_sfx("ui_button_click") 호출 시 예외 없음 | — | — | — | — | — | — | — | ✓ | — |
| AU-04 | SoundManager.stop_all() 호출 시 예외 없음 | — | — | — | — | — | — | — | ✓ | — |
| AU-05 | SoundManager.set_master_volume(0.5) 호출 시 예외 없음 (미래 API, no-op 단계도 통과) | — | — | — | — | — | — | — | ✓ | — |
| AU-06 | SoundManager.mute() 호출 시 예외 없음 (미래 API, no-op 단계도 통과) | — | — | — | — | — | — | — | ✓ | — |
| AU-07 | BGM 루프 재생 중 SFX 동시 재생 가능 (백엔드 교체 후 검증) | — | — | — | — | — | — | — | ✗ | — |
| AU-08 | PyInstaller 빌드 시 assets/audio/ 경로 정상 해석 (수동 검수 의존) | — | — | — | — | — | — | — | ✗ | — |

> AU-07: 실제 다채널 백엔드 도입 후 ✓ 전환. AU-08: .exe 빌드 수동 CAT 항목으로 관리.

---

### [TU] 튜토리얼 시나리오 (DECISION-PL-P4-001~008 연동, docs/12_tutorial_design.md)

> TU-01~TU-10: Dev Lead(Issue #26) 라운드 src/scenes/tutorial_scene.py 구현 결과에 의존.
> 본 라운드 작성 시점(Dev Lead 병렬 진행 중)에는 ✗. Dev Lead 머지 완료 후 QA Lead가 ✓ 전환.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| TU-01 | 저장 슬롯 비어 있을 때 새 게임 → 튜토리얼 자동 진입 (DECISION-PL-P4-002) | — | — | — | — | — | — | ✗ | — | ✗ |
| TU-02 | 메인 메뉴 튜토리얼 버튼 → 단계 1부터 재진입 (DECISION-PL-P4-005) | ✗ | — | — | — | — | — | — | — | ✗ |
| TU-03 | 튜토리얼 8단계 순차 완주 → tutorial_completed=True 저장 (DECISION-PL-P4-002) | — | — | — | — | — | — | ✗ | — | ✗ |
| TU-04 | 스킵 버튼/ESC → 확인 다이얼로그 1회 표시 (DECISION-PL-P4-004) | — | — | — | — | — | — | — | — | ✗ |
| TU-05 | 다시 보지 않기 체크 후 예 → tutorial_dismissed=True + stage_select 이동 (DECISION-PL-P4-004) | — | — | — | — | — | — | ✗ | — | ✗ |
| TU-06 | ESC 키 → 스킵 다이얼로그 호출 (단계 1~8 모든 단계 공통) | — | — | — | — | — | — | — | — | ✗ |
| TU-07 | 단계 4 mock wave (tang_soldier x2, interval 1.5s) 정상 진행·종료 (DECISION-PL-P4-007) | — | — | ✗ | — | — | — | — | — | ✗ |
| TU-08 | 단계 8 시작하기 클릭 → stage_select 화면 이동 (DECISION-PL-P4-002) | — | ✗ | — | — | — | — | ✗ | — | ✗ |
| TU-09 | tutorial_dismissed=True 상태에서 재실행 → 자동 진입 없음 (DECISION-PL-P4-002) | — | — | — | — | — | — | ✗ | — | ✗ |
| TU-10 | tutorial_completed=False + tutorial_dismissed=False → 이어하기 시 자동 진입 없음, 메뉴 버튼만 가능 (DECISION-PL-P4-002) | ✗ | — | — | — | — | — | ✗ | — | ✗ |

> 갱신 안내: Dev Lead 라운드 머지 후 TU-01~TU-10 ✗ → ✓ 전환 담당은 QA Lead.

---

### [BL] 난이도 밸런스 시나리오 (DECISION-PL-P4-009~016 연동, docs/13_difficulty_balance.md)

> BL-01~BL-03, BL-06~BL-07: Dev Team1(Issue #27) 데이터 패치 결과 검증. 본 라운드 시점 ✗.
> BL-04~BL-05: stage_04~05 무변경 가드 — 현재 데이터 기준 ✓ 자동화 포함 (test_regression_p4.py).

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| BL-01 | stage_01 reward.grain = 100 (DECISION-PL-P4-011/015, 현재 50 → 패치 후 100) | — | — | — | — | — | — | ✗ | — | — |
| BL-02 | stage_02 wave 수 = 4, W1 count = 3, W1 interval_s = 1.0, reward.grain = 150 (DECISION-PL-P4-010/009/015) | — | — | ✗ | — | — | — | — | — | — |
| BL-03 | stage_03 wave 수 = 4, W1 단일 path=p_gorge, reward.grain = 220, night_vision_radius_multiplier 필드 존재 (DECISION-PL-P4-010/014/015) | — | — | ✗ | — | — | — | — | — | — |
| BL-04 | stage_04 wave 수 무변경 (현재 7), reward.grain 무변경 (현재 200) — 영향 0 가드 (DECISION-PL-P4-013) | — | — | ✓ | — | — | — | — | — | — |
| BL-05 | stage_05 wave 수 무변경 (현재 10), reward.grain 무변경 (현재 300) — 영향 0 가드 (DECISION-PL-P4-013) | — | — | ✓ | — | — | — | — | — | — |
| BL-06 | stage_03 schema 검증 통과 — night_vision_radius_multiplier 옵션 필드 허용, 범위 0.5~2.0 (DECISION-PL-P4-014) | — | — | ✗ | — | — | — | — | — | — |
| BL-07 | 자동 모드 mock 시뮬레이션 5회 → stage_01~03 클리어율 95%+ (DECISION-PL-P4-012) | — | — | ✗ | — | — | — | — | — | — |

> BL-01~BL-03, BL-06: Dev Team1 머지 후 ✓ 전환 예정. BL-07: Dev Team1 전투 로직 구현 필요.

---

## 자동화 우선순위 (✗ → ✓ 전환 후보)

v1 항목(DECISION-TL-P3-5-003) 유지 + Phase 4 신규 후보 추가.

### v1 잔여 후보

| # | 시나리오 | 자동화 방법 | 신규 파일 |
|---|----------|-------------|----------|
| MN-01 | 앱 시작 빌드 오류 없음 | MenuScene 모듈 import 성공 검증 | test_regression_p4.py |
| SS-01 | StageSelectScene.build() 오류 없음 | FakeApp 확장 객체 생성 검증 | test_regression_p4.py |

### Phase 4 신규 후보 (DECISION-QA-P4-004)

| # | 시나리오 | 자동화 방법 | 우선순위 |
|---|----------|-------------|----------|
| TU-01 | 튜토리얼 자동 진입 | FakeApp + empty save_slot mock | Dev Lead 머지 후 |
| TU-09 | dismissed=True 시 자동 진입 없음 | save_slot mock + 씬 전환 추적 | Dev Lead 머지 후 |
| BL-06 | night_vision_radius_multiplier 스키마 허용 | validate_stage + 옵션 필드 주입 | Dev Team1 머지 후 |
| BL-07 | 클리어율 시뮬레이션 | mock BattleScene 자동 모드 5회 반복 | Dev Team1 머지 후 |

> headless 불가 항목 (MN-02, SS-03·04, TU-04·06·07·08): tkinter 창 초기화 및 이벤트 루프 필요. 수동 검수(scenario_catalog.md) 의존.

---

## CI 커버리지 점검 결과 (Phase 4 기준)

| 카테고리 | CI 커버 여부 | 비고 |
|----------|-------------|------|
| Menu | 부분 커버 (test_regression_p3_5.py) | 키보드 네비게이션 커버 완료 |
| StageSelect | 부분 커버 (test_regression_p3_5.py) | 잠금 로직 커버 완료 |
| Battle | 커버됨 (test_battle_scene_flow.py 등) | |
| Ending | 부분 커버 (test_regression_p3_5.py) | |
| Font | 커버됨 (test_fonts_runtime.py) | |
| DPI/Scaler | 커버됨 (test_scaler.py) | |
| Persistence | 미커버 | player_data 저장·로드 로직 미구현 상태 |
| Audio | 신규 부분 커버 (test_regression_p4.py) | AU-01~AU-06 ✓, AU-07~AU-08 백엔드 구현 후 전환 |
| Tutorial | 미커버 | Dev Lead #26 머지 후 ✓ 전환 예정 |

**CI 추가 step 검토 의견 (DECISION-QA-P4-005)**:
현재 `pytest -q` 명령이 `tests/` 전체를 커버하므로 별도 step 추가 불필요.
단, Phase 4 완료 후 `@pytest.mark.regression_p4` 마커로 선택 실행 경로를 확보하는 것이 권장됨 (v1 DECISION-TL-P3-5-004 연장).
BL-07 클리어율 시뮬레이션은 느릴 수 있으므로 `slow` 마커 분리 검토 권장.

---

## Phase 게이트 거부권 가이드 (DECISION-QA-P4-003)

**QA Lead 거부권 발동 조건**:

1. **green path 시나리오 ✗ 전환**: 아래 시나리오 중 1건이라도 테스트 케이스가 삭제·비활성화되어 ✓→✗ 전환 시
   - BT-01~BT-10 (배틀 시스템 핵심 흐름)
   - MN-03~MN-05 (메뉴 키보드 네비게이션)
   - SS-02, SS-05 (스테이지 선택 잠금 상태·ESC)
   - HM-01~HM-05 (영웅 M키 토글)

2. **자동 테스트 합격률 < 99%**: `pytest -q` 결과 1건 이상 FAILED 상태로 PR이 제출된 경우

**거부권 행사 방법** (본 라운드에서는 가이드만 — 실제 행사 없음):
- Slack/Issue 코멘트가 아닌, 대상 **머지 PR에 GitHub Review → Request Changes** 코멘트로 행사
- 코멘트 형식: [QA-VETO] DECISION-QA-P4-003: {시나리오 ID} 회귀 감지 — 머지 보류 요청
- 해결 확인 후 QA Lead가 직접 **Approve** 로 전환하여 게이트 해제

---

## 자동화 후보 Issue 등록 안내 (DECISION-QA-P4-006)

본 라운드 PR 본문 제출 후 다음 2건을 별도 GitHub Issue로 등록 예정:
1. AU-07 — 다채널 동시 재생 자동화: 백엔드 교체(simpleaudio/pygame.mixer) 시점 ✓ 전환 가이드 포함
2. BL-07 — 클리어율 시뮬레이션 자동화: mock BattleScene 5회 반복 95%+ 가드 케이스 작성

---

## 변경 이력

| 버전 | 일자 | 작성자 | 내용 |
|------|------|--------|------|
| v1 (Phase 3.5) | 2026-05-19 | Test Lead | 30 시나리오 (MN/SS/BT/HM/FD/EN), 8 모듈 열 |
| v2 (Phase 4) | 2026-05-19 | QA Lead (DECISION-PERSONA-002) | Phase 4 신규 25건 추가 (AU-01~08, TU-01~10, BL-01~07). Tutorial 모듈 열 추가 (총 9 모듈). 거부권 가이드 신설. DECISION-QA-P4-001~006. |