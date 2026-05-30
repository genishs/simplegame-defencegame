# SFX 자산 — assets/audio/sfx/

> 작성: Audio Engineer (Issue #29, 2026-05-19)
> DECISION-AUDIO-012 (simpleaudio SFX 시범 도입, Phase 4 후반)

---

## 현재 상태

이 디렉터리의 모든 `.wav` 파일은 **무음 placeholder** 입니다.
Python stdlib `wave` 모듈로 생성한 0.1초(44,100 Hz, 모노, 16-bit PCM) 무음 WAV 파일이며,
게임플레이에 아무 영향을 주지 않습니다.

**실수급(실제 음원)은 Phase 5 (#30)에서 교체 예정**입니다.

---

## 파일 목록

| 파일명 | 대응 이벤트 | 상태 |
|--------|------------|------|
| `sfx.arrow_shot.wav` | 화살 발사 | placeholder |
| `sfx.hit_light.wav` | 경량 타격 | placeholder |
| `sfx.hit_heavy.wav` | 중량 타격 | placeholder |
| `sfx.enemy_die.wav` | 적 사망 | placeholder |
| `sfx.hero_skill.wav` | 영웅 스킬 발동 | placeholder |
| `sfx.ui_click.wav` | UI 버튼 클릭 | placeholder |
| `sfx.ui_dialog.wav` | 다이얼로그 전환 | placeholder |
| `sfx.wave_start.wav` | 웨이브 시작 알림 | placeholder |

---

## 라이선스 정책 (DECISION-AUDIO-005)

Phase 5에서 실수급 자산 교체 시 다음 라이선스만 허용:
- **CC0 1.0 (Public Domain)** — 권장
- **CC BY 4.0** — 저작자 표시 필수 (`docs/audio/01_asset_inventory.md`에 기재)
- CC BY-SA 4.0 — 조건부 허용

**금지**: CC BY-NC, 무출처/불명 자산

현재 placeholder는 자체 생성(Python stdlib `wave`)이므로 저작권 무관.

---

## Phase 5 교체 가이드

1. 실수급 WAV 파일을 준비 (44,100 Hz, 모노, 16-bit PCM, < 100KB/파일)
2. 동일한 파일명으로 교체
3. `docs/audio/01_asset_inventory.md`에 출처·저작자·라이선스 기재
4. `tests/test_sound_simpleaudio.py` AU 테스트 그린 확인
5. PR 생성 및 Audio Engineer 리뷰 요청

> 참조: `docs/audio/00_audio_policy.md` §4~5
