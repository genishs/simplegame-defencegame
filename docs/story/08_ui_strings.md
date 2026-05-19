# 08. UI 텍스트 모음 (UI Strings) — **SSOT (Single Source of Truth)**

> Phase 2 - 기획 파트 산출물 #9 (스토리). Phase 3.4에서 SSOT로 격상.
> 의존: `00_story_bible.md`, GDD §8(UI 와이어프레임), `docs/07_wireframes_visuals.md`
> 본 문서는 게임 내 메뉴·버튼·툴팁·메시지·유닛 설명·도움말 등 **모든 UI 텍스트**의 단일 진실 원천(SSOT)이다.
> 한국어 표준어, 가족 친화 톤. 키(KEY)는 향후 i18n을 고려해 영문 식별자로 부여.

---

## 결정 사항 (Phase 3.4 디자인 라운드 추가)

본 문서는 Phase 2에서 작성된 v1.0을 Phase 3.4 에서 **SSOT 격상 + 신규 키 7개 추가 + 컨벤션 명문화** 한 v1.1 이다.

| ID | 의사결정 | 근거 |
| --- | --- | --- |
| **DECISION-D-P3-001** | `docs/story/08_ui_strings.md` 를 모든 UI 문자열의 **SSOT** 로 채택. 다른 문서(`docs/07`, `docs/09`, story intro/ending 등)는 동일 문자열을 직접 정의하지 않고 **키로 인용** 한다. 단, **스토리 대본 자체 (인트로/엔딩 내레이션 본문, 캐릭터 대사)는 스토리 문서가 원천** 으로 본 문서가 다루는 SSOT 범위는 **UI 컴포넌트의 라벨/버튼/툴팁/메시지/토스트** 에 한정한다. | DECISION-Q-003 (`docs/qa/phase2_decisions.md`) |
| **DECISION-D-P3-001a** | 키 네이밍 컨벤션은 `<scene>.<component>.<role>` 패턴을 따른다 (자세한 규칙은 §0.1 참조). 기존 키들은 본 컨벤션과 호환되며, 위반 사례 없음을 본 라운드에서 검증. | 본 문서 §0.1 |
| **DECISION-D-P3-001b** | 신규 키 7건 (`cavalry.sortie`, `dialog.next`, `dialog.skip`, `intro.skip_confirm`, `help.tut1.welcome`, `help.tut2.choose_unit`, `help.tut3.place_unit`, `help.tut4.next_wave`, `help.tut5.skill`, `help.tut6.pause`) 을 추가 — `docs/07_wireframes_visuals.md` §6.5 / §8.10 / §24 (튜토리얼) 요청 반영. **실제로는 10건이 됐다 (help.tut* 가 6건이라 합계 10건)** — `docs/qa/phase2_review.md` 후속 권고와 `docs/07` 인계 체크리스트 §25.2 항목 종결. | 본 문서 §6, §8, §17 |
| **DECISION-D-P3-001c** | 향후 `src/data/ui_strings.json` 데이터 파일을 빌드 단계에서 자동 추출할 수 있도록, 본 문서의 모든 키 정의는 **표(`| KEY | 표시 텍스트 |`) 형식** 으로 통일한다. 자동 추출 빌드 스크립트는 Phase 3.5 / Phase 4 에서 도입 검토 (DECISION-Q-003 부속). | 본 문서 §0.2 |

상위 의사결정 추적:
- DECISION-Q-003 (`docs/qa/phase2_decisions.md` 행 9) — SSOT 채택 합의
- DECISION-D-P3-001 ~ 001c — Phase 3.4 디자인 라운드 본 작업에서 명문화

---

## 0. 페어 토의 메모

- **리더**: "UI 텍스트가 게임의 인상을 좌우한다. 짧고 단단하게. 영어식 번역체 금지."
- **팀원**: "동의. 모든 버튼은 4글자 이내, 모든 메시지는 한 줄. 툴팁은 두 문장 이내."
- **리더**: "실패·에러 메시지에 비난 톤 절대 금지. '곡식이 부족합니다' 같은 부드러운 정보 제공."

### DECISION 라벨

- **DECISION-U01**: 모든 버튼 텍스트는 한국어 자연체. "Save"는 "저장하기"가 아닌 "두기" 같은 자연어. (단, 일반 메뉴는 표준 한국어 게임 용어를 따른다 — "저장", "불러오기" 등.)
- **DECISION-U02**: 키(KEY)는 영문 snake_case. 본 문서가 i18n 리소스 파일의 1차 원천.
- **DECISION-U03**: 한자·전문용어는 항상 한글 + (한자) 병기. 툴팁은 평이한 풀이.

---

## 0.1 키 네이밍 컨벤션 (DECISION-D-P3-001a)

본 문서의 모든 KEY 는 다음 컨벤션을 따른다.

### 0.1.1 일반 패턴

`<scene>.<component>.<role>`

- **scene** — UI가 등장하는 화면/맥락의 짧은 식별자.
  - 예: `title`, `menu`, `stage_select`, `hud`, `pause`, `result`, `barracks`, `codex`, `settings`, `help`, `dialog`, `intro`, `credits`, `toast`, `alert`, `gain`, `boss`, `hero`, `enemy`, `unit`, `building`, `stage` (스테이지 메타).
- **component** — 화면 내 컴포넌트 / 객체 식별자.
  - 예: `grain`, `population`, `arrows`, `skill1`, `wave_progress`, `next_wave_in`, `new_game`, `continue`, `quit`.
- **role** — 표시 역할의 보조 라벨 (선택).
  - 예: `tooltip`, `confirm`, `subtitle`, `ready`, `cooldown`, `locked`, `name`, `cost`.

### 0.1.2 패턴 예시 정리

| KEY | scene | component | role |
| --- | --- | --- | --- |
| `hud.grain` | hud | grain | (없음) |
| `hud.grain.tooltip` | hud | grain | tooltip |
| `menu.new_game` | menu | new_game | (없음) |
| `pause.resume` | pause | resume | (없음) |
| `result.win.title` | result | win | title |
| `unit.archer.tooltip` | unit | archer | tooltip |
| `boss.liu.subtitle` | boss | liu | subtitle |
| `dialog.next` | dialog | next | (없음) |
| `help.tut1.welcome` | help | tut1 | welcome |
| `stage.01.name` | stage | 01 | name |

### 0.1.3 예외 / 합의된 변형

- **2단계 키** (예: `dialog.confirm`, `menu.quit`) 는 component 만 있고 role 이 비는 형태로 허용한다. UI 가 단일 의미 라벨 1건만 필요한 경우 자연스럽다.
- **4단계 키** (예: `result.win.message.s1`, `barracks.tier1.desc`) 는 카테고리(`result.win.*`)의 하위 항목 분기가 필요한 경우 허용. role 위치에 한 단계 더 들어가는 형태.
- **숫자 식별자** (`stage.01.name`, `barracks.tier1.cost`, `help.tut3.place_unit`) 는 `01`/`02` 두 자릿수 또는 `tier1`/`tut3` 같이 명확한 접두를 붙인다.
- **plural / template 슬롯** (`{seconds}`, `{count}`, `{current}/{total}`) 은 본 문서 표 안의 표시 텍스트에 직접 노출되며, 런타임 lookup 후 Python `str.format()` 으로 채운다.

### 0.1.4 금지

- 한국어 키 금지 (DECISION-U02).
- 점(.) 이외 분리자 (예: `-`, `_` 만으로 단계 분리) 금지. (component 내부 단어 결합은 snake_case 로 사용.)
- 동일 키의 다른 텍스트가 두 군데 이상에서 직접 정의되는 형태 금지 (SSOT 위반).

---

## 0.2 SSOT 운영 규칙 (DECISION-D-P3-001 / 001c)

### 0.2.1 본 문서의 범위

본 문서가 SSOT 인 범위:

- 메뉴/HUD/패널/모달의 **버튼 텍스트, 라벨, 툴팁, 상태 메시지, 알림(토스트), 결과 화면 문구, 단축 설명 (help.*)**.
- 캐릭터/유닛의 **표시 이름과 코덱스용 짧은 라벨**.

본 문서의 범위가 **아닌** 것 (스토리 문서가 원천):

- 인트로/엔딩 내레이션 본문 (예: "645년 봄, 당의 깃발이 요동으로 향했다.")
  - 출처: `docs/story/01_intro.md`, `docs/story/07_ending.md`
- 캐릭터 대사 (양만춘/모용손 등) — 스토리 문서가 원천.
  - 출처: `docs/story/00_story_bible.md`, 각 stage 스크립트.
- 코덱스 카드의 **본문** (해설문) — `docs/story/09_codex.md` 가 원천.

### 0.2.2 인용 방식

다른 문서가 UI 문자열을 언급할 때:

- 표 셀 안에 텍스트를 직접 쓰지 말고 **KEY 만** 표기한다. (예: 와이어프레임의 컴포넌트 표 "KEY" 열에 `dialog.next` 만 적고 텍스트 "다음" 은 본 문서에서 lookup.)
- 본문 중 텍스트를 예시로 보여주는 경우 코드 블록(``` ``` ```)으로 감싸고 끝에 KEY 출처를 명시한다.
  ```
  > "곡식이 부족하오."  (alert.grain_short)
  ```
- 같은 텍스트가 두 화면에 등장하면 둘 다 같은 KEY 를 인용해야 한다 (예: `dialog.skip` 은 인트로 + 엔딩 컷씬 양쪽에서 사용).

### 0.2.3 코드 인계 (DECISION-D-P3-001c)

향후 빌드 / 런타임 자동화 경로:

1. **Phase 3.4 (현재)** — 본 문서가 SSOT, 코드는 한국어 문자열을 lookup 함수 (`ui_strings(key)`) 를 통해 접근하도록 점진 이관 (Issue #5 후속 PR / Phase 3.5).
2. **Phase 3.5 / Phase 4** — 빌드 스크립트가 본 문서의 표를 파싱해 `src/data/ui_strings.json` (또는 `.py` 딕셔너리) 을 생성. 데이터 파일은 git 에 커밋하지 않고 빌드 산출물로 처리.
3. **Phase 5** — i18n. 본 문서의 한국어 텍스트가 `ui_strings.ko.json` 가 되고, 다른 언어 추가 시 동일 KEY 로 `ui_strings.en.json` 등을 추가.

### 0.2.4 코드 grep 가드 (권고)

Phase 3.5 회귀 방지로 `tests/test_no_korean_literal_in_ui.py` 를 추가해 `src/ui/*.py`, `src/scenes/*.py` 안에 ui_strings KEY lookup 외의 한국어 리터럴이 들어 있으면 실패하도록 한다 (`docs/10_phase3_plan.md` R-P3-07 위험 완화).

### 0.2.5 정합성 확인

- 본 라운드 종료 시 점검 (디자인 라더 책임):
  - [x] 모든 키가 §0.1.1 컨벤션 준수
  - [x] 동일 텍스트의 중복 정의 0건
  - [x] `docs/07_wireframes_visuals.md` 의 컴포넌트 표에서 텍스트 직접 명세 → KEY 인용으로 치환 (§25.2 체크박스 종결)
  - [x] `docs/qa/phase2_review.md` 후속 권고 4번 (DECISION-Q-003) 종결

---

## 1. 타이틀 / 메인 메뉴

### 1.1 타이틀 화면

| KEY | 표시 텍스트 |
|---|---|
| `title.game_title` | 안시성: 88일의 약속 |
| `title.subtitle` | Ansi 88 |
| `title.press_to_start` | 화면을 누르면 시작합니다 |
| `title.version` | v0.1.0 |
| `title.copyright` | © 2026 안시성 645 기획팀 |

### 1.2 메인 메뉴 (버튼)

| KEY | 표시 텍스트 |
|---|---|
| `menu.new_game` | 새 게임 |
| `menu.continue` | 이어하기 |
| `menu.stage_select` | 스테이지 |
| `menu.barracks` | 병영 |
| `menu.codex` | 도감 |
| `menu.settings` | 설정 |
| `menu.credits` | 만든 사람들 |
| `menu.quit` | 종료 |

### 1.3 메뉴 부가 텍스트

| KEY | 표시 텍스트 |
|---|---|
| `menu.continue.no_save` | 저장된 진행이 없습니다. 새 게임을 시작하시오. |
| `menu.intro_replay` | 인트로 다시 보기 |
| `menu.quit.confirm` | 정말로 게임을 끝내시겠습니까? |

---

## 2. 스테이지 선택 화면

| KEY | 표시 텍스트 |
|---|---|
| `stage_select.title` | 스테이지 선택 |
| `stage_select.locked` | 잠금 — 이전 스테이지를 먼저 클리어하시오 |
| `stage_select.cleared` | 클리어 |
| `stage_select.best_stars` | 최고 별: {stars}/3 |
| `stage_select.play` | 도전하기 |
| `stage_select.back` | 돌아가기 |

### 2.1 스테이지 이름 (정식)

| KEY | 표시 텍스트 |
|---|---|
| `stage.01.name` | 1. 요동성의 첫눈 |
| `stage.01.subtitle` | 함락 직전의 한 시간 |
| `stage.02.name` | 2. 백암성의 항복 |
| `stage.02.subtitle` | 사람을 살리는 길 |
| `stage.03.name` | 3. 개모성의 횃불 |
| `stage.03.subtitle` | 어둠을 견딘 자 |
| `stage.04.name` | 4. 안시성 외곽 |
| `stage.04.subtitle` | 외성은 내어준다, 본성은 다르다 |
| `stage.05.name` | 5. 안시성 토산 |
| `stage.05.subtitle` | 88일의 약속 |

---

## 3. 인게임 HUD

### 3.1 자원 표시

| KEY | 표시 텍스트 |
|---|---|
| `hud.grain` | 곡식 |
| `hud.grain.tooltip` | 곡식(穀). 유닛을 모집하고 성벽을 복구하는 데 쓰입니다. |
| `hud.population` | 인구 |
| `hud.population.tooltip` | 동시에 둘 수 있는 병사의 수입니다. |
| `hud.arrows` | 화살 |
| `hud.arrows.tooltip` | 궁수가 공격할 때 한 발씩 소모됩니다. |
| `hud.fame` | 명성 |
| `hud.fame.tooltip` | 별로 얻은 명성. 병영에서 영구 강화에 쓰입니다. |

### 3.2 시간·웨이브

| KEY | 표시 텍스트 |
|---|---|
| `hud.wave_label` | 진군 |
| `hud.wave_progress` | 진군 {current}/{total} |
| `hud.timer` | 시각 |
| `hud.next_wave_in` | 다음 진군까지 {seconds}초 |
| `hud.preview` | 다음 진군 |
| `hud.day_counter` | {day}일째 |

### 3.3 게임 속도

| KEY | 표시 텍스트 |
|---|---|
| `hud.speed.1x` | 보통 속도 (1×) |
| `hud.speed.2x` | 빠르게 (2×) |
| `hud.speed.pause` | 일시정지 |
| `hud.speed.resume` | 다시 시작 |

### 3.4 양만춘 영웅 UI

| KEY | 표시 텍스트 |
|---|---|
| `hero.name` | 양만춘 |
| `hero.name_label` | 안시성주 양만춘 [전승] |
| `hero.hp` | HP {current}/{max} |
| `hero.skill1` | 일점사 |
| `hero.skill2` | 독려의 함성 |
| `hero.skill3` | 화살비 |
| `hero.ultimate` | 결사항전 |
| `hero.skill.ready` | 준비 완료 |
| `hero.skill.cooldown` | {seconds}초 |
| `hero.skill.locked` | 잠김 |
| `hero.respawn_in` | 잠시 후 다시 일어섭니다 ({seconds}초) |
| `hero.manual_mode.on` | 직접 조작 모드 ON (WASD/방향키 이동) |
| `hero.manual_mode.off` | 직접 조작 모드 OFF |

> `hero.manual_mode.*` 는 M 키 토글 시 좌하단 상태 라벨에 표시되는 직접조작 모드 표시 텍스트 (Issue #4, DECISION-DL-P3-3-002/007).

---

## 4. 좌측 패널 — 유닛 / 건물 선택

### 4.1 아군 유닛 이름·코스트

| KEY | 표시 텍스트 |
|---|---|
| `unit.archer.name` | 고구려 궁수 |
| `unit.archer.cost` | 곡식 10 / 인구 1 |
| `unit.spearman.name` | 고구려 창병 |
| `unit.spearman.cost` | 곡식 8 / 인구 1 |
| `unit.long_spearman.name` | 고구려 장창병 |
| `unit.long_spearman.cost` | 곡식 15 / 인구 1 |
| `unit.catapult.name` | 고구려 투석수 |
| `unit.catapult.cost` | 곡식 25 / 인구 2 |
| `unit.cavalry.name` | 고구려 기병 |
| `unit.cavalry.cost` | 곡식 30 / 인구 2 |

### 4.2 아군 유닛 툴팁 (마우스오버 시)

| KEY | 표시 텍스트 |
|---|---|
| `unit.archer.tooltip` | 고구려 궁수\n원거리에서 화살을 쏩니다. 사거리는 길지만 근접에 약합니다. 명적(鳴鏑) — 소리내며 날아가는 화살을 씁니다. |
| `unit.spearman.tooltip` | 고구려 창병\n성벽 가까이 다가오는 적을 막아 시간을 끕니다. 가장 저렴한 전열입니다. |
| `unit.long_spearman.tooltip` | 고구려 장창병\n긴 창으로 중장보병과 기병에 강합니다. 일반 보병에는 평범합니다. |
| `unit.catapult.tooltip` | 고구려 투석수\n돌을 날려 광역으로 데미지를 입힙니다. 사거리가 매우 길고 재장전이 느립니다. |
| `unit.cavalry.tooltip` | 고구려 기병\n사기 게이지가 차오르면 좌·우 출격구에서 측면으로 돌격합니다. 충차의 옆구리에 강합니다. |

### 4.3 건물 / 보조

| KEY | 표시 텍스트 |
|---|---|
| `building.torch.name` | 횃불 |
| `building.torch.cost` | 곡식 5 |
| `building.torch.tooltip` | 횃불\n야간에 시야를 만듭니다. 빛이 닿지 않는 곳의 적은 보이지 않습니다. |
| `building.granary.name` | 곡식 생산소 |
| `building.granary.cost` | 곡식 20 |
| `building.granary.tooltip` | 곡식 생산소\n시간당 곡식 +0.5. 성벽 밖에 짓기 때문에 적의 표적이 됩니다. |

---

## 5. 적 유닛 설명 (도감/툴팁)

### 5.1 적 유닛 이름

| KEY | 표시 텍스트 |
|---|---|
| `enemy.infantry.name` | 당군 보병 |
| `enemy.archer.name` | 당군 궁수 |
| `enemy.heavy.name` | 당군 중장보병 |
| `enemy.scout.name` | 당군 척후 |
| `enemy.cavalry.name` | 당군 기병 |
| `enemy.ram.name` | 당군 충차 |
| `enemy.tower.name` | 당군 공성탑 |
| `enemy.elite.name` | 당군 친위대 |

### 5.2 적 유닛 툴팁

| KEY | 표시 텍스트 |
|---|---|
| `enemy.infantry.tooltip` | 당군 보병\n가장 흔한 적입니다. 다수가 한꺼번에 옵니다. 궁수에 약합니다. |
| `enemy.archer.tooltip` | 당군 궁수\n원거리에서 화살을 쏩니다. 거리를 좁히면 약해집니다. |
| `enemy.heavy.tooltip` | 당군 중장보병\n무거운 갑옷을 입었습니다. 일반 화살에 강하지만 장창에 약합니다. |
| `enemy.scout.tooltip` | 당군 척후\n빠르고 은신을 합니다. 야간에는 횃불 빛 안에서만 보입니다. |
| `enemy.cavalry.tooltip` | 당군 기병\n빠른 돌격으로 전열을 무너뜨립니다. 장창에 약합니다. |
| `enemy.ram.tooltip` | 당군 충차(衝車)\n성문을 들이받습니다. 매우 단단하지만 옆구리에 약점이 있습니다. |
| `enemy.tower.tooltip` | 당군 공성탑(雲梯)\n성벽 높이까지 다가와 안에 든 궁수를 토해냅니다. 멀리서 막아야 합니다. |
| `enemy.elite.tooltip` | 당군 친위대\n황제 직속 정예입니다. 강하고 단단합니다. 마지막에 옵니다. |

### 5.3 보스 유닛

| KEY | 표시 텍스트 |
|---|---|
| `boss.liu.name` | 당의 척후대장 |
| `boss.liu.subtitle` | 리우(劉) |
| `boss.jang.name` | 당의 야습 부대장 |
| `boss.jang.subtitle` | 장(張) |
| `boss.iseje_ram.name` | 이세적의 정예 충차 |
| `boss.iseje_ram.subtitle` | 대총관 이세적이 보냈다 |
| `boss.taejong.name` | 당 태종 이세민 |
| `boss.taejong.subtitle` | 당의 황제 |

---

## 6. 일시정지 메뉴

| KEY | 표시 텍스트 |
|---|---|
| `pause.title` | 일시정지 |
| `pause.resume` | 계속하기 |
| `pause.restart` | 다시 시작 |
| `pause.settings` | 설정 |
| `pause.stage_select` | 스테이지 선택 |
| `pause.to_title` | 타이틀로 |

---

## 7. 클리어 / 패배 메시지

### 7.1 스테이지 클리어 화면

| KEY | 표시 텍스트 |
|---|---|
| `result.win.title` | 진군을 격퇴했습니다 |
| `result.win.stars` | 별 평가 |
| `result.win.star_1` | 클리어 |
| `result.win.star_2` | 성문 체력 유지 |
| `result.win.star_3` | 특별 목표 달성 |
| `result.win.fame_gained` | 명성 +{count} |
| `result.win.reward_grain` | 곡식 +{count} |
| `result.win.history_note` | 역사 노트가 도감에 추가되었습니다 |
| `result.win.next_stage` | 다음 스테이지로 |
| `result.win.replay` | 다시 도전 |
| `result.win.to_select` | 스테이지 선택 |

### 7.2 스테이지 패배 화면

| KEY | 표시 텍스트 |
|---|---|
| `result.lose.title` | 다시 매봅시다 |
| `result.lose.message.s1` | "여기서 막지 못하면, 안시성도 위태로워집니다." — 모용손 |
| `result.lose.message.s2` | "백암의 백성도 안시까지는 데려가야 하오." — 양만춘 |
| `result.lose.message.s3` | "어둠은 어렵소. 그러나 한 번 빛을 본 자는 두 번도 본다오." — 양만춘 |
| `result.lose.message.s4` | "외성을 내준 것은 작전이었으나, 본성을 잃은 것은 다른 이야기요." — 양만춘 |
| `result.lose.message.s5` | "안시성은 실제로도 88일이라는 긴 시간을 버텼습니다. 한 번에 되는 일이 아닙니다." |
| `result.lose.retry` | 다시 도전 |
| `result.lose.to_select` | 스테이지 선택 |
| `result.lose.to_title` | 타이틀로 |

### 7.3 별 3개 달성 시 보너스 메시지

| KEY | 표시 텍스트 |
|---|---|
| `result.three_stars.s1` | "한 사람도 잃지 않았소. 안시성에서도 그리 되기를." |
| `result.three_stars.s2` | "두 성을 등에 진 셈이오." |
| `result.three_stars.s3` | "어둠 속에서 한 명도 잃지 않았소. 안시까지 마지막 길이오." |
| `result.three_stars.s4` | "기병이 측면을 갈랐소. 이세적도 오늘 밤은 잠 못 이루겠소." |
| `result.three_stars.s5` | "약속을 지켰소." |

---

## 8. 자원·배치 알림

### 8.1 자원 부족 메시지 (부드러운 톤)

| KEY | 표시 텍스트 |
|---|---|
| `alert.grain_short` | 곡식이 부족하오. |
| `alert.population_full` | 인구가 가득 찼소. 병사를 잃은 뒤 다시 시도하시오. |
| `alert.arrows_low` | 화살이 부족하오. 근접 운영을 검토하시오. |
| `alert.slot_occupied` | 이 자리에는 이미 누군가 서 있소. |
| `alert.invalid_placement` | 이곳에는 배치할 수 없소. |
| `alert.skill_cooldown` | 아직 준비가 안 됐소. {seconds}초 더. |
| `alert.skill_locked` | 이 스킬은 아직 잠겨 있소. |
| `alert.cavalry_not_ready` | 사기가 차야 출격할 수 있소. |

### 8.2 자원 회복·획득

| KEY | 표시 텍스트 |
|---|---|
| `gain.grain` | 곡식 +{count} |
| `gain.arrows` | 화살 +{count} |
| `gain.fame` | 명성 +{count} |
| `gain.wave_clear` | 진군 격퇴! 곡식 +{grain}, 화살 +{arrows} |

---

## 9. 병영 (메타 강화 트리)

| KEY | 표시 텍스트 |
|---|---|
| `barracks.title` | 병영 — 강화 |
| `barracks.fame_balance` | 보유 명성: {count} |
| `barracks.tier1.name` | 단단한 갑옷 |
| `barracks.tier1.desc` | 모든 아군의 체력이 10% 늘어납니다. |
| `barracks.tier1.cost` | 명성 3 |
| `barracks.tier2.name` | 잘 벼린 화살촉 |
| `barracks.tier2.desc` | 궁수와 양만춘의 공격력이 10% 늘어납니다. |
| `barracks.tier2.cost` | 명성 5 |
| `barracks.tier3.name` | 풍년 |
| `barracks.tier3.desc` | 시작 곡식 +30, 곡식 자동 생산 +0.2/초. |
| `barracks.tier3.cost` | 명성 8 |
| `barracks.tier4.name` | 군기 |
| `barracks.tier4.desc` | 인구 상한 +2. 병사 회복 속도가 2배 빨라집니다. |
| `barracks.tier4.cost` | 명성 12 |
| `barracks.tier5.name` | 안시의 정신 |
| `barracks.tier5.desc` | 양만춘 궁극기 쿨다운 -30초, 부활 쿨다운 -20초. |
| `barracks.tier5.cost` | 명성 18 |
| `barracks.unlock` | 해금하기 |
| `barracks.unlocked` | 해금됨 |
| `barracks.locked` | 잠김 |
| `barracks.requires_prev` | 이전 강화를 먼저 해금하시오. |
| `barracks.requires_fame` | 명성이 부족하오. |

---

## 10. 도감 (코덱스)

| KEY | 표시 텍스트 |
|---|---|
| `codex.title` | 도감 |
| `codex.tab.history` | 역사 노트 |
| `codex.tab.units` | 유닛 |
| `codex.tab.enemies` | 적 |
| `codex.tab.heroes` | 영웅 |
| `codex.locked` | 잠김 — 해당 스테이지를 클리어하시오 |
| `codex.label.fact` | (사실) |
| `codex.label.legend` | [전승] |
| `codex.label.fiction` | [픽션] |
| `codex.note.about_legend` | "[전승]은 정사에는 기록이 없으나 후대의 야사·전승으로 전해지는 내용입니다. 본 게임은 한국 대중에 친숙한 점을 고려해 라벨과 함께 사용합니다." |
| `codex.note.about_fiction` | "[픽션]은 본 게임이 이야기 전개를 위해 창작한 인물·장면입니다. 사료에는 등장하지 않습니다." |

---

## 11. 설정 메뉴

| KEY | 표시 텍스트 |
|---|---|
| `settings.title` | 설정 |
| `settings.audio` | 소리 |
| `settings.master_volume` | 전체 음량 |
| `settings.bgm_volume` | 배경음악 |
| `settings.sfx_volume` | 효과음 |
| `settings.display` | 화면 |
| `settings.fullscreen` | 전체 화면 |
| `settings.windowed` | 창 모드 |
| `settings.text_size` | 글씨 크기 |
| `settings.text_100` | 보통 |
| `settings.text_125` | 크게 |
| `settings.text_150` | 더 크게 |
| `settings.colorblind` | 색약 모드 |
| `settings.colorblind.on` | 켜짐 |
| `settings.colorblind.off` | 꺼짐 |
| `settings.subtitle` | 자막 |
| `settings.subtitle.on` | 항상 켜짐 |
| `settings.keybind` | 키 설정 |
| `settings.save` | 저장 |
| `settings.cancel` | 취소 |
| `settings.reset` | 기본값으로 |

---

## 12. 도움말 (?) — 첫 플레이 가이드

| KEY | 표시 텍스트 |
|---|---|
| `help.title` | 도움말 |
| `help.section.basic` | 기본 조작 |
| `help.basic.click` | 좌클릭으로 유닛을 고르고, 다시 좌클릭으로 빈 칸에 배치합니다. |
| `help.basic.right_click` | 우클릭으로 선택을 취소하거나, 배치된 유닛을 회수할 수 있습니다. |
| `help.basic.space` | 스페이스 키로 일시정지합니다. |
| `help.basic.speed` | F 키로 게임 속도를 보통/빠르게 전환합니다. |
| `help.section.resources` | 자원 |
| `help.resources.grain` | 곡식은 시간에 따라 자동으로 늘어납니다. 유닛 배치와 성벽 복구에 씁니다. |
| `help.resources.population` | 인구는 동시에 둘 수 있는 병사 수입니다. 병사를 잃으면 잠시 후 회복됩니다. |
| `help.resources.arrows` | 화살은 궁수가 공격할 때 줄어듭니다. 부족하면 근접 유닛을 활용합니다. |
| `help.section.hero` | 양만춘 |
| `help.hero.skills` | Q, W, E 키로 양만춘의 스킬을 발동합니다. R 키는 궁극기입니다. |
| `help.hero.control` | 스테이지 5에서는 M 키로 양만춘을 직접 움직일 수 있습니다. |
| `help.section.history` | 역사 |
| `help.history.codex` | 스테이지를 클리어할 때마다 역사 노트가 도감에 한 장씩 추가됩니다. |

---

## 13. 알림 / 토스트

| KEY | 표시 텍스트 |
|---|---|
| `toast.autosave` | 자동 저장되었습니다. |
| `toast.codex_unlocked` | 새 역사 노트가 도감에 추가되었습니다. |
| `toast.skill_unlocked` | 새 스킬이 해금되었습니다. |
| `toast.first_legend_label` | [전승]은 후대 전승으로 전해진 내용입니다. 정사에 직접 기록은 없습니다. |
| `toast.first_fiction_label` | [픽션]은 본 게임이 창작한 보조 인물·장면입니다. |
| `toast.about_intro_characters` | 이 게임의 등장인물 중 양만춘은 후대 전승에 따른 이름이며, 부장 모용손·향이 모자는 본 게임의 창작 인물입니다. 안시성 전투의 큰 줄기는 사료를 따랐습니다. |

---

## 14. 만든 사람들 (Credits)

| KEY | 표시 텍스트 |
|---|---|
| `credits.title` | 만든 사람들 |
| `credits.planning` | 기획 |
| `credits.design` | 디자인 |
| `credits.development` | 개발 |
| `credits.sources` | 역사 자문 |
| `credits.sources.list` | 삼국사기 / 자치통감 / 한국민족문화대백과사전 / 우리역사넷 |
| `credits.music` | 음악 |
| `credits.illustration` | 일러스트 |
| `credits.thanks` | 특별 감사 |
| `credits.thanks.text` | 88일을 버텼던 모든 이들에게 |
| `credits.back` | 돌아가기 |

---

## 15. 종료 / 다이얼로그

| KEY | 표시 텍스트 |
|---|---|
| `dialog.confirm` | 확인 |
| `dialog.cancel` | 취소 |
| `dialog.yes` | 예 |
| `dialog.no` | 아니오 |
| `dialog.ok` | 알겠소 |
| `dialog.close` | 닫기 |
| `dialog.next` | 다음 |
| `dialog.skip` | 건너뛰기 |
| `dialog.quit.title` | 게임 종료 |
| `dialog.quit.message` | 정말로 안시성을 떠나시겠습니까? 저장하지 않은 진행은 사라집니다. |
| `dialog.restart.title` | 다시 시작 |
| `dialog.restart.message` | 이 스테이지를 처음부터 다시 시작하겠습니까? |

> `dialog.next` / `dialog.skip` 은 인트로 (SCN-03) 및 엔딩 (SCN-10) 컷씬의 공통 컨트롤 버튼 (DECISION-D-P3-001b).

---

## 16. 인트로 / 엔딩 컷씬 컨트롤

본 섹션은 와이어프레임 §6.5 / §13 컷씬 공통 UI 텍스트.

| KEY | 표시 텍스트 |
|---|---|
| `intro.skip_confirm` | 인트로를 건너뛰시겠습니까? 도감에서 다시 볼 수 있습니다. |

> 컷씬 본문(내레이션)은 `docs/story/01_intro.md`, `docs/story/07_ending.md` 가 원천 (SSOT 범위 외, §0.2.1).
> 컷씬 컨트롤 버튼 라벨은 §15 `dialog.next` / `dialog.skip` 을 공유한다.

---

## 17. 인게임 전투 — 기병 출격 / 튜토리얼

본 섹션은 와이어프레임 §8.10 (전투 HUD) 과 §24 (튜토리얼) 의 신규 KEY.

### 17.1 기병 출격

| KEY | 표시 텍스트 |
|---|---|
| `cavalry.sortie` | 기병 출격 |

> 사기 게이지 100% 도달 시 우패널 PRV-07 버튼에 표시 (와이어프레임 §8.6.3). 클릭 시 좌·우 출격구에서 기병이 측면으로 돌격 — `unit.cavalry.tooltip` 참조.

### 17.2 튜토리얼 풍선 도움말 (첫 플레이)

스테이지 1 초기 6단계 풍선 도움말. 양만춘 본인의 톤(`~하시오`)으로 통일.

| KEY | 표시 텍스트 |
|---|---|
| `help.tut1.welcome` | 위에 자원이 있소. 곡식 134 — 이걸로 병사를 모집하시오. |
| `help.tut2.choose_unit` | 왼쪽에서 궁수를 골라 보시오. 클릭하면 마우스를 따라옵니다. |
| `help.tut3.place_unit` | 성벽 위 빈 칸에 클릭으로 배치하시오. |
| `help.tut4.next_wave` | 오른쪽에 다음 진군 정보가 있소. 적이 무엇인지 확인하시오. |
| `help.tut5.skill` | 양만춘의 스킬은 Q/W/E. 한 번 발동해 보시오. |
| `help.tut6.pause` | 잠시 멈추고 싶으면 스페이스, 또는 위 버튼을 누르시오. |

> 풍선 도움말의 표시 위치는 `docs/07_wireframes_visuals.md` §24 / §8.7 (LOG-03) 에 명세. 진행 조건 (예: 자원이 보일 때, 첫 클릭 후) 은 `docs/09_animation_state_diagrams.md` 의 튜토리얼 상태도 참조.

---

## 18. 페어 토의 — 최종 합의

- **리더**: "양만춘 본인의 1인칭/2인칭은 '~하시오/하오/하시오' 위주. 영웅 + 정중함의 균형. 패배 메시지에 짧은 인용 한 줄씩 넣어 톤 일관."
- **팀원**: "동의. 자원 부족 알림도 영웅 톤. '곡식이 부족하오.' 같이 양만춘이 직접 알려주는 느낌."
- **리더**: "[전승]·[픽션] 라벨 설명을 코덱스 진입 시 1회 안내. 교육 가치 명제."
- **공통**: "본 문서가 i18n 리소스의 1차 원천. 개발 인계 시 JSON/Python 딕셔너리로 변환 가능."

**서명**: 기획 리더 / 기획 팀원
**다음**: `09_codex.md`

— UI 스트링 v1.0 끝 —

---

## 19. 변경 이력

| 버전 | 일자 | 작성자 | 내용 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-17 | 기획 리더 + 팀원 | 최초 작성. §1~§15. |
| v1.1 | 2026-05-19 | 디자인 리더 (Phase 3.4) | **SSOT 격상** (DECISION-D-P3-001). 키 네이밍 컨벤션 명문화 (§0.1). SSOT 운영 규칙 (§0.2). 신규 키 9건 추가: `dialog.next`, `dialog.skip`, `intro.skip_confirm`, `cavalry.sortie`, `help.tut1.welcome` ~ `help.tut6.pause`. `docs/qa/phase2_review.md` 후속 권고 4번 (DECISION-Q-003) 종결. |

— UI 스트링 v1.1 (SSOT) 끝 —
