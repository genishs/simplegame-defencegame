# 12. 튜토리얼 UX 명세 (Issue #26)

> Phase 4 · 기획 리더 산출물 #1 (Planning Lead, 2026-05-20).
> 의존: `docs/story/08_ui_strings.md` (SSOT v1.1), `docs/07_wireframes_visuals.md` §24 (튜토리얼 풍선), `docs/09_animation_state_diagrams.md` (튜토리얼 상태도), Issue #26.
> 본 문서는 **인터랙티브 튜토리얼**의 진입 흐름·8단계 UX·스킵/재진입 정책·신규 ui_strings 키 목록·자산 요구사항을 정의한다.
> 본 문서는 명세이며 구현 코드(.py)는 다루지 않는다. Design Lead 한국어 문구 확정 + Dev Team 구현은 후속 라운드에서 진행.

---

## 0. 페어 토의 메모 + 결정 라벨

- **리더**: "튜토리얼은 한 번 해 보면 끝. '다시 보지 않기' 토글을 1순위로. 메뉴 재진입 경로 확보."
- **리더**: "단계 수는 8로. 6단계는 기병/일시정지/결과 화면이 빠져 핵심 mechanic을 다 못 가르친다."
- **리더**: "M키 수동 모드는 Phase 3.3에서 도입된 핵심 신규 기능. 자동 모드가 기본임을 강조 — 신규 플레이어가 자동만으로도 클리어 가능하도록 Issue #27 난이도 하향과 짝을 이룬다."

### DECISION-PL-P4-001 ~ 008 (본 문서 누적)

| ID | 의사결정 | 근거 |
| --- | --- | --- |
| **DECISION-PL-P4-001** | 튜토리얼 단계 수를 **8단계** 로 확정. 6단계로 압축 시 `M키 수동 모드 / 일시정지 / 결과 화면`을 모두 다루지 못함. 8단계가 신규 플레이어 인지 부하 한계 내 (UX 업계 통상 7±2 단계). | `docs/story/08_ui_strings.md` §17.2 가 기존 6단계로 풍선 도움말을 두었으나, Phase 4 본 튜토리얼은 **별도 인터랙티브 흐름**으로 분리 (풍선 도움말은 보조 hint로 잔존). |
| **DECISION-PL-P4-002** | 자동 진입 조건: **저장 슬롯이 비어 있을 때 1회만**. 이후 메뉴 → "튜토리얼" 항목으로 명시 재진입. `tutorial.skip_forever` 플래그(`save_slot.tutorial_dismissed`)를 저장 슬롯에 기록 — true 시 자동 진입 영구 차단. | DOR 요구 |
| **DECISION-PL-P4-003** | 인터랙티브/패시브 분배: 단계 1~3은 입력 대기(클릭/배치), 단계 4(첫 wave)는 자동 관찰 + "다음" 버튼 비활성, 단계 5~6은 키 입력 대기(M, Space), 단계 7~8은 자동 진행 + "다음"/"시작" 버튼. **사용자 입력으로 진행되는 비율이 50% 이상**이라야 인터랙티브 튜토리얼이라 부를 수 있다. | UX 원칙 |
| **DECISION-PL-P4-004** | 스킵 정책: 각 단계 우상단 "튜토리얼 종료" 버튼 + **확인 다이얼로그 1회** 필수. ESC도 동일 다이얼로그 호출. 다이얼로그에서 "예" 선택 시 즉시 stage_select로 이동, "다시 보지 않기" 토글 옵션 제공. | DOR 요구, DECISION-PL-P4-002 |
| **DECISION-PL-P4-005** | 재진입 흐름: 메뉴에서 "튜토리얼" 클릭 → 항상 단계 1부터 시작. **중도 진입(특정 단계 점프) 옵션은 제공하지 않음** — 인지 부하 증가 + 상태 머신 복잡도. 대신 단계 1~3은 짧고 빠르게 통과 가능하도록 설계. | UX 단순성 |
| **DECISION-PL-P4-006** | ui_strings 신규 키 네이밍: `tutorial.<role>.<sub>` 패턴 (`docs/story/08_ui_strings.md` §0.1 컨벤션 준수). scene=`tutorial`, component=`intro/step1~8/skip/complete/hud_arrow`, role=`title/body/cta/yes/no`. **총 36개** (단계별 title/body/cta 24 + 메뉴/스킵/완료 5 + HUD 화살표 3 + 다이얼로그 토글 2 + 본문 보조 2). | 본 문서 §6 |
| **DECISION-PL-P4-007** | 튜토리얼 전용 스테이지/시나리오는 별도 데이터 파일이 아닌, **`stage_01` 일부 wave를 mock 재생**하는 형태로 구현 권고 (Dev Lead 판단 여지 인정). 단계 4 첫 wave는 `tang_soldier × 2, interval 1.5s`로 mock — 실제 stage_01 데이터를 변형하지 않는다. | 데이터 SSOT 유지 |
| **DECISION-PL-P4-008** | 자산 요구사항 최소화: **신규 일러스트 0건**, 기존 캐릭터 플레이스홀더(`docs/story/06` 5종) 재사용. 단계 1~2는 양만춘 플레이스홀더 + 텍스트 박스. HUD 강조는 반투명 마스크(검정 50%) + spotlight 원형 컷아웃 + 노란 화살표(픽션 가능, 기존 UI 자산). | Audio Engineer/Design Lead 부담 최소 |

---

## 1. 튜토리얼 진입 조건

### 1.1 자동 진입 (첫 실행)

| 조건 | 동작 |
| --- | --- |
| 저장 슬롯 비어 있음 (`save_slot.is_empty == True`) | 타이틀 → "새 게임" 클릭 → 인트로 컷씬 (SCN-03) 종료 직후 **튜토리얼 1단계로 자동 진입** |
| 저장 슬롯 존재 + `save_slot.tutorial_dismissed == True` | 자동 진입 안 함 |
| 저장 슬롯 존재 + `save_slot.tutorial_dismissed == False` + `save_slot.tutorial_completed == False` | "이어하기" 시 자동 진입 없음. 메뉴 "튜토리얼" 항목으로만 진입 |

### 1.2 메뉴에서 명시 재진입

- 메인 메뉴에 **신규 버튼** `menu.tutorial.button` 추가 (위치 우측 사이드, "도움말" 위).
- 클릭 시 단계 1부터 시작. 진행 중 스킵 시 1.1 자동 진입 흐름에 영향 없음 (`tutorial_dismissed`만 토글).
- 메뉴 진입 시 무조건 단계 1부터 — 중도 진입 옵션 없음 (DECISION-PL-P4-005).

### 1.3 "다시 보지 않기" 토글

- 스킵 확인 다이얼로그에 체크박스 `tutorial.skip.dont_show_again` 1개.
- 체크 후 "예" 선택 시 `save_slot.tutorial_dismissed = True` 저장 — 자동 진입 영구 차단.
- 토글 ON 상태라도 메뉴에서 명시 재진입은 가능 (사용자 선택권 보존).
- 토글을 OFF로 되돌리는 UI는 설정 메뉴에 `settings.tutorial.reset` 한 줄 추가 권고 (DEV 후속 검토, 본 라운드 신규 ui_strings에는 미포함 — 설정 메뉴 라운드에서 합류).

---

## 2. 단계별 UX (8 단계)

각 단계는 다음 5속성을 가진다.
- **모드**: 인터랙티브(I) / 패시브(P) — DECISION-PL-P4-003
- **CTA**: 다음 단계로 가는 진행 조건 (사용자 입력 vs 자동)
- **HUD 강조**: spotlight 위치 (DECISION-PL-P4-008)
- **표시 시간 상한**: 진행 조건 미충족 시 자동 진행 fallback (안전 장치)
- **ui_strings 키**: 본 단계에서 사용하는 신규 키

### 2.1 단계 1 — 게임 목표 소개 (P)

- **본문**: "645년 봄, 당의 깃발이 요동으로 향했소. 양만춘과 함께 88일의 약속을 지키시오."
- **표시**: 화면 중앙 대형 텍스트 박스 + 양만춘 플레이스홀더 일러스트 (좌측 1/3)
- **모드**: 패시브
- **CTA**: 사용자가 "다음" 버튼(`dialog.next`) 클릭 — 입력 대기 무한 (스킵 외 종료 없음)
- **HUD 강조**: 없음 (전체 화면 텍스트 단계)
- **표시 시간 상한**: 무한
- **ui_strings 키**: `tutorial.step1.title`, `tutorial.step1.body`, `tutorial.step1.cta`

### 2.2 단계 2 — 자원(곡식) 소개 (I)

- **본문**: "위에 곡식이 있소. 이걸로 병사를 모집하시오. 시간이 지나면 곡식은 자동으로 늘어나오."
- **표시**: 상단 HUD `hud.grain` 위치에 spotlight(원형 컷아웃) + 노란 화살표 + 본문 텍스트 박스(하단)
- **모드**: 인터랙티브
- **CTA**: HUD 곡식 아이콘 영역 클릭 — 클릭 시 단계 3 진입
- **HUD 강조**: 상단 곡식 아이콘 (X=화면중앙상단, Y=상단 HUD 위치)
- **표시 시간 상한**: **15초** 후 자동 진행 (사용자가 못 찾아도 막히지 않게)
- **ui_strings 키**: `tutorial.step2.title`, `tutorial.step2.body`, `tutorial.step2.cta`, `tutorial.hud_arrow.resource`

### 2.3 단계 3 — 아군 배치 (I)

- **본문**: "왼쪽에서 궁수를 골라 성벽 위 빈 칸에 배치하시오. 클릭으로 고르고, 클릭으로 두시오."
- **표시**: 좌측 유닛 패널(궁수 아이콘)에 spotlight + 첫 번째 build_zone 위치에도 spotlight (이중 강조)
- **모드**: 인터랙티브
- **CTA**: build_zone에 궁수가 배치 완료 — 곡식 차감 발생 시 단계 4 진입
- **HUD 강조**: 좌측 유닛 패널 + 우측 build_zone (mock stage_01 첫 번째 zone)
- **표시 시간 상한**: **30초** 후 자동 진행 + 가상 배치 데모 (사용자 없이도 진행되도록 안전)
- **ui_strings 키**: `tutorial.step3.title`, `tutorial.step3.body`, `tutorial.step3.cta`, `tutorial.hud_arrow.buildzone`

### 2.4 단계 4 — 첫 적 wave 관찰 (P)

- **본문**: "당군이 옵니다. 이 진군은 양만춘과 그대의 병사들이 알아서 막을 것이오. 가만히 보시오."
- **표시**: mock spawn(`tang_soldier × 2, interval 1.5s`, DECISION-PL-P4-007) + 본문 텍스트 박스 (좌하단, HUD 미가림)
- **모드**: 패시브
- **CTA**: mock wave 종료(2 적 모두 처치 또는 도달) → "다음" 버튼 활성화 + 사용자 클릭
- **HUD 강조**: 없음 (전투 화면 가시성 우선)
- **표시 시간 상한**: **45초** wave 자동 종료 fallback
- **ui_strings 키**: `tutorial.step4.title`, `tutorial.step4.body`, `tutorial.step4.cta`

### 2.5 단계 5 — 영웅 자동/수동 모드 (I)

- **본문**: "양만춘은 자동으로 적을 공격하오. M 키를 누르면 직접 움직일 수 있소. 한 번 눌러 보시오."
- **표시**: 양만춘 영웅 위치에 spotlight + 본문 텍스트 박스 (좌하단) + 좌하단 `hero.manual_mode.*` 라벨 강조 화살표
- **모드**: 인터랙티브
- **CTA**: 사용자가 M 키 1회 입력 — 토글 ON 확인 → 단계 6 진입
- **HUD 강조**: 양만춘 위치 + 좌하단 모드 라벨
- **표시 시간 상한**: **20초** 후 자동 진행 (수동 모드는 핵심 기능이지만 신규 플레이어가 못 누를 가능성 있음)
- **ui_strings 키**: `tutorial.step5.title`, `tutorial.step5.body`, `tutorial.step5.cta`, `tutorial.hud_arrow.hero`

### 2.6 단계 6 — 일시정지/재개 (I)

- **본문**: "잠시 멈추고 싶으면 스페이스 키를 누르시오. 한 번 더 누르면 다시 시작합니다."
- **표시**: 본문 텍스트 박스 + 상단 우측 일시정지 버튼 강조 (보조)
- **모드**: 인터랙티브
- **CTA**: 사용자가 Space 키 1회 + 다시 1회 (또는 일시정지 버튼 2회 클릭) — 토글 한 사이클 완료 → 단계 7 진입
- **HUD 강조**: 상단 우측 일시정지 버튼
- **표시 시간 상한**: **15초** 후 자동 진행
- **ui_strings 키**: `tutorial.step6.title`, `tutorial.step6.body`, `tutorial.step6.cta`

### 2.7 단계 7 — wave 클리어/보상 (P)

- **본문**: "진군을 막아냈소. 매 진군이 끝날 때마다 곡식·화살이 들어옵니다. 별 평가로 명성을 얻으면 병영에서 영구 강화에 쓸 수 있소."
- **표시**: 가상 결과 화면 미리보기 (작은 카드 + `result.win.title` 텍스트 미니어처)
- **모드**: 패시브
- **CTA**: "다음" 버튼 클릭 → 단계 8 진입
- **HUD 강조**: 없음 (미니어처 카드 자체가 강조)
- **표시 시간 상한**: 무한
- **ui_strings 키**: `tutorial.step7.title`, `tutorial.step7.body`, `tutorial.step7.cta`

### 2.8 단계 8 — 종료 + Stage 1로 (P)

- **본문**: "이제 준비는 끝났소. 안시성으로 가는 첫 걸음, 요동성에서 시작합시다."
- **표시**: 화면 중앙 종료 메시지 + 큰 "시작하기" 버튼 (`tutorial.complete.cta` = "Stage 1로 가기")
- **모드**: 패시브
- **CTA**: "시작하기" 버튼 클릭 → `save_slot.tutorial_completed = True` 기록 + `stage_select` 또는 직접 `stage_01` 진입 (Design Lead 판단 — 본 명세는 stage_select 권고 = 사용자가 선택권을 갖는 게 더 자연스러움)
- **HUD 강조**: 없음
- **표시 시간 상한**: 무한
- **ui_strings 키**: `tutorial.step8.title`, `tutorial.step8.body`, `tutorial.complete.cta`

### 2.9 단계 진행 요약 표

| 단계 | 모드 | CTA 입력 | 표시 상한 | HUD 강조 |
| --- | --- | --- | --- | --- |
| 1. 목표 소개 | P | "다음" 버튼 | 무한 | 없음 |
| 2. 자원 소개 | I | 곡식 클릭 | 15s | 상단 곡식 |
| 3. 아군 배치 | I | 궁수 배치 완료 | 30s | 좌패널 + build_zone |
| 4. 첫 wave | P | wave 종료 + "다음" | 45s | 없음 |
| 5. 영웅 M키 | I | M 키 입력 | 20s | 양만춘 + 좌하단 라벨 |
| 6. 일시정지 | I | Space 토글 1사이클 | 15s | 상단 우측 |
| 7. 보상 화면 | P | "다음" 버튼 | 무한 | 없음 (미니어처 자체) |
| 8. 종료 → Stage 1 | P | "시작하기" 버튼 | 무한 | 없음 |

**인터랙티브 단계 비율**: 4/8 = 50% (DECISION-PL-P4-003 충족).

---

## 3. 스킵 옵션 / 종료 흐름

### 3.1 스킵 진입 경로

- **모든 단계** 우상단 작은 버튼 `tutorial.skip.button` ("튜토리얼 종료").
- **ESC 키**: 모든 단계에서 동일 다이얼로그 호출.
- 단계 8(종료)에서도 스킵 버튼 표시 (사용자가 마지막에 마음 바꿔도 정상 종료와 동일 효과).

### 3.2 스킵 확인 다이얼로그

| 요소 | 키 | 표시 텍스트 (Design Lead 라운드 확정) |
| --- | --- | --- |
| 다이얼로그 제목 | `tutorial.skip.confirm.title` | (Design 확정) |
| 본문 | `tutorial.skip.confirm.body` | (Design 확정) |
| 체크박스 | `tutorial.skip.dont_show_again` | (Design 확정) |
| "예" 버튼 | `tutorial.skip.confirm.yes` | (Design 확정) |
| "아니오" 버튼 | `tutorial.skip.confirm.no` | (Design 확정) |

### 3.3 스킵 후 라우팅

- "예" 선택 시: `tutorial_dismissed = True` (체크박스 ON일 때만) + 현재 단계 무관 stage_select로 이동.
- "아니오" 선택 시: 다이얼로그 닫고 현재 단계 그대로 복귀 (mock wave 진행 중이었다면 동일 시점 재개).
- ESC 외 우상단 X 버튼은 다이얼로그를 "아니오"로 닫음 (관행).

---

## 4. 재진입 흐름 상세

### 4.1 메뉴 → 튜토리얼 진입

1. 사용자가 메인 메뉴에서 `menu.tutorial.button` 클릭.
2. 단계 1 자동 시작.
3. 진행 중 스킵 시 `tutorial_dismissed`는 사용자가 체크박스를 누른 경우에만 True로 변경 (재진입 자체가 자발적 의사이므로 강제 토글 금지).
4. 완주 시 단계 8 종료 후 stage_select로 이동 — `tutorial_completed = True` 재기록 (이미 True여도 idempotent).

### 4.2 중도 진입 미지원 근거

- 단계별 점프 옵션은 상태 머신(8 단계 × 시작점/종료점)을 복잡하게 만들며 Phase 4 일정 압박.
- 단계 1~3은 합쳐서 약 60초 이내 통과 가능하도록 설계.
- 후속 Phase 5에서 사용자 데이터 기반 필요성 재검토 (현재는 미지원).

### 4.3 인트로 컷씬과의 관계

- 인트로(SCN-03)는 튜토리얼 전에 1회 재생. 이미 `intro.skip_confirm`로 스킵 지원.
- 인트로 → (스킵 안 함) → 튜토리얼 단계 1 흐름이 정상.
- 인트로 → (스킵) → 튜토리얼 단계 1 흐름도 동일하게 유지 (인트로 스킵이 튜토리얼 스킵을 의미하지 않음).

---

## 5. HUD 강조 오버레이 — UI 부품 명세

### 5.1 부품 구성

| 부품 | 설명 | 사용 단계 |
| --- | --- | --- |
| **mask** | 반투명 검정 (알파 0.5) 전체 화면 마스크 | 모든 강조 단계 |
| **spotlight** | mask 위에 원형 컷아웃(반경 60~120px), 강조 대상 좌표 중심 | 단계 2, 3, 5, 6 |
| **arrow** | spotlight 옆 노란색 화살표(픽션 가능, 기존 UI 자산) | 단계 2, 3, 5 |
| **text_box** | 화면 하단 또는 좌하단 본문 박스 (300×120, 반투명 흰 배경) | 모든 단계 |
| **cta_button** | 화면 하단 중앙 큰 버튼 (240×60, primary 색) | 단계 1, 4, 7, 8 (패시브 단계) |

### 5.2 좌표 가이드 (1920×1080 기준)

| 강조 대상 | 중심 좌표 (X, Y) | 반경 |
| --- | --- | --- |
| 상단 곡식 HUD | (200, 50) | 80 |
| 좌측 유닛 패널 (궁수) | (80, 400) | 100 |
| stage_01 첫 build_zone | (740, 640) | 100 |
| 양만춘 영웅 위치 | (가변, hero.x) | 90 |
| 좌하단 manual_mode 라벨 | (200, 1000) | 80 |
| 상단 우측 일시정지 버튼 | (1720, 50) | 60 |

> 좌표는 Design Lead가 최종 와이어프레임 라운드에서 확정. 본 명세는 권고치.

---

## 6. 신규 ui_strings 키 목록 (총 35개)

본 라운드에서는 **키만 등록**. 한국어 표시 텍스트 확정은 Design Lead의 다음 라운드 책임 (DECISION-PL-P4-006).

> `tutorial.complete.cta` 는 §6.1 단계 8 CTA 와 §6.2 메뉴-종료 흐름에서 공유한다 — SSOT 원칙(§0.2 컨벤션) 에 따라 1건만 등재한다.

### 6.1 단계별 본문 (24 keys)

| KEY | 용도 |
| --- | --- |
| `tutorial.step1.title` | 단계 1 제목 |
| `tutorial.step1.body` | 단계 1 본문 |
| `tutorial.step1.cta` | 단계 1 진행 버튼 ("다음" 등) |
| `tutorial.step2.title` | 단계 2 제목 |
| `tutorial.step2.body` | 단계 2 본문 |
| `tutorial.step2.cta` | 단계 2 진행 안내 ("곡식을 누르시오" 등) |
| `tutorial.step3.title` | 단계 3 제목 |
| `tutorial.step3.body` | 단계 3 본문 |
| `tutorial.step3.cta` | 단계 3 진행 안내 |
| `tutorial.step4.title` | 단계 4 제목 |
| `tutorial.step4.body` | 단계 4 본문 |
| `tutorial.step4.cta` | 단계 4 진행 버튼 (wave 종료 후 활성화) |
| `tutorial.step5.title` | 단계 5 제목 |
| `tutorial.step5.body` | 단계 5 본문 |
| `tutorial.step5.cta` | 단계 5 진행 안내 ("M 키를 누르시오") |
| `tutorial.step6.title` | 단계 6 제목 |
| `tutorial.step6.body` | 단계 6 본문 |
| `tutorial.step6.cta` | 단계 6 진행 안내 |
| `tutorial.step7.title` | 단계 7 제목 |
| `tutorial.step7.body` | 단계 7 본문 |
| `tutorial.step7.cta` | 단계 7 진행 버튼 |
| `tutorial.step8.title` | 단계 8 제목 |
| `tutorial.step8.body` | 단계 8 본문 |
| `tutorial.complete.cta` | "Stage 1로 가기" 버튼 |

### 6.2 메뉴 / 스킵 / 완료 (7 keys)

| KEY | 용도 |
| --- | --- |
| `menu.tutorial.button` | 메인 메뉴의 "튜토리얼" 버튼 라벨 |
| `tutorial.skip.button` | 단계 우상단 "튜토리얼 종료" 버튼 |
| `tutorial.skip.confirm.title` | 스킵 확인 다이얼로그 제목 |
| `tutorial.skip.confirm.body` | 스킵 확인 다이얼로그 본문 |
| `tutorial.skip.confirm.yes` | "예, 종료" 버튼 |
| `tutorial.skip.confirm.no` | "아니오, 계속" 버튼 |
| `tutorial.skip.dont_show_again` | "다시 보지 않기" 체크박스 라벨 |

### 6.3 HUD 화살표 보조 라벨 (3 keys)

| KEY | 용도 |
| --- | --- |
| `tutorial.hud_arrow.resource` | 단계 2 곡식 HUD 옆 작은 라벨 ("여기" 등) |
| `tutorial.hud_arrow.buildzone` | 단계 3 build_zone 옆 라벨 ("여기에 배치") |
| `tutorial.hud_arrow.hero` | 단계 5 양만춘 옆 라벨 ("양만춘") |

### 6.4 보조 (2 keys)

| KEY | 용도 |
| --- | --- |
| `tutorial.intro.title` | 튜토리얼 진입 시 첫 화면 제목 (단계 1 직전, 1초 페이드인) |
| `tutorial.intro.body` | 같이 나오는 한 줄 부제 ("8단계로 익혀 봅시다" 등) |

### 6.5 키 총 개수

- 단계별 본문: 24 (단계 1~8 title/body/cta = 24, 단계 8 cta는 `tutorial.complete.cta` 로 §6.2와 공유)
- 메뉴/스킵/완료: 7 (`tutorial.complete.cta` 포함 — 단계 8 cta 와 공유)
- HUD 화살표: 3
- 보조: 2
- 공유 키 중복 제거 (-1): `tutorial.complete.cta`
- **합계: 35** (24 + 7 + 3 + 2 − 1)

> Design Lead 다음 라운드 인계 (`docs/story/08_ui_strings.md` §20 신설): 본 명세 기반으로 35개 키 + 한국어 텍스트 채워 SSOT 등재 — 본 PR 에서 §20 키 예약은 이미 등록 완료.

---

## 7. 자산 요구사항

### 7.1 신규 일러스트

- **없음** (DECISION-PL-P4-008). 기존 `assets/characters/yang_manchun_placeholder.png` 등 5종 재사용.

### 7.2 UI 신규 자산

| 자산 | 설명 | 출처 |
| --- | --- | --- |
| `assets/ui/tutorial_mask.png` | 반투명 검정 마스크 (1×1 stretchable) | 신규, Design Lead 작성 (10분 이내 작업) |
| `assets/ui/tutorial_arrow_yellow.png` | 노란 화살표 (좌·우·상·하 4방향 또는 단일 회전) | 신규, Design Lead (또는 기존 화살 아이콘 재색칠) |
| `assets/ui/tutorial_text_box.png` | 반투명 흰 배경 텍스트 박스 (9-slice) | 기존 dialog 박스 자산 재사용 가능 |

### 7.3 사운드

- 단계 진행 시 짧은 SFX 권고 (`audio/sfx/tutorial_step.wav`) — Audio Engineer 신설 라운드와 합류. Phase 4 본 라운드 필수 아님.

---

## 8. 구현 인계 체크리스트 (Dev Lead 다음 라운드)

- [ ] `save_slot.tutorial_dismissed`, `save_slot.tutorial_completed` 필드 신설 (스키마 마이그레이션).
- [ ] `src/scenes/tutorial_scene.py` (또는 동등) 신규 — 8 단계 상태 머신, mock wave 재생, HUD 강조 오버레이 렌더링.
- [ ] `src/scenes/menu_scene.py` — `menu.tutorial.button` 추가.
- [ ] `src/scenes/intro_scene.py` (또는 동등) — 종료 후 튜토리얼 자동 진입 분기.
- [ ] `tests/test_tutorial_flow.py` 신규 — 자동 진입, 메뉴 재진입, 스킵, "다시 보지 않기" 토글, 단계별 표시 상한 fallback 5종.
- [ ] `docs/story/08_ui_strings.md` §20 추가 — 36개 키 + 한국어 텍스트 (Design Lead).
- [ ] `docs/07_wireframes_visuals.md` §24 갱신 — 8단계 와이어프레임 (Design Lead).

---

## 9. 변경 이력

| 버전 | 일자 | 작성자 | 내용 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-20 | 기획 리더 (Phase 4) | 최초 작성. 8단계 UX, 스킵/재진입 정책, 36개 신규 ui_strings 키 등록, DECISION-PL-P4-001~008. |

— 튜토리얼 UX 명세 v1.0 끝 —
