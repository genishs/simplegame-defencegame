"""stage_01 reward.grain 데이터 패치 검증 (closes #2, DECISION-Q-011).

tk 비의존 단위 테스트.
"""

from __future__ import annotations

from src.data.loader import StageReward, load_stage
from src.systems.economy import grant

# ---------------------------------------------------------------------------
# 1. stage_01.json 로딩 — reward.grain 필드 검증
# ---------------------------------------------------------------------------


def test_stage01_reward_grain_exists() -> None:
    """stage_01 reward 가 grain 필드를 가진다."""
    stage = load_stage("stage_01")
    assert isinstance(stage.reward, StageReward)
    assert hasattr(stage.reward, "grain")


def test_stage01_reward_grain_positive() -> None:
    """stage_01 reward.grain 은 1 이상이다 (DECISION-Q-011)."""
    stage = load_stage("stage_01")
    assert stage.reward.grain >= 1


def test_stage01_reward_grain_value() -> None:
    """stage_01 reward.grain 은 GDD §자원/§경제 근거 50이다."""
    stage = load_stage("stage_01")
    assert stage.reward.grain == 50


def test_stage01_reward_gold_preserved() -> None:
    """기존 gold 필드가 그대로 유지된다."""
    stage = load_stage("stage_01")
    assert stage.reward.gold == 200


def test_stage01_reward_unlock_preserved() -> None:
    """기존 unlock 필드가 그대로 유지된다."""
    stage = load_stage("stage_01")
    assert stage.reward.unlock == "stage_02"


# ---------------------------------------------------------------------------
# 2. StageReward dataclass 기본값 (비파괴)
# ---------------------------------------------------------------------------


def test_stage_reward_defaults() -> None:
    """StageReward 기본값: gold=0, grain=0, unlock=None."""
    r = StageReward()
    assert r.gold == 0
    assert r.grain == 0
    assert r.unlock is None


def test_stage_reward_explicit_values() -> None:
    """명시적 값으로 생성 가능하다."""
    r = StageReward(gold=100, grain=50, unlock="stage_02")
    assert r.gold == 100
    assert r.grain == 50
    assert r.unlock == "stage_02"


def test_stage_reward_frozen() -> None:
    """StageReward 는 frozen dataclass — 속성 변경 불가."""
    import pytest

    r = StageReward(gold=100, grain=50)
    with pytest.raises((AttributeError, TypeError)):
        r.grain = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 3. EconomySystem grain 반영 경로 단위 검증
# ---------------------------------------------------------------------------


def test_economy_grant_grain_from_reward() -> None:
    """stage reward.grain 을 economy.grant 로 처리하면 정확히 반영된다."""
    stage = load_stage("stage_01")
    initial_grain = 0
    result = grant(initial_grain, stage.reward.grain)
    assert result == stage.reward.grain


def test_economy_grant_grain_accumulates() -> None:
    """기존 grain 에 reward.grain 을 더하면 합계가 된다."""
    stage = load_stage("stage_01")
    initial_grain = 30  # GDD starting_resources grain 기본값
    result = grant(initial_grain, stage.reward.grain)
    assert result == initial_grain + stage.reward.grain


def test_economy_grain_is_nonnegative() -> None:
    """reward.grain 은 음수가 아니다."""
    stage = load_stage("stage_01")
    assert stage.reward.grain >= 0
