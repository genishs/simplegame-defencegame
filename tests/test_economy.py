"""Economy 단위 테스트 (tk 비의존)."""
from __future__ import annotations

import pytest

from src.systems.combat import calc_damage, in_range
from src.systems.economy import EconomySystem, can_afford, grant, spend


def test_can_afford_basic() -> None:
    assert can_afford(100, 50) is True
    assert can_afford(50, 100) is False
    assert can_afford(50, 50) is True


def test_can_afford_rejects_negative_cost() -> None:
    assert can_afford(100, -1) is False


def test_spend_deducts() -> None:
    assert spend(100, 30) == 70


def test_spend_insufficient_raises() -> None:
    with pytest.raises(ValueError):
        spend(10, 20)


def test_spend_negative_cost_raises() -> None:
    with pytest.raises(ValueError):
        spend(100, -1)


def test_grant_adds() -> None:
    assert grant(0, 10) == 10
    assert grant(50, 25) == 75


def test_grant_negative_raises() -> None:
    with pytest.raises(ValueError):
        grant(50, -1)


def test_economy_system_accumulates_gold() -> None:
    world: dict = {"gold": 0, "events": None}
    eco = EconomySystem(world)
    # 1초 누적 → +1 골드 (GOLD_PER_SECOND=1.0).
    eco.update(1.0)
    assert world["gold"] == 1
    # 0.5초씩 두 번 → 추가 +1.
    eco.update(0.5)
    eco.update(0.5)
    assert world["gold"] == 2


def test_calc_damage_floor_one() -> None:
    # armor가 더 커도 최소 1.
    assert calc_damage(atk=5, armor=10) == 1


def test_calc_damage_linear() -> None:
    assert calc_damage(atk=50, armor=10) == 40


def test_in_range_basic() -> None:
    assert in_range(0, 0, 3, 4, 5) is True  # 거리 5 == radius 5.
    assert in_range(0, 0, 3, 4, 4.9) is False
