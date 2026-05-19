# 회귀 매트릭스 — Phase 4 (v2.3, 누적 모드)

> v1 → v2 갱신: QA Lead (DECISION-PERSONA-002 활성화, 2026-05-19)
> v2.1 갱신: SCM (PR #40/#41/#42 머지 후, DECISION-SCM-P4-002/003)
> v2.2 갱신: QA Lead (Phase 4 cleanup markers, DECISION-QA-P4M-003/004) + Dev Lead (Phase 5 준비, DECISION-DL-P5P-001/002)
> v2.3 갱신: Audio Engineer (Phase 5.1 BGM prep, Issue #30, DECISION-AUDIO-013) — BG-01~BG-04 추가
> v1 30 시나리오 전체 유지 + Phase 4 신규 25건 추가 + Phase 5 준비 9건 추가 + Phase 5.1 BGM 4건 추가 = **총 68 시나리오**

**DECISION-TL-P3-5-001**: 매트릭스 열 구성은 현행 씬/시스템 아키텍처(Menu·StageSelect·Battle·Ending·Font·DPI·Persistence·Audio) 8개 모듈 기준으로 설정. *(v1 유지)*
**DECISION-TL-P3-5-002**: 자동 테스트 표기(✓)는 현재 `tests/` 디렉터리에 동작하는 케이스가 존재할 때만 표기. headless 불가 UI 테스트는 ✗ 로 표기. *(v1 유지)*
**DECISION-QA-P4-001**: v2부터 Tutorial 모듈 열 추가 — 총 **9 모듈** 기준.
**DECISION-QA-P4-002**: 자동화 불가 판정 기준 추가 — tkinter 이벤트 루프 필요·음원 파일 필요·실제 백엔드 미구현 항목은 ✗.
**DECISION-QA-P4-003**: Phase 게이트 거부권 임계값 — green path 시나리오(BT-01~10, MN-03~05, SS-02/05, HM-01~05) 중 1건이라도 ✗ 전환, 또는 `pytest -q` 자동 테스트 합격률 < 99% 시 발동.
**DECISION-QA-P4M-003**: v2.2 — BL-07 (PR #41) · AU-01~07 (PR #42) 머지로 자동화 ✓ 전환. pytest markers 일관 적용 (5개 파일) 완료.
**DECISION-QA-P4M-004**: v2.2 — pytest markers 체계: `regression_p4` (71건) / `slow` (5건) / `audio` (18건) / `network` (0건, 미사용). CI 3-step 분리.

마지막 갱신: 2026-05-19 | 기준 커밋: `0773a5f` | 작성: QA Lead (DECISION-QA-P4M-003/004) | v2.3 갱신: Audio Engineer (DECISION-AUDIO-013)

---

## 범례

| 기호 | 의미 |
|------|------|
| ✓ | 자동 테스트 케이스 존재 (pytest 포함) |
| ✗ | 자동 테스트 없음 (수동 검수 또는 headless 불가) |
| — | 해당 모듈과 무관 |

---

## pytest Markers 체계 (v2.2, DECISION-QA-P4M-004)

| marker | 의미 | 사용처 |
| --- | --- | --- |
| `regression_p4` | Phase 4 회귀 가드 — 자동 실행 대상 | TU-01~10, BL-01~07, AU-01~06 커버 (71건) |
| `slow` | 1초 이상 소요 테스트 | BL-07 클리어율 시뮬레이션 (test_clear_rate_simulation.py, 5건) |
| `audio` | 오디오 시스템 테스트 | AU-01~08 (test_sound_simpleaudio.py, 18건) |
| `network` | 네트워크 의존 테스트 | (현재 미사용, 0건) |

```
# 선택 실행 예시
pytest -m regression_p4          # Phase 4 회귀 가드 71건
pytest -m "not slow"              # 빠른 검증 (CI fast-path step)
pytest -m audio                   # 오디오 18건
pytest                            # 전체 424건 (slow 포함)
```

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

### [AU] 오디오 정책 회귀 (DECISION-AUDIO-011/012 연동)

> AU-01~AU-07: simpleaudio SFX 백엔드 시범 도입 (Issue #29, DECISION-AUDIO-012) 완료.
> `tests/test_sound_simpleaudio.py` (12 케이스) 에서 자동화 가드 활성.
> AU-08: PyInstaller 빌드 수동 CAT 항목 유지.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| AU-01 | SoundManager.play_bgm("main_menu") 호출 시 예외 없음 (Phase 5 stub) | — | — | — | — | — | — | — | ✓ | — |
| AU-02 | SoundManager.play_sfx("sfx.arrow_shot") 호출 시 예외 없음 (simpleaudio fallback 포함) | — | — | — | — | — | — | — | ✓ | — |
| AU-03 | SoundManager.play_ui("sfx.ui_click") 호출 시 예외 없음 | — | — | — | — | — | — | — | ✓ | — |
| AU-04 | SoundManager.stop_all() 호출 시 예외 없음 | — | — | — | — | — | — | — | ✓ | — |
| AU-05 | SoundManager.set_master_volume(0.5) — 클램핑 검증 포함 | — | — | — | — | — | — | — | ✓ | — |
| AU-06 | SoundManager.mute() / unmute() 토글 — 볼륨 복원 검증 | — | — | — | — | — | — | — | ✓ | — |
| AU-07 | play_sfx 2회 연속 → 둘 다 play_buffer 큐잉 (다채널 동시 재생, mock 검증) | — | — | — | — | — | — | — | ✓ | — |
| AU-08 | PyInstaller 빌드 시 assets/audio/ 경로 정상 해석 (수동 검수 의존) | — | — | — | — | — | — | — | ✗ | — |

> AU-07: ✓ 전환 (DECISION-AUDIO-012, Issue #29) — simpleaudio mock 다채널 큐잉 pytest 자동화.
> AU-08: .exe 빌드 수동 CAT 항목 유지 — spec 파일에 hiddenimports + audio datas 번들링 추가 완료.
> **Issue #38 close 후보**: AU-07 자동화 가드 활성화로 다채널 SFX 회귀 감지 가능.

---

### [TU] 튜토리얼 시나리오 (DECISION-PL-P4-001~008 연동, docs/12_tutorial_design.md)

> TU-01~TU-10: Dev Lead(Issue #26 / PR #36) 머지 완료. `src/scenes/tutorial_scene.py` + `src/core/save_slot.py` + `tests/test_tutorial_scene.py` (23건 자동 테스트) 활성.
> 본 SCM 라운드(Phase 4 R1, DECISION-SCM-P4-002) 에서 자동 가드 가능 항목 ✓ 전환. headless 불가 항목(TU-04/06/07/08) 은 ✗ 유지하고 scenario_catalog.md 수동 검수 의존.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| TU-01 | 저장 슬롯 비어 있을 때 새 게임 → 튜토리얼 자동 진입 (DECISION-PL-P4-002) | — | — | — | — | — | — | ✓ | — | ✓ |
| TU-02 | 메인 메뉴 튜토리얼 버튼 → 단계 1부터 재진입 (DECISION-PL-P4-005) | ✓ | — | — | — | — | — | — | — | ✓ |
| TU-03 | 튜토리얼 8단계 순차 완주 → tutorial_completed=True 저장 (DECISION-PL-P4-002) | — | — | — | — | — | — | ✓ | — | ✓ |
| TU-04 | 스킵 버튼/ESC → 확인 다이얼로그 1회 표시 (DECISION-PL-P4-004) | — | — | — | — | — | — | — | — | ✗ |
| TU-05 | 다시 보지 않기 체크 후 예 → tutorial_dismissed=True + stage_select 이동 (DECISION-PL-P4-004) | — | — | — | — | — | — | ✓ | — | ✓ |
| TU-06 | ESC 키 → 스킵 다이얼로그 호출 (단계 1~8 모든 단계 공통) | — | — | — | — | — | — | — | — | ✗ |
| TU-07 | 단계 4 mock wave (tang_soldier x2, interval 1.5s) 정상 진행·종료 (DECISION-PL-P4-007) | — | — | ✗ | — | — | — | — | — | ✗ |
| TU-08 | 단계 8 시작하기 클릭 → stage_select 화면 이동 (DECISION-PL-P4-002) | — | ✗ | — | — | — | — | ✗ | — | ✗ |
| TU-09 | tutorial_dismissed=True 상태에서 재실행 → 자동 진입 없음 (DECISION-PL-P4-002) | — | — | — | — | — | — | ✓ | — | ✓ |
| TU-10 | tutorial_completed=False + tutorial_dismissed=False → 이어하기 시 자동 진입 없음, 메뉴 버튼만 가능 (DECISION-PL-P4-002) | ✓ | — | — | — | — | — | ✓ | — | ✓ |

> 갱신 안내: TU-04/06/07/08 은 tkinter 창·이벤트 루프 의존으로 headless 자동화 불가 — scenario_catalog.md CAT-05~07 수동 검수 의존. DECISION-SCM-P4-003 (본 라운드).

---

### [BL] 난이도 밸런스 시나리오 (DECISION-PL-P4-009~016 연동, docs/13_difficulty_balance.md)

> BL-01~BL-06: Dev Team1(Issue #27 / PR #34) 머지 완료. `tests/test_stage_balance.py` (22건 자동 테스트) 활성.
> BL-04~BL-05: stage_04~05 무변경 가드 — 현재 데이터 기준 ✓ 자동화 (test_regression_p4.py + test_stage_balance.py).
> BL-07: 클리어율 시뮬레이션은 mock BattleScene 자동 모드 구현 필요 — 후속 라운드 대상.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| BL-01 | stage_01 reward.grain = 100 (DECISION-PL-P4-011/015, 현재 50 → 패치 후 100) | — | — | — | — | — | — | ✓ | — | — |
| BL-02 | stage_02 wave 수 = 4, W1 count = 3, W1 interval_s = 1.0, reward.grain = 150 (DECISION-PL-P4-010/009/015) | — | — | ✓ | — | — | — | — | — | — |
| BL-03 | stage_03 wave 수 = 4, W1 단일 path=p_gorge, reward.grain = 220, night_vision_radius_multiplier 필드 존재 (DECISION-PL-P4-010/014/015) | — | — | ✓ | — | — | — | — | — | — |
| BL-04 | stage_04 wave 수 무변경 (현재 7), reward.grain 무변경 (현재 200) — 영향 0 가드 (DECISION-PL-P4-013) | — | — | ✓ | — | — | — | — | — | — |
| BL-05 | stage_05 wave 수 무변경 (현재 10), reward.grain 무변경 (현재 300) — 영향 0 가드 (DECISION-PL-P4-013) | — | — | ✓ | — | — | — | — | — | — |
| BL-06 | stage_03 schema 검증 통과 — night_vision_radius_multiplier 옵션 필드 허용, 범위 0.5~2.0 (DECISION-PL-P4-014) | — | — | ✓ | — | — | — | — | — | — |
| BL-07 | 자동 모드 mock 시뮬레이션 5회 → stage_01~03 클리어율 95%+ (DECISION-PL-P4-012) | — | — | ✓ | — | — | — | — | — | — |

> BL-01~BL-06: Phase 4 R1 SCM 라운드(DECISION-SCM-P4-002) 에서 ✓ 전환.
> BL-07: PR #41 머지 완료 → ✓ 전환 (DECISION-QA-P4M-003). `test_clear_rate_simulation.py` 9건 자동 가드 활성.

---

### [WV] WaveSystem 보스 path resolution (Phase 5 준비, Issue #43, DECISION-DL-P5P-001)

> WV-01~05: Dev Lead Phase 5 준비 라운드 (feature/phase5-prep-bug-fixes) 머지 후 ✓ 전환.
> `tests/test_wave_boss_path.py` (13 케이스) 에서 자동 가드. stage_03/04/05 보스 spawn
> 실패 결함 (p_main 하드코딩) 정식 해결.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| WV-01 | 보스 wave 의 `boss_path` 명시 시 그 값을 spawn path 로 사용 (DECISION-DL-P5P-001 우선순위 1) | — | — | ✓ | — | — | — | — | — | — |
| WV-02 | `boss_path` 미지정 + 같은 wave 의 spawns 첫 path 차용 (우선순위 2) | — | — | ✓ | — | — | — | — | — | — |
| WV-03 | boss-only wave (spawns 비어 있음) → `load(paths=)` 첫 path id 사용 (우선순위 3) | — | — | ✓ | — | — | — | — | — | — |
| WV-04 | paths 미주입 + `world['waypoints']` dict 첫 키 (우선순위 4) | — | — | ✓ | — | — | — | — | — | — |
| WV-05 | 완전 미지정 → `"p_main"` 호환 fallback (우선순위 5, legacy 보존) | — | — | ✓ | — | — | — | — | — | — |

> 실 stage 01~05 보스 spawn 가드 4건 (stage_01: tang_scout_captain, stage_03: tang_night_raider, stage_04: tang_elite_battering_ram, stage_05: tang_taizong) 가 모두 ✓ 통과 — stage_03/04/05 의 보스 wave 가 더 이상 `"p_main"` 으로 spawn 시도하지 않음을 회귀 가드.

---

### [CB] Projectile swept-circle 충돌 (Phase 5 준비, Issue #44, DECISION-DL-P5P-002)

> CB-01~05: Dev Lead Phase 5 준비 라운드 (feature/phase5-prep-bug-fixes) 머지 후 ✓ 전환.
> `tests/test_combat_sweep.py` (11 케이스) 에서 자동 가드. 발사체 hit_radius overshoot
> 결함 (DECISION-DT1-P4B-005 시뮬레이터 우회 사유) 정식 해결.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| CB-01 | 정지 타겟에 정면 충돌 (legacy 동작 보존) | — | — | ✓ | — | — | — | — | — | — |
| CB-02 | 도주하는 타겟을 빠른 발사체가 따라잡으면 명중 | — | — | ✓ | — | — | — | — | — | — |
| CB-03 | 빠른 타겟이 발사체 line 을 수직으로 가로지름 — swept-circle 동기 감지 | — | — | ✓ | — | — | — | — | — | — |
| CB-04 | 멀리 정지 타겟 + 느린 발사체 → 미명중 (false-positive 회귀 가드) | — | — | ✓ | — | — | — | — | — | — |
| CB-05 | hit_radius 경계 케이스 (안쪽 hit, 바깥쪽 no-hit) | — | — | ✓ | — | — | — | — | — | — |

> 보조 가드 (CB-06~10): dying 타겟 fly-through, target=None 스냅샷, legacy 타겟 (prev 좌표 없음) 호환, PathingSystem `_prev_x/_prev_y` 자동 갱신, 1000 px/s 고속 발사체 overshoot regression.

---

## Phase 5.1 신규 시나리오 — [BG] BGM 재생 회귀 (Issue #30, DECISION-AUDIO-013)

> BG-01~BG-04: Phase 5.1 BGM 백엔드(pygame.mixer) 구현 후 자동화 전환 예정.
> 현재: 모두 ✗ (자동화 대기 — BGM 백엔드 미구현, play_bgm stub 상태).
> `src/core/sound.py` play_bgm() Phase 5.1 구현 완료 시 ✓ 전환.

| # | 시나리오 | Menu | StageSelect | Battle | Ending | Font | DPI | Persistence | Audio | Tutorial |
|---|----------|------|-------------|--------|--------|------|-----|-------------|-------|----------|
| BG-01 | 메인 메뉴 진입 시 SoundManager.play_bgm("bgm.menu") 호출 — 예외 없음, BGM 시작 로그 확인 | ✗ | — | — | — | — | — | — | ✗ | — |
| BG-02 | 스테이지 전환(stage_01→stage_02) 시 BGM 페이드 아웃·인 — stop_bgm(fade_out=1.0) 후 play_bgm(fade_in=1.0) 순서 보장 | — | — | ✗ | — | — | — | — | ✗ | — |
| BG-03 | 일시정지(ESC) 시 BGM 볼륨 dimming — set_bgm_volume(0.2) 호출, 재개 시 원래 볼륨 복원 | — | — | ✗ | — | — | — | — | ✗ | — |
| BG-04 | 음소거 토글(mute/unmute) 시 BGM 정지·재개 — SFX mute와 BGM mute 독립 동작 검증 | ✗ | — | ✗ | — | — | — | — | ✗ | — |

> BG-01~BG-04: 자동화 대기 (Phase 5.1 본 작업 시 ✓ 전환).
> 자동화 방법 예정: `tests/test_sound_bgm.py` — pytest + pygame.mixer mock 패턴 (AU-07 선례).
> DECISION-AUDIO-013: pygame.mixer BGM 백엔드 채택 결정.

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
| Persistence | 신규 부분 커버 (test_tutorial_scene.py + test_regression_p4.py) | save_slot.tutorial_dismissed/completed 필드 가드 ✓ — player_data 본격 저장·로드는 Phase 4 후속 |
| Audio | 커버됨 (test_regression_p4.py + test_sound_simpleaudio.py) | AU-01~AU-07 ✓ (자동), AU-08 수동 검수 의존 (PyInstaller 빌드) |
| Tutorial | 신규 커버 (test_tutorial_scene.py 23건) | TU-01/02/03/05/09/10 ✓ (자동). TU-04/06/07/08 headless 불가 — 수동 검수. |

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
| v2.1 (Phase 4 R1) | 2026-05-19 | SCM (DECISION-SCM-P4-002) | PR #34/#36 머지 후 자동 가드 가능 시나리오 ✗→✓ 전환. TU-01/02/03/05/09/10 ✓ (자동 가드, test_tutorial_scene.py + test_regression_p4.py 활용). TU-04/06/07/08 은 headless 자동화 불가로 ✗ 유지(수동 검수 의존). BL-01/02/03/06 ✓ (test_stage_balance.py 자동 가드). BL-07 은 후속 라운드. |
| v2.2 (Phase 4 cleanup) | 2026-05-19 | QA Lead (DECISION-QA-P4M-003/004) | BL-07 ✗→✓ (PR #41, test_clear_rate_simulation.py 9건). AU-01~07 ✓ 확인 (PR #42, test_sound_simpleaudio.py 18건). pytest markers 5개 파일 일관 적용 (regression_p4 71건 선택 가능). markers 체계 표 추가. CI 3-step 분리. |
| v2.2 (Phase 5 준비) | 2026-05-19 | Dev Lead (DECISION-DL-P5P-001/002) | Phase 5 준비 라운드 신규 9 시나리오 추가: WV-01~05 (보스 path resolution, Issue #43) + CB-01~05 (Projectile swept-circle 충돌, Issue #44). 모두 자동 가드 (test_wave_boss_path.py 13건 + test_combat_sweep.py 11건). |
