"""양만춘 영웅 엔티티.

EXPECTED:
- team-member-1이 ult 게이지, 스킬 트리거, 페이즈 보스 메커닉(GDD §2.6) 채움.
- 4페이즈 전환은 hp 임계치 + 발행 이벤트(``hero.phase_changed``).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


class Hero(Entity):
    """양만춘 영웅.

    Attributes:
        ult_gauge: 0.0~1.0, 1.0일 때 발동 가능.
        phase: 0..3 (4페이즈 보스 메커닉).
    """

    def __init__(self, x: float = 960.0, y: float = 540.0, hp: int = 500) -> None:
        super().__init__(x, y, hp)
        self.ult_gauge: float = 0.0
        self.phase: int = 0

    def update(self, dt: float) -> None:
        # TODO(team-member-1): ult 충전, 페이즈 전환 판정, 자동 공격.
        return

    def draw(self, canvas: "tk.Canvas", scaler: "Scaler") -> None:
        # TODO(team-member-1): canvas_id의 coords 갱신 + ult 게이지 표시.
        return

    def cast_ult(self) -> bool:
        """궁극기 발동. 가능하면 True 반환."""
        # TODO(team-member-1): 화살 비, 토산 카운터 등 페이즈별 효과.
        if self.ult_gauge < 1.0:
            return False
        self.ult_gauge = 0.0
        return True
