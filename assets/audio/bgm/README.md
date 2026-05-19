# assets/audio/bgm — BGM Placeholder 디렉터리

> Phase 5.1 사전 작업 산출물 — Issue #30 (BGM 백엔드 + 자산 실수급)
> 생성: Audio Engineer (2026-05-19)
> 참조: `docs/audio/02_bgm_candidates.md`, `docs/audio/01_asset_inventory.md` §1

---

## 현재 상태

본 디렉터리는 **무음 WAV placeholder** 8건을 포함한다.
Phase 5.1 본 작업에서 실제 OGG 자산으로 교체 예정 (DECISION-AUDIO-006).

| 파일명 | 식별자 | 상태 | 비고 |
|--------|--------|------|------|
| `bgm.menu.wav` | `bgm.menu` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.menu.ogg` 교체 |
| `bgm.intro.wav` | `bgm.intro` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.intro.ogg` 교체 |
| `bgm.stage_01_02.wav` | `bgm.stage_01_02` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.stage_01_02.ogg` 교체 |
| `bgm.stage_03_04.wav` | `bgm.stage_03_04` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.stage_03_04.ogg` 교체 |
| `bgm.stage_05.wav` | `bgm.stage_05` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.stage_05.ogg` 교체 |
| `bgm.victory.wav` | `bgm.victory` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.victory.ogg` 교체 |
| `bgm.defeat.wav` | `bgm.defeat` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.defeat.ogg` 교체 |
| `bgm.tutorial.wav` | `bgm.tutorial` | placeholder (무음 30초 WAV) | Phase 5.1 → `bgm.tutorial.ogg` 교체 |

**WAV 규격**: 44,100 Hz, 스테레오 (2ch), 16-bit PCM, 30초 무음
(실 자산 교체 시 OGG Vorbis q5, 44.1kHz, 스테레오 — DECISION-AUDIO-006)

---

## 라이선스 정책

본 디렉터리의 placeholder WAV는 자체 생성(Python `wave` stdlib) — 저작권 없음.

Phase 5.1 실수급 후 적용될 라이선스 (예정):

| 식별자 | 후보 라이선스 | 저작자 후보 | 출처 후보 |
|--------|------------|----------|---------|
| bgm.menu | CC BY 4.0 | Kevin MacLeod | incompetech.com |
| bgm.intro | CC0 1.0 | — | opengameart.org |
| bgm.stage_01_02 | CC0 1.0 | szegvari | freesound.org |
| bgm.stage_03_04 | CC BY 4.0 | Sangue Voador | opengameart.org |
| bgm.stage_05 | CC BY 4.0 | Kevin MacLeod | incompetech.com |
| bgm.victory | CC BY 4.0 | Kevin MacLeod | incompetech.com |
| bgm.defeat | CC0 1.0 | szegvari | freesound.org |
| bgm.tutorial | CC0 1.0 | Mrthenoronha | freesound.org |

전체 라이선스 정책: `docs/audio/00_audio_policy.md` §4
후보 상세: `docs/audio/02_bgm_candidates.md`

---

## Phase 5.1 교체 절차

1. `ffmpeg -i input.wav -c:a libvorbis -q:a 5 -ar 44100 -ac 2 bgm.{name}.ogg` 변환
2. 기존 `.wav` placeholder 삭제, `.ogg` 파일 커밋
3. `src/core/sound.py` `play_bgm()` 구현 (pygame.mixer 기반, DECISION-AUDIO-013)
4. `docs/audio/01_asset_inventory.md` BGM 행 상태 `[확정]` 갱신
5. CC BY 4.0 트랙: 본 README 하단 크레딧 섹션에 저작자 기재

---

## CC BY 4.0 크레딧 (Phase 5.1 실수급 후 갱신 예정)

```
[placeholder — 실수급 후 CC BY 4.0 저작자 표기 추가 예정]

예시 형식:
"Track Name" by Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/
```
