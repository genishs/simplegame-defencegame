"""엔티티 추상 베이스 + 풀.

DESIGN: 모든 엔티티는 ``canvas_id``를 보유하고, ``update(dt)``로 시뮬레이션
상태를 갱신하며 ``draw(canvas, scaler)``로 자기 ``canvas_id``의 ``coords``를
이동시킨다(생성/삭제 금지).

EXPECTED: team-member-1이 ObjectPool 본 구현. 현 단계는 시그니처만.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


class Entity:
    """모든 엔티티의 베이스.

    Attributes:
        x, y: 베이스 좌표(float).
        hp: 현재 체력.
        alive: 풀 회수 여부 플래그.
        canvas_id: 캔버스 아이템 id (없으면 None).
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, hp: int = 1) -> None:
        self.x = float(x)
        self.y = float(y)
        self.hp = int(hp)
        self.alive: bool = True
        self.canvas_id: int | None = None

    def update(self, dt: float) -> None:
        """매 틱 시뮬레이션 갱신. 서브클래스 override."""
        raise NotImplementedError

    def draw(self, canvas: "tk.Canvas", scaler: "Scaler") -> None:
        """캔버스 아이템의 좌표만 갱신. 생성/삭제 금지(풀에서 처리)."""
        raise NotImplementedError


class ObjectPool:
    """Canvas item id 재사용 풀 (DECISION-A).

    TODO(team-member-1): 본 구현. 현 단계는 인터페이스만 noted.
    설계 스케치는 ``docs/04`` §2.1 참고.
    """

    def __init__(self, canvas: Any, factory, capacity: int) -> None:  # type: ignore[no-untyped-def]
        self._canvas = canvas
        self._factory = factory
        self._free: list[int] = []
        self._capacity = capacity
        self._created: int = 0

    def acquire(self) -> int:
        """비활성 아이템 id를 반환. 풀이 비면 factory로 새로 생성."""
        # TODO(team-member-1): state="normal"로 활성화 + capacity 가드.
        raise NotImplementedError

    def release(self, iid: int) -> None:
        """아이템을 풀에 반환 (state="hidden")."""
        # TODO(team-member-1): 구현.
        raise NotImplementedError
