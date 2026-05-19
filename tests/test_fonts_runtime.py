"""src/core/fonts.py — 런타임 폰트 해석 + 폴백 정책 테스트.

Issue #7 / DECISION-Q-007 회귀 방지:
  - 번들 폰트 경로 해석이 PyInstaller 환경(`sys._MEIPASS`) / 개발 모드 양쪽
    에서 올바르게 분기.
  - 번들 파일이 모두 존재할 때 `family_regular()/family_bold()` 가 'Noto
    Sans KR' 을 반환.
  - 번들이 없거나 등록 실패 상태에서는 Malgun Gothic 으로 폴백.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.core import fonts as fonts_mod


@pytest.fixture(autouse=True)
def _reset_fonts_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """각 테스트 시작 시 모듈 캐시를 초기화 → 등록 결과 격리."""
    monkeypatch.setattr(fonts_mod, "_registered", False, raising=True)
    monkeypatch.setattr(fonts_mod, "_registration_ok", False, raising=True)


# ---------------------------------------------------------------------------
# resolve_fonts_dir
# ---------------------------------------------------------------------------


def test_resolve_fonts_dir_dev_mode_points_to_repo_assets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """개발 모드: sys._MEIPASS 가 없을 때 repo/assets/fonts 를 가리켜야."""
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    p = fonts_mod.resolve_fonts_dir()
    assert p.name == "fonts"
    assert p.parent.name == "assets"


def test_resolve_fonts_dir_meipass_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """PyInstaller 환경: sys._MEIPASS 를 우선 사용."""
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    p = fonts_mod.resolve_fonts_dir()
    assert p == tmp_path / "assets" / "fonts"


# ---------------------------------------------------------------------------
# bundled_font_files / has_bundled_fonts
# ---------------------------------------------------------------------------


def test_bundled_font_files_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    reg, bold = fonts_mod.bundled_font_files()
    assert reg.name == "NotoSansKR-Regular.otf"
    assert bold.name == "NotoSansKR-Bold.otf"
    assert reg.parent == bold.parent == tmp_path / "assets" / "fonts"


def test_has_bundled_fonts_true_when_both_present(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fonts_dir = tmp_path / "assets" / "fonts"
    fonts_dir.mkdir(parents=True)
    (fonts_dir / "NotoSansKR-Regular.otf").write_bytes(b"fake")
    (fonts_dir / "NotoSansKR-Bold.otf").write_bytes(b"fake")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert fonts_mod.has_bundled_fonts() is True


def test_has_bundled_fonts_false_when_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert fonts_mod.has_bundled_fonts() is False


def test_has_bundled_fonts_false_when_only_regular(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fonts_dir = tmp_path / "assets" / "fonts"
    fonts_dir.mkdir(parents=True)
    (fonts_dir / "NotoSansKR-Regular.otf").write_bytes(b"fake")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert fonts_mod.has_bundled_fonts() is False


# ---------------------------------------------------------------------------
# family_regular / family_bold — 등록 전후 분기
# ---------------------------------------------------------------------------


def test_family_returns_noto_when_not_yet_registered() -> None:
    """등록 시도 전(_registered=False)에는 Noto 패밀리명을 노출.

    시스템에 이미 Noto Sans KR 이 설치되어 있을 가능성 + tkinter 자동 폴백을
    신뢰. 등록 실패 확정 시에만 명시 폴백.
    """
    assert fonts_mod.family_regular() == fonts_mod.FAMILY_REGULAR
    assert fonts_mod.family_bold() == fonts_mod.FAMILY_BOLD


def test_family_falls_back_after_failed_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fonts_mod, "_registered", True, raising=True)
    monkeypatch.setattr(fonts_mod, "_registration_ok", False, raising=True)
    assert fonts_mod.family_regular() == fonts_mod.FAMILY_FALLBACK
    assert fonts_mod.family_bold() == fonts_mod.FAMILY_FALLBACK


def test_family_stays_noto_after_successful_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fonts_mod, "_registered", True, raising=True)
    monkeypatch.setattr(fonts_mod, "_registration_ok", True, raising=True)
    assert fonts_mod.family_regular() == fonts_mod.FAMILY_REGULAR
    assert fonts_mod.family_bold() == fonts_mod.FAMILY_BOLD


# ---------------------------------------------------------------------------
# font_tuple — tkinter `font=` 호환 튜플 생성
# ---------------------------------------------------------------------------


def test_font_tuple_regular_returns_normal_style() -> None:
    family, pt, style = fonts_mod.font_tuple(14)
    assert family == fonts_mod.FAMILY_REGULAR
    assert pt == 14
    assert style == "normal"


def test_font_tuple_bold_returns_bold_style() -> None:
    family, pt, style = fonts_mod.font_tuple(20, bold=True)
    assert family == fonts_mod.FAMILY_BOLD
    assert pt == 20
    assert style == "bold"


def test_font_tuple_uses_fallback_on_failed_registration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fonts_mod, "_registered", True, raising=True)
    monkeypatch.setattr(fonts_mod, "_registration_ok", False, raising=True)
    family, _pt, _style = fonts_mod.font_tuple(16)
    assert family == fonts_mod.FAMILY_FALLBACK


# ---------------------------------------------------------------------------
# register_korean_fonts — 미존재 시 우아한 실패
# ---------------------------------------------------------------------------


def test_register_returns_false_when_fonts_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """폰트 파일이 없는 환경에서 register 가 False 반환 + 폴백 모드 진입."""
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    # root 인자는 사용되지 않음(실제 Tk 없이도 동작해야).
    result = fonts_mod.register_korean_fonts(root=None)  # type: ignore[arg-type]
    assert result is False
    # 이후 family 호출은 폴백.
    assert fonts_mod.family_regular() == fonts_mod.FAMILY_FALLBACK


def test_register_is_idempotent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """register 2회 호출 시 두 번째는 캐시된 결과만 반환."""
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    first = fonts_mod.register_korean_fonts(root=None)  # type: ignore[arg-type]
    second = fonts_mod.register_korean_fonts(root=None)  # type: ignore[arg-type]
    assert first == second
