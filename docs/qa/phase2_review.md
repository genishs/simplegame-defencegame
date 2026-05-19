# Phase 2 종합 리뷰 (Test Lead)

- 작성: Test Lead 페르소나 (시니어 QA + 코드 리뷰어)
- 날짜: 2026-05-19
- 리뷰 대상: Phase 2 4개 feature 브랜치
  - `feature/phase2-story` (PM 산출물) — HEAD `9d7c3f2`
  - `feature/phase2-wireframes` (Design) — HEAD `d075200`
  - `feature/phase2-impl-team1` (entities + combat/pathing) — HEAD `783c328`
  - `feature/phase2-impl-team2` (UI + scenes + wave) — HEAD `4b89e3f`
- 환경: 격리된 리뷰 clone(`C:\Users\user\AppData\Local\Temp\defensegame-review`), Python `PYTHONUTF8=1`, deps 설치 후 ruff/black/pytest 실행
- 베이스: `origin/develop` (`97c0d60`)

---

## 1. 브랜치별 단독 리뷰 결과

| 브랜치 | 산출물 점검 | 불변 규칙 | ruff | black | pytest | 결과 |
| --- | --- | --- | --- | --- | --- | --- |
| `feature/phase2-story` | 10개 문서 모두 존재(`00`~`09`), 라벨 사용 빈도 정상(파일당 3~15회), DECISION-S03/5B/E03 모두 명시 | N/A (문서) | N/A | N/A | N/A | **PASS** |
| `feature/phase2-wireframes` | `07/08/09` 라인 수 1757/759/1176 정합, 9개 화면(SCN-01~SCN-09) 모두 명세, 색약(DECISION-D-005/D-009), 3축 스케일(coords/images/fonts), `[픽션·승인대기]` 라벨 18회 사용 | N/A (문서) | N/A | N/A | N/A | **PASS** |
| `feature/phase2-impl-team1` | entities 6개(`entity/hero/ally/enemy/projectile/effect.py`) + systems(`combat/pathing.py`) 본구현, `PoolExhausted`/`free_count`/`active_count`/capacity 가드 정합, 신규 테스트 5종 모두 존재 | `src/systems/*`에 `import tkinter` 없음 (PASS) | All checks passed | All done | **89 collected / 89 passed** | **PASS** |
| `feature/phase2-impl-team2` | UI(`widgets/hud/dialog`) + scenes(`menu/stage_select/battle/ending`) + `wave.py` 본구현, BattleScene 시스템 호출 순서 `wave → pathing → combat → economy → hud` 정합, `pathing.update(dt)` 시그니처 일관, WaveSystem 오버슈트 dt 처리 검증 (wave.py L103~L108), 신규 테스트 5종 모두 존재 | `src/systems/wave.py`에 실제 `import tkinter` 없음(주석 라인만 존재) (PASS) | All checks passed | All done | **139 collected / 139 passed** | **PASS** |

### 세부 발견
- `src/scenes/battle_scene.py:140-157` 시스템 갱신 순서 정확히 명세대로 구현됨.
- `src/scenes/battle_scene.py:206-211` `_spawn_enemy`가 enemy x좌표를 하드코딩(`x=0.0`) — Phase 3 이슈로 권고 (아래 OPEN-T2-002 결정 참조).
- `src/data/stages/stage_01.json:40` `reward = { "gold": 200, "unlock": "stage_02" }` — `grain` 키 부재. `battle_scene.py:256`에서 `reward.get("grain", 0)` 폴백으로 안전 (아래 OPEN-T2-003 결정 참조).
- `src/entities/entity.py:20` `PoolExhausted` 모듈 최상위 정의 — Dev OPEN-T1-001 정합.

---

## 2. 통합 시뮬레이션 결과

권장 머지 순서로 `qa-merge-cascade` 임시 브랜치(베이스: `origin/develop`)에 4개 브랜치를 차례로 `git merge --no-ff` 실행.

| # | 머지 | 결과 |
| --- | --- | --- |
| 1 | `develop` ← `feature/phase2-story` | 충돌 0건 (문서 신규 추가만) |
| 2 | `develop` ← `feature/phase2-wireframes` | 충돌 0건 (문서 신규 추가만) |
| 3 | `develop` ← `feature/phase2-impl-team1` | 충돌 0건 (entities/systems 본구현 + 테스트 추가) |
| 4 | `develop` ← `feature/phase2-impl-team2` | 충돌 0건 (UI/scenes 추가, `wave.py` 본구현 갱신, BattleScene·HUD·dialog 본구현) |

### 통합 후 검증
- `python -m ruff check .` → **All checks passed!**
- `python -m black --check .` → **50 files would be left unchanged.**
- `python -m pytest` → **139 collected / 139 passed**

머지 충돌 없음. 통합 후 quality gate 0 에러.

---

## 3. DECISION-Q-### (OPEN 항목 결정)

본 Test Lead 권한으로 다음 OPEN 항목을 종결한다.

| ID | 항목 | 결정 | 근거 |
| --- | --- | --- | --- |
| **DECISION-Q-001** | PM OPEN-1: 픽션 캐릭터(모용손·향이·리우·장 등) 등장 승인 | **승인 (Approved)** | `[픽션]` 라벨로 사료와 명확히 분리, 디자인이 `[픽션·승인대기]` 시각 표지(18회 적용) 정의 완료. 향후 사용자 검토 여지 보존(단순 캐릭터 묶음). |
| **DECISION-Q-002** | PM OPEN-2: 워킹 트리 race 회피 | **종결 (Resolved)** | 별도 clone 전략(페르소나 isolation `worktree`)로 이미 해결됨. |
| **DECISION-Q-003** | PM OPEN-3: `ui_strings` / intro 토스트 중복 동기화 | **`docs/story/08_ui_strings.md` 단일 진실 원천(SSOT) 채택** | intro 및 기타 문서는 동일 키를 인용. 후속 PR에서 비-SSOT 사본을 키 참조로 치환 권고. |
| **DECISION-Q-004** | Dev OPEN-1 (sound): 사운드 라이브러리 | **`winsound` 기본 채택** | `tkinter` 표준 라이브러리 한정 정책 준수. 추가 의존성 없음. |
| **DECISION-Q-005** | Dev OPEN-T1-001: `PoolExhausted` 정의 위치 | **`src/entities/entity.py` 최상위 (현 상태) 채택** | 단일 진입점, 순환 의존 회피, 테스트가 직접 import 가능. |
| **DECISION-Q-006** | Design OPEN-D-001: 픽션 캐릭터 비주얼 | **Phase 2에서 플레이스홀더 5종 채택, Phase 3에서 상세 일러스트화** | PM OPEN-1 승인에 따른 후속 처리. |
| **DECISION-Q-007** | Design OPEN-D-002: 폰트 라이선스 | **Noto Sans KR (OFL) 채택, 폴백 `Malgun Gothic`** | 상용 배포 가능, 한국어 가독성 우수, PyInstaller bundling 용이. |
| **DECISION-Q-008** | Design OPEN-D-101: 컷씬 일러스트 18장 | **Phase 3 내부 작업 채택 (외주 보류)** | 일정·예산 변동 위험 회피. |
| **DECISION-Q-009** | Design OPEN-D-201 / Team2 OPEN-T2-001: 영웅 M키 직접 조작 | **Phase 3 상세 명세 후 구현. Phase 2에서는 플래그/바인딩만 유지** | 현재 `battle_scene.py:137-138`에 `m`/`M` 키 바인딩만 존재. |
| **DECISION-Q-010** | Team2 OPEN-T2-002: `_spawn_enemy` x=0.0 고정 | **Phase 2 현 동작 유지(테스트 그린), Phase 3 GitHub Issue 등록 — stage JSON 첫 waypoint 참조로 개선** | `battle_scene.py:211` 하드코딩. 1280x720 등 가변 캔버스에 대비해야 함. |
| **DECISION-Q-011** | Team2 OPEN-T2-003: `stage_01.json reward.grain` 누락 | **Phase 3 데이터 패치 PR로 등록, Phase 2 현 동작(grain=0 폴백) 유지** | `battle_scene.py:256`에서 안전한 `.get("grain", 0)` 폴백 작동. UX 영향 미미. |

---

## 4. SCM 인계 사항

SCM 페르소나가 Phase 2 종료 머지·태그·문서 갱신·이슈 등록 시 참고할 사항.

- **머지 순서 권고**: 위 통합 시뮬레이션과 동일하게 ① story → ② wireframes → ③ impl-team1 → ④ impl-team2를 `develop`에 `--no-ff` 머지. 4개 모두 충돌 없음을 본 리뷰에서 확인.
- **머지 충돌**: 없음. 추가 가이드 불필요.
- **v0.2.0 태그 시점**: develop에 4건 모두 머지 후, `develop → main` 머지 commit에 `v0.2.0` annotated tag. 태그 메시지에 Phase 2 주요 추가(스토리/와이어프레임/entities/UI/wave) 요약 1단락.
- **README/CHANGELOG 갱신 항목** (Added/Changed):
  - Added: 스토리 10종(`docs/story/00`~`09`), 디자인 문서 3종(`docs/07/08/09`), entities 6종, UI 위젯/HUD/Dialog, Scenes 4종(menu/stage_select/battle/ending), WaveSystem 본구현, 통합 테스트 10건(WaveSystem/BattleScene/Dialog/HUD/ObjectPool/HeroPhases/EnemyFade/Projectile/Combat-Pathing 통합/wave_schedule_load)
  - Changed: `src/systems/wave.py` 본구현 갱신, BattleScene 시스템 호출 순서 명세화
  - Tests: 89 → 139 (50개 증가)
- **후속 GitHub Issue 등록 권고**:
  1. `[Phase 3] BattleScene._spawn_enemy: stage JSON 첫 waypoint 참조로 spawn 좌표 일반화` (OPEN-T2-002 / DECISION-Q-010)
  2. `[Phase 3] stage_01.json reward.grain 키 추가 (UX 일관성)` (OPEN-T2-003 / DECISION-Q-011)
  3. `[Phase 3] 영웅 M키 직접 조작 모드 상세 명세 + 구현` (OPEN-D-201/T2-001 / DECISION-Q-009)
  4. `[Phase 3] ui_strings SSOT 일관화: intro/codex 등 중복 사본을 키 참조로 치환` (DECISION-Q-003)
  5. `[Phase 3] 픽션 캐릭터 5종 상세 일러스트화` (DECISION-Q-006)
  6. `[Phase 3] Noto Sans KR 번들링 + PyInstaller spec 갱신` (DECISION-Q-007)
- **불변 규칙 회귀 방지**: CI에 `! grep -rE "^(import|from) tkinter" src/systems` 가드 추가 권고.

---

## 5. 최종 권고

### **Pass** — 4개 브랜치를 `develop`로 머지 진행 권고

- 모든 단독 리뷰 PASS, 통합 시뮬레이션에서 충돌 0건, ruff/black/pytest 모두 그린.
- 불변 규칙(`src/systems/*`에 tkinter import 금지) 양 팀 모두 준수.
- 미해결 OPEN 항목은 본 리뷰에서 DECISION-Q-001~011로 모두 종결.
- 후속 개선 사항(OPEN-T2-002/003, M키 모드 등)은 Phase 3 GitHub Issue로 이관 권고 — Phase 2 머지를 차단할 정도의 결함 없음.