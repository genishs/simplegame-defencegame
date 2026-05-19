# 08. 자산 인벤토리 (Asset Inventory) — 안시성: 88일의 약속

> Phase 2 - 디자인 파트 산출물 #2
> 작성: 디자인 리더
> 작성일: 2026-05-17
> 인풋: `docs/07_wireframes_visuals.md` (컴포넌트·아이콘 KEY 정의), `docs/03_game_design_document.md` (§4, §5 유닛/적 명세), `docs/04_technical_architecture.md` (§2.4 이미지 처리)
> 본 문서는 게임에서 필요한 **모든 시각 자산**의 파일명·종류·픽셀·알파·형식·용량을 표로 정리하며 아트 파트(또는 외주)의 제작 사양 인계용이다.

---

## 0. 본 문서의 사용법

- **아트 파트에게**: 본 문서의 각 행이 작업 단위. `KEY`는 `docs/07_wireframes_visuals.md`의 KEY와 동일하며 코드의 자산 ID와 일치.
- **개발 파트에게**: `src/core/assets.py`의 AssetManager가 본 문서의 KEY를 받아 PNG를 로드. 사이즈는 베이스 크기 + Pillow LANCZOS 리사이즈로 다중 사이즈 캐시.
- **외주 작업 시**: 파일명 컨벤션 §1.2 엄수. 폴더 구조 §1.3.

### 자산 분류

1. **유닛 스프라이트** (§2): 아군 5종 + 영웅 1종 + 적 8종 + 보스 4종 = 18종
2. **건물·구조물 스프라이트** (§3): 횃불, 곡식 생산소, 성벽, 성문, 토산 등
3. **배경 일러스트** (§4): 5스테이지 × 1 배경 + 메인 메뉴 + 컷씬 18패널
4. **UI 자산** (§5): 9-슬라이스 13종, 아이콘 49종
5. **이펙트 / 투사체** (§6): 화살, 돌, 폭발, 사망 페이드
6. **데코레이션** (§7): 타일 (지형 8종), 파티클(대체용), 깃발
7. **시작 화면 / 마케팅** (§8): 스플래시, 아이콘(.ico)
8. **음향 큐 (참조용)** (§9): 본 산출물 아님. 사운드 자산 명세는 별도

---

## 1. 결정 사항 (DECISIONS)

| ID | 결정 | 근거 |
|---|---|---|
| **DECISION-D-101** | 모든 베이스 자산은 **PNG-32 (RGBA)** 알파 채널 포함. 단 배경 일러스트는 PNG-24(또는 PNG-8 인덱스). | docs/04 §2.4 |
| **DECISION-D-102** | 유닛/적/영웅 스프라이트는 **64×64 베이스** (큰 인물은 96×96 또는 128×128). 모두 정사각. | GDD §9.3 |
| **DECISION-D-103** | 애니메이션은 **스프라이트 시트** (가로 배치). 프레임 수 ≤ 4 (tkinter Canvas 한계). | docs/04 §2.4 |
| **DECISION-D-104** | 배경 일러스트는 **1920×1080 PNG-24** (알파 불필요). 톤 60% 명도. | docs/07 §13 |
| **DECISION-D-105** | UI 9-슬라이스는 **64×64 또는 80×80 PNG-32**. 슬라이스 마진 명시 (top, right, bottom, left). | docs/07 §23 |
| **DECISION-D-106** | 파일명은 영문 snake_case, 카테고리 prefix. 예: `ally_archer_idle.png`, `bg_stage_05_tosan.png`. | docs/07 KEY 컨벤션 |
| **DECISION-D-107** | 색상 인덱스 최적화: 배경은 PNG-8(인덱스 컬러, 256색) 시도 후 용량 ≥ 300KB이면 PNG-24로 폴백. | 빌드 최적화 |
| **DECISION-D-108** | 1차 작업물은 64x64 베이스로만, 리사이즈는 런타임 Pillow LANCZOS. PyInstaller 빌드 크기 최소화. | docs/04 §2.4 |
| **DECISION-D-109** | 픽션 캐릭터 스프라이트는 사용자 승인(OPEN-D-001) 후 작업. 사전 작업 시 플레이스홀더 (단색 + 한자 캘리). | PM OPEN-1 |
| **DECISION-D-110** | 총 자산 용량 목표 **≤ 50MB** (PyInstaller --onefile 빌드 시 압축 약 30MB). | docs/04 §1.1 |
| **DECISION-D-111** | 색약 모드 ON용 흑백 보조 글리프는 **단일 색 (#1A1410) PNG-32**로 별도 세트. KEY는 `_mono` 접미. | docs/07 §16.9 |

## 2. OPEN 사항

| ID | 항목 |
|---|---|
| **OPEN-D-101** | 컷씬 일러스트 18장의 외주 vs 내부 작업 결정 (아트 인력 부재) |
| **OPEN-D-102** | 픽션 캐릭터 5인의 비주얼 시안 (PM OPEN-1) |
| **OPEN-D-103** | 사운드 자산은 별도 산출물 — 현 단계는 게임 큐 시점 표시만 |
| **OPEN-D-104** | 한자 캘리그래피 폰트(서예 풍) — 라이선스 미정 |

---

## 1. 파일 컨벤션

### 1.1 파일 형식 표준

| 형식 | 알파 | 사용처 |
|---|---|---|
| **PNG-32 RGBA** | 있음 | 스프라이트, UI, 아이콘, 9-슬라이스 |
| **PNG-24 RGB** | 없음 | 배경 일러스트, 컷씬 패널 |
| **PNG-8 (인덱스 256색)** | 1비트 | 작은 단색 그래픽, 패턴 |
| **ICO** | 있음 | 윈도우 실행 파일 아이콘 |

### 1.2 파일명 컨벤션

`{category}_{subcategory}_{name}_{variant}.png`

| 카테고리 prefix | 설명 |
|---|---|
| `ally_` | 아군 유닛 스프라이트 |
| `hero_` | 영웅 (양만춘) 스프라이트 |
| `enemy_` | 적 유닛 스프라이트 |
| `boss_` | 보스 스프라이트 |
| `bld_` | 건물/구조물 |
| `bg_` | 배경 일러스트 |
| `intro_` | 인트로 컷씬 패널 |
| `end_` | 엔딩 컷씬 패널 |
| `ui_` | UI 컴포넌트 (9-슬라이스, 버튼 등) |
| `ico_` | 아이콘 |
| `fx_` | 이펙트, 투사체 |
| `tile_` | 타일 (지형) |

variant 예: `_idle`, `_walk`, `_atk`, `_death`, `_phase1`

### 1.3 폴더 구조

```
assets/
├── images/
│   ├── allies/          # ally_*.png
│   ├── heroes/          # hero_*.png
│   ├── enemies/         # enemy_*.png
│   ├── bosses/          # boss_*.png
│   ├── buildings/       # bld_*.png
│   ├── backgrounds/     # bg_*.png
│   ├── cutscenes/       # intro_*, end_*.png
│   ├── ui/              # ui_*.png
│   ├── icons/           # ico_*.png
│   ├── effects/         # fx_*.png
│   └── tiles/           # tile_*.png
├── fonts/               # (선택) 추가 한글 폰트
└── sounds/              # (별도 산출물)
```

### 1.4 사이즈 등급 (베이스 px)

| 등급 | 크기 | 사용처 |
|---|---|---|
| XS | 24×24 | 인라인 아이콘, 도트 마커 |
| S | 32×32 | 작은 UI 아이콘 |
| M | 48×48 | HUD 자원 아이콘 |
| L | 56×56 | 좌패널 유닛 카드 |
| XL | 64×64 | **스프라이트 표준** |
| XXL | 96×96 | 큰 적 (충차, 공성탑) |
| 3XL | 128×128 | 보스, 영웅 |
| 4XL | 256×256 | 컷씬 인물 클로즈업 |
| 풀스크린 | 1920×1080 | 배경, 컷씬 |
| 와이드 | 1920×820 | 컷씬 정지화 (텍스트 박스 위) |

---

## 2. 유닛 스프라이트 (18종)

각 유닛은 **idle / walk / attack / death** 4 애니메이션 × 2~4 프레임. 스프라이트 시트는 가로 배치.

### 2.1 아군 유닛 (5종)

| KEY | 파일명 | 크기 (단일 프레임) | 프레임 수 | 시트 크기 | 알파 | 형식 | 추정 용량 |
|---|---|---|---|---|---|---|---|
| `ally_archer` | `ally_archer.png` | 64×64 | idle:2, walk:2, atk:3, death:3 = 10 | 640×64 | O | PNG-32 | 30KB |
| `ally_spearman` | `ally_spearman.png` | 64×64 | idle:2, walk:2, atk:2, death:3 = 9 | 576×64 | O | PNG-32 | 28KB |
| `ally_long_spearman` | `ally_long_spearman.png` | 64×80 (긴 창 위로) | idle:2, walk:2, atk:3, death:3 = 10 | 640×80 | O | PNG-32 | 35KB |
| `ally_catapult` | `ally_catapult.png` | 96×96 | idle:2, atk:4, death:2 = 8 | 768×96 | O | PNG-32 | 45KB |
| `ally_cavalry` | `ally_cavalry.png` | 96×64 (말 포함) | idle:2, walk:3, atk:3, death:3 = 11 | 1056×64 | O | PNG-32 | 50KB |

### 2.2 영웅 - 양만춘 (1종, 페이즈 4단계)

양만춘은 게임 진행에 따라 외형이 변화한다 (DECISION-D-110a: 누적이 아닌 단계, GDD §3.1).

| KEY | 파일명 | 크기 | 프레임 구성 | 시트 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|---|
| `hero_yang_phase1` | `hero_yang_phase1.png` | 96×96 | idle:2, walk:2, atk:3, ult_cast:3, ult_active:3, death:3 = 16 | 1536×96 | O | PNG-32 | 70KB |
| `hero_yang_phase2` | `hero_yang_phase2.png` | 96×96 | 동일 | 1536×96 | O | PNG-32 | 70KB |
| `hero_yang_phase3` | `hero_yang_phase3.png` | 96×96 | 동일 | 1536×96 | O | PNG-32 | 70KB |
| `hero_yang_phase4` | `hero_yang_phase4.png` | 96×96 | 동일 | 1536×96 | O | PNG-32 | 70KB |
| `hero_yang_portrait` | `hero_yang_portrait.png` | 128×128 | 1 | 128×128 | O | PNG-32 | 15KB |

**페이즈 시각 차이** (누적 변화):
- Phase 1 (스테이지 1~2): 청 두루마기 + 황토 가슴판
- Phase 2 (스테이지 3): + 어깨에 깃발 (사기 진작 스킬 해금 표시)
- Phase 3 (스테이지 4): + 망토 (외성 방어 후 멋 더해짐)
- Phase 4 (스테이지 5): + 머리띠 + 갑옷 손상 흔적(흙·먼지) → 88일을 버틴 흔적

### 2.3 적 유닛 (8종)

| KEY | 파일명 | 크기 | 프레임 구성 | 시트 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|---|
| `enemy_infantry` | `enemy_infantry.png` | 64×64 | idle:2, walk:2, atk:2, death:3 = 9 | 576×64 | O | PNG-32 | 28KB |
| `enemy_archer` | `enemy_archer.png` | 64×64 | idle:2, walk:2, atk:3, death:3 = 10 | 640×64 | O | PNG-32 | 30KB |
| `enemy_heavy` | `enemy_heavy.png` | 64×80 (큰 갑옷) | idle:2, walk:2, atk:2, death:3 = 9 | 576×80 | O | PNG-32 | 35KB |
| `enemy_scout` | `enemy_scout.png` | 64×64 | idle:2, walk:3, atk:2, death:3 = 10 | 640×64 | O | PNG-32 | 28KB |
| `enemy_cavalry` | `enemy_cavalry.png` | 96×64 | idle:2, walk:3, atk:3, death:3 = 11 | 1056×64 | O | PNG-32 | 50KB |
| `enemy_ram` | `enemy_ram.png` | 128×96 (충차) | idle:1, walk:2, atk:3, death:3 = 9 | 1152×96 | O | PNG-32 | 70KB |
| `enemy_tower` | `enemy_tower.png` | 96×128 (공성탑) | idle:1, walk:2, deploy:3, death:3 = 9 | 864×128 | O | PNG-32 | 65KB |
| `enemy_elite` | `enemy_elite.png` | 64×80 (친위대) | idle:2, walk:2, atk:3, death:3 = 10 | 640×80 | O | PNG-32 | 38KB |

### 2.4 보스 (4종)

| KEY | 파일명 | 크기 | 프레임 구성 | 시트 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|---|
| `boss_liu` | `boss_liu.png` | 96×96 | idle:2, walk:2, atk:3, death:4 = 11 | 1056×96 | O | PNG-32 | 60KB |
| `boss_jang` | `boss_jang.png` | 96×96 | idle_stealth:2, idle:2, atk:3, death:4 = 11 | 1056×96 | O | PNG-32 | 60KB |
| `boss_iseje_ram` | `boss_iseje_ram.png` | 160×128 (큰 충차) | idle:1, walk:2, atk:3, death:4 = 10 | 1600×128 | O | PNG-32 | 110KB |
| `boss_taejong` | `boss_taejong.png` | 128×128 | idle:2, walk:2, atk:3, death:0, retreat:3, phase_transition:4 (4페이즈 별) | × 4 시트 (P1~P4) | O | PNG-32 | 4×80KB = 320KB |
| `boss_taejong_portrait` | `boss_taejong_portrait.png` | 256×256 | 1 (보스 등장 컷) | 256×256 | O | PNG-32 | 40KB |

### 2.5 유닛 스프라이트 합계

총 18종 + 양만춘 4페이즈 + 보스 초상화 2종 = **24개 PNG 파일**, 추정 용량 **약 1.4MB**.

---

## 3. 건물 / 구조물 / 환경 스프라이트 (12종)

### 3.1 건물 / 보조 시설

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `bld_torch_lit` | `bld_torch_lit.png` | 48×64 | 점등 애니메이션 4프레임 | O | PNG-32 | 25KB |
| `bld_torch_unlit` | `bld_torch_unlit.png` | 48×64 | 1 | O | PNG-32 | 5KB |
| `bld_granary` | `bld_granary.png` | 80×80 | idle:2, harvest:2, destroyed:1 = 5 | O | PNG-32 | 35KB |

### 3.2 성벽 / 성문

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `bld_wall_segment` | `bld_wall_segment.png` | 64×96 | 정상/손상50%/손상25%/파괴 = 4 | O | PNG-32 | 30KB |
| `bld_wall_corner` | `bld_wall_corner.png` | 64×96 | 동일 4단계 | O | PNG-32 | 30KB |
| `bld_gate` | `bld_gate.png` | 128×128 | 정상/손상/파괴 = 3 | O | PNG-32 | 55KB |
| `bld_bridge` | `bld_bridge.png` | 192×64 | 1 (스테이지 2) | O | PNG-32 | 25KB |

### 3.3 토산 (스테이지 5 전용)

토산은 시간에 따라 성장하는 동적 구조물. 3단계 + 붕괴 애니메이션.

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `bld_tosan_stage1` | `bld_tosan_stage1.png` | 192×128 (작은 흙더미) | 1 | O | PNG-32 | 40KB |
| `bld_tosan_stage2` | `bld_tosan_stage2.png` | 192×192 (중간) | 1 | O | PNG-32 | 50KB |
| `bld_tosan_stage3` | `bld_tosan_stage3.png` | 192×256 (성벽 높이) | 1 | O | PNG-32 | 70KB |
| `bld_tosan_collapse` | `bld_tosan_collapse.png` | 256×256 | 붕괴 6프레임 (먼지 + 흙 흩어짐) | O | PNG-32 | 150KB |

### 3.4 구조물 합계

총 12종, 추정 용량 **약 520KB**.

---

## 4. 배경 일러스트 (Backgrounds)

### 4.1 스테이지 배경 (5종)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 (PNG-24) | 용량 (PNG-8) |
|---|---|---|---|---|---|---|
| `bg_stage_01_yodong` | `bg_stage_01_yodong.png` | 1920×1080 | X | PNG-24 | 400KB | 180KB |
| `bg_stage_02_baekam` | `bg_stage_02_baekam.png` | 1920×1080 | X | PNG-24 | 420KB | 200KB |
| `bg_stage_03_gaemo_night` | `bg_stage_03_gaemo_night.png` | 1920×1080 | X | PNG-24 | 380KB | 160KB |
| `bg_stage_04_anseong_outer` | `bg_stage_04_anseong_outer.png` | 1920×1080 | X | PNG-24 | 450KB | 200KB |
| `bg_stage_05_anseong_tosan` | `bg_stage_05_anseong_tosan.png` | 1920×1080 | X | PNG-24 | 460KB | 200KB |

배경 톤:
- **STG1 요동성**: 봄, 옅은 하늘색, 옅은 안개 — 패배 직전의 분위기
- **STG2 백암성**: 초여름, 강이 보이는 평지, 따뜻한 톤
- **STG3 개모성 야간**: 어두운 청, 횃불 빛만 도드라짐
- **STG4 안시성 외곽**: 가을 초입, 약간 누런 톤
- **STG5 안시성 토산**: 가을~겨울, 회청색 + 황토 토산이 도드라짐

### 4.2 메인 메뉴 배경

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `bg_title` | `bg_title.png` | 1920×1080 | X | PNG-24 | 500KB |

안시성 원경 + 양만춘 실루엣 + 깃발. 가장 정성 들인 일러스트.

### 4.3 결과 / 메뉴 배경

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `bg_result_win` | `bg_result_win.png` | 1920×1080 | X | PNG-24 | 300KB |
| `bg_result_lose` | `bg_result_lose.png` | 1920×1080 | X | PNG-24 | 280KB |
| `bg_stage_select` | `bg_stage_select.png` | 1920×1080 | X | PNG-24 | 350KB |
| `bg_codex` | `bg_codex.png` | 1920×1080 | X | PNG-24 | 350KB |
| `bg_barracks` | `bg_barracks.png` | 1920×1080 | X | PNG-24 | 350KB |
| `bg_settings` | `bg_settings.png` | 1920×1080 | X | PNG-24 | 300KB |
| `bg_credits` | `bg_credits.png` | 1920×1080 | X | PNG-24 | 280KB |

### 4.4 스테이지 카드 썸네일

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `bg_stage_01_thumb` | `bg_stage_01_thumb.png` | 320×200 | X | PNG-24 | 25KB |
| `bg_stage_02_thumb` | `bg_stage_02_thumb.png` | 320×200 | X | PNG-24 | 25KB |
| `bg_stage_03_thumb` | `bg_stage_03_thumb.png` | 320×200 | X | PNG-24 | 22KB |
| `bg_stage_04_thumb` | `bg_stage_04_thumb.png` | 320×200 | X | PNG-24 | 25KB |
| `bg_stage_05_thumb` | `bg_stage_05_thumb.png` | 320×200 | X | PNG-24 | 28KB |

### 4.5 배경 합계

총 18장, 추정 용량 **약 5MB** (PNG-24 기준). PNG-8 폴백 시 약 2.5MB.

---

## 5. 컷씬 일러스트 (Cutscene Panels)

### 5.1 인트로 (10패널)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 | 라벨 |
|---|---|---|---|---|---|---|
| `intro_p1_map` | `intro_p1_map.png` | 1920×820 | X | PNG-24 | 250KB | (사실) |
| `intro_p2_taejong` | `intro_p2_taejong.png` | 1920×820 | X | PNG-24 | 280KB | (사실) |
| `intro_p3_yodong_fall` | `intro_p3_yodong_fall.png` | 1920×820 | X | PNG-24 | 300KB | (사실) |
| `intro_p4_anseong_walls` | `intro_p4_anseong_walls.png` | 1920×820 | X | PNG-24 | 280KB | (사실) |
| `intro_p5_yang_silhouette` | `intro_p5_yang_silhouette.png` | 1920×820 | X | PNG-24 | 260KB | [전승] |
| `intro_p6_moyong` | `intro_p6_moyong.png` | 1920×820 | X | PNG-24 | 270KB | **[픽션·승인대기]** |
| `intro_p7_villagers` | `intro_p7_villagers.png` | 1920×820 | X | PNG-24 | 290KB | **[픽션·승인대기]** |
| `intro_p8_yang_close` | `intro_p8_yang_close.png` | 1920×820 | X | PNG-24 | 280KB | [전승] |
| `intro_p9_dialogue` | `intro_p9_dialogue.png` | 1920×820 | X | PNG-24 | 290KB | **[픽션·승인대기]** |
| `intro_p10_oath` | `intro_p10_oath.png` | 1920×820 | X | PNG-24 | 270KB | [전승] |

### 5.2 인트로 플레이스홀더 (승인 전)

OPEN-D-001 차단 시 P6, P7, P9는 다음으로 대체:

| KEY | 파일명 | 크기 | 내용 |
|---|---|---|---|
| `intro_p6_placeholder` | `intro_p6_placeholder.png` | 1920×820 | 한자 "충(忠)" 캘리그래피 + 녹색 그라데이션 |
| `intro_p7_placeholder` | `intro_p7_placeholder.png` | 1920×820 | 한자 "민(民)" 캘리그래피 + 베이지 그라데이션 |
| `intro_p9_placeholder` | `intro_p9_placeholder.png` | 1920×820 | 인용 부호 "「」" 큰 + 양만춘 실루엣 |

### 5.3 엔딩 (8패널)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 | 라벨 |
|---|---|---|---|---|---|---|
| `end_p1_snow` | `end_p1_snow.png` | 1920×820 | X | PNG-24 | 250KB | (사실) |
| `end_p2_taejong_retreat` | `end_p2_taejong_retreat.png` | 1920×820 | X | PNG-24 | 280KB | (사실) |
| `end_p3_walls_silence` | `end_p3_walls_silence.png` | 1920×820 | X | PNG-24 | 250KB | (사실) |
| `end_p4_yang_bow` | `end_p4_yang_bow.png` | 1920×820 | X | PNG-24 | 270KB | [전승] |
| `end_p5_villagers_smile` | `end_p5_villagers_smile.png` | 1920×820 | X | PNG-24 | 280KB | **[픽션·승인대기]** |
| `end_p6_silk` | `end_p6_silk.png` | 1920×820 | X | PNG-24 | 270KB | [전승] |
| `end_p7_hyangee_bow` | `end_p7_hyangee_bow.png` | 1920×820 | X | PNG-24 | 260KB | **[픽션·승인대기]** |
| `end_p8_oath_kept` | `end_p8_oath_kept.png` | 1920×820 | X | PNG-24 | 240KB | [전승] |

### 5.4 엔딩 플레이스홀더 (승인 전)

| KEY | 파일명 | 내용 |
|---|---|---|
| `end_p5_placeholder` | `end_p5_placeholder.png` | 한자 "휴(休)" + 따뜻한 베이지 |
| `end_p7_placeholder` | `end_p7_placeholder.png` | 한자 "약(約)" + 활 실루엣 |

### 5.5 컷씬 합계

인트로 10 + 엔딩 8 = **18장**, 추정 용량 **약 5MB**.

---

## 6. UI 자산 (9-슬라이스 + 아이콘 + 컨트롤)

### 6.1 9-슬라이스 (13종)

`docs/07_wireframes_visuals.md` §23.1과 완전 일치.

| KEY | 파일명 | 베이스 크기 | 슬라이스 마진 (T,R,B,L) | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `ui_panel_default` | `ui_panel_default.png` | 64×64 | 16,16,16,16 | O | PNG-32 | 8KB |
| `ui_panel_dark` | `ui_panel_dark.png` | 64×64 | 16,16,16,16 | O | PNG-32 | 8KB |
| `ui_panel_quote` | `ui_panel_quote.png` | 80×80 | 20,20,20,20 | O | PNG-32 | 10KB |
| `ui_button_default` | `ui_button_default.png` | 64×32 | 12,12,12,12 | O | PNG-32 | 6KB |
| `ui_button_primary` | `ui_button_primary.png` | 64×32 | 12,12,12,12 | O | PNG-32 | 6KB |
| `ui_button_secondary` | `ui_button_secondary.png` | 64×32 | 12,12,12,12 | O | PNG-32 | 6KB |
| `ui_button_disabled` | `ui_button_disabled.png` | 64×32 | 12,12,12,12 | O | PNG-32 | 5KB |
| `ui_card_stage` | `ui_card_stage.png` | 320×80 | 16,16,16,16 | O | PNG-32 | 12KB |
| `ui_card_unit` | `ui_card_unit.png` | 288×100 | 14,14,14,14 | O | PNG-32 | 10KB |
| `ui_card_codex` | `ui_card_codex.png` | 360×50 | 12,12,12,12 | O | PNG-32 | 8KB |
| `ui_chip_label` | `ui_chip_label.png` | 32×24 | 12,8,12,8 | O | PNG-32 | 4KB |
| `ui_balloon_tutorial` | `ui_balloon_tutorial.png` | 64×64 | 16,16,16,16 | O | PNG-32 | 8KB |
| `ui_tooltip_bg` | `ui_tooltip_bg.png` | 32×24 | 8,8,8,8 | O | PNG-32 | 4KB |

**9-슬라이스 합계**: 약 95KB.

### 6.2 자원 아이콘 (4종) - 컬러 + 흑백 보조

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_grain` | `ico_grain.png` | 64×64 | O | PNG-32 | 5KB |
| `ico_grain_mono` | `ico_grain_mono.png` | 64×64 | O | PNG-32 | 3KB |
| `ico_population` | `ico_population.png` | 64×64 | O | PNG-32 | 4KB |
| `ico_population_mono` | `ico_population_mono.png` | 64×64 | O | PNG-32 | 3KB |
| `ico_arrows` | `ico_arrows.png` | 64×64 | O | PNG-32 | 5KB |
| `ico_arrows_mono` | `ico_arrows_mono.png` | 64×64 | O | PNG-32 | 3KB |
| `ico_fame` | `ico_fame.png` | 64×64 | O | PNG-32 | 4KB |
| `ico_fame_mono` | `ico_fame_mono.png` | 64×64 | O | PNG-32 | 3KB |

### 6.3 유닛 아이콘 (좌패널, 7종)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_unit_archer` | `ico_unit_archer.png` | 56×56 | O | PNG-32 | 5KB |
| `ico_unit_spearman` | `ico_unit_spearman.png` | 56×56 | O | PNG-32 | 5KB |
| `ico_unit_long_spearman` | `ico_unit_long_spearman.png` | 56×56 | O | PNG-32 | 5KB |
| `ico_unit_catapult` | `ico_unit_catapult.png` | 56×56 | O | PNG-32 | 5KB |
| `ico_unit_cavalry` | `ico_unit_cavalry.png` | 56×56 | O | PNG-32 | 5KB |
| `ico_building_torch` | `ico_building_torch.png` | 56×56 | O | PNG-32 | 5KB |
| `ico_building_granary` | `ico_building_granary.png` | 56×56 | O | PNG-32 | 5KB |

### 6.4 적 아이콘 (12종, 미니맵·도감용)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_enemy_infantry` | `ico_enemy_infantry.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_archer` | `ico_enemy_archer.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_heavy` | `ico_enemy_heavy.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_scout` | `ico_enemy_scout.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_cavalry` | `ico_enemy_cavalry.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_ram` | `ico_enemy_ram.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_tower` | `ico_enemy_tower.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_enemy_elite` | `ico_enemy_elite.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_boss_liu` | `ico_boss_liu.png` | 80×80 | O | PNG-32 | 8KB |
| `ico_boss_jang` | `ico_boss_jang.png` | 80×80 | O | PNG-32 | 8KB |
| `ico_boss_iseje_ram` | `ico_boss_iseje_ram.png` | 80×80 | O | PNG-32 | 10KB |
| `ico_boss_taejong` | `ico_boss_taejong.png` | 80×80 | O | PNG-32 | 10KB |

### 6.5 버프 / 디버프 / 상태 아이콘 (12종)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_buff_rally` | `ico_buff_rally.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_buff_attack_up` | `ico_buff_attack_up.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_buff_last_stand` | `ico_buff_last_stand.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_debuff_stun` | `ico_debuff_stun.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_debuff_slow` | `ico_debuff_slow.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_stealth` | `ico_state_stealth.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_morale_low` | `ico_state_morale_low.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_torch_lit` | `ico_state_torch_lit.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_locked` | `ico_state_locked.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_check` | `ico_state_check.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_cross` | `ico_state_cross.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_state_pause` | `ico_state_pause.png` | 32×32 | O | PNG-32 | 3KB |

### 6.6 영웅 스킬 아이콘 (4종)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_skill_focus_shot` | `ico_skill_focus_shot.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_skill_rally_cry` | `ico_skill_rally_cry.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_skill_arrow_rain` | `ico_skill_arrow_rain.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_ult_last_stand` | `ico_ult_last_stand.png` | 48×48 | O | PNG-32 | 5KB |

### 6.7 보스 페이즈 아이콘 (당 태종, 4종)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_boss_phase_1` | `ico_boss_phase_1.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_boss_phase_2` | `ico_boss_phase_2.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_boss_phase_3` | `ico_boss_phase_3.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_boss_phase_4` | `ico_boss_phase_4.png` | 32×32 | O | PNG-32 | 3KB |

### 6.8 UI 컨트롤 아이콘 (8종)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_ui_settings` | `ico_ui_settings.png` | 48×48 | O | PNG-32 | 4KB |
| `ico_ui_help` | `ico_ui_help.png` | 48×48 | O | PNG-32 | 3KB |
| `ico_ui_back` | `ico_ui_back.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_ui_pause` | `ico_ui_pause.png` | 48×48 | O | PNG-32 | 3KB |
| `ico_ui_play` | `ico_ui_play.png` | 48×48 | O | PNG-32 | 3KB |
| `ico_ui_speed_1x` | `ico_ui_speed_1x.png` | 48×48 | O | PNG-32 | 3KB |
| `ico_ui_speed_2x` | `ico_ui_speed_2x.png` | 48×48 | O | PNG-32 | 3KB |
| `ico_ui_close` | `ico_ui_close.png` | 32×32 | O | PNG-32 | 3KB |

### 6.9 별 평가 아이콘

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `ico_star_filled` | `ico_star_filled.png` | 120×120 | O | PNG-32 | 12KB |
| `ico_star_empty` | `ico_star_empty.png` | 120×120 | O | PNG-32 | 10KB |
| `ico_star_small_filled` | `ico_star_small_filled.png` | 32×32 | O | PNG-32 | 3KB |
| `ico_star_small_empty` | `ico_star_small_empty.png` | 32×32 | O | PNG-32 | 3KB |

### 6.10 UI 합계

9-슬라이스 13 + 아이콘 49 + 별 4 = **66개 PNG**, 추정 용량 **약 380KB**.

---

## 7. 이펙트 / 투사체 (Effects & Projectiles)

### 7.1 투사체

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `fx_arrow_ally` | `fx_arrow_ally.png` | 32×8 | 1 | O | PNG-32 | 2KB |
| `fx_arrow_enemy` | `fx_arrow_enemy.png` | 32×8 | 1 | O | PNG-32 | 2KB |
| `fx_arrow_yang` | `fx_arrow_yang.png` | 32×8 | 1 (황금 삼익촉) | O | PNG-32 | 3KB |
| `fx_stone` | `fx_stone.png` | 24×24 | 1 | O | PNG-32 | 2KB |

투사체는 모두 `Canvas.create_line()` 또는 `create_oval()`로 그릴 수 있으나, 시각 풍부함을 위해 작은 PNG로도 준비.

### 7.2 충격 / 폭발 / 히트

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `fx_hit_small` | `fx_hit_small.png` | 48×48 | 3 (페이드) | O | PNG-32 | 8KB |
| `fx_hit_large` | `fx_hit_large.png` | 96×96 | 4 | O | PNG-32 | 20KB |
| `fx_explosion_stone` | `fx_explosion_stone.png` | 128×128 | 5 (빨강→노랑→회색) | O | PNG-32 | 35KB |
| `fx_arrow_rain` | `fx_arrow_rain.png` | 256×256 | 6 (점선 화살 떨어짐) | O | PNG-32 | 80KB |

### 7.3 사망 페이드

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `fx_death_fade_overlay` | `fx_death_fade_overlay.png` | 64×64 | 4 (회색 마스크 + 알파 감소) | O | PNG-32 | 12KB |
| `fx_death_dust` | `fx_death_dust.png` | 64×64 | 3 (먼지 흩어짐) | O | PNG-32 | 10KB |

### 7.4 영웅 스킬 이펙트

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `fx_skill_focus_shot` | `fx_skill_focus_shot.png` | 128×16 | 1 (황금 잔상 라인) | O | PNG-32 | 5KB |
| `fx_skill_rally_aura` | `fx_skill_rally_aura.png` | 256×256 | 4 (확장 링) | O | PNG-32 | 30KB |
| `fx_ult_screen_edge` | `fx_ult_screen_edge.png` | 1920×1080 | 1 (황토 테두리 빛, 알파) | O | PNG-32 | 80KB |
| `fx_ult_kanji_glow` | `fx_ult_kanji_glow.png` | 96×96 | 4 (결사 한자 펄스) | O | PNG-32 | 15KB |

### 7.5 환경 이펙트

| KEY | 파일명 | 크기 | 프레임 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `fx_torch_glow` | `fx_torch_glow.png` | 240×240 | 4 (불빛 확장 → 수축) | O | PNG-32 | 40KB |
| `fx_snow_flake` | `fx_snow_flake.png` | 8×8 | 1 (엔딩, 토산 단계) | O | PNG-32 | 1KB |
| `fx_dust_collapse` | `fx_dust_collapse.png` | 256×128 | 6 (토산 붕괴 먼지) | O | PNG-32 | 60KB |

### 7.6 토스트 / 알림

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `fx_toast_bg` | `fx_toast_bg.png` | 64×32 | O | PNG-32 (9-슬라이스 12,12,12,12) | 5KB |
| `fx_gain_grain` | `fx_gain_grain.png` | 48×48 | O | PNG-32 | 4KB |
| `fx_gain_arrows` | `fx_gain_arrows.png` | 48×48 | O | PNG-32 | 4KB |
| `fx_gain_fame` | `fx_gain_fame.png` | 48×48 | O | PNG-32 | 4KB |

### 7.7 이펙트 합계

총 약 30종, 추정 용량 **약 430KB**.

---

## 8. 타일 (지형, Tiles)

### 8.1 타일 종류 (8종)

각 타일은 64×64 베이스. 일부 변형(2~3종)으로 시각 다양성.

| KEY | 파일명 | 크기 | 변형 수 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|---|
| `tile_grass` | `tile_grass.png` | 64×64 | 3 변형 | X | PNG-24 | 8KB |
| `tile_dirt` | `tile_dirt.png` | 64×64 | 3 변형 | X | PNG-24 | 8KB |
| `tile_road` | `tile_road.png` | 64×64 | 3 변형 | X | PNG-24 | 8KB |
| `tile_wall_top` | `tile_wall_top.png` | 64×64 | 2 변형 | O | PNG-32 | 10KB |
| `tile_water` | `tile_water.png` | 64×64 | 2 프레임 애니 | O | PNG-32 | 12KB |
| `tile_mountain` | `tile_mountain.png` | 64×128 | 2 변형 | O | PNG-32 | 15KB |
| `tile_snow` | `tile_snow.png` | 64×64 | 2 변형 (스테이지 5 후반) | X | PNG-24 | 6KB |
| `tile_bridge` | `tile_bridge.png` | 64×64 | 1 | O | PNG-32 | 6KB |

### 8.2 타일 합계

총 8종 (× 변형 평균 2.3) = **약 18 PNG**, 추정 용량 **약 75KB**.

---

## 9. 시작 화면 / 마케팅 / 배포 자산

### 9.1 실행 파일 아이콘

| KEY | 파일명 | 크기 | 형식 | 용량 |
|---|---|---|---|---|
| `app_icon` | `ansiseong.ico` | 16/32/48/64/128/256 멀티 | ICO | 100KB |
| `app_icon_png` | `ansiseong_512.png` | 512×512 | PNG-32 | 60KB |

### 9.2 스플래시

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `splash` | `splash.png` | 800×600 | X | PNG-24 | 80KB |

부팅 1초 표시. 안시성 + 게임명 + 로고.

### 9.3 마케팅 키 아트 (선택)

| KEY | 파일명 | 크기 | 알파 | 형식 | 용량 |
|---|---|---|---|---|---|
| `marketing_key` | `marketing_key.png` | 2560×1440 | X | PNG-24 | 800KB |
| `marketing_logo` | `marketing_logo.png` | 1024×512 | O | PNG-32 | 60KB |

---

## 10. 총괄 용량 / 카운트 표

| 카테고리 | 자산 수 | 추정 용량 |
|---|---|---|
| 유닛 스프라이트 | 24 | 1.4 MB |
| 건물/구조물 | 12 | 520 KB |
| 배경 일러스트 | 18 | 5 MB (PNG-24) / 2.5 MB (PNG-8) |
| 컷씬 패널 | 18 + 5 플레이스홀더 = 23 | 5 MB |
| UI 9-슬라이스 | 13 | 95 KB |
| UI 아이콘 | 49 + 4 보조 mono = 53 | 380 KB |
| 별 아이콘 | 4 | 30 KB |
| 이펙트 | 30 | 430 KB |
| 타일 | 18 | 75 KB |
| 시작/스플래시/마케팅 | 5 | 1.1 MB |
| **합계** | **≈ 200 PNG** | **≈ 14 MB** |

- 압축 시 (PyInstaller --onefile) 약 8~10MB
- DECISION-D-110 목표 ≤ 50MB 대비 매우 여유 — **이펙트와 컷씬 일러스트 품질을 1~2단계 더 올릴 여유 있음**

---

## 11. 작업 우선순위 (M3 알파 목표)

스테이지 1 플레이어블(M3) 마일스톤(docs/03 §15) 기준 우선순위.

### Priority 1 (M3 차단)
- ally_archer, ally_spearman 스프라이트 (스테이지 1 기본 유닛)
- enemy_infantry, enemy_archer 스프라이트
- boss_liu 스프라이트 (스테이지 1 보스)
- bg_stage_01_yodong 배경
- hero_yang_phase1 스프라이트 + portrait
- UI 9-슬라이스 7종 (panel_default, panel_dark, button_default/primary/secondary/disabled, card_unit)
- 자원 아이콘 3종 + mono 3종
- 유닛 아이콘 2종 (archer, spearman)
- 스킬 아이콘 1종 (focus_shot — 스테이지 1에서 양만춘 기본기는 패시브)
- 별 아이콘 2종 (filled, empty)
- 이펙트 5종 (fx_arrow_ally, fx_hit_small, fx_death_fade_overlay, fx_toast_bg, fx_gain_grain)
- 타일 4종 (grass, dirt, road, wall_top)
- splash + app_icon

### Priority 2 (M4 전체 알파)
- 나머지 유닛/적/건물 스프라이트 전체
- 스테이지 2~5 배경
- 모든 UI 컴포넌트
- 스킬 아이콘 4종 전체
- hero_yang_phase2~4

### Priority 3 (M5 베타)
- 컷씬 18패널 (또는 외주)
- 보스 4종 풀 애니메이션
- 마케팅 자산
- 색약 모드 보조 mono 아이콘 전체

### Priority 4 (사용자 승인 후)
- 픽션 캐릭터 등장 컷씬 5장 (intro_p6/7/9, end_p5/7)
- 모용손/향이 모자 일러스트 디테일

---

## 12. 외주 / 작업 인계 명세

### 12.1 작업 단위 (Work Package)

| WP | 내용 | 추정 시간 | 우선순위 |
|---|---|---|---|
| WP-01 | 아군 유닛 5종 스프라이트 (idle+walk+atk+death) | 5일 | P1 |
| WP-02 | 적 유닛 8종 스프라이트 | 8일 | P1/P2 |
| WP-03 | 영웅 양만춘 4페이즈 스프라이트 + portrait | 6일 | P1 |
| WP-04 | 보스 4종 스프라이트 | 6일 | P2 |
| WP-05 | 건물/구조물 12종 | 3일 | P1/P2 |
| WP-06 | 배경 일러스트 5스테이지 + 8 메뉴 = 13장 | 13일 | P1/P2 |
| WP-07 | 컷씬 일러스트 18장 | 18일 | P3 |
| WP-08 | UI 9-슬라이스 13종 | 3일 | P1 |
| WP-09 | 아이콘 49종 (+ mono 4) | 5일 | P1/P2 |
| WP-10 | 이펙트 30종 | 4일 | P1/P2 |
| WP-11 | 타일 8종 (× 변형) | 2일 | P1 |
| WP-12 | 픽션 캐릭터 (사용자 승인 후) | 5일 | P4 |
| **합계** | | **약 78일** (1인) | |

병렬 작업 시 (2명) 약 6~8주.

### 12.2 인계 시점 자산 체크리스트

- [ ] 파일명이 컨벤션 §1.2 준수
- [ ] 폴더 구조 §1.3 준수
- [ ] 모든 PNG가 알파 채널 명시대로 작성됨
- [ ] 스프라이트 시트의 프레임 사이 1px 패딩 (스케일 시 누설 방지)
- [ ] 외곽선 2px (#1A1410) 일관성
- [ ] 색상 팔레트 일치 (docs/07 §14)
- [ ] 색약 모드 mono 아이콘 4종 동봉
- [ ] 9-슬라이스 마진 정확 (PNG에 메타 또는 별도 메모)

### 12.3 자산 라이선스

| 자산 | 라이선스 | 권리자 |
|---|---|---|
| 내부 작업 자산 (전체) | 본 프로젝트 사용권 | 디자인 리더 (양도) |
| 외주 작업 자산 | 작업 종료 시 양도 계약 | 외주 작업자 |
| 한자 캘리그래피 폰트 | OPEN-D-104 | TBD |
| Pillow (런타임) | HPND | Python Imaging Library |

---

## 13. 음향 자산 큐 (참조용 — 별도 산출물 아님)

음향은 본 산출물 범위 아니나 화면별 음향 큐만 참조용 표시.

### 13.1 BGM 큐

GDD §10.1과 일치. 화면별 트랙:

| 화면 | BGM | 길이 |
|---|---|---|
| SCN-01 메인 메뉴 | `bgm_title` (가야금 + 대금) | 약 2분 루프 |
| SCN-03 인트로 | `bgm_intro` (장중) | 약 3분 |
| SCN-04 브리핑 | `bgm_briefing_sting` (가야금 한 음) | 1.5초 |
| SCN-05 전투 (STG1~2) | `bgm_battle_calm` (가야금 + 해금) | 약 3분 루프 |
| SCN-05 전투 (STG3) | `bgm_battle_night` (단소 + 낮은 북) | 약 3분 |
| SCN-05 전투 (STG4) | `bgm_battle_march` (북 + 나발) | 약 3분 |
| SCN-05 전투 (STG5 전반) | `bgm_battle_climax_1` (빠른 북 + 해금) | 약 3분 |
| SCN-05 전투 (STG5 후반) | `bgm_battle_climax_2` (풀 편성) | 약 3분 |
| SCN-07 결과(승) | `bgm_victory` (가야금 + 단소) | 약 1분 |
| SCN-08 결과(패) | `bgm_defeat` (가야금 한 음 페이드) | 약 30초 |
| SCN-10 엔딩 | `bgm_ending` (가야금 단조) | 약 4분 |
| SCN-13 크레딧 | `bgm_credits` (잔잔) | 약 3분 |

### 13.2 SFX 큐 (이펙트별)

| SFX | 트리거 |
|---|---|
| `sfx_click` | UI 버튼 클릭 |
| `sfx_hover` | UI 호버 (옵션) |
| `sfx_grain_gain` | 곡식 획득 |
| `sfx_arrow_release` | 화살 발사 |
| `sfx_arrow_hit` | 화살 적중 |
| `sfx_unit_place` | 유닛 배치 "쿵" |
| `sfx_unit_death_soft` | 사망 (부드러운 천 소리) |
| `sfx_skill_q` | 일점사 시전 (양만춘 한 마디) |
| `sfx_skill_w` | 독려의 함성 |
| `sfx_skill_e` | 화살비 |
| `sfx_ult` | 결사항전 ("결사!") |
| `sfx_boss_appear` | 보스 등장 ("둥-") |
| `sfx_wave_clear` | 진군 격퇴 |
| `sfx_tosan_collapse` | 토산 붕괴 ("콰르릉") |
| `sfx_star_pop` | 별 페이드인 ("딩") |
| `sfx_snow` | 눈 떨어짐 (엔딩) |

---

## 14. 사용자 승인 대기 (OPEN 정리)

### 14.1 PM OPEN-1: 픽션 캐릭터 비주얼

승인 전까지 다음 자산은 **플레이스홀더 PNG**로 대체:

| 영향 자산 | 플레이스홀더 KEY |
|---|---|
| `intro_p6_moyong` | `intro_p6_placeholder` (한자 "충") |
| `intro_p7_villagers` | `intro_p7_placeholder` (한자 "민") |
| `intro_p9_dialogue` | `intro_p9_placeholder` (인용 부호) |
| `end_p5_villagers_smile` | `end_p5_placeholder` (한자 "휴") |
| `end_p7_hyangee_bow` | `end_p7_placeholder` (한자 "약") |

UI 라벨은 항상 `[픽션·승인대기]` 노란 칩.

### 14.2 OPEN-D-104: 한자 캘리그래피 폰트

대체안: 일반 한자 폰트 (예: 나눔명조, Noto Serif KR Black)를 굵게 + 약간 회전(2~3도)으로 캘리그래피 풍 모방.

---

## 15. 변경 이력

| 버전 | 일자 | 내용 | 작성자 |
|---|---|---|---|
| v0.1 (Draft) | 2026-05-17 | 최초 작성. 200 PNG 자산 명세, 작업 우선순위 4단계, 외주 단위 12 WP | 디자인 리더 |

---

## 16. 다음 액션

1. `docs/09_animation_state_diagrams.md` 작성 → 본 문서의 스프라이트 시트 프레임 의미 정의
2. PM에게 OPEN-D-101 (외주 vs 내부) 결정 요청
3. PM에게 OPEN-D-102 (픽션 캐릭터 비주얼 승인) 요청
4. 개발 파트에게 본 문서 인계 → `src/core/assets.py` AssetManager에 KEY 목록 반영
5. 아트 파트 (또는 외주)에게 본 문서 + docs/07 인계

---

— 자산 인벤토리 v0.1 끝 —
