"""Prerelease tag classifier for GitHub Actions release workflow.

Background
----------
릴리즈 워크플로 (`.github/workflows/release-windows.yml`) 는 태그 푸시 시
``softprops/action-gh-release`` 의 ``prerelease`` 입력값을 결정해야 한다.
Phase 2 에서는 단순히 "태그가 있으면 GA(정식)" 로 분기했기 때문에
``v0.2.0`` 이 자동으로 GA Release 로 마킹되어 SCM PATCH 라운드가 발생했다.

본 스크립트는 SemVer 2.0.0 §9 (pre-release identifier) 규칙을 따른다:

- ``vX.Y.Z`` 또는 ``X.Y.Z``                 → GA  (prerelease=false)
- ``vX.Y.Z-<pre>``  (예: ``v1.0.0-rc.1``)   → prerelease=true
- 그 외 (비표준 태그, 임시 prd-build 태그) → prerelease=true (안전 측 분기)

사용법
------
직접 실행::

    python scripts/check_prerelease_tag.py v0.3.0-rc.1
    # stdout: ``true``
    # exit code: 0

GitHub Actions 에서 사용 (PowerShell)::

    $val = python scripts/check_prerelease_tag.py "$env:GITHUB_REF_NAME"
    "is_prerelease=$val" | Out-File -FilePath $env:GITHUB_OUTPUT -Append

라이브러리로 사용::

    from scripts.check_prerelease_tag import is_prerelease_tag
    assert is_prerelease_tag("v1.2.3-rc.1") is True
    assert is_prerelease_tag("v1.2.3") is False

설계 결정 (DECISION-SCM-P3-001)
-------------------------------
SemVer 2.0.0 spec 의 일반 pre-release 식별자 매칭을 채택한다.
특정 키워드 화이트리스트 (alpha/beta/rc) 가 아닌 "하이픈 + 식별자" 패턴
전체를 prerelease 로 본다. 이렇게 하면 향후 ``-snapshot``, ``-dev``,
``-preview``, ``-nightly`` 등 어떤 식별자가 도입되어도 워크플로 수정 없이
정상 동작한다.
"""

from __future__ import annotations

import re
import sys

# SemVer 2.0.0 §2: vMAJOR.MINOR.PATCH
# SemVer 2.0.0 §9: pre-release identifier = "-<dot-separated identifiers>"
#   identifier  = alphanumeric + hyphen, 빈 segment 불가, 숫자만일 경우 leading-zero 불가(여기서는 검증 생략)
_GA_RE = re.compile(r"^v?\d+\.\d+\.\d+$")
_PRERELEASE_RE = re.compile(r"^v?\d+\.\d+\.\d+-([0-9A-Za-z-]+)(\.[0-9A-Za-z-]+)*(\+[0-9A-Za-z.-]+)?$")


def is_prerelease_tag(tag: str) -> bool:
    """Return True if ``tag`` should be marked as a GitHub prerelease.

    Rules:
        - ``vX.Y.Z`` / ``X.Y.Z``         → False (GA)
        - ``vX.Y.Z-<pre>`` (SemVer)      → True  (prerelease)
        - 비-SemVer 태그 (예: ``foo``)    → True  (안전 측: GA 자동 승격 방지)
    """
    if not tag:
        # 태그가 비었으면 prerelease 로 간주 (수동 build 등)
        return True
    if _GA_RE.match(tag):
        return False
    if _PRERELEASE_RE.match(tag):
        return True
    # SemVer 패턴에 맞지 않는 임시/비표준 태그 (예: v0.0.0-prd-123) → prerelease
    return True


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_prerelease_tag.py <tag>", file=sys.stderr)
        return 2
    tag = argv[1].strip()
    print("true" if is_prerelease_tag(tag) else "false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
