"""캔버스 기반 재사용 위젯 (Button / Panel / Label).

DESIGN-D-007: 모든 클릭 가능 컴포넌트 hit-target ≥ 44×44 px (베이스 좌표 기준).
DESIGN-D-006: 폰트는 Malgun Gothic 1순위, 폴백 순서로 시스템 기본 사용.
모든 위젯은 scaler를 받아 1920×1080 베이스 좌표를 실제 캔버스 좌표로 변환한다.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


# ---------------------------------------------------------------------------
# 색상 상수 (팔레트 DECISION-D-005 기준)
# ---------------------------------------------------------------------------
_CLR_BTN_NORMAL = "#3a2a1c"
_CLR_BTN_HOVER = "#5a4a2c"
_CLR_BTN_PRESS = "#2a1a0c"
_CLR_BTN_OUTLINE_NORMAL = "#a88a5c"
_CLR_BTN_OUTLINE_HOVER = "#d4a84a"  # D-007 황금 테두리
_CLR_BTN_DISABLED = "#2a2a2a"
_CLR_BTN_OUTLINE_DISABLED = "#555555"
_CLR_TEXT_NORMAL = "#f0e0c0"
_CLR_TEXT_DISABLED = "#888888"
_CLR_PANEL_DEFAULT = "#1e1610"
_CLR_PANEL_OUTLINE = "#7a5c3a"


def _font(base_pt: int, bold: bool = False, scaler: Scaler | None = None) -> tuple[str, int, str]:
    pt = base_pt
    if scaler is not None:
        pt = scaler.font_pt(base_pt)
    style = "bold" if bold else "normal"
    return ("Malgun Gothic", pt, style)


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------


class Button:
    """Canvas 기반 버튼 위젯.

    Args:
        canvas: 대상 tkinter Canvas.
        x, y: 베이스 좌표 기준 좌상단.
        w, h: 베이스 좌표 기준 크기. h는 최소 44 강제.
        text: 버튼 레이블.
        on_click: 클릭 콜백.
        scaler: 좌표 변환용 Scaler (None이면 변환 없음).
        font_pt: 베이스 폰트 pt.
        disabled: True이면 클릭 불가, 회색 표시.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        on_click: Callable[[], None],
        *,
        scaler: Scaler | None = None,
        font_pt: int = 20,
        disabled: bool = False,
        tag: str = "ui_button",
    ) -> None:
        self._canvas = canvas
        self._on_click = on_click
        self._disabled = disabled
        self._tag = tag
        self._ids: list[int] = []

        # hit-target 최소 44×44 보장 (DECISION-D-007)
        h = max(h, 44.0)
        w = max(w, 44.0)

        # 좌표 변환
        if scaler is not None:
            sx1, sy1 = scaler.to_screen(x, y)
            sx2, sy2 = scaler.to_screen(x + w, y + h)
            cx = (sx1 + sx2) / 2
            cy = (sy1 + sy2) / 2
            font = _font(font_pt, bold=True, scaler=scaler)
        else:
            sx1, sy1 = x, y
            sx2, sy2 = x + w, y + h
            cx = x + w / 2
            cy = y + h / 2
            font = _font(font_pt, bold=True)

        fill = _CLR_BTN_DISABLED if disabled else _CLR_BTN_NORMAL
        outline = _CLR_BTN_OUTLINE_DISABLED if disabled else _CLR_BTN_OUTLINE_NORMAL
        text_clr = _CLR_TEXT_DISABLED if disabled else _CLR_TEXT_NORMAL

        self._rect_id = canvas.create_rectangle(
            sx1,
            sy1,
            sx2,
            sy2,
            fill=fill,
            outline=outline,
            width=2,
            tags=(tag,),
        )
        self._text_id = canvas.create_text(
            cx,
            cy,
            text=text,
            fill=text_clr,
            font=font,
            tags=(tag,),
        )
        self._ids = [self._rect_id, self._text_id]

        if not disabled:
            self._bind_events()

    # ------------------------------------------------------------------
    # 이벤트 바인딩
    # ------------------------------------------------------------------

    def _bind_events(self) -> None:
        for item_id in self._ids:
            self._canvas.tag_bind(item_id, "<Enter>", self._on_hover_enter)
            self._canvas.tag_bind(item_id, "<Leave>", self._on_hover_leave)
            self._canvas.tag_bind(item_id, "<ButtonPress-1>", self._on_press)
            self._canvas.tag_bind(item_id, "<ButtonRelease-1>", self._on_release)

    def _on_hover_enter(self, _event: Any) -> None:
        self._canvas.itemconfig(self._rect_id, fill=_CLR_BTN_HOVER, outline=_CLR_BTN_OUTLINE_HOVER)

    def _on_hover_leave(self, _event: Any) -> None:
        self._canvas.itemconfig(self._rect_id, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE_NORMAL)

    def _on_press(self, _event: Any) -> None:
        self._canvas.itemconfig(self._rect_id, fill=_CLR_BTN_PRESS)

    def _on_release(self, _event: Any) -> None:
        self._canvas.itemconfig(self._rect_id, fill=_CLR_BTN_HOVER)
        if not self._disabled:
            self._on_click()

    # ------------------------------------------------------------------
    # 공개 인터페이스
    # ------------------------------------------------------------------

    def destroy(self) -> None:
        """캔버스에서 버튼 아이템 일괄 삭제."""
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------


class Panel:
    """Canvas 기반 사각형 패널 (9-슬라이스 흉내).

    실제 이미지 없이 단색 직사각형으로 패널을 표현한다.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        fill: str = _CLR_PANEL_DEFAULT,
        outline: str = _CLR_PANEL_OUTLINE,
        alpha: float = 1.0,  # 0~1 (tkinter 미지원, 향후 확장용 파라미터)
        scaler: Scaler | None = None,
        tag: str = "ui_panel",
    ) -> None:
        self._canvas = canvas
        self._ids: list[int] = []

        if scaler is not None:
            sx1, sy1 = scaler.to_screen(x, y)
            sx2, sy2 = scaler.to_screen(x + w, y + h)
        else:
            sx1, sy1 = x, y
            sx2, sy2 = x + w, y + h

        self._rect_id = canvas.create_rectangle(
            sx1,
            sy1,
            sx2,
            sy2,
            fill=fill,
            outline=outline,
            width=2,
            tags=(tag,),
        )
        self._ids = [self._rect_id]

    def destroy(self) -> None:
        """패널 삭제."""
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []


# ---------------------------------------------------------------------------
# Label
# ---------------------------------------------------------------------------


class Label:
    """Canvas 기반 텍스트 레이블."""

    def __init__(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        text: str,
        *,
        font_pt: int = 16,
        bold: bool = False,
        fill: str = _CLR_TEXT_NORMAL,
        anchor: str = "center",
        scaler: Scaler | None = None,
        tag: str = "ui_label",
    ) -> None:
        self._canvas = canvas
        self._ids: list[int] = []

        if scaler is not None:
            sx, sy = scaler.to_screen(x, y)
            font = _font(font_pt, bold=bold, scaler=scaler)
        else:
            sx, sy = x, y
            font = _font(font_pt, bold=bold)

        self._text_id = canvas.create_text(
            sx,
            sy,
            text=text,
            fill=fill,
            font=font,
            anchor=anchor,
            tags=(tag,),
        )
        self._ids = [self._text_id]

    def set_text(self, text: str) -> None:
        """텍스트 내용 갱신 (itemconfig)."""
        self._canvas.itemconfig(self._text_id, text=text)

    def destroy(self) -> None:
        """레이블 삭제."""
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []


# ---------------------------------------------------------------------------
# 하위 호환 헬퍼 (기존 코드가 사용하는 make_text_button / make_progress_bar)
# ---------------------------------------------------------------------------


def make_text_button(
    canvas: tk.Canvas,
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
    font: tuple[str, int, str] = ("Malgun Gothic", 14, "bold"),
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
    text_id = canvas.create_text(cx, cy, text=label, fill=text_color, font=font, tags=(tag,))

    def _hit(_event: Any) -> None:
        on_click()

    canvas.tag_bind(rect_id, "<Button-1>", _hit)
    canvas.tag_bind(text_id, "<Button-1>", _hit)
    return rect_id, text_id


def make_progress_bar(
    canvas: tk.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    tag: str = "progress",
    bg: str = "#222",
    fg: str = "#cc6633",
) -> tuple[int, int]:
    """진행바(배경+전경). 반환 ``(bg_id, fg_id)``."""
    bg_id = canvas.create_rectangle(x, y, x + w, y + h, fill=bg, outline="", tags=(tag,))
    fg_id = canvas.create_rectangle(x, y, x + w, y + h, fill=fg, outline="", tags=(tag,))
    return bg_id, fg_id
