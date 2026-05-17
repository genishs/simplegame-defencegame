"""다이얼로그(일시정지/결과).

EXPECTED: team-member-2가 모달 캔버스 오버레이 + 배경 dim + 버튼 2~3개로 구현.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.app import App


class PauseDialog:
    """일시정지 다이얼로그."""

    TAG: str = "dialog_pause"

    def __init__(self, app: "App") -> None:
        self.app = app

    def show(self) -> None:
        # TODO(team-member-2): dim 사각형 + 패널 + ["재개", "메뉴로"] 버튼.
        return

    def hide(self) -> None:
        try:
            self.app.canvas.delete(self.TAG)
        except Exception:  # noqa: BLE001
            pass


class ResultDialog:
    """전투 결과 다이얼로그(승리/패배)."""

    TAG: str = "dialog_result"

    def __init__(self, app: "App") -> None:
        self.app = app

    def show(self, victory: bool, stars: int = 0) -> None:
        # TODO(team-member-2): 별 평가 + 다음 스테이지/재시도 버튼.
        return

    def hide(self) -> None:
        try:
            self.app.canvas.delete(self.TAG)
        except Exception:  # noqa: BLE001
            pass
