"""전투 시스템 (데미지 계산 + 타겟팅, tk 비의존).

DESIGN: ``calc_damage(atk, armor)``는 순수 함수로 단위 테스트 핵심.
GDD: 방어력 1당 1 데미지 감쇄. 최소 1 데미지 보장(0 데미지는 게임성 저해).
EXPECTED: team-member-1이 ``CombatSystem.update``로 사거리 검색 + 발사 트리거.
"""

from __future__ import annotations


def calc_damage(atk: int, armor: int = 0) -> int:
    """기본 데미지 공식.

    Args:
        atk: 공격력(>= 0).
        armor: 방어력(>= 0).

    Returns:
        최종 데미지. 최소 1 보장.
    """
    if atk < 0:
        raise ValueError(f"atk must be >= 0, got {atk}")
    if armor < 0:
        raise ValueError(f"armor must be >= 0, got {armor}")
    return max(1, atk - armor)


def in_range(ax: float, ay: float, bx: float, by: float, radius: float) -> bool:
    """A의 사거리 ``radius`` 안에 B가 있는가."""
    dx = bx - ax
    dy = by - ay
    return (dx * dx + dy * dy) <= (radius * radius)


class CombatSystem:
    """매 틱 ``world['allies']``의 타겟팅과 발사 트리거.

    EXPECTED: team-member-1이 본 구현. 현 단계 stub.
    """

    def __init__(self, world: dict) -> None:  # type: ignore[type-arg]
        self.world = world

    def update(self, dt: float) -> None:
        # TODO(team-member-1): allies x enemies 사거리 검색, 쿨다운 만료 시 projectile 스폰.
        return
