"""캔버스 기반 위젯 헬퍼(버튼/진행바/라벨).

DESIGN: tkinter 표준 위젯(Button 등)은 Canvas 위에서 어색하므로,
캔버스 rect + text + tag_bind 조합으로 게임 풍 버튼을 만든다.
EXPECTED: team-member-2가 hover/disabled 상태 추가.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk


def make_text_button(
    canvas: "tk.Canvas",
    cx: float,
    cy: float,
    label: str,
    on_click: Callable[[], None],
    *,
    width: int = 240,
    height: int = 44,
    tag: str = "ui_button",
    fill: str = "#3a2a1c",
    outline: str = "#a88a5c",
    text_color: str = "#f0e0c0",
    font: tuple = ("Malgun Gothic", 14, "bold"),
) -> tuple[int, int]:
    """텍스트 버튼을 그리고 ``(rect_id, text_id)``를 반환."""
    rect_id = canvas.create_rectangle(
        cx - width / 2,
        cy - height / 2,
        cx + width / 2,
        cy + height / 2,
        fill=fill,
        outline=outline,
        width=2,
        tags=(tag,),
    )
    text_id = canvas.create_text(
        cx, cy, text=label, fill=text_color, font=font, tags=(tag,)
    )

    def _hit(_event) -> None:  # type: ignore[no-untyped-def]
        on_click()

    canvas.tag_bind(rect_id, "<Button-1>", _hit)
    canvas.tag_bind(text_id, "<Button-1>", _hit)
    return rect_id, text_id


def make_progress_bar(
    canvas: "tk.Canvas",
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    tag: str = "progress",
    bg: str = "#222",
    fg: str = "#cc6633",
) -> tuple[int, int]:
    """진행바(배경+전경). 반환 ``(bg_id, fg_id)``. ``fg`` 폭은 ``coords``로 갱신."""
    bg_id = canvas.create_rectangle(x, y, x + w, y + h, fill=bg, outline="", tags=(tag,))
    fg_id = canvas.create_rectangle(x, y, x + w, y + h, fill=fg, outline="", tags=(tag,))
    return bg_id, fg_id
