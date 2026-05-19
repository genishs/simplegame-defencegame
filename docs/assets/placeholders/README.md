# Placeholder 자산 보관소

- 작성: Design Lead 페르소나 (Phase 3.4)
- 작성일: 2026-05-19
- 상위 문서: `docs/08_asset_inventory.md`, `docs/qa/phase2_decisions.md`

본 디렉토리는 **placeholder 만** 보관한다. 정식 자산(.png, .ttf 등)은 본 디렉토리에 두지 않는다.

---

## 결정 사항

| ID | 의사결정 | 근거 |
| --- | --- | --- |
| **DECISION-D-P3-004** | Placeholder (ASCII 시안 / 글리프 정의 / 컬러 가이드) 는 `docs/assets/placeholders/` 에 보관. 정식 PNG/TTF 자산은 Phase 4/5 에서 작업하여 `assets/` 본 폴더로 이관. | DECISION-P3-007 (`docs/10_phase3_plan.md`) — Phase 3 에서는 placeholder 까지만, 정식화는 Phase 4/5. |

---

## 1. 디렉토리 정책

### 1.1 본 디렉토리에 두는 것

- 캐릭터 / 컷씬 / UI 자산의 **placeholder 명세 문서** (Markdown).
- 한자 캘리그래피 글리프 / 단색 도형 / ASCII baseplate 시안.
- 라이센스 / 작성자 정보 (placeholder 라도 후일 정식 자산으로 교체 시 lineage 추적용).

### 1.2 본 디렉토리에 두지 않는 것

- 실제 PNG / SVG / 이미지 파일 — Phase 4/5 작업 후 `assets/images/...` 본 폴더로 직행.
- 폰트 파일 (`.ttf`, `.otf`) — `assets/fonts/` (Phase 3.4 Issue #7 별도 처리).
- 사운드 / BGM — 별도 산출물 (`docs/08_asset_inventory.md` §13).

### 1.3 정식화 시 이관 경로

| 본 디렉토리 (Phase 3) | 정식 경로 (Phase 4/5) |
| --- | --- |
| `docs/assets/placeholders/character_placeholders.md` (5종) | `assets/images/cutscenes/intro_p5_yang_silhouette.png` 등 / `assets/images/heroes/hero_yang_portrait.png` / 픽션 4종은 `assets/images/cutscenes/intro_p6_*.png` 등 |

이관 시 `docs/08_asset_inventory.md` §5 / §11 의 우선순위 표에서 "확보(placeholder)" → "확보(정식)" 으로 상태 업데이트한다.

---

## 2. 현재 placeholder 목록 (Phase 3.4 시점)

| 파일 | 종류 | 적용 영역 |
| --- | --- | --- |
| `character_placeholders.md` | 캐릭터 5종 (양만춘 + 픽션 4) | 인트로/엔딩 컷씬, 영웅 portrait, 코덱스 영웅 탭 |

향후 추가 예정 (Phase 3.5 또는 별도 라운드):
- `tile_placeholders.md` — 타일 8종 placeholder 시안
- `ui_placeholders.md` — 9-슬라이스 13종 placeholder 시안
- `effect_placeholders.md` — 이펙트 30종 placeholder 시안

---

## 3. 라이센스 / 저작권

- 본 디렉토리의 모든 placeholder 명세는 본 프로젝트 (안시성 디펜스) 자체 산출물이며, 본 프로젝트 사용권으로 묶인다.
- 한자 캘리그래피 글리프는 한자 자체의 자형(字形)이며 저작권 객체가 아니다. 다만 실제 PNG 화 시 사용하는 폰트의 라이센스를 `docs/08_asset_inventory.md` §12.3 의 표에 등록해야 한다.
- 정식 자산 작업 시 `OPEN-D-104` (한자 캘리그래피 폰트 라이센스) 를 그 시점에 종결한다.

---

## 4. 다음 작업

1. Phase 4 진입 시 본 README 의 §1.3 이관 표를 따라 정식 PNG 작업으로 승격.
2. PM OPEN-1 종결 (DECISION-Q-001) 에 따라 `[픽션]` → `[픽션]` 으로 라벨 교체 (`docs/07_wireframes_visuals.md` 등) — 본 라운드 (Phase 3.4) 에서 함께 처리.
3. Phase 3.5 통합 테스트 단계에서 placeholder ASCII 가 코드 (`src/scenes/intro_scene.py` 등) 에서 실제 그려지는지 시각 검수 — DECISION-D-109 (`docs/08_asset_inventory.md`) 의 "단색 + 한자 캘리" 정책에 정합.

— Placeholder README v1.0 (Phase 3.4) —