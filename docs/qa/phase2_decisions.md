# Phase 2 OPEN 항목 결정 (DECISION-Q-###)

본 문서는 Test Lead 페르소나가 Phase 2 종료 시점에 OPEN 상태로 남아 있던 PM·Dev·Design·Team2 OPEN 항목을 일괄 종결한 결정 기록이다. 사용자 부재 상황에서 페르소나 자율 진행 정책(`feedback_autonomy_and_docs`)에 따라 Test Lead 권한으로 닫는다.

| ID | 원천 OPEN | 결정 | 후속 액션 |
| --- | --- | --- | --- |
| DECISION-Q-001 | PM OPEN-1 | 픽션 캐릭터 등장 **승인** | `[픽션]` / `[픽션·승인대기]` 라벨 유지 |
| DECISION-Q-002 | PM OPEN-2 | 워킹 트리 race **종결** (별도 clone 전략으로 해결) | 페르소나 가이드에 명시 |
| DECISION-Q-003 | PM OPEN-3 | `docs/story/08_ui_strings.md` **SSOT 채택** | Phase 3에서 비-SSOT 사본을 키 참조로 치환 |
| DECISION-Q-004 | Dev OPEN-1 | 사운드 라이브러리: **winsound 기본 채택** | 추가 의존성 없음 |
| DECISION-Q-005 | Dev OPEN-T1-001 | `PoolExhausted` 위치: **`src/entities/entity.py` 최상위** | 현 상태 유지 |
| DECISION-Q-006 | Design OPEN-D-001 | 픽션 비주얼: **Phase 2 플레이스홀더 5종 / Phase 3 상세화** | Phase 3 일러스트 작업 항목 등록 |
| DECISION-Q-007 | Design OPEN-D-002 | 폰트: **Noto Sans KR (OFL) 채택, 폴백 `Malgun Gothic`** | PyInstaller spec 업데이트 필요 |
| DECISION-Q-008 | Design OPEN-D-101 | 컷씬 18장: **Phase 3 내부 작업 (외주 보류)** | Phase 3 backlog |
| DECISION-Q-009 | Design OPEN-D-201 / Team2 OPEN-T2-001 | M키 영웅 조작: **Phase 3 명세 후 구현, Phase 2 플래그만** | 현 `battle_scene.py`의 `m`/`M` 바인딩 유지 |
| DECISION-Q-010 | Team2 OPEN-T2-002 | `_spawn_enemy` x=0.0: **Phase 2 유지, Phase 3 첫 waypoint 참조** | GitHub Issue 등록 |
| DECISION-Q-011 | Team2 OPEN-T2-003 | `stage_01.json reward.grain` 누락: **Phase 2 폴백 유지, Phase 3 데이터 패치** | GitHub Issue 등록 |

## 권한 근거

- `MEMORY.md` → `feedback_autonomy_and_docs.md` 자율 진행 규칙
- 본 작업 명시: "당신이 OPEN 항목을 닫을 수 있는 권한도 갖습니다."
- 사용자 부재 상황, Phase 2 종료를 위한 머지 차단 해소 필요