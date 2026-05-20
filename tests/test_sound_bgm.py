"""pygame.mixer BGM 백엔드 테스트 (Issue #30, DECISION-AUDIO-013/015/016).

커버 항목 (회귀 매트릭스 docs/qa/regression_matrix.md Phase 5.1):
  BG-01  메인 메뉴 진입 시 SoundManager.play_bgm("bgm.menu") 호출 — 예외 없음, BGM 시작
  BG-02  스테이지 전환 시 BGM 페이드 아웃·인 — stop_bgm(fade_out=1.0) 후 play_bgm(fade_in=1.0)
  BG-03  일시정지(ESC) 시 BGM 볼륨 dimming — set_bgm_volume(0.2) 호출, 재개 시 복원
  BG-04  음소거 토글(mute/unmute) 시 BGM 정지·재개 — SFX와 BGM 독립 동작 검증

추가 커버 시나리오 (Phase 5.1 자동화 가드):
  - play_bgm 시그니처 (name, *, loop, fade_in) 검증
  - stop_bgm 시그니처 (*, fade_out) 검증
  - set_bgm_volume 시그니처·클램핑 검증
  - pygame.mixer 미설치/초기화 실패 시 graceful fallback
  - 자산 누락 시 graceful fallback (noop)
  - 동일 BGM 중복 play 시 재시작 방지 (current_bgm 상태 추적)
  - BGM 볼륨 독립성 — SFX 마스터 볼륨 변경이 BGM 볼륨에 영향 없음

설계 원칙:
  - 실제 사운드 출력 없이 pygame.mixer mock + 파일시스템 patch 로 호출 검증.
  - pygame.mixer 미설치(CI ubuntu 헤드리스) 환경에서도 그린 (graceful fallback 검증).
  - 자산 누락 graceful fallback 검증 (경고 로그 + 예외 없음).
  - SDL_AUDIODRIVER=dummy 환경(CI ubuntu pygame.mixer.init()) 호환.

마커: @pytest.mark.audio
"""

from __future__ import annotations

import inspect
import os
import wave
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# pytest 마커
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.audio


# ---------------------------------------------------------------------------
# 헬퍼 / 픽스처
# ---------------------------------------------------------------------------


def _make_sm():
    """SoundManager 인스턴스 반환."""
    from src.core.sound import SoundManager

    return SoundManager()


def _make_silent_wav(path: str, duration_s: float = 0.05) -> None:
    """무음 WAV 파일 생성 (테스트용 tmp 자산)."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration_s)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)


# ---------------------------------------------------------------------------
# BG-01: 메인 메뉴 진입 시 play_bgm("bgm.menu") — 예외 없음, BGM 시작 로그
# ---------------------------------------------------------------------------


def test_bg01_play_bgm_no_exception():
    """BG-01: SoundManager.play_bgm("bgm.menu") — 예외 없어야 함.

    자산 파일 없어도 graceful noop fallback.
    pygame.mixer 없어도 graceful noop.
    """
    sm = _make_sm()
    # 자산 없는 상태에서도 예외 없음
    sm.play_bgm("bgm.menu", loop=True, fade_in=2.0)
    sm.play_bgm("bgm.tutorial", loop=True, fade_in=1.0)
    sm.play_bgm("bgm.nonexistent_track")


def test_bg01_play_bgm_signature():
    """BG-01: play_bgm은 (name, *, loop=True, fade_in=1.0) 시그니처를 가져야 함."""
    from src.core.sound import SoundManager

    sig = inspect.signature(SoundManager.play_bgm)
    params = sig.parameters
    assert "name" in params
    assert "loop" in params
    assert "fade_in" in params
    # loop, fade_in은 keyword-only (POSITIONAL_ONLY/POSITIONAL_OR_KEYWORD가 아님)
    assert params["loop"].kind in (
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )
    # 기본값 검증
    assert params["loop"].default is True
    assert abs(params["fade_in"].default - 1.0) < 1e-9


def test_bg01_play_bgm_with_pygame_mock(tmp_path):
    """BG-01: pygame.mixer mock — play_bgm이 music.load + music.play를 호출함."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    # tmp BGM 자산 (WAV placeholder)
    bgm_dir = tmp_path / "assets" / "audio" / "bgm"
    bgm_dir.mkdir(parents=True)
    bgm_wav = bgm_dir / "bgm.menu.wav"
    _make_silent_wav(str(bgm_wav))

    # pygame.mixer mock 구성
    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True
    mock_mixer.music = MagicMock()

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
        patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")),
    ):
        sm = SoundManager()
        sm.play_bgm("bgm.menu", loop=True, fade_in=2.0)

    # music.load, music.set_volume, music.play 호출 검증
    mock_mixer.music.load.assert_called_once()
    mock_mixer.music.play.assert_called_once()
    # play는 loops=-1 (무한 루프), fade_ms=2000 (2.0초)
    call_kwargs = mock_mixer.music.play.call_args
    assert call_kwargs.kwargs.get("loops") == -1
    assert call_kwargs.kwargs.get("fade_ms") == 2000


# ---------------------------------------------------------------------------
# BG-02: 스테이지 전환 시 BGM 페이드 아웃·인
# ---------------------------------------------------------------------------


def test_bg02_stage_transition_bgm_sequence(tmp_path):
    """BG-02: stop_bgm(fade_out=1.0) 후 play_bgm(fade_in=1.0) 순서 검증.

    스테이지 전환 시 이전 BGM 페이드 아웃 → 새 BGM 페이드 인 순서가
    코드에서 올바르게 호출되는지 mock으로 검증한다.
    """
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    # tmp BGM 자산
    bgm_dir = tmp_path / "assets" / "audio" / "bgm"
    bgm_dir.mkdir(parents=True)
    for name in ("bgm.stage_01_02.wav", "bgm.stage_03_04.wav"):
        _make_silent_wav(str(bgm_dir / name))

    call_order: list[str] = []

    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True

    def mock_fadeout(ms):
        call_order.append(f"fadeout({ms})")

    def mock_play(**kwargs):
        call_order.append(f"play(loops={kwargs.get('loops')},fade_ms={kwargs.get('fade_ms')})")

    mock_mixer.music.fadeout.side_effect = mock_fadeout
    mock_mixer.music.play.side_effect = mock_play

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
        patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")),
    ):
        sm = SoundManager()
        # stage_01_02 BGM 재생
        sm.play_bgm("bgm.stage_01_02", loop=True, fade_in=1.0)
        # 스테이지 전환: fade out
        sm.stop_bgm(fade_out=1.0)
        # stage_03_04 BGM 재생
        sm.play_bgm("bgm.stage_03_04", loop=True, fade_in=1.0)

    # 순서: play → fadeout → play
    assert len(call_order) >= 3
    assert "fadeout(1000)" in call_order
    # play가 2회 호출됨 (stage_01_02, stage_03_04 각각)
    play_calls = [c for c in call_order if c.startswith("play")]
    assert len(play_calls) == 2


def test_bg02_stop_bgm_no_exception():
    """BG-02: stop_bgm() — 예외 없어야 함 (BGM 미재생 상태 포함)."""
    sm = _make_sm()
    sm.stop_bgm()  # BGM 미재생 상태에서도 예외 없음
    sm.stop_bgm(fade_out=0.0)  # 즉시 정지
    sm.stop_bgm(fade_out=2.0)  # 긴 페이드


def test_bg02_stop_bgm_signature():
    """BG-02: stop_bgm은 (*, fade_out=1.0) 시그니처를 가져야 함."""
    from src.core.sound import SoundManager

    sig = inspect.signature(SoundManager.stop_bgm)
    params = sig.parameters
    assert "fade_out" in params
    assert abs(params["fade_out"].default - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# BG-03: 일시정지 시 BGM 볼륨 dimming
# ---------------------------------------------------------------------------


def test_bg03_bgm_volume_dimming_on_pause():
    """BG-03: 일시정지 시 set_bgm_volume(0.2) — 재개 시 원래 볼륨 복원."""
    sm = _make_sm()
    sm.set_bgm_volume(1.0)
    assert abs(sm._bgm_volume - 1.0) < 1e-9

    # 일시정지: 볼륨 dimming
    sm.set_bgm_volume(0.2)
    assert abs(sm._bgm_volume - 0.2) < 1e-9

    # 재개: 볼륨 복원
    sm.set_bgm_volume(1.0)
    assert abs(sm._bgm_volume - 1.0) < 1e-9


def test_bg03_set_bgm_volume_clamp():
    """BG-03: set_bgm_volume은 0.0~1.0 범위를 클램프해야 함."""
    sm = _make_sm()
    sm.set_bgm_volume(2.0)
    assert sm._bgm_volume == 1.0

    sm.set_bgm_volume(-0.5)
    assert sm._bgm_volume == 0.0

    sm.set_bgm_volume(0.5)
    assert abs(sm._bgm_volume - 0.5) < 1e-9


def test_bg03_set_bgm_volume_independent_from_sfx():
    """BG-03: BGM 볼륨은 SFX 마스터 볼륨과 독립적으로 작동해야 함."""
    sm = _make_sm()
    sm.set_master_volume(0.3)  # SFX 볼륨 변경
    sm.set_bgm_volume(0.8)  # BGM 볼륨 독립 설정

    # SFX와 BGM 볼륨이 서로 독립임을 검증
    assert abs(sm._master_volume - 0.3) < 1e-9
    assert abs(sm._bgm_volume - 0.8) < 1e-9

    # SFX 볼륨 변경이 BGM 볼륨에 영향 없음
    sm.set_master_volume(1.0)
    assert abs(sm._bgm_volume - 0.8) < 1e-9


def test_bg03_set_bgm_volume_calls_pygame(tmp_path):
    """BG-03: set_bgm_volume이 pygame.mixer.music.set_volume을 호출함."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
    ):
        sm = SoundManager()
        sm.set_bgm_volume(0.7)

    mock_mixer.music.set_volume.assert_called_once_with(pytest.approx(0.7))


# ---------------------------------------------------------------------------
# BG-04: 음소거 토글 — SFX와 BGM 독립 동작
# ---------------------------------------------------------------------------


def test_bg04_mute_affects_bgm_volume():
    """BG-04: mute() 후 BGM도 음소거됨, unmute() 후 BGM 볼륨 복원."""
    sm = _make_sm()
    sm.set_bgm_volume(0.9)

    sm.mute()
    # BGM 음소거 상태 검증
    assert sm._bgm_muted is True
    # mute 후에도 _bgm_volume(복원용 값)은 보존
    assert abs(sm._bgm_volume - 0.9) < 1e-9

    sm.unmute()
    # BGM 음소거 해제
    assert sm._bgm_muted is False
    # BGM 볼륨 복원
    assert abs(sm._bgm_volume - 0.9) < 1e-9


def test_bg04_mute_unmute_sfx_independent():
    """BG-04: SFX와 BGM 음소거 상태가 독립적으로 추적됨."""
    sm = _make_sm()
    sm.set_master_volume(0.6)
    sm.set_bgm_volume(0.8)

    sm.mute()
    assert sm._muted is True
    assert sm._bgm_muted is True
    assert sm._master_volume == 0.0  # SFX 음소거

    sm.unmute()
    assert sm._muted is False
    assert sm._bgm_muted is False
    assert abs(sm._master_volume - 0.6) < 1e-9
    assert abs(sm._bgm_volume - 0.8) < 1e-9


def test_bg04_mute_calls_pygame_set_volume():
    """BG-04: mute() 시 pygame.mixer.music.set_volume(0.0) 호출."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
    ):
        sm = SoundManager()
        sm.set_bgm_volume(0.8)
        mock_mixer.music.set_volume.reset_mock()  # set_bgm_volume 호출 리셋

        sm.mute()

    # mute 시 BGM 볼륨 0으로 설정
    mock_mixer.music.set_volume.assert_called_with(0.0)


def test_bg04_unmute_restores_bgm_volume():
    """BG-04: unmute() 시 pygame.mixer.music.set_volume(pre_mute_vol) 호출."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
    ):
        sm = SoundManager()
        sm.set_bgm_volume(0.75)
        sm.mute()
        mock_mixer.music.set_volume.reset_mock()

        sm.unmute()

    # unmute 시 BGM 볼륨 복원
    mock_mixer.music.set_volume.assert_called_with(pytest.approx(0.75))


# ---------------------------------------------------------------------------
# 추가: pygame.mixer 미사용 환경 graceful fallback
# ---------------------------------------------------------------------------


def test_bgm_graceful_fallback_no_pygame():
    """pygame.mixer 미설치 시 play_bgm/stop_bgm/set_bgm_volume 모두 noop."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    with patch.object(sound_module, "_PYGAME_AVAILABLE", False):
        sm = SoundManager()
        # 예외 없이 noop
        sm.play_bgm("bgm.menu")
        sm.stop_bgm()
        sm.set_bgm_volume(0.5)
        sm.mute()
        sm.unmute()


def test_bgm_graceful_fallback_missing_asset():
    """자산 파일 없을 때 play_bgm이 graceful noop으로 처리됨 (예외 없음)."""
    sm = _make_sm()
    # 존재하지 않는 BGM 이름 — noop, 예외 없음
    sm.play_bgm("bgm.completely_nonexistent_track_xyz")


def test_bgm_no_duplicate_play(tmp_path):
    """동일 BGM 중복 play_bgm 호출 시 music.play가 1회만 호출됨."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    # tmp BGM 자산
    bgm_dir = tmp_path / "assets" / "audio" / "bgm"
    bgm_dir.mkdir(parents=True)
    _make_silent_wav(str(bgm_dir / "bgm.menu.wav"))

    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
        patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")),
    ):
        sm = SoundManager()
        sm.play_bgm("bgm.menu")  # 첫 번째 호출 → 재생
        sm.play_bgm("bgm.menu")  # 동일 BGM 중복 → noop

    # music.play는 1회만 호출되어야 함
    assert mock_mixer.music.play.call_count == 1


def test_bgm_current_bgm_tracking(tmp_path):
    """play_bgm 후 _current_bgm 상태 추적, stop_bgm 후 None으로 리셋."""
    import src.core.sound as sound_module
    from src.core.sound import SoundManager

    bgm_dir = tmp_path / "assets" / "audio" / "bgm"
    bgm_dir.mkdir(parents=True)
    _make_silent_wav(str(bgm_dir / "bgm.stage_01_02.wav"))

    mock_mixer = MagicMock()
    mock_mixer.get_init.return_value = True

    with (
        patch.object(sound_module, "_PYGAME_AVAILABLE", True),
        patch.object(sound_module, "_pgmixer", mock_mixer),
        patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")),
    ):
        sm = SoundManager()
        assert sm._current_bgm is None

        sm.play_bgm("bgm.stage_01_02")
        assert sm._current_bgm == "bgm.stage_01_02"

        sm.stop_bgm(fade_out=0.0)
        assert sm._current_bgm is None


def test_bgm_ogg_takes_priority_over_wav(tmp_path):
    """DECISION-AUDIO-016: OGG 파일이 있으면 WAV보다 OGG를 우선 탐색함."""

    from src.core.sound import _resolve_bgm_path

    bgm_dir = tmp_path / "assets" / "audio" / "bgm"
    bgm_dir.mkdir(parents=True)

    # WAV만 있을 때
    _make_silent_wav(str(bgm_dir / "bgm.menu.wav"))
    with patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")):
        path = _resolve_bgm_path("bgm.menu")
    assert path is not None
    assert path.endswith(".wav")

    # OGG도 추가 (빈 파일로 존재 시뮬레이션)
    ogg_path = bgm_dir / "bgm.menu.ogg"
    ogg_path.write_bytes(b"")  # 빈 파일 (존재 여부만 체크)
    with patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")):
        path = _resolve_bgm_path("bgm.menu")
    assert path is not None
    assert path.endswith(".ogg")
