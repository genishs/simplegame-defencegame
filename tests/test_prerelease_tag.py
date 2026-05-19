"""Unit tests for ``scripts/check_prerelease_tag.is_prerelease_tag``.

릴리즈 워크플로 prerelease 자동 판단 (Issue #9 / DECISION-SCM-P3-001)
의 회귀 가드.

테스트 정책:
- GA 케이스: ``vX.Y.Z`` 및 ``X.Y.Z`` 모두 False
- prerelease 케이스: SemVer pre-release 식별자(``-...``) 가 붙은 경우 True
- 비표준 태그 (예: 임시 prd-build): 안전 측 prerelease=True
- 빈 입력: prerelease=True (실수 방지)
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

# scripts/ 디렉터리는 Python 패키지가 아니므로 importlib 로 직접 로드.
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_SCRIPT = _REPO_ROOT / "scripts" / "check_prerelease_tag.py"
_spec = importlib.util.spec_from_file_location("check_prerelease_tag", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

is_prerelease_tag = _mod.is_prerelease_tag


@pytest.mark.parametrize(
    "tag",
    [
        "v0.3.0",
        "v1.2.3",
        "v10.20.30",
        "0.3.0",  # SemVer 는 'v' prefix 가 선택적이라고 본다
        "v0.2.0",  # Phase 2 실 사례 (정식 GA)
    ],
)
def test_ga_tags(tag: str) -> None:
    """일반 ``vX.Y.Z`` 태그는 GA — prerelease=False."""
    assert is_prerelease_tag(tag) is False


@pytest.mark.parametrize(
    "tag",
    [
        "v0.3.0-rc.1",
        "v0.3.0-rc1",
        "v0.3.0-alpha",
        "v0.3.0-alpha.1",
        "v0.3.0-beta.2",
        "v1.0.0-pre",
        "v1.0.0-preview.3",
        "v1.0.0-dev",
        "v1.0.0-snapshot",
        "v1.0.0-nightly.20260519",
        "v0.3.0-rc.1+build.42",  # build metadata 포함도 prerelease
    ],
)
def test_prerelease_semver_tags(tag: str) -> None:
    """SemVer pre-release identifier 가 붙으면 prerelease=True."""
    assert is_prerelease_tag(tag) is True


@pytest.mark.parametrize(
    "tag",
    [
        "v0.0.0-prd-123",  # 워크플로 branch-push 시 생성되는 임시 태그
        "foo",
        "release-2026",
        "vNext",
    ],
)
def test_non_semver_tags_are_prerelease(tag: str) -> None:
    """SemVer 패턴에 맞지 않는 임시/비표준 태그는 안전 측 prerelease=True."""
    assert is_prerelease_tag(tag) is True


def test_empty_input_is_prerelease() -> None:
    """빈 태그는 prerelease 로 간주 (자동 GA 승격 방지)."""
    assert is_prerelease_tag("") is True


def test_v020_regression_is_ga() -> None:
    """회귀 가드: ``v0.2.0`` (Phase 2 사고 태그) 는 GA 로 분류된다.

    이 테스트는 정규식 변경 시 Phase 2 의 실 시나리오가 깨지지 않는지 확인한다.
    """
    assert is_prerelease_tag("v0.2.0") is False


def test_v030_rc1_is_prerelease() -> None:
    """회귀 가드: ``v0.3.0-rc.1`` (Phase 3.5 예정 태그) 는 prerelease 로 분류된다."""
    assert is_prerelease_tag("v0.3.0-rc.1") is True
