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


class PoolExhausted(Exception):
    """ObjectPool의 capacity가 가득 차서 새 객체를 만들 수 없을 때."""


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

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """캔버스 아이템의 좌표만 갱신. 생성/삭제 금지(풀에서 처리)."""
        raise NotImplementedError


class ObjectPool:
    """Entity 객체 재사용 풀 (DECISION-A).

    Canvas item id 기반 재사용 패턴을 Entity 레벨로 추상화한다.
    ``canvas``가 None이면 헤드리스(pytest) 환경으로 간주해 canvas 호출을 건너뛴다.

    Attributes:
        stats: ``created`` / ``reused`` / ``released`` / ``exhausted`` 카운터.
    """

    def __init__(self, canvas: Any, factory: Any, capacity: int) -> None:
        self._canvas = canvas
        self._factory = factory  # () -> Entity
        self._free: list[Any] = []
        self._capacity = capacity
        self._active: list[Any] = []  # 활성 객체 목록 (id() 대신 직접 참조)
        self.stats: dict[str, int] = {
            "created": 0,
            "reused": 0,
            "released": 0,
            "exhausted": 0,
        }

    # ------------------------------------------------------------------
    # 공개 인터페이스
    # ------------------------------------------------------------------

    @property
    def free_count(self) -> int:
        """현재 풀에 대기 중인(비활성) 객체 수."""
        return len(self._free)

    @property
    def active_count(self) -> int:
        """현재 활성 객체 수."""
        return len(self._active)

    def acquire(self, state: str = "normal") -> Any:
        """비활성 객체를 꺼내거나 새로 생성해 반환.

        Args:
            state: Canvas itemconfig 상태 문자열 (기본 ``"normal"``).

        Returns:
            활성화된 Entity 인스턴스.

        Raises:
            PoolExhausted: capacity를 초과하고 재사용 가능한 객체도 없을 때.
        """
        if self._free:
            obj = self._free.pop()
            obj.alive = True
            if self._canvas is not None and obj.canvas_id is not None:
                self._canvas.itemconfig(obj.canvas_id, state=state)
            self._active.append(obj)
            self.stats["reused"] += 1
            return obj

        if len(self._active) >= self._capacity:
            self.stats["exhausted"] += 1
            raise PoolExhausted(
                f"ObjectPool capacity={self._capacity} exhausted; " f"active={len(self._active)}"
            )

        obj = self._factory()
        obj.alive = True
        if self._canvas is not None and obj.canvas_id is not None:
            self._canvas.itemconfig(obj.canvas_id, state=state)
        self._active.append(obj)
        self.stats["created"] += 1
        return obj

    def release(self, obj: Any) -> None:
        """객체를 비활성화하고 풀에 반환.

        Args:
            obj: ``acquire``로 받았던 Entity 인스턴스.
        """
        obj.alive = False
        if self._canvas is not None and obj.canvas_id is not None:
            self._canvas.itemconfig(obj.canvas_id, state="hidden")
        try:
            self._active.remove(obj)
        except ValueError:
            pass
        self._free.append(obj)
        self.stats["released"] += 1
