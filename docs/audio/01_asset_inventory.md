# 01. 오디오 자산 인벤토리 (Audio Asset Inventory) — 안시성: 88일의 약속

> Phase 4 킥오프 산출물 #2
> 작성: Audio Engineer (DECISION-PERSONA-001, 2026-05-19)
> 기준 커밋: `2b247b5` (develop HEAD, v0.3.0-rc.1 직후)
> 참조: `docs/audio/00_audio_policy.md`, `docs/08_asset_inventory.md` §9

---

## 0. 본 문서의 사용법

- **현재 상태**: 모든 자산은 `[픽션·승인대기]` — Phase 4 킥오프 기준으로 실제 파일 없음.
- **Phase 5 수급 시**: 실제 파일명, 라이선스 URL, 저작자를 각 행에 기입하고 라벨을 `[확정]`으로 변경.
- **식별자(ID)**: 코드(`SoundManager.play_bgm(name)`, `SoundManager.play_sfx(name)`)에 직접 사용하는 키.
- **출처 후보**: 1순위 = freesound.org(CC0/CC BY 다수), 2순위 = opengameart.org(CC0/CC BY 다수), 3순위 = 자체 제작.
- 라이선스 정책 전문: `docs/audio/00_audio_policy.md` §4 참조.

### 라벨 범례

| 라벨 | 의미 |
|------|------|
| `[픽션·승인대기]` | 자산 미수급 — placeholder 행만 존재 |
| `[픽션]` | 스크립트/기획은 확정, 제작 미착수 |
| `[전승]` | 역사·전통 소재 기반 자체 제작 또는 CC0 |
| `[자체제작]` | 팀 내부 또는 AI 도구 생성 |
| `[확정]` | 파일 수급·라이선스 검토 완료, 커밋됨 |

---

## 1. BGM (Background Music)

| ID | 파일명 (placeholder) | 카테고리 | 예상 길이 | 포맷 | 라이선스 후보 | 출처 후보 | 상태 |
|----|---------------------|----------|----------|------|--------------|----------|------|
| `bgm_main_menu` | `bgm_main_menu.ogg` | BGM | 2:30~3:00 | OGG q5 | CC0 / CC BY 4.0 | freesound.org, opengameart.org | `[픽션·승인대기]` |
| `bgm_stage_01` | `bgm_stage_01_battle.ogg` | BGM | 2:00~2:30 | OGG q5 | CC0 / CC BY 4.0 | opengameart.org | `[픽션·승인대기]` |
| `bgm_stage_02` | `bgm_stage_02_battle.ogg` | BGM | 2:00~2:30 | OGG q5 | CC0 / CC BY 4.0 | opengameart.org | `[픽션·승인대기]` |
| `bgm_stage_03` | `bgm_stage_03_battle.ogg` | BGM | 2:00~2:30 | OGG q5 | CC0 / CC BY 4.0 | opengameart.org | `[픽션·승인대기]` |
| `bgm_stage_04` | `bgm_stage_04_battle.ogg` | BGM | 2:00~2:30 | OGG q5 | CC0 / CC BY 4.0 | opengameart.org | `[픽션·승인대기]` |
| `bgm_stage_05` | `bgm_stage_05_battle.ogg` | BGM | 2:00~2:30 | OGG q5 | CC0 / CC BY 4.0 | opengameart.org | `[픽션·승인대기]` |
| `bgm_ending_victory` | `bgm_ending_victory.ogg` | BGM | 1:30~2:00 | OGG q5 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `bgm_ending_defeat` | `bgm_ending_defeat.ogg` | BGM | 1:30~2:00 | OGG q5 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |

**소계**: 8곡, 예상 크기 ~20MB

---

## 2. SFX (Sound Effects) — 전투

| ID | 파일명 (placeholder) | 카테고리 | 예상 길이 | 포맷 | 라이선스 후보 | 출처 후보 | 상태 |
|----|---------------------|----------|----------|------|--------------|----------|------|
| `sfx_arrow_shoot` | `sfx_arrow_shoot.wav` | SFX | ~0.3초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_arrow_hit` | `sfx_arrow_hit.wav` | SFX | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_stone_throw` | `sfx_stone_throw.wav` | SFX | ~0.4초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_stone_hit` | `sfx_stone_hit.wav` | SFX | ~0.3초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_enemy_hit` | `sfx_enemy_hit.wav` | SFX | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `sfx_enemy_death` | `sfx_enemy_death.wav` | SFX | ~0.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `sfx_hero_move` | `sfx_hero_move.wav` | SFX | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_hero_skill` | `sfx_hero_skill.wav` | SFX | ~0.6초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org, opengameart.org | `[픽션·승인대기]` |
| `sfx_wave_start` | `sfx_wave_start.wav` | SFX | ~1.0초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `sfx_wave_end` | `sfx_wave_end.wav` | SFX | ~1.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `sfx_gate_damaged` | `sfx_gate_damaged.wav` | SFX | ~0.5초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_gate_destroyed` | `sfx_gate_destroyed.wav` | SFX | ~1.0초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |

**소계**: 12개, 예상 크기 ~1.5MB

---

## 3. SFX — 일시정지·시스템

| ID | 파일명 (placeholder) | 카테고리 | 예상 길이 | 포맷 | 라이선스 후보 | 출처 후보 | 상태 |
|----|---------------------|----------|----------|------|--------------|----------|------|
| `sfx_pause` | `sfx_pause.wav` | SFX | ~0.3초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_resume` | `sfx_resume.wav` | SFX | ~0.3초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_stage_clear` | `sfx_stage_clear.wav` | SFX | ~2.0초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org, opengameart.org | `[픽션·승인대기]` |
| `sfx_stage_fail` | `sfx_stage_fail.wav` | SFX | ~1.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `sfx_resource_earn` | `sfx_resource_earn.wav` | SFX | ~0.4초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_unit_place` | `sfx_unit_place.wav` | SFX | ~0.3초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_unit_remove` | `sfx_unit_remove.wav` | SFX | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `sfx_unit_upgrade` | `sfx_unit_upgrade.wav` | SFX | ~0.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |

**소계**: 8개, 예상 크기 ~0.7MB

---

## 4. UI Sound

| ID | 파일명 (placeholder) | 카테고리 | 예상 길이 | 포맷 | 라이선스 후보 | 출처 후보 | 상태 |
|----|---------------------|----------|----------|------|--------------|----------|------|
| `ui_button_click` | `ui_button_click.wav` | UI | ~0.1초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_button_hover` | `ui_button_hover.wav` | UI | ~0.08초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_menu_open` | `ui_menu_open.wav` | UI | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_menu_close` | `ui_menu_close.wav` | UI | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_menu_transition` | `ui_menu_transition.wav` | UI | ~0.3초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `ui_dialog_open` | `ui_dialog_open.wav` | UI | ~0.25초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_dialog_close` | `ui_dialog_close.wav` | UI | ~0.25초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_reward_get` | `ui_reward_get.wav` | UI | ~0.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / CC BY 4.0 | freesound.org | `[픽션·승인대기]` |
| `ui_error` | `ui_error.wav` | UI | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |
| `ui_stage_locked` | `ui_stage_locked.wav` | UI | ~0.2초 | WAV 16-bit 44.1kHz 모노 | CC0 | freesound.org | `[픽션·승인대기]` |

**소계**: 10개, 예상 크기 ~0.4MB

---

## 5. Voice / 외침

| ID | 파일명 (placeholder) | 카테고리 | 예상 길이 | 포맷 | 라이선스 후보 | 출처 후보 | 상태 |
|----|---------------------|----------|----------|------|--------------|----------|------|
| `voice_hero_spawn` | `voice_hero_spawn.wav` | Voice | ~0.8초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_hero_skill_01` | `voice_hero_skill_01.wav` | Voice | ~0.6초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_hero_skill_02` | `voice_hero_skill_02.wav` | Voice | ~0.6초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_hero_damaged` | `voice_hero_damaged.wav` | Voice | ~0.5초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_commander_wave` | `voice_commander_wave.wav` | Voice | ~1.5초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_commander_victory` | `voice_commander_victory.wav` | Voice | ~2.0초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_commander_defeat` | `voice_commander_defeat.wav` | Voice | ~2.0초 | WAV 16-bit 44.1kHz 모노 | 자체제작 / CC0 | 자체제작 우선 | `[픽션·승인대기]` |
| `voice_enemy_attack` | `voice_enemy_attack.wav` | Voice | ~0.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / 자체제작 | freesound.org / 자체제작 | `[픽션·승인대기]` |
| `voice_enemy_death` | `voice_enemy_death.wav` | Voice | ~0.5초 | WAV 16-bit 44.1kHz 모노 | CC0 / 자체제작 | freesound.org / 자체제작 | `[픽션·승인대기]` |

**소계**: 9개, 예상 크기 ~2.5MB

---

## 6. 전체 요약

| 카테고리 | 자산 수 | 예상 크기 | 상태 |
|----------|--------|----------|------|
| BGM | 8 | ~20MB | 전체 `[픽션·승인대기]` |
| SFX (전투) | 12 | ~1.5MB | 전체 `[픽션·승인대기]` |
| SFX (시스템) | 8 | ~0.7MB | 전체 `[픽션·승인대기]` |
| UI Sound | 10 | ~0.4MB | 전체 `[픽션·승인대기]` |
| Voice | 9 | ~2.5MB | 전체 `[픽션·승인대기]` |
| **합계** | **47** | **~25.1MB** | — |

목표 예산(≤ 30MB, DECISION-AUDIO-010) 대비 여유 ~4.9MB. BGM 추가 또는 품질 향상 시 사용 가능.

---

## 7. 위험 사항

| 위험 | 내용 | 대응 |
|------|------|------|
| **라이선스 호환성** | CC BY-SA 자산 혼입 시 게임 전체에 SA 조건 전파 가능 | 수급 전 라이선스 원본 URL 반드시 확인. CC0 우선 |
| **저작자 충돌** | 동일 효과음을 여러 출처에서 수급 시 크레딧 중복/누락 | 인벤토리 행 단위로 원본 URL + 저작자명 필수 기재 |
| **파일 크기 초과** | BGM 품질 향상(q7+) 시 1곡 3MB 초과 가능 | q5 상한 준수. 초과 시 Tech Lead 승인 후 예산 재조정 |
| **Voice 자체제작 지연** | 성우 또는 AI 생성 의존 — Phase 5 수급 지연 가능 | placeholder로 무음 WAV(1초) 대체 허용. Release Blocker 아님 |
| **OGG 디코더 미지원** | winsound 스텁 단계에서는 OGG 재생 불가 | 백엔드 교체(Phase 4 후반~Phase 5) 전까지 BGM no-op 유지 |
| **전체 번들 크기** | 오디오 + 이미지 + 폰트 합산 50MB 초과 시 | 이미지 자산 압축 우선 검토. 오디오 예산 30MB 고수 |

---

## 8. 수급 우선순위 (Phase 5 착수 시 참고)

1. **UI Sound** 10종 — 가장 짧고 CC0 다수, 즉시 수급 가능
2. **SFX 시스템** 8종 — 단순 효과음, CC0 freesound.org 다수
3. **SFX 전투** 12종 — 전투 몰입감 핵심
4. **BGM** 8곡 — 파일 크기 큼, 라이선스 검토 시간 여유 필요
5. **Voice** 9종 — 자체제작 의존도 높음, 마지막 수급

---

## 9. 변경 이력

| 날짜 | 작성자 | 내용 |
|------|-------|------|
| 2026-05-19 | Audio Engineer | 초안 작성 — Phase 4 킥오프, 전체 placeholder |