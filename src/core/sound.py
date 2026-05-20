"""사운드 백엔드 — simpleaudio SFX + pygame.mixer BGM (Phase 5.1, Issue #30).

DECISION-AUDIO-012 (2026-05-19, Audio Engineer 자율 명문화):
    - DECISION-AUDIO-003/004에 따라 Phase 4 후반 simpleaudio 시범 도입 실행.
    - SFX / UI Sound: simpleaudio.WaveObject 비동기 재생 (다채널 동시 재생).
    - BGM: Phase 5 #30 위임 — stub only (play_bgm/stop_bgm은 no-op 유지).
    - 자산·파일 누락 → graceful fallback (noop, 경고 로그만).
    - 헤드리스 CI 환경(ubuntu, sound device 없음) → try/except noop fallback.
    - 볼륨: simpleaudio는 자체 볼륨 API 없음 → 소프트웨어 PCM 스케일링 적용.

DECISION-AUDIO-013 (2026-05-19, Audio Engineer 자율 결정):
    - BGM 백엔드로 pygame.mixer 채택.
    - pygame.mixer.init() 만 단독 초기화 — pygame.init() 미호출로 tkinter 이벤트 루프 충돌 회피.
    - OGG Vorbis 네이티브 지원. WAV도 지원(fallback).
    - BGM 독립 볼륨 채널: pygame.mixer.music.set_volume()으로 SFX와 별도 제어.

DECISION-AUDIO-015 (2026-05-21, Audio Engineer 자율 결정):
    - pygame 표준 패키지 채택 (pygame-ce 대신). 안정성·PyPI 배포 우선.
    - pygame.mixer 모듈만 사용 (BGM 스트리밍 전용). SFX는 simpleaudio 유지.

DECISION-AUDIO-016 (2026-05-21, Audio Engineer 자율 결정):
    - BGM placeholder: WAV 파일로 유지 (OGG 강제 전환 없음).
    - pygame.mixer는 WAV/OGG 모두 지원하므로 OGG 강제 X.
    - 실수급 시 OGG로 교체 예정 (Phase 5.2). 현재 placeholder는 .wav.
    - 자산 탐색 순서: {name}.ogg → {name}.wav (OGG 우선, WAV fallback).

자산 규약 (DECISION-AUDIO-006, DECISION-AUDIO-008):
    - SFX:  assets/audio/sfx/{name}.wav   (예: "sfx.arrow_shot" → sfx.arrow_shot.wav)
    - UI:   assets/audio/sfx/{name}.wav   (ui_ 접두사도 sfx/ 디렉터리에 배치)
    - BGM:  assets/audio/bgm/{name}.ogg   (Phase 5, OGG 우선, WAV fallback)
    - 전체 인벤토리: docs/audio/01_asset_inventory.md

인터페이스:
    play_sfx(name: str) -> None                           — SFX 비동기 재생 (다채널)
    play_ui(name: str) -> None                            — UI Sound 비동기 재생
    play_bgm(name, *, loop=True, fade_in=1.0) -> None     — BGM 스트리밍 재생
    stop_bgm(*, fade_out=1.0) -> None                     — BGM 페이드 아웃 정지
    set_bgm_volume(v: float) -> None                      — BGM 독립 볼륨
    stop_all() -> None                                    — 모든 재생 중지
    set_master_volume(v: float)                           — 0.0~1.0, PCM 스케일링
    mute() / unmute()                                     — 음소거 토글 (SFX+BGM 동시)
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

# ---------------------------------------------------------------------------
# pygame.mixer 임포트 — 헤드리스/패키지 미설치 환경 graceful fallback
# DECISION-AUDIO-013: BGM 전용. pygame.init() 미호출로 tkinter 충돌 회피.
# ---------------------------------------------------------------------------
try:
    import pygame.mixer as _pgmixer  # type: ignore[import]

    _PYGAME_AVAILABLE = True
except (ImportError, OSError):
    _pgmixer = None  # type: ignore[assignment]
    _PYGAME_AVAILABLE = False
    _log.warning("pygame.mixer를 불러올 수 없음. BGM이 no-op으로 fallback됩니다.")


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


def _init_mixer() -> bool:
    """pygame.mixer를 초기화한다. 이미 초기화된 경우 스킵.

    pygame.init()은 호출하지 않음 — tkinter 이벤트 루프 충돌 방지.
    (DECISION-AUDIO-013, docs/audio/03_bgm_backend_proposal.md §4)

    Returns:
        True if mixer is available and initialized, False otherwise.
    """
    if not _PYGAME_AVAILABLE:
        return False
    try:
        if not _pgmixer.get_init():  # type: ignore[union-attr]
            _pgmixer.init(frequency=44100, size=-16, channels=2, buffer=2048)  # type: ignore[union-attr]
        return True
    except Exception as exc:  # noqa: BLE001
        _log.warning("pygame.mixer.init() 실패 (헤드리스 환경 예상, no-op fallback): %s", exc)
        return False


def _resolve_bgm_path(name: str) -> str | None:
    """BGM 자산 경로를 탐색한다. OGG 우선, WAV fallback.

    DECISION-AUDIO-016: OGG → WAV 순으로 탐색. 실수급 시 OGG 배치로 자동 전환됨.

    Args:
        name: BGM 식별자. 예: "bgm.menu".

    Returns:
        절대 파일 경로 문자열, 또는 파일 없으면 None.
    """
    base = _asset_base()
    bgm_dir = os.path.join(base, "bgm")
    for ext in ("ogg", "wav"):
        path = os.path.join(bgm_dir, f"{name}.{ext}")
        if os.path.isfile(path):
            return path
    _log.warning("BGM 파일 없음 (graceful skip): %s.[ogg|wav]", os.path.join(bgm_dir, name))
    return None


class SoundManager:
    """simpleaudio(SFX) + pygame.mixer(BGM) 사운드 매니저 (Phase 5.1).

    - SFX/UI Sound: simpleaudio 비동기, 다채널 동시 재생.
    - BGM: pygame.mixer.music 스트리밍, 루프, 페이드 인/아웃.
    - 자산 누락 또는 백엔드 없음 → graceful noop fallback.
    - 마스터 볼륨: set_master_volume() 로 SFX PCM 스케일링.
    - BGM 볼륨: set_bgm_volume() 로 BGM 독립 채널 제어.
    - 음소거: mute()/unmute() — SFX + BGM 동시 처리.

    사용 예시::

        sm = SoundManager()
        sm.play_sfx("sfx.arrow_shot")            # SFX 비동기 재생
        sm.play_ui("sfx.ui_click")               # UI Sound 비동기 재생
        sm.play_bgm("bgm.menu", fade_in=2.0)     # BGM 페이드 인 재생
        sm.set_bgm_volume(0.7)                   # BGM 볼륨 70%
        sm.set_master_volume(0.7)                # SFX 전체 볼륨 70%
        sm.mute()                                # 전체 음소거
        sm.unmute()                              # 음소거 해제
        sm.stop_bgm(fade_out=1.0)               # BGM 페이드 아웃 정지
        sm.stop_all()                            # 전체 중지
    """

    def __init__(self) -> None:
        self._master_volume: float = 1.0
        self._muted: bool = False
        self._pre_mute_volume: float = 1.0
        # BGM 전용 볼륨 (SFX와 독립 — DECISION-AUDIO-002)
        self._bgm_volume: float = 1.0
        self._bgm_muted: bool = False
        self._pre_mute_bgm_volume: float = 1.0
        # 현재 재생 중인 BGM 이름 (중복 재생 방지 및 상태 추적용)
        self._current_bgm: str | None = None
        # 재생 중인 WaveObject 핸들 목록 (완료된 것 자동 정리)
        self._playing: list[object] = []
        # 자산 캐시: name → (data_bytes, num_channels, bytes_per_sample, sample_rate)
        self._cache: dict[str, tuple[bytes, int, int, int]] = {}

    # ------------------------------------------------------------------
    # 공개 API — SFX
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

    # ------------------------------------------------------------------
    # 공개 API — BGM (pygame.mixer.music)
    # ------------------------------------------------------------------

    def play_bgm(self, name: str, *, loop: bool = True, fade_in: float = 1.0) -> None:
        """BGM을 스트리밍 재생한다. (Phase 5.1, pygame.mixer.music 백엔드)

        이미 같은 BGM이 재생 중이면 no-op (동일 트랙 재시작 방지).
        다른 BGM 재생 중이면 즉시 stop 후 새 BGM 시작.
        자산 파일 없거나 pygame.mixer 초기화 실패 시 graceful noop.

        Args:
            name: BGM 식별자. 예: ``"bgm.menu"``, ``"bgm.stage_01_02"``.
                  파일 탐색 순서: ``assets/audio/bgm/{name}.ogg`` → ``.wav``
                  (DECISION-AUDIO-016: OGG 우선, WAV fallback).
                  전체 식별자 목록: ``docs/audio/01_asset_inventory.md`` §1.
            loop: True이면 트랙 종료 시 처음부터 반복 재생 (기본값 True).
                  pygame.mixer.music.play(loops=-1) 에 매핑.
            fade_in: 페이드 인 시간(초). 기본값 1.0.
                  pygame.mixer.music.play(fade_ms=int(fade_in*1000)) 으로 구현.
                  0.0이면 즉시 재생.

        참조:
            - DECISION-AUDIO-013: pygame.mixer BGM 백엔드 채택
            - DECISION-AUDIO-016: OGG 우선 WAV fallback 탐색 정책
            - ``docs/audio/03_bgm_backend_proposal.md`` §5.2
        """
        _log.debug("SoundManager.play_bgm(%s, loop=%s, fade_in=%s)", name, loop, fade_in)

        if not _init_mixer():
            return

        # 동일 BGM 중복 재생 방지
        if self._current_bgm == name:
            _log.debug("play_bgm: 동일 BGM 이미 재생 중 (%s), 스킵", name)
            return

        path = _resolve_bgm_path(name)
        if path is None:
            return

        try:
            _pgmixer.music.load(path)  # type: ignore[union-attr]
            loops = -1 if loop else 0
            fade_ms = max(0, int(fade_in * 1000))
            _pgmixer.music.set_volume(  # type: ignore[union-attr]
                self._bgm_volume if not self._bgm_muted else 0.0
            )
            _pgmixer.music.play(loops=loops, fade_ms=fade_ms)  # type: ignore[union-attr]
            self._current_bgm = name
            _log.info("BGM 재생 시작: %s (loop=%s, fade_in=%.1fs)", name, loop, fade_in)
        except Exception as exc:  # noqa: BLE001
            _log.warning("play_bgm(%s) 실패 (no-op fallback): %s", name, exc)

    def stop_bgm(self, *, fade_out: float = 1.0) -> None:
        """BGM을 페이드 아웃 후 정지한다.

        Args:
            fade_out: 페이드 아웃 시간(초). 기본값 1.0.
                      pygame.mixer.music.fadeout(int(fade_out * 1000)) 으로 구현.
                      0.0이면 즉시 정지.

        pygame.mixer 미초기화 또는 BGM 미재생 시 no-op.
        """
        _log.debug("SoundManager.stop_bgm(fade_out=%s)", fade_out)

        if not _PYGAME_AVAILABLE:
            return

        try:
            if not _pgmixer.get_init():  # type: ignore[union-attr]
                return
            if fade_out > 0.0:
                _pgmixer.music.fadeout(int(fade_out * 1000))  # type: ignore[union-attr]
            else:
                _pgmixer.music.stop()  # type: ignore[union-attr]
            self._current_bgm = None
            _log.info("BGM 정지 (fade_out=%.1fs)", fade_out)
        except Exception as exc:  # noqa: BLE001
            _log.warning("stop_bgm() 실패 (no-op fallback): %s", exc)

    def set_bgm_volume(self, v: float) -> None:
        """BGM 전용 볼륨을 설정한다. SFX 마스터 볼륨과 독립.

        Args:
            v: 0.0(음소거) ~ 1.0(최대). 범위 밖 값은 클램프.

        pygame.mixer.music.set_volume()으로 즉시 적용.
        음소거 상태에서는 pre_mute 값만 갱신, 실제 볼륨 변경 안 함.

        참조: DECISION-AUDIO-002 (카테고리별 독립 볼륨 채널)
        """
        v = max(0.0, min(1.0, float(v)))
        self._bgm_volume = v
        if self._bgm_muted:
            self._pre_mute_bgm_volume = v
            return

        if _PYGAME_AVAILABLE:
            try:
                if _pgmixer.get_init():  # type: ignore[union-attr]
                    _pgmixer.music.set_volume(v)  # type: ignore[union-attr]
            except Exception as exc:  # noqa: BLE001
                _log.warning("set_bgm_volume(%s) 실패: %s", v, exc)
        _log.debug("SoundManager.set_bgm_volume(%s)", v)

    # ------------------------------------------------------------------
    # 공개 API — 공통 제어
    # ------------------------------------------------------------------

    def stop_all(self) -> None:
        """모든 재생 중인 SFX·BGM을 즉시 중지한다.

        씬 전환, 일시정지, 앱 종료 시 호출.
        """
        _log.debug("SoundManager.stop_all()")
        # SFX 중지
        if _SA_AVAILABLE:
            try:
                _sa.stop_all()
            except Exception as exc:  # noqa: BLE001
                _log.warning("stop_all() SFX 실패: %s", exc)
            self._playing.clear()
        # BGM 중지 (즉시 — fade_out=0)
        self.stop_bgm(fade_out=0.0)

    def set_master_volume(self, v: float) -> None:
        """전체 마스터 볼륨을 설정한다 (SFX PCM 스케일링).

        Args:
            v: 0.0(음소거) ~ 1.0(최대). 범위 밖 값은 클램프.

        simpleaudio는 자체 볼륨 API가 없으므로 PCM 스케일링으로 구현.
        다음 play_sfx/play_ui 호출부터 적용. 현재 재생 중인 소리에는 영향 없음.

        BGM 볼륨은 set_bgm_volume()으로 별도 제어 (DECISION-AUDIO-002).
        """
        v = max(0.0, min(1.0, float(v)))
        self._master_volume = v
        if self._muted and v > 0.0:
            # unmute 상태 전환 없이 볼륨만 갱신 (pre_mute 값도 업데이트)
            self._pre_mute_volume = v
        _log.debug("SoundManager.set_master_volume(%s)", v)

    def mute(self) -> None:
        """모든 사운드(SFX + BGM)를 음소거한다.

        현재 마스터 볼륨·BGM 볼륨을 저장하고 각각 0으로 설정.
        unmute() 호출 시 이전 볼륨으로 복원.
        """
        if not self._muted:
            self._pre_mute_volume = self._master_volume
            self._master_volume = 0.0
            self._muted = True
        # BGM 음소거
        if not self._bgm_muted:
            self._pre_mute_bgm_volume = self._bgm_volume
            self._bgm_muted = True
            if _PYGAME_AVAILABLE:
                try:
                    if _pgmixer.get_init():  # type: ignore[union-attr]
                        _pgmixer.music.set_volume(0.0)  # type: ignore[union-attr]
                except Exception as exc:  # noqa: BLE001
                    _log.warning("mute() BGM 볼륨 설정 실패: %s", exc)
        _log.debug("SoundManager.mute()")

    def unmute(self) -> None:
        """음소거를 해제하고 이전 볼륨으로 복원한다 (SFX + BGM)."""
        if self._muted:
            self._master_volume = self._pre_mute_volume
            self._muted = False
        # BGM 음소거 해제
        if self._bgm_muted:
            self._bgm_muted = False
            if _PYGAME_AVAILABLE:
                try:
                    if _pgmixer.get_init():  # type: ignore[union-attr]
                        _pgmixer.music.set_volume(self._bgm_volume)  # type: ignore[union-attr]
                except Exception as exc:  # noqa: BLE001
                    _log.warning("unmute() BGM 볼륨 복원 실패: %s", exc)
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
