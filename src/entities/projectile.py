"""발사체(화살/돌).

EXPECTED: team-member-1이 직선/포물선 궤적 + 명중 판정 + 풀 회수.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


class Projectile(Entity):
    """발사체."""

    def __init__(
        self,
        x: float,
        y: float,
        target_x: float,
        target_y: float,
        damage: int,
        speed: float,
    ) -> None:
        super().__init__(x, y, hp=1)
        self.target_x = target_x
        self.target_y = target_y
        self.damage = damage
        self.speed = speed

    def update(self, dt: float) -> None:
        # TODO(team-member-1): 직선 이동, 타깃 도달 판정, 데미지 적용.
        return

    def draw(self, canvas: "tk.Canvas", scaler: "Scaler") -> None:
        # TODO(team-member-1): coords 갱신.
        return
