# 13. 초반 3스테이지 난이도 하향 정책 (Issue #27)

> Phase 4 · 기획 리더 산출물 #2 (Planning Lead, 2026-05-20).
> 의존: `src/data/stages/stage_01.json` ~ `stage_03.json`, `src/data/enemies.json`, `docs/03_game_design_document.md`, Issue #27.
> 본 문서는 **stage_01~03 난이도 하향 정책**의 5개 축 조정 비율, wave 수 축소 여부, 보상 상향 폭을 정의한다.
> 후반 stage_04~05의 난이도 곡선은 **변경 없음** (DOD 명시).
> 본 문서는 정책이며, 데이터 패치(.json) 실제 변경은 Dev Lead 다음 라운드에서 수행.

---

## 0. 페어 토의 메모 + 결정 라벨

- **리더**: "사용자 요청은 명확하다 — '매우 낮게'. 통상 -20%가 아니라 신규 플레이어가 자동 모드만으로 한 번에 클리어 가능한 수준."
- **리더**: "stage_01은 이미 가장 쉽다(3 wave). 여기까지 더 깎으면 학습 기회가 사라진다. stage_01은 보상만 상향."
- **리더**: "stage_02/03이 진짜 문제. wave 수 자체를 축소하고(6→4), 적 count -40%, 보상 +50% 정도가 적절."
- **리더**: "stage_03 야간 페널티는 신규 플레이어 좌절의 1순위. 시야 반경 +40% + 첫 wave를 단일 path로 단순화 권고."
- **리더**: "stage_04는 손대지 않음. 거기서 진짜 난이도 곡선이 시작된다."

### DECISION-PL-P4-009 ~ 016 (본 문서 누적)

| ID | 의사결정 | 근거 |
| --- | --- | --- |
| **DECISION-PL-P4-009** | 5개 축 조정 비율 확정: **(1) 적 count -40%, (2) 적 HP/속도 무변경, (3) spawn interval +30%, (4) 보상 grain +50%, (5) 야간 시야 반경 +40%**. HP/속도를 건드리면 enemies.json 데이터 자체에 글로벌 영향 (전체 스테이지 공유) — stage_04~05 영향 0 원칙 위반 위험. 따라서 stage JSON 내부에서 조정 가능한 count/interval/reward만 손댐. | DOD: stage_04~05 영향 0 |
| **DECISION-PL-P4-010** | wave 수 축소: **stage_01 3→3 (유지)**, **stage_02 6→4**, **stage_03 6→4**. stage_02/03의 wave 4·5는 적 조합이 wave 2·3과 유사한 점진 강화 — 신규 플레이어에게 인지 부하만 늘리고 학습 가치 낮음. 보스 wave는 마지막 1개로 유지. | 본 문서 §3 |
| **DECISION-PL-P4-011** | stage_01 예외: 적 count/interval/wave 수 **무변경**. 보상 grain만 50→100 (+100%, 다른 스테이지보다 큰 비율) 상향. 첫 스테이지의 즉시 보상감 강화 + 학습 곡선 유지의 균형. | 본 문서 §4 |
| **DECISION-PL-P4-012** | 목표 클리어율: **신규 플레이어가 자동 모드만으로 첫 시도 클리어 가능**. 본 정책 적용 후 stage_01~03 클리어율 95%+ 가정 (Dev Lead 다음 라운드 통합 테스트로 검증). | Issue #27 DOD |
| **DECISION-PL-P4-013** | stage_04~05 무변경 명시. enemies.json HP/speed/armor 등 글로벌 데이터 손대지 않음으로써 후반 곡선 자동 보존. | Issue #27 DOD |
| **DECISION-PL-P4-014** | 야간 페널티(stage_03) 완화 방식: **시야 반경 +40%**를 stage JSON 신규 필드 `night_vision_radius_multiplier: 1.4`로 전달하는 안 + 첫 wave를 `p_flank` 미사용(단일 path)으로 단순화. 신규 필드는 schema validator에 옵션 추가 필요 (Dev Lead 인계). | 본 문서 §5 |
| **DECISION-PL-P4-015** | 보상 grain 상향 폭: stage_01 +100%(50→100), stage_02 +50%(100→150), stage_03 +50%(150→225 → 반올림 220). gold 보상은 무변경 (그것은 다음 스테이지 시작 자금에 영향 없음, 단순 명성 환산). | 본 문서 §4 |
| **DECISION-PL-P4-016** | starting_gold 상향 검토 → **무변경**. starting_gold는 stage 진입 시점 자원이며, 초기치 상향은 첫 wave 전 다수 유닛 배치를 허용해 학습 효과를 떨어뜨림. wave 사이 보상으로 점진 누적시키는 게 학습 의도. | 본 문서 §6 |

---

## 1. 현재 stage_01~03 사양 요약

### 1.1 stage_01 — 요동성의 첫눈

- 자원: starting_gold=300, starting_population=10, lives=20
- paths: 1개 (`p_main`)
- build_zones: 2개
- waves: **3개**
  - W1: tang_soldier × 4, interval 0.8s (delay 3.0s)
  - W2: tang_soldier × 6, interval 0.7s (delay 8.0s)
  - W3 (boss): tang_soldier × 4 + boss `tang_scout_captain` (delay 10.0s, interval 0.8s)
- 적 총 수: 14 (보스 포함 14 + boss 1 = 15)
- reward: gold 200, grain 50, unlock stage_02

### 1.2 stage_02 — 백암성의 항복

- 자원: starting_gold=350, starting_population=12, lives=20
- paths: 1개
- build_zones: 4개
- waves: **6개**
  - W1: tang_soldier × 5
  - W2: tang_soldier × 6 + tang_archer × 3
  - W3: tang_soldier × 7
  - W4: tang_archer × 5 + tang_soldier × 4
  - W5: tang_soldier × 8 + tang_archer × 4
  - W6 (boss): tang_soldier × 6 + boss `tang_vanguard_captain`
- 적 총 수: 48 + boss
- reward: gold 250, grain 100, unlock stage_03

### 1.3 stage_03 — 개모성의 횃불 (야간 + 다중경로)

- 자원: starting_gold=400, starting_population=14, lives=20
- paths: 2개 (`p_gorge`, `p_flank`)
- build_zones: 5개
- waves: **6개**
  - W1: tang_scout × 4 (p_gorge)
  - W2: tang_scout × 5 + tang_soldier × 4 (양 경로)
  - W3: tang_soldier × 6 + tang_archer × 4 (양 경로)
  - W4: tang_scout × 6 + tang_soldier × 5 (양 경로)
  - W5: tang_heavy_infantry × 4 + tang_archer × 5 (양 경로)
  - W6 (boss): tang_scout × 5 + tang_soldier × 4 + boss `tang_night_raider`
- 적 총 수: 56 + boss
- reward: gold 300, grain 150, unlock stage_04

---

## 2. 하향 정책 — 5개 축

### 2.1 (축 1) 적 spawn count 감소: **-40%**

- 모든 spawn block의 `count`를 0.6배(소수점 올림). 단, count=1은 1 유지 (최소 1).
- stage_01: count 변경 없음 (DECISION-PL-P4-011).
- stage_02: 모든 wave count -40%.
- stage_03: 모든 wave count -40%.

### 2.2 (축 2) 적 HP / 속도 하향: **무변경**

- DECISION-PL-P4-009 — enemies.json은 전체 스테이지가 공유하므로 손대면 stage_04~05 영향 발생.
- stage_01~03 전용 HP/speed 오버라이드는 schema 확장 필요 → Phase 4 일정 압박. 본 라운드 미적용.
- 향후 (Phase 5 또는 후속) stage-level enemy stats override가 필요하면 별도 결정.

### 2.3 (축 3) spawn interval 증가: **+30%**

- 모든 spawn block의 `interval_s`를 1.3배(소수점 둘째 자리 반올림).
- 신규 플레이어가 spawn 간 반응 시간을 확보. 0.8 → 1.04 ≈ **1.0**, 0.7 → 0.91 ≈ **0.9**, 1.0 → 1.30, 1.2 → 1.56 ≈ **1.6**.
- stage_01: 무변경 (DECISION-PL-P4-011).
- stage_02/03: 적용.

### 2.4 (축 4) 보상 grain 상향

- stage_01: 50 → **100** (+100%, DECISION-PL-P4-011 + 015)
- stage_02: 100 → **150** (+50%)
- stage_03: 150 → **220** (반올림 — 약 +47%)
- gold 보상은 무변경.

### 2.5 (축 5) 야간 페널티 완화 (stage_03 전용)

- **신규 stage JSON 필드** (옵션): `night_vision_radius_multiplier: 1.4` — 횃불 등 시야 객체의 반경에 1.4 곱. (schema validator에서 0.5~2.0 범위 옵션 number로 허용 권고 → Dev Lead 인계)
- 만약 신규 필드 도입을 미루고 싶다면 대안: stage_03의 W1 첫 wave를 단일 path(`p_gorge`만)로 단순화하는 wave 변경만 적용. 본 명세는 둘 다 적용 권고 (시야 +40% + W1 단일 path).

---

## 3. wave 수 축소

### 3.1 stage_01: 3→3 (유지)

- 변경 없음. 첫 스테이지의 학습 가치 보존.

### 3.2 stage_02: 6→4

- 유지: W1, W2, W3, W6(boss)
- 제거: W4(tang_archer × 5 + tang_soldier × 4), W5(tang_soldier × 8 + tang_archer × 4)
- 사유: W4/W5는 W2/W3의 점진 강화로 학습 가치 낮음. boss wave만 유지하면 서사도 보존.
- 결과 적 총 수: count -40% 적용 후 5*0.6=3, (6+3)*0.6=5+2, 7*0.6=5, (6 boss + soldier)*0.6 = (4 + boss) → **약 19 + boss** (기존 48 + boss → -60% 효과).

### 3.3 stage_03: 6→4

- 유지: W1, W2, W3, W6(boss)
- 제거: W4(tang_scout × 6 + tang_soldier × 5), W5(tang_heavy_infantry × 4 + tang_archer × 5)
- 사유: W4/W5는 다양성 위주이며 신규 플레이어에게 인지 부하만 증가. heavy_infantry는 첫 등장이 stage_03 W5인데 본 정책에서는 stage_04로 미룸 (stage_04~05 데이터는 변경 없으니 자동 보존).
- 추가: W1은 `p_gorge`만 사용(단일 path)으로 단순화 (DECISION-PL-P4-014).
- 결과 적 총 수: 56 → 약 22 + boss (-60% 효과).

---

## 4. 변경 후 스펙 (목표 데이터 형태)

> 본 절은 Dev Lead 인계용. JSON 파일 직접 패치는 다음 라운드.

### 4.1 stage_01 (보상만 상향)

```
reward: { gold: 200, grain: 100, unlock: "stage_02" }
```

- 그 외 모두 동일.

### 4.2 stage_02 (4 wave, count -40%, interval +30%, reward +50%)

```
waves:
  W1: tang_soldier × 3  @ interval 1.0  (count 5→3, interval 0.8→1.0)
  W2: tang_soldier × 4  @ 0.9  +  tang_archer × 2 @ 1.3  (6→4, 3→2)
  W3: tang_soldier × 5  @ 0.9  (7→5)
  W4 (boss): tang_soldier × 4 @ 0.9 + boss tang_vanguard_captain  (6→4)
reward: { gold: 250, grain: 150, unlock: "stage_03" }
```

### 4.3 stage_03 (4 wave, count -40%, interval +30%, reward +50%, 야간 시야 1.4×, W1 단일 path)

```
night_vision_radius_multiplier: 1.4   (신규 필드)
waves:
  W1: tang_scout × 3 @ 1.3 (p_gorge만, single path)  (4→3, 1.0→1.3)
  W2: tang_scout × 3 @ 1.2 (p_gorge) + tang_soldier × 3 @ 1.0 (p_flank)  (5→3, 4→3)
  W3: tang_soldier × 4 @ 0.9 (p_gorge) + tang_archer × 3 @ 1.2 (p_flank)  (6→4, 4→3)
  W4 (boss): tang_scout × 3 @ 0.9 (p_gorge) + tang_soldier × 3 @ 1.0 (p_flank) + boss tang_night_raider  (5→3, 4→3)
reward: { gold: 300, grain: 220, unlock: "stage_04" }
```

---

## 5. 목표 클리어율

### 5.1 목표

- **신규 플레이어가 자동 모드만으로 첫 시도에 stage_01~03 모두 클리어 가능** (DECISION-PL-P4-012).
- 자동 모드 = M키 수동 모드 미사용, 영웅 AI에게 위임, 기본 유닛 배치만.

### 5.2 검증 방법 (Dev Lead 인계)

- `tests/test_balance_stages_01_03.py` 신규 — 자동 모드 mock 시뮬레이션 5회 반복, 95%+ 클리어 가드.
- 또는 회귀 매트릭스 (`docs/qa/regression_matrix.md`) 에 BAL-01~03 항목 추가 — 사용자 검수 카탈로그.

### 5.3 별 평가 영향

- 본 정책은 클리어 가능성을 높이는 것이 목표. 별 3개 달성 난이도는 **상대적으로 그대로** (별 평가는 명성 보상이고, 명성은 병영 강화 전용 → 본 정책의 grain 상향과 분리).
- 별 평가 목표값(`docs/03_game_design_document.md`)은 본 라운드에서 손대지 않음.

---

## 6. 부수 정책 (starting_gold / lives)

- `starting_gold`, `starting_population`, `lives` 무변경 (DECISION-PL-P4-016).
- 사유: 초기 자원 상향은 첫 wave 전 다수 유닛 배치를 허용 → 학습 효과 저하. 점진 누적 모델 유지.

---

## 7. stage_04~05 영향 0 — 명시 보존

- enemies.json 무변경 (DECISION-PL-P4-009/013).
- stage_04.json / stage_05.json 무변경.
- night_vision_radius_multiplier 신규 필드 도입 시 schema validator는 옵션 필드로 처리하므로 stage_04~05 (필드 없음)는 영향 없음.

---

## 8. 구현 인계 체크리스트 (Dev Lead 다음 라운드)

- [ ] `src/data/stages/stage_01.json` — reward.grain 50 → 100. 그 외 무변경.
- [ ] `src/data/stages/stage_02.json` — 6→4 wave 재구성 (W4/W5 제거), 모든 spawn count -40%, interval +30%, reward.grain 100 → 150.
- [ ] `src/data/stages/stage_03.json` — 6→4 wave 재구성, W1 single path, count -40%, interval +30%, reward.grain 150 → 220, **신규 필드 `night_vision_radius_multiplier: 1.4`**.
- [ ] `src/data/schema.py` — `night_vision_radius_multiplier` 옵션 필드 (0.5~2.0 범위, float).
- [ ] `tests/test_stage_data.py` (기존 40건) — stage_01/02/03 변경 반영. wave 수, count, interval, reward 검증 케이스 갱신.
- [ ] `tests/test_balance_stages_01_03.py` 신규 — 자동 모드 mock 5회 95%+ 클리어 가드 (BAL-01~03).
- [ ] `docs/qa/regression_matrix.md` 추가 항목 — BAL-01~03.

---

## 9. 변경 이력

| 버전 | 일자 | 작성자 | 내용 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-20 | 기획 리더 (Phase 4) | 최초 작성. 5축 조정 비율 확정, stage_01 보상만 상향, stage_02/03 wave 6→4 축소 + count -40% + interval +30% + reward +50%, 야간 시야 +40%, stage_04~05 무변경. DECISION-PL-P4-009~016. |

— 난이도 하향 정책 v1.0 끝 —
