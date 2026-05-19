"""사운드 백엔드 — no-op 스텁 (Phase 4 킥오프 기준).

현재 상태 (DECISION-Q-006 -> DECISION-AUDIO-003):
    - 모든 메서드는 no-op. 호출자는 자유롭게 호출 가능하며 예외 없이 통과.
    - winsound(Windows stdlib)는 단일 채널·WAV 전용·볼륨 제어 없음 등 한계로
      실제 구현에 사용하지 않는다. 참고: docs/audio/00_audio_policy.md §2.

백엔드 교체 로드맵 (DECISION-AUDIO-004):
    - Phase 4 후반: simpleaudio 시범 도입 (SFX 전용, Tech Lead 승인 필요)
    - Phase 5: pygame.mixer 또는 동급으로 BGM + 전체 채널 구현
    - 교체 시 본 파일의 no-op 구현을 실제 백엔드 호출로 교체하며
      호출부(BattleScene, MenuScene 등)는 변경 없이 유지.

자산 규약 (DECISION-AUDIO-006, DECISION-AUDIO-008):
    - BGM: assets/audio/bgm/*.ogg  (예: "bgm_main_menu" -> bgm_main_menu.ogg)
    - SFX: assets/audio/sfx/*.wav  (예: "sfx_arrow_shoot" -> sfx_arrow_shoot.wav)
    - UI:  assets/audio/ui/*.wav   (예: "ui_button_click" -> ui_button_click.wav)
    - Voice: assets/audio/voice/*.wav (예: "voice_hero_skill_01")
    - 전체 인벤토리: docs/audio/01_asset_inventory.md

미래 API (Phase 4 후반~Phase 5 구현 예정):
    set_master_volume(v: float) -> None
    set_category_volume(category: str, v: float) -> None
    mute() -> None
    unmute() -> None
    fade_out_bgm(duration_ms: int) -> None
"""

from __future__ import annotations

from src.core.logger import get_logger

_log = get_logger(__name__)


class SoundManager:
    """no-op 사운드 매니저 — Phase 4 후반 백엔드 교체 전까지 인터페이스 고정 역할.

    사용 예시::

        sm = SoundManager()
        sm.play_bgm("bgm_main_menu")        # BGM 재생 (루프)
        sm.play_sfx("sfx_arrow_shoot")      # SFX 1회 재생
        sm.play_sfx("ui_button_click")      # UI sound 1회 재생
        sm.set_master_volume(0.7)           # 전체 볼륨 (미구현 — 미래 API)
        sm.mute()                           # 음소거 (미구현 — 미래 API)
        sm.stop_all()                       # 모든 재생 중지
    """

    def play_bgm(self, name: str, loop: bool = True) -> None:
        """BGM을 재생한다.

        Args:
            name: 자산 식별자. 예: "bgm_main_menu", "bgm_stage_01_battle".
                  실제 파일 경로는 assets/audio/bgm/{name}.ogg 로 해석됨.
                  전체 식별자 목록: docs/audio/01_asset_inventory.md §1.
            loop: True이면 트랙 끝에서 처음으로 루프. 기본값 True.

        현재 구현: no-op (로그만 출력).
        Phase 5 구현 시: pygame.mixer.music.load() / .play(loops=-1) 패턴 예정.
        """
        _log.debug("SoundManager.play_bgm(%s, loop=%s) [no-op]", name, loop)

    def play_sfx(self, name: str) -> None:
        """SFX 또는 UI Sound를 1회 재생한다.

        Args:
            name: 자산 식별자. 예: "sfx_arrow_shoot", "ui_button_click".
                  sfx_ 접두사  -> assets/audio/sfx/{name}.wav
                  ui_ 접두사   -> assets/audio/ui/{name}.wav
                  voice_ 접두사 -> assets/audio/voice/{name}.wav
                  전체 식별자 목록: docs/audio/01_asset_inventory.md §2~§5.

        현재 구현: no-op (로그만 출력).
        Phase 4 후반 구현 시: simpleaudio.WaveObject.from_wave_file().play() 패턴 예정.
        """
        _log.debug("SoundManager.play_sfx(%s) [no-op]", name)

    def stop_all(self) -> None:
        """모든 재생 중인 사운드(BGM + SFX)를 즉시 중지한다.

        씬 전환, 일시정지, 앱 종료 시 호출.

        현재 구현: no-op (로그만 출력).
        """
        _log.debug("SoundManager.stop_all() [no-op]")

    def set_master_volume(self, v: float) -> None:
        """전체 마스터 볼륨을 설정한다. (미래 API — Phase 5 구현 예정)

        Args:
            v: 0.0(음소거) ~ 1.0(최대). 범위 밖 값은 클램프.

        현재 구현: no-op.
        참고: DECISION-AUDIO-002 (카테고리별 독립 볼륨 채널).
        """
        _log.debug("SoundManager.set_master_volume(%s) [no-op]", v)

    def mute(self) -> None:
        """모든 사운드를 음소거한다. (미래 API — Phase 5 구현 예정)

        재생 상태는 유지하되 볼륨만 0으로 설정.
        unmute() 호출 시 이전 볼륨으로 복원.

        현재 구현: no-op.
        """
        _log.debug("SoundManager.mute() [no-op]")

    def unmute(self) -> None:
        """음소거를 해제한다. (미래 API — Phase 5 구현 예정)

        mute() 호출 전 볼륨으로 복원.

        현재 구현: no-op.
        """
        _log.debug("SoundManager.unmute() [no-op]")