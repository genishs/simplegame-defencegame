"""HUD (자원/웨이브/영웅 HP).

EXPECTED: team-member-2가 자원 3종(곡식·인구·화살) + 웨이브 번호 + 영웅 HP 바를
화면 상단에 캔버스 텍스트로 그린다. 이벤트 ``gold.changed``, ``wave.started``
구독.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.app import App


class HUD:
    """전투 화면 상단 HUD."""

    TAG: str = "hud"

    def __init__(self, app: "App") -> None:
        self.app = app
        self._text_ids: dict[str, int] = {}

    def build(self) -> None:
        # TODO(team-member-2): 자원 텍스트 3개, 웨이브 텍스트 1개 등 생성.
        return

    def update(self) -> None:
        """world 상태를 텍스트에 반영."""
        # TODO(team-member-2): canvas.itemconfigure(text_id, text=...).
        return

    def teardown(self) -> None:
        try:
            self.app.canvas.delete(self.TAG)
        except Exception:  # noqa: BLE001
            pass
