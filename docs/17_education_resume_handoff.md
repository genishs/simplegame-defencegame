# 17. 교육 통합 작업 — 중단/이어가기 핸드오프

> 작성: 2026-06-03 (세션 중단 시점)
> 브랜치: `feature/education-integration` (develop 대비 10커밋 ahead, **원격 미푸시**)
> 운영: 자율 팀 모드 — 되돌릴 수 있는 로컬 작업은 진행, 푸시/배포 등 외부행위는 사용자 승인 대기

---

## 0. 한눈에 — 다음에 여기서 이어가면 됨

- **다음 작업 = 출시 블로커 수정**(아래 §4). `git switch feature/education-integration` 후 §4의 Task #5부터.
- 모든 코드/문서/웹은 이 브랜치에 커밋됨. 워킹트리 clean. **아무것도 유실 안 됨.**
- pytest **666 passed**, tk-free 가드 통과, ruff clean (중단 시점 그린).

---

## 1. 이번에 내린 결정 (사용자 승인)

플랫폼 라운드테이블(6 페르소나) 결과, 사용자가 두 가지를 확정:

1. **플랫폼 = 무후회 2트랙**
   - (지금) Python 게임에 교육 메커닉 심화 — 플랫폼 중립
   - (병행) 기존 JSON으로 정적 웹 도감 구축 — 웹의 유통/접근성 이점을 게임 폐기 없이 확보 + 전면포팅 리스크 사전검증
   - (게이트) 전면 웹 포팅은 ".exe가 실제 배포 장벽"으로 확인될 때만 별도 착수
2. **교육 범위 = 풀 스펙** (5원칙 + 후크 10종 + 코덱스 3층 + 라벨 전역통일 + 한문 토글 + 선택 퀴즈)

미결 4건 자율 결정(`docs/15` 내 DECISION-EDU-001~004): 결과카드 앞면만 / 퀴즈 스킵가능·보상형 채택 / 한문은 (사실)라벨 카드 우선 / 로컬통계 오프라인+1줄 고지.

---

## 2. 완료된 것 (커밋됨)

| 산출물 | 위치 | 담당 |
|---|---|---|
| 교육 통합 확정 스펙 (5원칙·H1~H10·라벨·LO매핑·스키마) | `docs/15_education_integration_spec.md` | product-lead |
| 구현 계획 (웨이브별 파일단위 분해) | `docs/16_education_build_plan.md` | dev-lead |
| 데이터 기반: codex.json(15장), units `history_blurb`, enemies `intro_banner`, stage `history_caption`, schema/loader 확장, ui_strings §22 | `src/data/*`, `docs/story/08_ui_strings.md` | dev-lead |
| MUST UI 훅 7종 (H1 캡션 / H2 배너 / H3 툴팁 / H4 결과카드 / H5 도감 / H6 토스트 / H7 토산게이지) | `src/ui/*`, `src/systems/{education_state,codex_progress,endurance}.py`, `src/scenes/{battle_scene,menu_scene,codex_scene}.py` | developer |
| 정적 웹 도감 MVP (Track B) | `web/` (index.html, styles/, scripts/app.js, data/codex.json) | design-publisher |
| 교육 테스트 +80건 | `tests/test_education_data.py`(33), `tests/test_education_hooks.py`(47) | dev-lead/developer |

검증(QA): 666 passed, tk-free EXIT 0, ruff clean, **라벨 무결성(QA-EDU-11) PASS**. 학습목표 LO1·LO4·LO5 자연 노출 확인.

---

## 3. 커밋 목록 (이 브랜치, 미푸시)

```
020a7a0 feat(edu): H7 토산 버티기 게이지 + 버티기 승리 (스테이지5)
4f72a45 feat(edu): H5 도감 화면 (그리드+상세+완성도+한문토글)
4c33d2c feat(edu): H4 결과 카드 앞면 연출 + 해금/진행도 영속
c271d82 feat(edu): H2 적 첫등장 배너 + H6 라벨 첫노출 토스트   ← web/·docs/15도 함께 포함(git add -A 부수효과, 무해)
0085142 feat(edu): H3 유닛 사료 툴팁
4564f03 feat(edu): H1 도입 역사 캡션 비모달 오버레이
eca6f93 docs(education): add build plan + register new ui_strings keys
c009fd7 test(data): add education-integration schema/loader tests (33)
4e9dbdd feat(data): extend schema/loader for codex + education fields
3306f51 feat(data): add education-integration content fields (Track A Wave 0)
```

---

## 4. ★ 다음 작업 = 출시 블로커 수정 (Task #5, 미착수)

QA가 규명한 **기존 잠복 결함**(이 브랜치 회귀 아님, develop/main에도 존재):

> `enemies.json`에는 적이 6종(`tang_soldier, tang_archer, tang_scout, tang_scout_captain, tang_vanguard_captain, tang_night_raider`)뿐인데, **stage_05는 미정의 적 5종 + 보스를 스폰**한다: `tang_heavy_infantry`, `tang_siege_tower`, `tang_cavalry`, `tang_elite_guard`, 보스 `tang_taizong`.
> 실 게임 `BattleScene._spawn_enemy()`(`src/scenes/battle_scene.py:974`)는 미정의 타입을 **경고 후 조용히 drop** → 최종 스테이지 적 175체 중 **132체(75%)·보스가 영영 미등장**. stage_05는 일반 클리어는 되지만 보스전·난이도·연출이 붕괴.
> README "BL-07 15/15 클리어"는 *fallback EnemyDef를 합성하는* `src/systems/auto_mode_simulator.py`(L87-104)로 통과한 것. 실 게임/통합시뮬엔 fallback 없음. **stage_04/05 실클리어 자동 테스트가 부재**해 잠복.

### 수정 항목 (dev-lead 주도 권장)
1. **enemies.json 백필** — GDD `docs/03_game_design_document.md` §5 적 유닛 표 + 보스 표 기준으로 누락 5종+보스 추가. (스탯이 §5에 전부 정의되어 있음: 당군 중장보병 HP200, 충차 HP600, 공성탑 HP800, 기병 HP150, 엘리트 친위대 HP350, 당 태종 HP3000 4페이즈)
   - 주의: stage_05 스폰 키 ↔ enemies.json 키 ↔ GDD 명칭 매핑 정합(예: `tang_siege_tower`=공성탑/운제 어느 쪽인지 확정).
2. **simulator 분기 정합** — `_spawn_enemy` drop-on-missing을 fail-loud(또는 명시 에러)로, auto_mode_simulator의 fallback 합성과 실게임 동작을 일치시켜 잠복 방지.
3. **테스트 공백 메우기** — stage_04/05 **실게임 클리어 경로** 자동 회귀 테스트 추가(`tests/battle_scene_simulator.py` 패턴).
4. **H7 재튜닝** — 로스터 정상화 후 `stage_05.json`의 `endurance` 블록(`kills_for_full` 등) 재튜닝하여 "버티기 승리"가 실제 발동하도록(현재 적 부족으로 게이지 0.954 캡, 일반클리어가 선점). 게이지 승리 우선순위 검토.

→ 블로커 해소 후 stage_05 실클리어 + H7 버티기 승리 발동 + 666+ 그린 + tk-free 유지 검증, 그 다음 QA 재검수(QA-EDU-02/03, LO2/LO3).

### SHOULD/COULD 잔여 (블로커 아님)
- H8 충돌노트(C1/C2/C3) — 문구는 `edu_strings`에 있으나 씬 렌더 미연결. C1 HUD 영웅이름 "양만춘 [전승]" 배지 누락.
- H10 진엔딩 퀴즈(COULD) 미구현.
- [픽션] 토스트 in-battle 트리거 없음 → 도감 픽션 카드 진입 트리거로 연결 권장.

---

## 5. 수동 육안 검수 남은 항목 (실 Tk 실행 필요, headless로 로직만 검증됨)
캡션 페이드/배너/토스트 위치·가독성, 결과카드 일러스트, 도감 3×5 그리드·잠금카드·완성도 칭호, 한문 토글 레이아웃, stage_05 실플레이 체감.

---

## 6. 사용자 권한 대기 (외부행위 — 승인 시 실행) — 배치 승인 목록
1. **`feature/education-integration` origin 푸시 + develop PR 생성** (현재 로컬에만 10커밋)
2. **정적 웹 도감(`web/`) 배포** (예: GitHub Pages) — 원하면 별도 호스팅
3. (선택) stage_05 로스터 결함을 **별도 이슈로 등록**할지 여부

> 위 3건은 되돌리기 어렵거나 외부로 나가는 행위라 사용자 승인 전까지 보류. 그 외 수정(§4)은 자율 진행 가능.
