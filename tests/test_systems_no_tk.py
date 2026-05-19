"""도메인 계층 tkinter import 금지 가드 테스트 (closes #8, DECISION-4.1).

``src/systems/`` 와 ``src/entities/`` 내 모든 .py 파일에
런타임 tkinter import 가 없음을 AST 수준에서 검증한다.

허용: ``if TYPE_CHECKING:`` 블록 내 import (타입 힌트 전용, 런타임 비실행).
금지: 최상위 또는 함수/메서드 내 직접 ``import tkinter`` / ``from tkinter import ...``.

tk 비의존 단위 테스트.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# 프로젝트 루트: tests/ 의 부모
PROJECT_ROOT = Path(__file__).resolve().parent.parent

GUARDED_DIRS = [
    PROJECT_ROOT / "src" / "systems",
    PROJECT_ROOT / "src" / "entities",
]


# ---------------------------------------------------------------------------
# 내부 헬퍼 — check_systems_no_tk 스크립트와 동일 로직을 인라인으로 보유
# ---------------------------------------------------------------------------


def _is_type_checking_block(node: ast.If) -> bool:
    """``if TYPE_CHECKING:`` 또는 ``if typing.TYPE_CHECKING:`` 블록 판별."""
    test = node.test
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    if isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
        return True
    return False


def _collect_type_checking_linenos(tree: ast.AST) -> set[int]:
    """TYPE_CHECKING 블록 내의 모든 라인 번호를 수집."""
    linenos: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_type_checking_block(node):
            for child in ast.walk(node):
                ln: int = getattr(child, "lineno", 0)
                if ln:
                    linenos.add(ln)
    return linenos


def _has_runtime_tkinter_import(path: Path) -> list[tuple[int, str]]:
    """파일 내 런타임 tkinter import 목록 (line_no, line) 반환.

    TYPE_CHECKING 가드 내 import는 허용으로 처리해 목록에서 제외.
    """
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    tc_linenos = _collect_type_checking_linenos(tree)
    lines = source.splitlines()
    violations: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        is_violation = False
        if isinstance(node, ast.Import):
            is_violation = any(
                alias.name == "tkinter" or alias.name.startswith("tkinter.") for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            is_violation = node.module is not None and (
                node.module == "tkinter" or node.module.startswith("tkinter.")
            )
        if is_violation:
            lineno: int = getattr(node, "lineno", 0)
            if lineno in tc_linenos:
                continue  # TYPE_CHECKING 가드 내 — 허용
            src = lines[lineno - 1].strip() if lineno > 0 and lineno <= len(lines) else ""
            violations.append((lineno, src))
    return violations


def _collect_py_files() -> list[Path]:
    """감시 대상 .py 파일 목록."""
    files: list[Path] = []
    for d in GUARDED_DIRS:
        if d.exists():
            files.extend(sorted(d.rglob("*.py")))
    return files


# 감시 대상 파일 목록을 모듈 로드 시 수집
_PY_FILES = _collect_py_files()


@pytest.mark.parametrize(
    "py_file",
    _PY_FILES,
    ids=[str(f.relative_to(PROJECT_ROOT)) for f in _PY_FILES],
)
def test_no_runtime_tkinter_import_in_domain_layer(py_file: Path) -> None:
    """도메인 계층 파일에 런타임 tkinter import 가 없어야 한다 (DECISION-4.1).

    TYPE_CHECKING 가드 내 import(타입 힌트 전용)는 허용.
    """
    violations = _has_runtime_tkinter_import(py_file)
    rel = py_file.relative_to(PROJECT_ROOT)
    assert violations == [], (
        f"런타임 tkinter import detected in domain layer file '{rel}':\n"
        + "\n".join(f"  line {ln}: {src}" for ln, src in violations)
        + "\n도메인 계층(src/systems/, src/entities/)은 런타임 tk-free 를 유지해야 합니다. "
        "TYPE_CHECKING 블록 내 import는 허용됩니다. (DECISION-4.1, closes #8)"
    )


def test_guarded_dirs_exist() -> None:
    """감시 대상 디렉토리가 존재해야 한다."""
    for d in GUARDED_DIRS:
        assert d.exists(), f"감시 대상 디렉토리가 없습니다: {d}"


def test_at_least_one_systems_file_checked() -> None:
    """src/systems/ 아래 최소 1개 파일이 검사됨을 확인한다."""
    systems_dir = PROJECT_ROOT / "src" / "systems"
    systems_files = [f for f in _PY_FILES if systems_dir in f.parents or f.parent == systems_dir]
    assert len(systems_files) >= 1, "src/systems/ 에 .py 파일이 없습니다."


def test_type_checking_import_is_allowed() -> None:
    """TYPE_CHECKING 가드 내 tkinter import 는 위반으로 처리하지 않는다."""
    import tempfile

    sample = """\
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import tkinter as tk
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
        f.write(sample)
        tmp = Path(f.name)
    try:
        violations = _has_runtime_tkinter_import(tmp)
        assert violations == [], f"TYPE_CHECKING 가드 내 import가 잘못 위반으로 처리됨: {violations}"
    finally:
        tmp.unlink(missing_ok=True)


def test_runtime_tkinter_import_is_detected() -> None:
    """런타임 직접 import tkinter 는 위반으로 감지된다."""
    import tempfile

    sample = """\
from __future__ import annotations
import tkinter as tk
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as f:
        f.write(sample)
        tmp = Path(f.name)
    try:
        violations = _has_runtime_tkinter_import(tmp)
        assert len(violations) == 1, f"런타임 tkinter import 가 감지되지 않음: {violations}"
    finally:
        tmp.unlink(missing_ok=True)


def test_check_script_returns_zero_violations() -> None:
    """scripts/check_systems_no_tk.py 를 직접 실행해도 위반이 없다."""
    import importlib
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "check_systems_no_tk",
        PROJECT_ROOT / "scripts" / "check_systems_no_tk.py",
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    violations = mod.run(PROJECT_ROOT, verbose=False)
    assert violations == 0, f"check_systems_no_tk 스크립트가 {violations}건 위반을 감지함."
