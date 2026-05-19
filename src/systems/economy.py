"""자원(곡식·인구·화살) 회계 (tk 비의존).

DESIGN: GDD DECISION-02. 자원은 정수. 음수 방지는 ``can_spend`` + ``spend``
2단 인터페이스로 강제. 단위 테스트 가능하도록 모든 함수는 순수.
EXPECTED: lead 골격 + 기본 산수 / team-member-2가 곡식 생산소, 인구 캡 추가.
"""

from __future__ import annotations


def can_afford(balance: int, cost: int) -> bool:
    """``balance``로 ``cost``를 지불 가능한가."""
    return balance >= cost >= 0


def spend(balance: int, cost: int) -> int:
    """지불. 잔액 부족 시 ``ValueError``."""
    if cost < 0:
        raise ValueError(f"cost must be >= 0, got {cost}")
    if balance < cost:
        raise ValueError(f"insufficient balance: {balance} < {cost}")
    return balance - cost


def grant(balance: int, amount: int) -> int:
    """획득. 음수 amount는 ``ValueError``."""
    if amount < 0:
        raise ValueError(f"amount must be >= 0, got {amount}")
    return balance + amount


class EconomySystem:
    """``world`` 딕셔너리의 자원을 dt 기반으로 갱신.

    GDD: 곡식 자동 생성(스테이지 1은 +1/s 등). 현 시점은 stub.
    """

    GOLD_PER_SECOND: float = 1.0  # GDD: 스테이지 1 기본값.

    def __init__(self, world: dict) -> None:  # type: ignore[type-arg]
        self.world = world
        self._acc: float = 0.0

    def update(self, dt: float) -> None:
        """초당 골드 누적. ``world['gold']``는 정수 유지."""
        self._acc += self.GOLD_PER_SECOND * dt
        if self._acc >= 1.0:
            inc = int(self._acc)
            self.world["gold"] = int(self.world.get("gold", 0)) + inc
            self._acc -= inc
            bus = self.world.get("events")
            if bus is not None:
                bus.publish("gold.changed", {"gold": self.world["gold"]})
