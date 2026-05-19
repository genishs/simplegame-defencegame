# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Ansiseong Defense.

DECISION-Q-007 / Issue #7: Noto Sans KR (OFL 1.1) 폰트를 .exe 에 번들링.
DECISION-DESIGN-P3-4-001: spec 파일로 ``datas`` 를 SSOT 관리 (워크플로 yaml
의 ``--add-data`` 중복 분기 방지).

빌드:
  pyinstaller --noconfirm AnsiseongDefense.spec

산출물:
  ``dist/AnsiseongDefense.exe`` (단일 파일, --onefile 호환).
  런타임에 ``sys._MEIPASS/assets/fonts/`` 로 폰트가 추출된다.
  ``src/core/fonts.py:resolve_fonts_dir()`` 이 이 경로를 처리.
"""
from __future__ import annotations

from pathlib import Path

block_cipher = None

PROJECT_ROOT = Path(SPECPATH).resolve()  # noqa: F821 - PyInstaller 주입 변수

# ---------------------------------------------------------------------------
# 번들 자원: assets/fonts/ 전체.
# 향후 assets/images, assets/audio 가 생기면 동일 패턴으로 추가.
# ---------------------------------------------------------------------------
datas: list[tuple[str, str]] = []

fonts_dir = PROJECT_ROOT / "assets" / "fonts"
if fonts_dir.is_dir():
    # (source_abs, dest_in_bundle). dest 는 sys._MEIPASS 기준 상대경로.
    datas.append((str(fonts_dir), "assets/fonts"))

a = Analysis(
    [str(PROJECT_ROOT / "src" / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AnsiseongDefense",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX 비활성 — 안티바이러스 오탐 빈도 ↓
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
