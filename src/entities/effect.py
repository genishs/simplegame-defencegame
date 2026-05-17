"""이펙트(폭발, 회색조 페이드 사망). 수 제한 풀로 관리.

EXPECTED: team-member-1이 짧은 수명(0.5~1.0s) 타이머 + 알파/회색조 페이드.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


class Effect(Entity):
    """이펙트(파티클 대체. 단순 스프라이트 페이드)."""

    def __init__(self, x: float, y: float, kind: str, lifetime_s: float = 0.6) -> None:
        super().__init__(x, y, hp=1)
        self.kind = kind
        self.lifetime_s = lifetime_s
        self.elapsed_s: float = 0.0

    def update(self, dt: float) -> None:
        self.elapsed_s += dt
        if self.elapsed_s >= self.lifetime_s:
            self.alive = False

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        # TODO(team-member-1): alpha/fade 적용.
        return
