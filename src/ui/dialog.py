"""모달 다이얼로그 (일시정지 / 결과).

DESIGN:
- PauseDialog: 전투 화면 위 반투명 dim + 패널 + 버튼 (SCN-06).
- ResultDialog: 승리/패배 결과 + 별 평가 + 버튼 3개 (SCN-07/08).
- show() / hide() 토글. hide 시 모든 canvas item state=hidden.
- tkinter Canvas 기반; App 의존 없음 (canvas, scaler, 콜백만 받음).

베이스 해상도 1920×1080 기준 좌표.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler

# UI 문자열 (docs/story/08_ui_strings.md §6, §7)
_STRINGS: dict[str, str] = {
    "pause.title": "일시정지",
    "pause.resume": "계속하기",
    "pause.restart": "다시 시작",
    "pause.settings": "설정",
    "pause.stage_select": "스테이지 선택",
    "pause.to_title": "타이틀로",
    "toast.autosave": "현재 진행 자동 저장됨",
    "result.win.title": "진군을 격퇴했습니다",
    "result.lose.title": "성이 함락되었습니다",
    "result.next": "다음 스테이지로",
    "result.retry": "다시 도전",
    "result.menu": "스테이지 선택",
    "result.win.star_1": "클리어",
    "result.win.star_2": "체력 유지",
    "result.win.star_3": "적은 희생",
    "result.win.fame_gained": "명성 +{fame}",
    "result.win.reward_grain": "곡식 +{grain}",
}

_CLR_DIM = "#000000"
_CLR_PANEL = "#1e1610"
_CLR_PANEL_OUTLINE = "#7a5c3a"
_CLR_BTN_NORMAL = "#3a2a1c"
_CLR_BTN_HOVER = "#5a4a2c"
_CLR_BTN_PRESS = "#2a1a0c"
_CLR_BTN_OUTLINE = "#a88a5c"
_CLR_BTN_HOVER_OUTLINE = "#d4a84a"
_CLR_TEXT = "#f0e0c0"
_CLR_TITLE = "#e8d080"
_CLR_STAR_FILLED = "#e8c040"
_CLR_STAR_EMPTY = "#444444"


def _fpt(scaler: Scaler | None, pt: int) -> int:
    if scaler is None:
        return pt
    return scaler.font_pt(pt)


def _font(scaler: Scaler | None, pt: int, bold: bool = False) -> tuple[str, int, str]:
    style = "bold" if bold else "normal"
    family = _family_bold() if bold else _family_regular()
    return (family, _fpt(scaler, pt), style)


def _sx(scaler: Scaler | None, x: float, y: float) -> tuple[float, float]:
    if scaler is None:
        return x, y
    return scaler.to_screen(x, y)


# ---------------------------------------------------------------------------
# PauseDialog
# ---------------------------------------------------------------------------


class PauseDialog:
    """일시정지 다이얼로그 (SCN-06).

    Args:
        canvas: 대상 Canvas.
        scaler: 좌표 변환 Scaler (None이면 raw 좌표).
        on_resume: '계속하기' 콜백.
        on_quit: '타이틀로' 콜백.
        on_stage_select: '스테이지 선택' 콜백 (기본 None).
    """

    TAG: str = "dialog_pause"

    def __init__(
        self,
        canvas: tk.Canvas,
        scaler: Scaler | None,
        on_resume: Callable[[], None],
        on_quit: Callable[[], None],
        *,
        on_stage_select: Callable[[], None] | None = None,
    ) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._on_resume = on_resume
        self._on_quit = on_quit
        self._on_stage_select = on_stage_select
        self._ids: list[int] = []
        self._visible: bool = False

    # ------------------------------------------------------------------

    def show(self) -> None:
        """다이얼로그를 캔버스에 그린다."""
        if self._visible:
            return
        self._visible = True
        c = self._canvas
        s = self._scaler
        tag = self.TAG

        def sx(x: float, y: float) -> tuple[float, float]:
            return _sx(s, x, y)

        # dim 오버레이
        x1, y1 = sx(0, 0)
        x2, y2 = sx(1920, 1080)
        dim = c.create_rectangle(x1, y1, x2, y2, fill=_CLR_DIM, outline="", stipple="gray50", tags=(tag,))
        self._ids.append(dim)

        # 모달 패널 (PAU-02)
        px1, py1 = sx(660, 280)
        px2, py2 = sx(1260, 800)
        panel = c.create_rectangle(
            px1, py1, px2, py2, fill=_CLR_PANEL, outline=_CLR_PANEL_OUTLINE, width=3, tags=(tag,)
        )
        self._ids.append(panel)

        # 타이틀 (PAU-03)
        tcx, tcy = sx(960, 325)
        title = c.create_text(
            tcx,
            tcy,
            text=_STRINGS["pause.title"],
            fill=_CLR_TITLE,
            font=_font(s, 36, bold=True),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(title)

        # 버튼 정의: (y_base, label_key, callback)
        btn_defs: list[tuple[float, str, Callable[[], None]]] = [
            (420, "pause.resume", self._on_resume),
            (500, "pause.restart", lambda: self._on_quit()),  # 간략화
            (580, "pause.settings", lambda: None),
            (660, "pause.stage_select", self._on_stage_select or self._on_quit),
            (740, "pause.to_title", self._on_quit),
        ]
        for by, key, cb in btn_defs:
            self._add_button(720, by, 480, 64, _STRINGS.get(key, key), cb, s, tag)

        # 자동 저장 안내 (PAU-09)
        ax, ay = sx(960, 790)
        autosave = c.create_text(
            ax,
            ay,
            text=_STRINGS["toast.autosave"],
            fill="#888888",
            font=_font(s, 14),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(autosave)

    def hide(self) -> None:
        """다이얼로그를 숨긴다 (canvas item 삭제)."""
        if not self._visible:
            return
        self._visible = False
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []

    @property
    def visible(self) -> bool:
        return self._visible

    # ------------------------------------------------------------------

    def _add_button(
        self,
        bx: float,
        by: float,
        bw: float,
        bh: float,
        label: str,
        on_click: Callable[[], None],
        s: Scaler | None,
        tag: str,
    ) -> None:
        c = self._canvas
        x1, y1 = _sx(s, bx, by)
        x2, y2 = _sx(s, bx + bw, by + bh)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        rect_id = c.create_rectangle(
            x1, y1, x2, y2, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE, width=2, tags=(tag,)
        )
        text_id = c.create_text(
            cx, cy, text=label, fill=_CLR_TEXT, font=_font(s, 22, bold=True), anchor="center", tags=(tag,)
        )

        self._ids.extend([rect_id, text_id])

        def _hover_enter(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_HOVER, outline=_CLR_BTN_HOVER_OUTLINE)

        def _hover_leave(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE)

        def _press(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_PRESS)

        def _release(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_HOVER)
            on_click()

        for iid in (rect_id, text_id):
            c.tag_bind(iid, "<Enter>", _hover_enter)
            c.tag_bind(iid, "<Leave>", _hover_leave)
            c.tag_bind(iid, "<ButtonPress-1>", _press)
            c.tag_bind(iid, "<ButtonRelease-1>", _release)


# ---------------------------------------------------------------------------
# ResultDialog
# ---------------------------------------------------------------------------


class ResultDialog:
    """전투 결과 다이얼로그 (SCN-07 승리 / SCN-08 패배).

    Args:
        canvas: 대상 Canvas.
        scaler: 좌표 변환 Scaler.
        victory: True이면 승리, False이면 패배.
        stats: 결과 통계 dict (stars, fame, grain 등).
        on_next: '다음 스테이지' 콜백.
        on_retry: '다시 도전' 콜백.
        on_menu: '스테이지 선택' 콜백.
    """

    TAG: str = "dialog_result"

    def __init__(
        self,
        canvas: tk.Canvas,
        scaler: Scaler | None,
        victory: bool,
        stats: dict[str, Any],
        on_next: Callable[[], None],
        on_retry: Callable[[], None],
        on_menu: Callable[[], None],
    ) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._victory = victory
        self._stats = stats
        self._on_next = on_next
        self._on_retry = on_retry
        self._on_menu = on_menu
        self._ids: list[int] = []
        self._visible: bool = False

    # ------------------------------------------------------------------

    def show(self) -> None:
        """결과 화면을 그린다."""
        if self._visible:
            return
        self._visible = True
        c = self._canvas
        s = self._scaler
        tag = self.TAG

        def sx(x: float, y: float) -> tuple[float, float]:
            return _sx(s, x, y)

        # 배경 (RWN-01 / 패배는 어두운 청회색)
        bg_fill = "#2a1c10" if self._victory else "#101828"
        x1, y1 = sx(0, 0)
        x2, y2 = sx(1920, 1080)
        bg = c.create_rectangle(x1, y1, x2, y2, fill=bg_fill, outline="", tags=(tag,))
        self._ids.append(bg)

        # 결과 타이틀
        title_key = "result.win.title" if self._victory else "result.lose.title"
        title_clr = "#e8d080" if self._victory else "#cc8888"
        tcx, tcy = sx(960, 120)
        title_id = c.create_text(
            tcx,
            tcy,
            text=_STRINGS[title_key],
            fill=title_clr,
            font=_font(s, 48, bold=True),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(title_id)

        # 결과 패널 박스
        px1, py1 = sx(480, 200)
        px2, py2 = sx(1440, 700)
        panel = c.create_rectangle(
            px1, py1, px2, py2, fill="#1e1610", outline=_CLR_PANEL_OUTLINE, width=2, tags=(tag,)
        )
        self._ids.append(panel)

        if self._victory:
            self._draw_victory_contents(sx, tag)
        else:
            self._draw_defeat_contents(sx, tag)

        # 버튼 3개 (SCN-07/08 공통)
        btn_y = 750
        btn_configs = [
            (560, "result.next", self._on_next),
            (860, "result.retry", self._on_retry),
            (1160, "result.menu", self._on_menu),
        ]
        for bcx, key, cb in btn_configs:
            self._add_button(bcx - 160, btn_y, 320, 64, _STRINGS.get(key, key), cb, s, tag)

    def _draw_victory_contents(self, sx: Callable[[float, float], tuple[float, float]], tag: str) -> None:
        c = self._canvas
        s = self._scaler
        stars = self._stats.get("stars", 0)

        # 별 3개 (DECISION-D-013)
        star_positions = [(660, 350), (900, 350), (1140, 350)]
        star_captions = [
            _STRINGS["result.win.star_1"],
            _STRINGS["result.win.star_2"],
            _STRINGS["result.win.star_3"],
        ]
        for i, ((bx, by), cap) in enumerate(zip(star_positions, star_captions, strict=True)):
            filled = i < stars
            clr = _CLR_STAR_FILLED if filled else _CLR_STAR_EMPTY
            scx, scy = sx(bx, by)
            star_id = c.create_text(
                scx, scy, text="★", fill=clr, font=_font(s, 56, bold=True), anchor="center", tags=(tag,)
            )
            self._ids.append(star_id)
            capx, capy = sx(bx, by + 80)
            cap_id = c.create_text(
                capx, capy, text=cap, fill="#c0b080", font=_font(s, 14), anchor="center", tags=(tag,)
            )
            self._ids.append(cap_id)

        # 보상 텍스트
        fame = self._stats.get("fame", 0)
        grain = self._stats.get("grain", 0)
        ry = 520
        for reward_text in [
            _STRINGS["result.win.fame_gained"].format(fame=fame),
            _STRINGS["result.win.reward_grain"].format(grain=grain),
        ]:
            rx, ryl = sx(960, ry)
            rid = c.create_text(
                rx,
                ryl,
                text=reward_text,
                fill="#e8d080",
                font=_font(s, 20, bold=True),
                anchor="center",
                tags=(tag,),
            )
            self._ids.append(rid)
            ry += 50

        # 역사 노트 추가 알림
        notex, notey = sx(960, 640)
        note_id = c.create_text(
            notex,
            notey,
            text="역사 노트가 도감에 추가되었습니다.",
            fill="#90a880",
            font=_font(s, 16),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(note_id)

    def _draw_defeat_contents(self, sx: Callable[[float, float], tuple[float, float]], tag: str) -> None:
        c = self._canvas
        s = self._scaler
        msg_x, msg_y = sx(960, 440)
        msg_id = c.create_text(
            msg_x,
            msg_y,
            text="성벽이 무너졌습니다. 다시 도전하십시오.",
            fill="#cc9090",
            font=_font(s, 22),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(msg_id)

        # 통계
        survived = self._stats.get("waves_survived", 0)
        sv_x, sv_y = sx(960, 520)
        sv_id = c.create_text(
            sv_x,
            sv_y,
            text=f"격퇴한 진군: {survived}파",
            fill="#a0a0a0",
            font=_font(s, 18),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(sv_id)

    def hide(self) -> None:
        """결과 화면을 숨긴다 (삭제)."""
        if not self._visible:
            return
        self._visible = False
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []

    @property
    def visible(self) -> bool:
        return self._visible

    # ------------------------------------------------------------------

    def _add_button(
        self,
        bx: float,
        by: float,
        bw: float,
        bh: float,
        label: str,
        on_click: Callable[[], None],
        s: Scaler | None,
        tag: str,
    ) -> None:
        c = self._canvas
        x1, y1 = _sx(s, bx, by)
        x2, y2 = _sx(s, bx + bw, by + bh)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        rect_id = c.create_rectangle(
            x1, y1, x2, y2, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE, width=2, tags=(tag,)
        )
        text_id = c.create_text(
            cx, cy, text=label, fill=_CLR_TEXT, font=_font(s, 20, bold=True), anchor="center", tags=(tag,)
        )

        self._ids.extend([rect_id, text_id])

        def _hover_enter(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_HOVER, outline=_CLR_BTN_HOVER_OUTLINE)

        def _hover_leave(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE)

        def _press(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_PRESS)

        def _release(_e: Any) -> None:
            c.itemconfig(rect_id, fill=_CLR_BTN_HOVER)
            on_click()

        for iid in (rect_id, text_id):
            c.tag_bind(iid, "<Enter>", _hover_enter)
            c.tag_bind(iid, "<Leave>", _hover_leave)
            c.tag_bind(iid, "<ButtonPress-1>", _press)
            c.tag_bind(iid, "<ButtonRelease-1>", _release)
