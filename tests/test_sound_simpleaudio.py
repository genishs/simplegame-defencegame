"""simpleaudio SFX 백엔드 시범 도입 테스트 (Issue #29, DECISION-AUDIO-012).

커버 항목 (회귀 매트릭스 docs/qa/regression_matrix.md):
  AU-01  SoundManager.play_bgm 시그니처 유지 + 예외 없음 (Phase 5 stub)
  AU-02  SoundManager.play_sfx 시그니처 유지 + 예외 없음
  AU-03  SoundManager.play_ui 시그니처 유지 + 예외 없음
  AU-04  SoundManager.stop_all 예외 없음
  AU-05  SoundManager.set_master_volume 시그니처·범위 클램핑 검증
  AU-06  SoundManager.mute / unmute 토글 검증
  AU-07  play_sfx 2회 연속 호출 — 둘 다 큐잉 (다채널 동시 재생 검증)
  AU-08  마스터 볼륨 + 뮤트 토글 완전 사이클 검증

설계 원칙:
  - 실제 사운드 출력 없이 mock / 파일시스템 patch 로 호출 검증.
  - simpleaudio 미설치(CI ubuntu 헤드리스) 환경에서도 그린.
  - 자산 누락 graceful fallback 검증 (경고 로그 + 예외 없음).
  - 파일시스템 의존 테스트는 실제 placeholder WAV를 사용.

마커: @pytest.mark.audio
"""

from __future__ import annotations

import os
import struct
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


def _make_silent_wav(path: str, duration_s: float = 0.1) -> None:
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
# AU-01: play_bgm 시그니처 유지 + Phase 5 stub (예외 없음)
# ---------------------------------------------------------------------------


def test_au01_play_bgm_no_exception():
    """AU-01: SoundManager.play_bgm() — Phase 5 stub, 예외 없어야 함."""
    sm = _make_sm()
    sm.play_bgm("bgm_main_menu")
    sm.play_bgm("bgm_stage_01_battle", loop=False)
    sm.play_bgm("bgm_nonexistent")


def test_au01_play_bgm_signature():
    """AU-01: play_bgm은 name(str) + loop(bool=True) 시그니처를 가져야 함."""
    import inspect

    from src.core.sound import SoundManager

    sig = inspect.signature(SoundManager.play_bgm)
    params = list(sig.parameters)
    assert "name" in params
    assert "loop" in params
    default_loop = sig.parameters["loop"].default
    assert default_loop is True


# ---------------------------------------------------------------------------
# AU-02: play_sfx 시그니처 유지 + 예외 없음
# ---------------------------------------------------------------------------


def test_au02_play_sfx_no_exception():
    """AU-02: SoundManager.play_sfx() — 예외 없어야 함 (자산 누락 포함)."""
    sm = _make_sm()
    # 자산 누락 케이스 — graceful fallback
    sm.play_sfx("sfx.nonexistent_sound")
    # 정상 케이스 — 실제 placeholder WAV 존재 여부와 무관하게 예외 없음
    sm.play_sfx("sfx.arrow_shot")
    sm.play_sfx("sfx.enemy_die")


def test_au02_play_sfx_signature():
    """AU-02: play_sfx는 name(str) 단일 파라미터 시그니처를 가져야 함."""
    import inspect

    from src.core.sound import SoundManager

    sig = inspect.signature(SoundManager.play_sfx)
    params = list(sig.parameters)
    assert "name" in params


# ---------------------------------------------------------------------------
# AU-03: play_ui 시그니처 유지 + 예외 없음
# ---------------------------------------------------------------------------


def test_au03_play_ui_no_exception():
    """AU-03: SoundManager.play_ui() — 예외 없어야 함."""
    sm = _make_sm()
    sm.play_ui("sfx.ui_click")
    sm.play_ui("sfx.ui_dialog")
    sm.play_ui("sfx.nonexistent_ui")


def test_au03_play_ui_signature():
    """AU-03: play_ui는 name(str) 단일 파라미터 시그니처를 가져야 함."""
    import inspect

    from src.core.sound import SoundManager

    sig = inspect.signature(SoundManager.play_ui)
    params = list(sig.parameters)
    assert "name" in params


# ---------------------------------------------------------------------------
# AU-04: stop_all 예외 없음
# ---------------------------------------------------------------------------


def test_au04_stop_all_no_exception():
    """AU-04: SoundManager.stop_all() — 예외 없어야 함."""
    sm = _make_sm()
    sm.stop_all()  # 재생 없는 상태에서도 예외 없음

    # play 후 stop_all
    sm.play_sfx("sfx.arrow_shot")
    sm.stop_all()


# ---------------------------------------------------------------------------
# AU-05: set_master_volume 시그니처·범위 클램핑
# ---------------------------------------------------------------------------


def test_au05_set_master_volume_no_exception():
    """AU-05: SoundManager.set_master_volume() — 예외 없어야 함."""
    sm = _make_sm()
    sm.set_master_volume(0.0)
    sm.set_master_volume(0.5)
    sm.set_master_volume(1.0)
    # 범위 밖 값
    sm.set_master_volume(1.5)
    sm.set_master_volume(-0.5)


def test_au05_set_master_volume_clamp():
    """AU-05: set_master_volume은 0.0~1.0 범위를 클램프해야 함."""
    sm = _make_sm()
    sm.set_master_volume(2.0)
    assert sm._master_volume == 1.0

    sm.set_master_volume(-1.0)
    assert sm._master_volume == 0.0

    sm.set_master_volume(0.7)
    assert abs(sm._master_volume - 0.7) < 1e-9


# ---------------------------------------------------------------------------
# AU-06: mute / unmute 토글
# ---------------------------------------------------------------------------


def test_au06_mute_no_exception():
    """AU-06: SoundManager.mute() / unmute() — 예외 없어야 함."""
    sm = _make_sm()
    sm.mute()
    sm.unmute()
    sm.mute()
    sm.mute()  # 중복 mute
    sm.unmute()
    sm.unmute()  # 중복 unmute


def test_au06_mute_sets_volume_zero():
    """AU-06: mute() 후 _master_volume == 0.0, unmute() 후 복원."""
    sm = _make_sm()
    sm.set_master_volume(0.8)
    sm.mute()
    assert sm._master_volume == 0.0
    assert sm._muted is True

    sm.unmute()
    assert abs(sm._master_volume - 0.8) < 1e-9
    assert sm._muted is False


# ---------------------------------------------------------------------------
# AU-07: 다채널 동시 재생 — play_sfx 2회 연속 큐잉
# ---------------------------------------------------------------------------


def test_au07_multichannel_play(tmp_path):
    """AU-07: play_sfx 2회 연속 호출 — 둘 다 큐잉됨 (다채널 동시 재생).

    simpleaudio.play_buffer를 mock하여 실제 사운드 출력 없이
    호출 횟수·인자를 검증한다.
    """
    from src.core.sound import SoundManager

    # tmp 자산 생성
    sfx_dir = tmp_path / "assets" / "audio" / "sfx"
    sfx_dir.mkdir(parents=True)
    wav1 = sfx_dir / "sfx.arrow_shot.wav"
    wav2 = sfx_dir / "sfx.enemy_die.wav"
    _make_silent_wav(str(wav1))
    _make_silent_wav(str(wav2))

    # play_buffer mock 설정
    mock_play_obj = MagicMock()
    mock_play_obj.is_playing.return_value = True

    with (
        patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")),
        patch("src.core.sound._SA_AVAILABLE", True),
        patch("src.core.sound._sa") as mock_sa,
    ):
        mock_sa.play_buffer.return_value = mock_play_obj

        sm = SoundManager()
        sm.play_sfx("sfx.arrow_shot")
        sm.play_sfx("sfx.enemy_die")

        # 두 번 모두 play_buffer 호출됐는지 검증
        assert (
            mock_sa.play_buffer.call_count == 2
        ), f"play_buffer가 {mock_sa.play_buffer.call_count}회 호출됨 (예상: 2회)"
        # 두 play 핸들이 모두 _playing 목록에 있는지
        assert len(sm._playing) == 2


def test_au07_graceful_fallback_missing_asset(tmp_path):
    """AU-07 보조: 자산 누락 시 graceful fallback (예외 없음, 큐잉 없음)."""
    from src.core.sound import SoundManager

    sfx_dir = tmp_path / "assets" / "audio" / "sfx"
    sfx_dir.mkdir(parents=True)
    # 자산을 생성하지 않고 테스트

    with (
        patch("src.core.sound._asset_base", return_value=str(tmp_path / "assets" / "audio")),
        patch("src.core.sound._SA_AVAILABLE", True),
        patch("src.core.sound._sa") as mock_sa,
    ):
        sm = SoundManager()
        sm.play_sfx("sfx.nonexistent")  # 누락 자산

        # play_buffer는 호출되지 않아야 함
        mock_sa.play_buffer.assert_not_called()
        assert len(sm._playing) == 0


# ---------------------------------------------------------------------------
# AU-08: 마스터 볼륨 + 뮤트 완전 사이클 + PCM 스케일링
# ---------------------------------------------------------------------------


def test_au08_volume_mute_cycle():
    """AU-08: 볼륨 설정 → 뮤트 → 언뮤트 전체 사이클 상태 검증."""
    sm = _make_sm()

    # 초기 상태
    assert sm._master_volume == 1.0
    assert sm._muted is False

    # 볼륨 조정
    sm.set_master_volume(0.6)
    assert abs(sm._master_volume - 0.6) < 1e-9

    # 뮤트
    sm.mute()
    assert sm._master_volume == 0.0
    assert sm._muted is True
    assert abs(sm._pre_mute_volume - 0.6) < 1e-9

    # 뮤트 상태에서 play → no-op (volume 0 이므로)
    sm.play_sfx("sfx.arrow_shot")  # 예외 없어야 함

    # 언뮤트
    sm.unmute()
    assert abs(sm._master_volume - 0.6) < 1e-9
    assert sm._muted is False


def test_au08_pcm_scaling():
    """AU-08: _scale_pcm 함수 — 볼륨 스케일링 PCM 계산 검증."""
    from src.core.sound import _scale_pcm

    # 단일 샘플: 32767 (max positive)
    sample = struct.pack("<h", 32767)

    # 볼륨 1.0 → 원본 유지
    result = _scale_pcm(sample, 1.0)
    assert result == sample

    # 볼륨 0.0 → 무음 (0)
    result = _scale_pcm(sample, 0.0)
    val = struct.unpack("<h", result)[0]
    assert val == 0

    # 볼륨 0.5 → 약 16383
    result = _scale_pcm(sample, 0.5)
    val = struct.unpack("<h", result)[0]
    assert abs(val - int(32767 * 0.5)) <= 1  # 반올림 허용 오차


def test_au08_simpleaudio_unavailable_noop():
    """AU-08: simpleaudio 미설치 환경 — play_sfx no-op (예외 없음)."""
    with patch("src.core.sound._SA_AVAILABLE", False):
        from src.core.sound import SoundManager

        sm = SoundManager()
        sm.play_sfx("sfx.arrow_shot")  # 예외 없어야 함
        sm.play_ui("sfx.ui_click")
        sm.stop_all()
        sm.set_master_volume(0.5)
        sm.mute()
        sm.unmute()


# ---------------------------------------------------------------------------
# 자산 placeholder 존재 검증
# ---------------------------------------------------------------------------


def test_placeholder_wav_files_exist():
    """SFX placeholder WAV 8건 모두 존재해야 함 (Issue #29 요구사항)."""
    here = os.path.dirname(os.path.abspath(__file__))
    sfx_dir = os.path.normpath(os.path.join(here, "..", "assets", "audio", "sfx"))

    expected = [
        "sfx.arrow_shot.wav",
        "sfx.hit_light.wav",
        "sfx.hit_heavy.wav",
        "sfx.enemy_die.wav",
        "sfx.hero_skill.wav",
        "sfx.ui_click.wav",
        "sfx.ui_dialog.wav",
        "sfx.wave_start.wav",
    ]

    for fname in expected:
        path = os.path.join(sfx_dir, fname)
        assert os.path.isfile(path), f"placeholder WAV 파일 없음: {path}"


def test_placeholder_wav_valid_format():
    """placeholder WAV가 유효한 WAV 포맷(44100Hz, 모노, 16-bit)인지 검증."""
    here = os.path.dirname(os.path.abspath(__file__))
    sfx_dir = os.path.normpath(os.path.join(here, "..", "assets", "audio", "sfx"))
    wav_path = os.path.join(sfx_dir, "sfx.ui_click.wav")

    if not os.path.isfile(wav_path):
        pytest.skip("placeholder WAV가 아직 생성되지 않음")

    with wave.open(wav_path, "rb") as wf:
        assert wf.getnchannels() == 1, "모노(1ch) 이어야 함"
        assert wf.getsampwidth() == 2, "16-bit(2 bytes) 이어야 함"
        assert wf.getframerate() == 44100, "44100 Hz 이어야 함"
        assert wf.getnframes() > 0, "프레임이 1개 이상 있어야 함"
