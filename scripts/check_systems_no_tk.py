"""AST 기반 tkinter import 감지 스크립트 (DECISION-4.1, closes #8).

도메인 계층 ``src/systems/`` 와 ``src/entities/`` 에 런타임 tkinter import가
없는지 검증한다. TYPE_CHECKING 가드 하의 import(타입 힌트 전용)는 허용.

CI 및 로컬 pytest 에서 호출.

사용:
    python scripts/check_systems_no_tk.py            # exit 0 = 클린
    python scripts/check_systems_no_tk.py --verbose  # 검사 파일 목록 출력

반환 코드:
    0 — 위반 없음
    1 — 위반 1건 이상 발견 (런타임 tkinter import 감지)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# 감시 대상 디렉토리 (프로젝트 루트 기준 상대 경로)
GUARDED_DIRS: list[str] = [
    "src/systems",
    "src/entities",
]


def _is_type_checking_block(node: ast.If) -> bool:
    """``if TYPE_CHECKING:`` 블록인지 판별."""
    test = node.test
    # ``if TYPE_CHECKING:``
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    # ``if typing.TYPE_CHECKING:``
    if isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
        return True
    return False


def _collect_type_checking_linenos(tree: ast.AST) -> set[int]:
    """TYPE_CHECKING 블록 내의 모든 라인 번호를 수집."""
    linenos: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_type_checking_block(node):
            for child in ast.walk(node):
                lineno: int = getattr(child, "lineno", 0)
                if lineno:
                    linenos.add(lineno)
    return linenos


def _is_tkinter_import(node: ast.stmt) -> bool:
    """AST 노드가 tkinter 관련 import 인지 판별."""
    if isinstance(node, ast.Import):
        return any(alias.name == "tkinter" or alias.name.startswith("tkinter.") for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return node.module is not None and (node.module == "tkinter" or node.module.startswith("tkinter."))
    return False


def scan_file(path: Path) -> list[tuple[int, str]]:
    """파일 내 런타임 tkinter import 위반 목록 반환 (line_no, source_line).

    ``TYPE_CHECKING`` 가드 내 import는 위반으로 보지 않는다.
    """
    violations: list[tuple[int, str]] = []
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return violations
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return violations

    # TYPE_CHECKING 블록 내 라인 번호 — 이 라인의 import는 허용
    tc_linenos = _collect_type_checking_linenos(tree)

    lines = source.splitlines()
    for node in ast.walk(tree):
        if _is_tkinter_import(node):
            lineno: int = getattr(node, "lineno", 0)
            if lineno in tc_linenos:
                # TYPE_CHECKING 가드 내 타입힌트 전용 import — 허용
                continue
            src_line = lines[lineno - 1].strip() if lineno > 0 and lineno <= len(lines) else ""
            violations.append((lineno, src_line))
    return violations


def run(project_root: Path, verbose: bool = False) -> int:
    """지정 루트 기준으로 감시 디렉토리를 전체 스캔.

    반환값: 총 위반 파일 수 (0 = 클린).
    """
    total_violations = 0

    for guarded in GUARDED_DIRS:
        target = project_root / guarded
        if not target.exists():
            if verbose:
                print(f"[SKIP] {guarded} (디렉토리 없음)")
            continue

        py_files = sorted(target.rglob("*.py"))
        for py_file in py_files:
            if verbose:
                print(f"[CHECK] {py_file.relative_to(project_root)}")
            violations = scan_file(py_file)
            if violations:
                total_violations += 1
                rel = py_file.relative_to(project_root)
                for lineno, src_line in violations:
                    print(
                        f"ERROR: tkinter import in domain layer — {rel}:{lineno}: {src_line}",
                        file=sys.stderr,
                    )

    if total_violations == 0:
        if verbose:
            print("[OK] 도메인 계층 tk-free 검사 통과.")
    else:
        print(
            f"ERROR: {total_violations} 파일에서 런타임 tkinter import 발견. "
            "도메인 계층(src/systems/, src/entities/)은 런타임 tk-free 를 유지해야 합니다. "
            "(DECISION-4.1, TYPE_CHECKING 가드는 허용)",
            file=sys.stderr,
        )
    return total_violations


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    root = Path(__file__).resolve().parent.parent
    sys.exit(run(root, verbose=verbose))
