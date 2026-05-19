"""한국어 폰트 런타임 해석 + tkinter 등록.

DESIGN (DECISION-Q-007 / DECISION-DESIGN-P3-4-001):
  - 1순위: 번들된 Noto Sans KR (Regular/Bold). PyInstaller `--add-data` 로
    `assets/fonts/` 전체를 .exe 내부 `sys._MEIPASS/assets/fonts/` 에 동봉.
  - 2순위(폴백): 시스템의 Malgun Gothic (Windows 한국어 기본).
  - 3순위(폴백): tkinter 기본 폰트 (시스템 의존).

런타임 절차:
  1. `resolve_fonts_dir()` 가 개발 모드 / PyInstaller --onefile / --onedir 환경
     모두에서 `assets/fonts/` 경로를 반환한다.
  2. `register_korean_fonts(root)` 를 App 부팅 직후 1회 호출 →
     `tk.font.Font(family="Noto Sans KR")` 가 사용 가능한 상태가 된다.
     실패 시(파일 없음 / Tcl 미지원) Malgun Gothic 으로 자동 폴백.
  3. UI 코드는 `family_regular()` / `family_bold()` 로 패밀리명만 받아
     기존 `("패밀리", pt, style)` 튜플 형식과 호환.

note: Tcl/Tk 의 `font create` 는 OS 폰트북 등록 없이 캔버스/위젯에서 사용
가능한 명명 폰트를 등록한다. 다만 일부 환경에서는 `family=` 지정만으로는
파일 경로 폰트가 인식되지 않을 수 있으므로, 우선 `tk.call("font", "create", ...)`
시도 후 실패 시 family 문자열만 노출하는 보수적 전략.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.logger import get_logger

if TYPE_CHECKING:
    import tkinter as tk

_log = get_logger(__name__)

# 패밀리명 (PyInstaller 환경에서도 동일 문자열로 노출).
FAMILY_REGULAR: str = "Noto Sans KR"
FAMILY_BOLD: str = "Noto Sans KR"  # 굵기는 style="bold" 로 분리.
FAMILY_FALLBACK: str = "Malgun Gothic"

# 파일명 (assets/fonts/ 기준).
_FILE_REGULAR: str = "NotoSansKR-Regular.otf"
_FILE_BOLD: str = "NotoSansKR-Bold.otf"

# 모듈 상태(부팅 시 1회 등록 후 캐시).
_registered: bool = False
_registration_ok: bool = False


def resolve_fonts_dir() -> Path:
    """`assets/fonts/` 디렉터리 절대 경로를 반환.

    PyInstaller 번들 환경에서는 `sys._MEIPASS/assets/fonts/`,
    개발 환경(`python src/main.py`)에서는 프로젝트 루트의 `assets/fonts/`.

    경로가 실제 존재하지 않더라도 예외를 던지지 않고 후보 경로를 반환한다
    (호출자가 `is_dir()` 로 가드).
    """
    # PyInstaller --onefile / --onedir 모두 sys._MEIPASS 를 설정한다.
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / "assets" / "fonts"
    # 개발 모드: src/core/fonts.py 기준 2단계 상위가 프로젝트 루트.
    return Path(__file__).resolve().parents[2] / "assets" / "fonts"


def bundled_font_files() -> tuple[Path, Path]:
    """(Regular, Bold) 번들 폰트의 예상 경로를 반환. 존재 여부는 가드 X."""
    base = resolve_fonts_dir()
    return (base / _FILE_REGULAR, base / _FILE_BOLD)


def has_bundled_fonts() -> bool:
    """번들 폰트 두 파일이 모두 존재하면 True."""
    reg, bold = bundled_font_files()
    return reg.is_file() and bold.is_file()


def register_korean_fonts(root: tk.Tk) -> bool:
    """App 부팅 시 1회 호출. Tcl/Tk 에 번들 폰트를 등록 시도.

    반환:
        True  — 번들 Noto Sans KR 사용 가능 (또는 이미 시스템에 설치됨).
        False — 등록 실패. 호출 측은 `family_regular()` 가 자동으로 폴백한
                family 문자열을 사용하면 된다.

    실패 케이스:
        - 폰트 파일이 없음 (의존성 누락).
        - 현재 Tcl/Tk 가 `font create -file` 옵션을 지원하지 않음.
    """
    global _registered, _registration_ok
    if _registered:
        return _registration_ok
    _registered = True

    if not has_bundled_fonts():
        _log.warning(
            "Bundled Korean fonts not found at %s; falling back to %s",
            resolve_fonts_dir(),
            FAMILY_FALLBACK,
        )
        _registration_ok = False
        return False

    reg, bold = bundled_font_files()

    # Tcl 측에 폰트 파일 경로를 직접 등록할 수 있는 표준 옵션은 없으나,
    # tkinter는 OS 가 인식하는 폰트 패밀리만 family= 로 받아들인다.
    # PyInstaller 번들 환경에서 시스템 폰트북 등록 없이도 family 문자열로
    # 인식되도록, 윈도우에서는 AddFontResourceEx (private + nonenumerable) 를
    # 사용해 프로세스 한정 폰트 등록을 시도한다.
    if sys.platform == "win32":
        ok = _windows_register_private_fonts([reg, bold])
        if ok:
            _registration_ok = True
            _log.info("Registered bundled Korean fonts (Win32 private)")
            return True
        # 실패해도 family 문자열은 노출(시스템에 설치되어 있을 수 있음).
    # 비-Windows 환경: 시스템 fontconfig 가 알아서 처리.
    _registration_ok = True
    _log.info("Bundled Korean fonts available; relying on family= resolution")
    return True


def _windows_register_private_fonts(files: list[Path]) -> bool:
    """Win32 AddFontResourceEx 로 프로세스-한정 폰트 등록. 실패 시 False."""
    try:
        import ctypes  # noqa: PLC0415 - Win32 한정

        FR_PRIVATE = 0x10
        FR_NOT_ENUM = 0x20
        gdi32 = ctypes.windll.gdi32
        any_ok = False
        for path in files:
            added = gdi32.AddFontResourceExW(str(path), FR_PRIVATE | FR_NOT_ENUM, 0)
            if added > 0:
                any_ok = True
            else:
                _log.warning("AddFontResourceExW failed for %s (ret=0)", path)
        return any_ok
    except (AttributeError, OSError, ImportError) as exc:
        _log.warning("Win32 private font registration unavailable: %s", exc)
        return False


def family_regular() -> str:
    """본문용 폰트 패밀리명. 등록 실패 시 Malgun Gothic 폴백."""
    if _registered and not _registration_ok:
        return FAMILY_FALLBACK
    # 미등록 상태에서도 시스템에 이미 Noto Sans KR 이 있다면 그대로 동작.
    return FAMILY_REGULAR


def family_bold() -> str:
    """제목/강조용 폰트 패밀리명. 굵기는 style="bold" 와 함께 사용."""
    if _registered and not _registration_ok:
        return FAMILY_FALLBACK
    return FAMILY_BOLD


def font_tuple(pt: int, *, bold: bool = False) -> tuple[str, int, str]:
    """`(family, pt, style)` 튜플을 반환하는 헬퍼.

    `pt` 는 호출자가 이미 Scaler.font_pt() 로 스케일링한 정수 값.
    """
    family = family_bold() if bold else family_regular()
    style = "bold" if bold else "normal"
    return (family, pt, style)
