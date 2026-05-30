# Phase 5 진행 체크리스트

본 체크리스트는 `docs/14_phase5_plan.md` 의 sub-phase 별 진행을 1줄 단위로 추적한다. 각 페르소나가 작업 완료 시 체크를 채우고, PR/커밋 해시를 옆에 기록한다.

> 갱신 규칙: 체크 박스 옆에 `(#PR번호 / commit-hash)` 또는 `(N/A — 해당 작업이 별도 PR 없이 본 plan 내 처리)` 형태로 추적.

> 기준 베이스라인: develop@`0773a5f` (Phase 4 R3 종료), pytest **448 passed**, ruff/black 0 에러.

> **버전 매핑(SCM 정정 2026-05-19)**: Phase 4 종료 = v0.4.0-rc.1 → v0.4.0(GA, 사용자 검수 대기). Phase 5 sub-phase는 develop 누적 진행, Phase 5 종료 = v1.0.0-rc.1 → v1.0.0. 중간 마이너(v0.5.0/v0.6.0) 도입 여부 OPEN-PL-P5-006.

---

## Phase 5.1 — BGM 통합 (대상: develop 누적, Phase 5 RC 합산)

- [ ] OPEN-AUDIO-001 클로즈 — BGM 백엔드 선택 (pygame.mixer / pyminiaudio / playsound3 등) — 담당: Audio Engineer
- [ ] DECISION-AUDIO-013 기록 — `docs/audio/00_audio_policy.md` §3.1 갱신
- [ ] `src/core/sound.py` BGM 백엔드 추가 — `play_bgm()`/`stop_bgm()` 실 동작 + 헤드리스 graceful fallback — 담당: Audio Engineer
- [ ] `assets/audio/bgm/` 8 placeholder OGG (무음 또는 사인파) + 라이선스 노트 README
- [ ] PyInstaller spec `datas` 에 `assets/audio/bgm/` 추가 (DECISION-AUDIO-009 패턴)
- [ ] `tests/test_sound_bgm.py` 신규 10+건 — BGM 루프/페이드/fallback mock — 담당: Audio Engineer
- [ ] `pytest -m audio` 18 + 신규 10+ 모두 그린
- [ ] ubuntu CI 헤드리스 fallback 검증 (`.github/workflows/ci.yml` 변경 최소화)
- [ ] PyInstaller `--onefile` 빌드 사이즈 ≤ 40MB 측정
- [ ] DoD 체크 — ruff/black/pytest 0 에러, BGM 백엔드 통합 동작
- [ ] CHANGELOG `[Unreleased]` Phase 5.1 항목 추가
- [ ] (OPEN-PL-P5-006 채택 시) 중간 마이너 태그 + GitHub Release prerelease=true — Steering 표결 후 결정

## Phase 5.2 — 전체 스토리 통합 (대상: develop 누적, Phase 5 RC 합산)

- [ ] `src/scenes/intro_scene.py` 신규 또는 `menu_scene.py` 확장 — 인트로 컷씬 텍스트 + BGM 동기화 — 담당: Dev Team2 + Design Lead
- [ ] 각 스테이지 진입 시 intro 대사 5종 (`docs/story/02~06` cold-open) overlay 출력
- [ ] 각 스테이지 클리어 시 outro 대사 5종 출력 + stage_05 → 엔딩 풀 시퀀스
- [ ] 5인 픽션 캐릭터 대사 SSOT를 `docs/story/08_ui_strings.md` §21에 보강 (60~80건 한국어 확정) — 담당: Design Member
- [ ] 양만춘 화자 라벨 **[전승]** 명시 (역사 인물 직접 인용 회피 정책)
- [ ] stage_02 백암성 평화 항복 분기 텍스트 게임 내 실 표시
- [ ] `tests/test_story_integration.py` 신규 — intro/outro 텍스트 lookup + 회귀 가드
- [ ] `tests/test_no_korean_literal_in_ui.py` 가드 그린 (한국어 리터럴 회귀 0건)
- [ ] 인트로/엔딩 컷씬 ESC/SPACE 스킵 가능, M키 토글과 충돌 없음
- [ ] pytest 누적 480+ passed
- [ ] DoD 체크 — ruff/black/pytest 0 에러, 5스테이지 intro/outro 통합 동작
- [ ] CHANGELOG `[Unreleased]` Phase 5.2 항목 추가
- [ ] (OPEN-PL-P5-006 채택 시) 중간 마이너 태그 + GitHub Release prerelease=true — Steering 표결 후 결정

## Phase 5.3 — 자산 실수급 / 최종 완성 (대상 버전: v1.0.0-rc.1 진입 준비)

- [ ] BGM 8곡 실 수급 — freesound/opengameart CC0/CC BY 4.0 또는 자체 제작 ([자체제작]/[전승]) — 담당: Audio Engineer
- [ ] `docs/audio/01_asset_inventory.md` BGM 8행 출처 URL + 저작자 + 라이선스 ID 기입, `[픽션·승인대기]` → `[확정]`/`[자체제작]` 전환
- [ ] SFX 8 placeholder → 20개 풀세트 실수급 또는 자체 제작
- [ ] AU-01~08 회귀 가드 그린 (실 자산 교체 후 회귀 0)
- [ ] 픽션 캐릭터 일러스트 5종 — 옵션 B(강화된 placeholder) 우선 적용 (DECISION-PL-P5-002) — 담당: Design Lead
- [ ] `docs/08_asset_inventory.md` `[픽션·승인대기]` 행 0건 전환
- [ ] PyInstaller `--onefile` 빌드 사이즈 ≤ 50MB 측정 (DECISION-AUDIO-010 예산)
- [ ] Test Lead 시각 매트릭스 검수 보고서 — `docs/qa/phase5_visual_review.md` 신규
- [ ] DoD 체크 — ruff/black/pytest 0 에러, 자산 라이선스 검증 N/N ✓
- [ ] CHANGELOG `[Unreleased]` Phase 5.3 항목 추가

## Phase 5.4 — 1.0.0 패키징 / 릴리즈 (대상 버전: v1.0.0)

- [ ] 자동 릴리즈 노트 생성 — `release-windows.yml` `gh release create --generate-notes` 또는 release-please-action 검토 — 담당: SCM (또는 Release Engineer)
- [ ] Linux 빌드 CI 추가 — `build-linux.yml` 신규 또는 `ci.yml` 확장 (DECISION-PL-P5-005)
- [ ] macOS 빌드 보류 (OPEN-PL-P5-002 후속 라운드)
- [ ] 코드 서명 미적용 유지 (DECISION-PL-P5-004) + README에 SmartScreen 우회 가이드 추가
- [ ] `docs/qa/v1_0_0_ga_checklist.md` 신규 — 자동 가드 N/N + 사용자 검수 CAT-01~10 + DPI 매트릭스 + 매크로 OS 1건
- [ ] pytest 누적 500+ passed 안정
- [ ] `v1.0.0-rc.1` 태그 + GitHub Release prerelease=true 자동 게시
- [ ] Phase 5 회고 `docs/phase5/retrospective.md` 작성 — 담당: Planning Lead
- [ ] CHANGELOG `[1.0.0-rc.1]` 섹션 — Phase 5 전체 산출물 요약 + DECISION-PL-P5-### 목록 포함
- [ ] README "현재 진행 상태" 표 Phase 5 ⏳ → ✅ 전환 준비 (사용자 검수 통과 후 SCM 별도 라운드)

## Phase 5 GA 진입 (사용자 의존 — Phase 4 GA 대기 패턴 동일)

- [ ] CAT-01~10 사용자 시각 검수 통과
- [ ] DPI 매트릭스 (1920×1080 + 100%/125% + Linux 1건) 통과
- [ ] SCM 별도 라운드에서 `develop → main` 머지
- [ ] `v1.0.0` 태그 + GitHub Release prerelease=false 전환
- [ ] CHANGELOG `[1.0.0]` 섹션 GA 갱신
- [ ] README "현재 진행 상태" 표 Phase 5 ✅ + 1.0.0 정식 릴리즈 명시

---

## OPEN-PL-P5-### 추적 (후속 라운드 위임)

- [ ] OPEN-PL-P5-001 — Localization Engineer 페르소나 신설 표결 (Steering)
- [ ] OPEN-PL-P5-002 — Release Engineer 페르소나 신설 표결 + macOS 빌드 CI 추가 (Steering, Phase 5.4 진입 시)
- [ ] OPEN-PL-P5-003 — macOS Apple notarization 인증서 정책 (Planning Lead + SCM, v1.0.0 이후)
- [ ] OPEN-PL-P5-004 — BGM 백엔드 최종 선택 (Audio Engineer, Phase 5.1 진입 시)
- [ ] OPEN-PL-P5-005 — 픽션 캐릭터 일러스트 옵션 A(정식) 도입 시점 (Design Lead, Phase 5.3 진행 중)
- [ ] OPEN-PL-P5-006 — Phase 5 중간 마이너 태그(v0.5.0/v0.6.0) 도입 여부 (Steering, Phase 5.2 진입 시점) — SCM 정정 2026-05-19 신설
