"""아군 유닛(궁수/창병/투석병 등).

EXPECTED: team-member-1이 ``UnitDef``로부터 인스턴스화 + 사거리 내 타깃팅 + 쿨다운.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler
    from src.data.loader import UnitDef


class Ally(Entity):
    """배치 가능한 아군 유닛."""

    def __init__(self, x: float, y: float, unit_def: "UnitDef") -> None:
        super().__init__(x, y, hp=unit_def.hp)
        self.unit_def = unit_def
        self.cooldown: float = 0.0
        self.target: Entity | None = None

    def update(self, dt: float) -> None:
        # TODO(team-member-1): 쿨다운 감소, 타깃 검색, 공격 트리거.
        if self.cooldown > 0:
            self.cooldown -= dt

    def draw(self, canvas: "tk.Canvas", scaler: "Scaler") -> None:
        # TODO(team-member-1): coords 동기화 + 사거리 미리보기.
        return
