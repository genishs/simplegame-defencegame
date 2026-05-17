"""입력 라우팅 (마우스/키).

DESIGN: tk 바인딩은 BattleScene이 직접 등록(이미 ``Escape``, ``space``).
이 모듈은 마우스 좌표 변환 + 등록된 콜백 호출의 헬퍼.
EXPECTED: team-member-2가 빌드 UI(클릭으로 유닛 배치) 구현 시 사용.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.scaler import Scaler


class InputRouter:
    """canvas 마우스 좌표를 베이스 좌표로 변환한 뒤 핸들러에 전달."""

    def __init__(self, scaler: "Scaler") -> None:
        self.scaler = scaler
        self._on_click: Callable[[float, float], None] | None = None
        self._on_motion: Callable[[float, float], None] | None = None

    def set_on_click(self, fn: Callable[[float, float], None]) -> None:
        self._on_click = fn

    def set_on_motion(self, fn: Callable[[float, float], None]) -> None:
        self._on_motion = fn

    def handle_click(self, screen_x: float, screen_y: float) -> None:
        bx, by = self.scaler.to_base(screen_x, screen_y)
        if self._on_click is not None:
            self._on_click(bx, by)

    def handle_motion(self, screen_x: float, screen_y: float) -> None:
        bx, by = self.scaler.to_base(screen_x, screen_y)
        if self._on_motion is not None:
            self._on_motion(bx, by)
