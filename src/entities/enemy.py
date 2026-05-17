"""적 유닛(당군 보병/방패/장수/충차/장수).

EXPECTED:
- team-member-1이 ``EnemyDef`` 인스턴스화 + path 추종(pathing 시스템 사용) + 사망 처리.
- 사망 시 ``enemy.killed`` 이벤트 발행 → economy.gold +=.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler
    from src.data.loader import EnemyDef


class Enemy(Entity):
    """경로를 따라 진군하는 적 유닛."""

    def __init__(self, x: float, y: float, enemy_def: "EnemyDef", path_id: str) -> None:
        super().__init__(x, y, hp=enemy_def.hp)
        self.enemy_def = enemy_def
        self.path_id: str = path_id
        self.waypoint_idx: int = 0
        self.reached_castle: bool = False

    def update(self, dt: float) -> None:
        # TODO(team-member-1): pathing 시스템에서 위치 갱신.
        return

    def draw(self, canvas: "tk.Canvas", scaler: "Scaler") -> None:
        # TODO(team-member-1): coords 동기화 + hp 바.
        return
