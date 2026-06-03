# 16. 교육 통합 구현 계획 (Education Build Plan) — Track A

> Phase 5 · 개발 PL(Dev Lead) 산출물.
> 선행: `docs/15_education_integration_spec.md` (교육 통합 스펙 v1.0, product-lead 확정) — MUST 7종(H1~H7)·라벨 규칙·인계 스키마.
> 정본 인용: `docs/story/09_codex.md` (코덱스 본문·라벨 SSOT), `docs/story/08_ui_strings.md` (UI 문자열 SSOT), `web/data/codex.json` (design-publisher 정본 콘텐츠).
> 본 문서가 다루는 것: *어느 파일을 어떻게* 만들/고치는지(파일 단위 태스크·의존 순서·테스트·회귀 위험). 신규 데이터 스키마 확정.
> 본 라운드에서 **데이터 기반(Wave 0)은 직접 구현 완료**. UI/씬 렌더링(Wave 1~3)은 developer 인계.

---

## 0. 코딩 표준 / 제약 (전 웨이브 공통)

- **ruff / black line-length 110** (pyproject.toml `[tool.ruff]`·`[tool.black]`). 커밋 전 `python -m black` + `python -m ruff check` 통과.
- **데이터/코드 분리**: 콘텐츠는 `src/data/*.json`, 로직은 `.py`. 한국어 표시 텍스트는 `08_ui_strings.md` SSOT(또는 데이터 정본 필드).
- **도메인 계층 tk-free 유지**: `src/systems/`·`src/entities/` 는 런타임 tkinter import 금지(`scripts/check_systems_no_tk.py`, `tests/test_systems_no_tk.py`). 교육 데이터/로더는 `src/data/`(tk-free)에 둔다. UI 렌더는 `src/ui/`·`src/scenes/`(tk 허용)에서만.
- **스키마 검증 stdlib-only**: `jsonschema`/`pydantic` 도입 금지(DECISION-DL-P3-001). `src/data/schema.py` 헬퍼(`_require_*`)만 사용.
- **비파괴 로딩**: 신규 필드는 전부 옵션(default None). 기존 JSON 에 없어도 로드되어야 한다(회귀 0).
- **라벨 무결성(EP2/R1~R5)**: 화면 노출 역사 서술은 (사실)/[전승]/[픽션] 중 하나로 분류. 라벨 텍스트 원천은 `codex.label.*` 단 하나(R2).

---

## 1. 신규 데이터 스키마 확정 (인계 계약)

> 본 절이 Wave 0 구현의 계약이며, 본 라운드에서 실제 반영·검증 완료.

### 1.1 `src/data/codex.json` (신설 — 코덱스 15장 메타 + 본문)

```jsonc
{
  "version": 1,
  "cards": [
    {
      "id": "codex_01",                     // ★필수 non-empty str, 카드 식별자(중복 금지)
      "title": "645년, 고구려와 당",          // ★필수
      "label": "fact",                       // ★필수 enum: fact | fact_adapted | legend | fiction
      "summary": "당 태종의 친정과 ...",       // ★필수 한 줄 요약(L2 카드 앞면)
      "body": "645년, ...\n...",             // ★필수 본문(문단 구분 \n). 09_codex.md 정본
      "source": "삼국사기, 자치통감, ...",      // ★필수 출처 줄(EP5)
      "unlock_condition": {                  // ★필수
        "type": "auto",                      // enum: auto | stage_clear | stage_three_stars | true_ending
        "stage": 1                           // stage_clear/stage_three_stars 일 때만 필수(1~5)
      },
      "source_original": "李世民",            // 옵션(H9): 한문 원문 — (사실) 라벨 카드 우선(DECISION-EDU-003)
      "source_reading": "이세민",             // 옵션(H9): 독음
      "source_translation": "당 태종"         // 옵션(H9): 짧은 풀이
    }
  ]
}
```

- 라벨 enum은 `fact_adapted`(언더스코어)로 정규화. web/data/codex.json 의 `fact-adapted`(하이픈)와 표기만 다름(게임 로더 키 규칙). 배지는 (사실) + 본문 각색 고지(R5).
- `source_original/reading/translation` 은 **(사실) 라벨 카드에만** 채움. [전승]/[픽션]엔 한문 원문 금지(EP2 — 야사를 사료처럼 보이게 하지 않음). 검증 테스트가 이를 가드.
- 본문 콘텐츠는 `09_codex.md` §2 / `web/data/codex.json` 정본을 재사용·정합화.

### 1.2 `src/data/units.json` — 유닛별 `history_blurb` (H3, 옵션 str)

```jsonc
"archer": { "...기존 필드...": "...", "history_blurb": "고구려는 활의 강국 ..." }
```

### 1.3 `src/data/enemies.json` — 적별 `intro_banner` (H2, 옵션 str)

```jsonc
"tang_soldier": { "...기존 필드...": "...", "intro_banner": "당군 보병이 밀려옵니다. ... — 궁수의 화살에 약합니다." }
```

- 문구 = 한 줄 소개 + 약점 힌트(스펙 §6.3).

### 1.4 `src/data/stages/stage_0[1-5].json` — `history_caption` (H1, 옵션 str)

```jsonc
{ "id": "stage_01", "title": "...", "history_caption": "645년 5월, 당군이 요동으로 ...", "...": "..." }
```

- GDD §13.1 의사스키마엔 있으나 실제 JSON 5종 전부 누락 → 신설.

### 1.5 스키마/로더 확장 (`src/data/schema.py` + `loader.py`)

- `schema.py`: `validate_codex()` 신설(라벨 enum `CODEX_LABELS`, unlock enum `CODEX_UNLOCK_TYPES`, stage 범위, id 중복, 옵션 한문 필드). 기존 `validate_stage/units/enemies` 에 옵션 필드(`history_caption`/`history_blurb`/`intro_banner`) non-empty 검증 추가.
- `loader.py`: `CodexCard`/`CodexUnlock` dataclass + `load_codex()` 신설. `UnitDef.history_blurb`·`EnemyDef.intro_banner`·`StageDef.history_caption` 필드 추가(default None) 및 매핑.

---

## 2. 웨이브별 구현 태스크 (파일 단위 분해)

### Wave 0 — 데이터/스키마/검증 토대 [본 라운드 완료]

| # | 파일 | 작업 | 상태 |
|---|---|---|---|
| 0-1 | `src/data/codex.json` | 신설. 15카드 메타+본문(09_codex 정본 정합) | ✅ |
| 0-2 | `src/data/units.json` | `history_blurb` 2유닛(archer/spear) | ✅ |
| 0-3 | `src/data/enemies.json` | `intro_banner` 6적 | ✅ |
| 0-4 | `src/data/stages/stage_0[1-5].json` | `history_caption` 5스테이지 | ✅ |
| 0-5 | `src/data/schema.py` | `validate_codex` + 옵션 필드 검증 | ✅ |
| 0-6 | `src/data/loader.py` | `CodexCard`/`load_codex` + 필드 매핑 | ✅ |
| 0-7 | `tests/test_education_data.py` | 신규 스키마/로더/정합 테스트 33건 | ✅ |
| 0-8 | `docs/story/08_ui_strings.md` | §22 신규 키군 등재 | ✅ |

의존: 0-1~0-4 → 0-5 → 0-6 → 0-7. (스키마 검증이 로더보다 먼저 통과해야 dataclass 매핑 가능.)

### Wave 1 — L1 인게임 즉시 노출 (툴팁/배너/캡션) [developer]

| # | 후크 | 신규/수정 파일(진입점) | 핵심 작업 |
|---|---|---|---|
| 1-1 | H1 도입 캡션 | `src/scenes/battle_scene.py`(스테이지 진입 hook) + `src/ui/` 신규 `caption_overlay.py` | `StageDef.history_caption` 을 스테이지 시작 시 화면 중앙 1줄 페이드(2초)·스킵 가능·모달 금지(EP1). `None` 이면 표시 생략 |
| 1-2 | H3 유닛 툴팁 | `src/ui/hud/`(유닛 패널 툴팁 렌더) | 기존 스탯 툴팁에 `UnitDef.history_blurb` 한 줄 추가. 호버 시에만 |
| 1-3 | H2 적 배너 | `src/systems/`(spawn 이벤트) + `src/ui/` 배너 위젯 | 적 타입 **최초 스폰 1회** `EnemyDef.intro_banner` 상단 배너 3초 자동 소멸. "노출됨" 플래그는 세션 상태(systems, tk-free). 렌더만 ui |
| 1-4 | H6 라벨 토스트 | `src/scenes/`/`src/ui/` 토스트 + 세션 상태 | [전승]/[픽션] 라벨 게임 내 **최초 1회** `toast.first_legend_label`/`toast.first_fiction_label`. 이후 배지만 |

> 주의(1-3·1-4): "최초 1회" 플래그 로직은 도메인 상태(systems/엔티티 세션)로 두어 tk-free 유지. UI는 상태를 구독해 렌더만.
> 주의(1-3 데이터 정합): 적 spawn 타입과 `enemies.json` 키 불일치 존재(§4 리스크 R-3) — 배너 lookup 은 `EnemyDef` 존재 키에 한해 동작하도록 graceful(없으면 배너 생략).

### Wave 2 — L2 결과 카드 (클리어 보상) [developer]

| # | 후크 | 파일(진입점) | 작업 |
|---|---|---|---|
| 2-1 | H4 결과 카드 | `src/scenes/`(결과 화면) + 신규 `src/ui/result_card.py` | 클리어 시 해당 스테이지 해금 카드 **앞면만 자동**(일러스트+제목+라벨 배지+NEW). 본문 강제 금지(DECISION-EDU-001). "도감에서 읽기" 버튼(`result.card.read_in_codex`) → L3 |
| 2-2 | 해금 매핑 | `src/data/loader.py`(이미 제공) + 세이브/진행 상태 모듈 | `unlock_condition`(stage_clear/three_stars/auto/true_ending) → 클리어 이벤트에 카드 해금. 진행 상태(획득 카드 집합)는 로컬 세이브(DECISION-EDU-004 오프라인) |

### Wave 3 — L3 도감 + 완성도 메타 + 충돌 노트 [developer]

| # | 후크 | 파일(진입점) | 작업 |
|---|---|---|---|
| 3-1 | H5 도감 화면 | 신규 `src/scenes/codex_scene.py`(메뉴 `menu.codex` 진입; `menu_scene.py` 에 라우팅 존재) | 09_codex §3 구조: 3×5 그리드 + 카드 상세. `load_codex()` 사용. 잠금 카드 회색+`codex.locked` |
| 3-2 | H5 완성도 메타 | codex_scene + 진행 상태 | 상단 "역사 노트 {n}/15"(`codex.progress.label`), 라벨 분포(`codex.progress.label_breakdown`), 5/10/15 칭호(`codex.progress.milestone_*`). **능력치 보상 없음**(EP1) |
| 3-3 | H9 한문 원문 토글 | 카드 상세 | (사실) 카드의 `source_original/reading/translation` 펼침/접힘(`codex.source.original_toggle`). 미입력 카드는 토글 숨김 |
| 3-4 | H8 충돌 노트 | 영웅 도감 상세 + 카드13/스테이지5 엔딩 | `hero.name_note`(C1)·`codex.conflict.taizong`(C2)·`codex.conflict.mound_days`(C3) — SHOULD |

### Wave 4 — H7 토산/추위 게이지 [developer, MUST]

| # | 후크 | 파일(진입점) | 작업 |
|---|---|---|---|
| 4-1 | H7 토산 게이지 | `src/systems/`(스테이지5 전용 게이지 상태) + `src/ui/`(게이지 위젯) + `stage_05.json` 메타 검토 | 토산/추위·사기 "버티기 승리" 게이지. 게이지 상태=systems(tk-free), 표시=ui. `stage_05.json` 에 `mound`/`morale` 메타 필드 신설 여부는 developer 판단(본 데이터 라운드 비강제) |

> 주의(4-1): 신규 stage 메타 필드를 추가하면 `validate_stage` 옵션 검증을 함께 확장하고 회귀 테스트 추가.

### Wave 5 (COULD) — H10 진엔딩 퀴즈 [developer, 선택]

| # | 파일 | 작업 |
|---|---|---|
| 5-1 | 신규 `src/data/quiz.json` + `validate_quiz`/`load_quiz` | 4문항(LO1~4) 데이터. 스킵 가능·오답 비차단(DECISION-EDU-002) |
| 5-2 | `src/scenes/`(진엔딩 분기) | 퀴즈 화면. `quiz.*` 키. 능력치 무관 보상 |

---

## 3. 테스트 전략

### 3.1 Wave 0 (완료) — `tests/test_education_data.py` 33건

- 코덱스: 검증 통과, **15장 고정**, 라벨 enum 전수, (사실)≥8 한문 채움, [전승]/[픽션] 한문 금지(EP2), unlock enum/stage 범위, id 중복 거부, 빈 body/빈 cards/비-dict 거부, 로더 매핑·순서·해금 매핑.
- units `history_blurb`: 전 유닛 존재(QA-EDU-04), 빈 문자열 거부, 부재 시 통과(비파괴), 로더 매핑.
- enemies `intro_banner`: 전 적 존재, 빈 거부, 부재 통과, 로더 매핑.
- stages `history_caption`: 5스테이지 전수 존재(QA-EDU-01 데이터 충족), 빈 거부, 부재 통과.

### 3.2 Wave 1~5 (developer) 권고 테스트

- **systems 단위(tk-free)**: 최초노출 플래그(H2/H6 — 같은 타입/라벨 2회째엔 토스트/배너 미발생), 카드 해금 매핑(클리어→카드 집합 증가, QA-EDU-07), 완성도 카운트·라벨 분포 계산, 토산 게이지 상태 전이(H7).
- **씬/UI smoke(headless)**: 기존 `tests/battle_scene_simulator.py` 패턴 재사용해 캡션/배너/결과카드/도감 렌더 호출이 예외 없이 수행되는지.
- **라벨 무결성 가드(QA-EDU-11, blocker)**: 코덱스/배너/캡션 텍스트에 라벨 없는 야사 단정이 없는지(전승/픽션 항목은 codex.json label 로 분류 가능). 이미 코덱스 enum 으로 보장; 배너/캡션은 (사실) 영역 텍스트만 사용.
- `tests/test_systems_no_tk.py` 그린 유지(신규 UI import 가 systems/entities 로 새지 않는지).

---

## 4. 회귀 위험 / 주의 (리스크 레지스터)

| ID | 위험 | 영향 | 완화 |
|---|---|---|---|
| **R-1** | 신규 옵션 필드가 기존 로더/검증을 깨뜨림 | 583+ 그린 붕괴 | 전 필드 default None·옵션 검증. Wave 0 풀 스위트 619 그린 확인 |
| **R-2** | 라벨 표기 불일치(web `fact-adapted` vs src `fact_adapted`) | 라벨 무결성·정합 혼선 | src 로더 enum 정규화(언더스코어) 확정·문서화(§1.1). UI 배지는 codex.label.* SSOT |
| **R-3** | 적 spawn 타입(`tang_heavy_infantry`·`tang_siege_tower`·`tang_cavalry`·`tang_elite_guard`)이 `enemies.json` 키에 없음(기존 데이터 분기) | H2 배너 lookup 실패 가능 | **본 데이터 라운드 범위 밖(기존 이슈)**. Wave 1-3 배너는 키 존재 시에만 표시(graceful). 별도 이슈로 적 로스터 정합 권고 |
| **R-4** | units.json 2종만 존재(web codex 5종) | H3 일부 유닛 blurb 누락 | 존재 유닛만 채움(archer/spear). 장창/투석/기병 추가 시 동일 패턴+`unit.history.*` 키. QA-EDU-04 는 "존재 유닛 전수" 기준 |
| **R-5** | H6/H2 "최초 1회" 상태가 tk 의존 코드로 흘러듦 | tk-free 가드 위반 | 플래그=systems 세션 상태, 렌더만 ui. `check_systems_no_tk` CI 가드 |
| **R-6** | 완성도 메타가 명성/병영 트리에 영향 | EP1 흐름·공정성 훼손 | 칭호·시각 보상만. 능력치 영향 금지(테스트로 가드 권고) |
| **R-7** | 결과 카드 본문 강제 노출 | EP1 위반(흐름 끊김) | DECISION-EDU-001: 앞면만 자동. 본문은 "도감에서 읽기" 자발 진입 |

---

## 5. QA-EDU 매핑 (스펙 §5.3 → 본 계획)

| QA-ID | 충족 웨이브 | 데이터 토대(Wave 0) |
|---|---|---|
| QA-EDU-01 (캡션 5/5) | 1-1 | `history_caption` 5종 + 테스트 |
| QA-EDU-03 (적 배너) | 1-3 | `intro_banner` 6종 + 테스트 |
| QA-EDU-04 (유닛 blurb) | 1-2 | `history_blurb` 전수 + 테스트 |
| QA-EDU-05 (라벨 토스트 1회) | 1-4 | 기존 토스트 키 재사용 |
| QA-EDU-02 (토산 게이지) | 4-1 | (Wave 4) |
| QA-EDU-06 (충돌 노트) | 3-4 | `hero.name_note`/`codex.conflict.*` 키 |
| QA-EDU-07 (카드 획득+게이지) | 2-1·2-2·3-2 | `unlock_condition` + 로더 |
| QA-EDU-08 (출처 100%) | 3-1 | 전 카드 `source` 필수(검증) |
| QA-EDU-09 (한문 토글) | 3-3 | (사실) 카드 한문 3필드 |
| QA-EDU-10 (퀴즈 스킵) | 5 (COULD) | quiz.json |
| QA-EDU-11 (라벨 무결성, blocker) | 전 웨이브 | codex label enum 검증 |

---

## 6. 변경 이력

| 버전 | 일자 | 작성자 | 내용 |
|---|---|---|---|
| v1.0 | 2026-06-03 | 개발 PL (Phase 5) | 최초 작성. 신규 스키마 확정(§1), 웨이브별 파일 단위 태스크(§2), 테스트 전략(§3), 리스크(§4), QA 매핑(§5). Wave 0 데이터 기반 직접 구현 완료(codex.json/units/enemies/stages + schema/loader + 테스트 33건 + ui_strings §22). |

— 교육 통합 구현 계획 v1.0 끝 —
