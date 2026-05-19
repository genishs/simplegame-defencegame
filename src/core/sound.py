"""사운드 백엔드 — simpleaudio SFX 시범 도입 (Phase 4 후반, Issue #29).

DECISION-AUDIO-012 (2026-05-19, Audio Engineer 자율 명문화):
    - DECISION-AUDIO-003/004에 따라 Phase 4 후반 simpleaudio 시범 도입 실행.
    - SFX / UI Sound: simpleaudio.WaveObject 비동기 재생 (다채널 동시 재생).
    - BGM: Phase 5 #30 위임 — stub only (play_bgm/stop_bgm은 no-op 유지).
    - 자산·파일 누락 → graceful fallback (noop, 경고 로그만).
    - 헤드리스 CI 환경(ubuntu, sound device 없음) → try/except noop fallback.
    - 볼륨: simpleaudio는 자체 볼륨 API 없음 → 소프트웨어 PCM 스케일링 적용.

자산 규약 (DECISION-AUDIO-006, DECISION-AUDIO-008):
    - SFX:  assets/audio/sfx/{name}.wav   (예: "sfx.arrow_shot" → sfx.arrow_shot.wav)
    - UI:   assets/audio/sfx/{name}.wav   (ui_ 접두사도 sfx/ 디렉터리에 배치)
    - BGM:  assets/audio/bgm/{name}.ogg   (Phase 5, no-op stub)
    - 전체 인벤토리: docs/audio/01_asset_inventory.md

인터페이스:
    play_sfx(name: str) -> None       — SFX 비동기 재생 (다채널)
    play_ui(name: str) -> None        — UI Sound 비동기 재생
    play_bgm(name: str, loop: bool)   — Phase 5 stub
    stop_all() -> None                — 모든 재생 중지
    set_master_volume(v: float)       — 0.0~1.0, PCM 스케일링
    mute() / unmute()                 — 음소거 토글
"""

from __future__ import annotations

import os
import struct
import sys
import wave

from src.core.logger import get_logger

_log = get_logger(__name__)

# ---------------------------------------------------------------------------
# simpleaudio 임포트 — 헤드리스/패키지 미설치 환경 graceful fallback
# ---------------------------------------------------------------------------
try:
    import simpleaudio as _sa  # type: ignore[import]

    _SA_AVAILABLE = True
except (ImportError, OSError):
    _sa = None  # type: ignore[assignment]
    _SA_AVAILABLE = False
    _log.warning("simpleaudio를 불러올 수 없음. SFX가 no-op으로 fallback됩니다.")


def _asset_base() -> str:
    """자산 루트 경로 반환 (dev 모드 vs PyInstaller _MEIPASS).

    DECISION-AUDIO-009: fonts.py resolve_fonts_dir() 패턴 동일 적용.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets", "audio")  # type: ignore[attr-defined]
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "assets", "audio"))


def _scale_pcm(data: bytes, volume: float) -> bytes:
    """16-bit PCM 원시 데이터에 볼륨 스케일링 적용.

    simpleaudio는 볼륨 API가 없으므로 소프트웨어 PCM 스케일링으로 대체.
    volume 범위: 0.0(무음) ~ 1.0(원본).
    """
    if volume >= 1.0:
        return data
    if volume <= 0.0:
        return b"\x00\x00" * (len(data) // 2)

    # little-endian 16-bit signed PCM
    num_samples = len(data) // 2
    samples = struct.unpack(f"<{num_samples}h", data)
    scaled = [int(s * volume) for s in samples]
    # clamp to int16 range
    scaled = [max(-32768, min(32767, s)) for s in scaled]
    return struct.pack(f"<{num_samples}h", *scaled)


class SoundManager:
    """simpleaudio 기반 SFX 사운드 매니저 (Phase 4 후반 시범 도입).

    - SFX/UI Sound: 비동기, 다채널 동시 재생.
    - BGM: Phase 5 #30 위임 — stub.
    - 자산 누락 또는 simpleaudio 없음 → graceful noop fallback.
    - 볼륨: set_master_volume() 로 전역 PCM 스케일링 적용.

    사용 예시::

        sm = SoundManager()
        sm.play_sfx("sfx.arrow_shot")    # SFX 비동기 재생
        sm.play_ui("sfx.ui_click")       # UI Sound 비동기 재생
        sm.set_master_volume(0.7)        # 전체 볼륨 70%
        sm.mute()                        # 음소거
        sm.unmute()                      # 음소거 해제
        sm.stop_all()                    # 전체 중지
        sm.play_bgm("bgm_main_menu")     # Phase 5 stub — no-op
    """

    def __init__(self) -> None:
        self._master_volume: float = 1.0
        self._muted: bool = False
        self._pre_mute_volume: float = 1.0
        # 재생 중인 WaveObject 핸들 목록 (완료된 것 자동 정리)
        self._playing: list[object] = []
        # 자산 캐시: name → (data_bytes, num_channels, bytes_per_sample, sample_rate)
        self._cache: dict[str, tuple[bytes, int, int, int]] = {}

    # ------------------------------------------------------------------
    # 공개 API
    # ------------------------------------------------------------------

    def play_sfx(self, name: str) -> None:
        """SFX를 비동기로 1회 재생한다 (다채널, 자동 채널 관리).

        Args:
            name: 자산 식별자. 예: "sfx.arrow_shot".
                  파일 경로: assets/audio/sfx/{name}.wav
                  전체 식별자: docs/audio/01_asset_inventory.md §2.

        자산 누락 또는 simpleaudio 사용 불가 시 no-op (경고 로그만).
        헤드리스 환경(CI ubuntu) try/except 내장.
        """
        _log.debug("SoundManager.play_sfx(%s)", name)
        self._play_wav(name, category="sfx")

    def play_ui(self, name: str) -> None:
        """UI Sound를 비동기로 1회 재생한다.

        Args:
            name: 자산 식별자. 예: "sfx.ui_click", "sfx.ui_dialog".
                  파일 경로: assets/audio/sfx/{name}.wav

        자산 누락 또는 simpleaudio 사용 불가 시 no-op.
        """
        _log.debug("SoundManager.play_ui(%s)", name)
        self._play_wav(name, category="sfx")

    def play_bgm(self, name: str, loop: bool = True) -> None:
        """BGM을 재생한다. (Phase 5 #30 위임 — 현재 stub)

        Args:
            name: BGM 식별자. 예: "bgm_main_menu".
            loop: True이면 루프. 기본값 True.

        현재 구현: no-op (로그만 출력).
        Phase 5 구현 시: pygame.mixer.music 패턴 예정.
        """
        _log.debug("SoundManager.play_bgm(%s, loop=%s) [Phase 5 stub — no-op]", name, loop)

    def stop_all(self) -> None:
        """모든 재생 중인 SFX를 즉시 중지한다.

        씬 전환, 일시정지, 앱 종료 시 호출.
        BGM stop은 Phase 5에서 추가 예정.
        """
        _log.debug("SoundManager.stop_all()")
        if not _SA_AVAILABLE:
            return
        try:
            _sa.stop_all()
        except Exception as exc:  # noqa: BLE001
            _log.warning("stop_all() 실패: %s", exc)
        self._playing.clear()

    def set_master_volume(self, v: float) -> None:
        """전체 마스터 볼륨을 설정한다.

        Args:
            v: 0.0(음소거) ~ 1.0(최대). 범위 밖 값은 클램프.

        simpleaudio는 자체 볼륨 API가 없으므로 PCM 스케일링으로 구현.
        다음 play_sfx/play_ui 호출부터 적용. 현재 재생 중인 소리에는 영향 없음.

        DECISION-AUDIO-002 (카테고리별 독립 볼륨 채널)은 Phase 5에서 구현 예정.
        """
        v = max(0.0, min(1.0, float(v)))
        self._master_volume = v
        if self._muted and v > 0.0:
            # unmute 상태 전환 없이 볼륨만 갱신 (pre_mute 값도 업데이트)
            self._pre_mute_volume = v
        _log.debug("SoundManager.set_master_volume(%s)", v)

    def mute(self) -> None:
        """모든 사운드를 음소거한다.

        현재 마스터 볼륨을 저장하고 볼륨을 0으로 설정.
        unmute() 호출 시 이전 볼륨으로 복원.
        """
        if not self._muted:
            self._pre_mute_volume = self._master_volume
            self._master_volume = 0.0
            self._muted = True
        _log.debug("SoundManager.mute()")

    def unmute(self) -> None:
        """음소거를 해제하고 이전 볼륨으로 복원한다."""
        if self._muted:
            self._master_volume = self._pre_mute_volume
            self._muted = False
        _log.debug("SoundManager.unmute()")

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _play_wav(self, name: str, category: str = "sfx") -> None:
        """WAV 파일을 로드·스케일링·비동기 재생한다.

        헤드리스 환경 및 파일 누락에 대해 graceful fallback.
        재생 완료된 핸들을 자동 정리해 메모리 누수를 방지한다.
        """
        if not _SA_AVAILABLE:
            return

        try:
            # 완료된 play 객체 정리
            self._playing = [p for p in self._playing if p.is_playing()]  # type: ignore[union-attr]

            wav_data = self._load_wav(name, category)
            if wav_data is None:
                return

            raw, num_channels, bytes_per_sample, sample_rate = wav_data

            # 볼륨 스케일링
            effective_vol = self._master_volume
            if effective_vol <= 0.0:
                return
            scaled_raw = _scale_pcm(raw, effective_vol)

            play_obj = _sa.play_buffer(  # type: ignore[union-attr]
                scaled_raw,
                num_channels=num_channels,
                bytes_per_sample=bytes_per_sample,
                sample_rate=sample_rate,
            )
            self._playing.append(play_obj)

        except Exception as exc:  # noqa: BLE001
            # CI 헤드리스 환경 등에서 AudioUnavailableError 포함 모든 예외 noop
            _log.warning("play_wav(%s) 실패 (no-op fallback): %s", name, exc)

    def _load_wav(self, name: str, category: str) -> tuple[bytes, int, int, int] | None:
        """WAV 파일을 캐시에서 반환하거나 신규 로드한다.

        Returns:
            (raw_bytes, num_channels, bytes_per_sample, sample_rate) 또는
            파일 누락/오류 시 None.
        """
        cache_key = f"{category}/{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        base = _asset_base()
        path = os.path.join(base, category, f"{name}.wav")

        if not os.path.isfile(path):
            _log.warning("SFX 파일 없음 (graceful skip): %s", path)
            return None

        try:
            with wave.open(path, "rb") as wf:
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                raw = wf.readframes(wf.getnframes())
            result = (raw, num_channels, sample_width, sample_rate)
            self._cache[cache_key] = result
            return result
        except Exception as exc:  # noqa: BLE001
            _log.warning("WAV 로드 실패 (%s): %s", path, exc)
            return None
