"""이펙트(폭발, 회색조 페이드 사망). 수 제한 풀로 관리.

``lifetime_s`` 경과 후 ``alive=False``로 전환.
``fade_tick``은 ``update``와 동일하므로 어느 쪽을 호출해도 된다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


class Effect(Entity):
    """이펙트(파티클 대체. 단순 스프라이트 페이드).

    Attributes:
        kind: 이펙트 종류 식별자 (예: ``"hit"``, ``"explosion"``).
        lifetime_s: 총 수명(초).
        elapsed_s: 경과 시간(초).
        alpha: 현재 투명도 (1.0 → 0.0 선형 감소).
    """

    def __init__(self, x: float, y: float, kind: str, lifetime_s: float = 0.6) -> None:
        super().__init__(x, y, hp=1)
        self.kind = kind
        self.lifetime_s = lifetime_s
        self.elapsed_s: float = 0.0
        self.alpha: float = 1.0

    # ------------------------------------------------------------------
    # 업데이트
    # ------------------------------------------------------------------

    def fade_tick(self, dt: float) -> None:
        """경과 시간 누적 + 알파 선형 감소. ``lifetime_s`` 도달 시 ``alive=False``.

        Args:
            dt: 경과 시간(초).
        """
        if not self.alive:
            return
        self.elapsed_s += dt
        if self.lifetime_s > 0:
            self.alpha = max(0.0, 1.0 - self.elapsed_s / self.lifetime_s)
        if self.elapsed_s >= self.lifetime_s:
            self.alpha = 0.0
            self.alive = False

    def update(self, dt: float) -> None:
        """``fade_tick``의 별칭. Entity 인터페이스 준수."""
        self.fade_tick(dt)

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """alpha/fade 적용 (렌더러가 호출)."""
        return
