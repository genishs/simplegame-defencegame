"""메인 메뉴 씬 (SCN-01).

DESIGN: 와이어프레임 §4 준수.
- 타이틀 + 부제 + 8개 버튼(새 게임/이어하기/스테이지/병영/도감/설정/만든이들/종료)
- 키보드 Enter = 포커스 선택, Esc = 무반응(SCN-01 사양).
- 색상: 팔레트 DECISION-D-005 기준.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.scenes.base_scene import BaseScene

if TYPE_CHECKING:
    from src.core.app import App

# UI 문자열 (docs/story/08_ui_strings.md §1.1~1.2)
_STRINGS: dict[str, str] = {
    "title.game_title": "안시성: 88일의 약속",
    "title.subtitle": "Ansi 88",
    "title.version": "v0.1.0",
    "title.copyright": "© 2026 안시성 645 기획팀",
    "menu.new_game": "새 게임",
    "menu.continue": "이어하기",
    "menu.stage_select": "스테이지",
    "menu.barracks": "병영",
    "menu.codex": "도감",
    "menu.settings": "설정",
    "menu.credits": "만든 사람들",
    "menu.quit": "종료",
}

# 와이어프레임 §4.2 버튼 배치 (베이스 1920×1080)
# Phase 3.5 (Issue #12, DECISION-DL-P3-5-002):
# 수직 슬라이스 흐름 (메뉴 → 스테이지 선택 → 배틀 → 엔딩) 을 위해
# "새 게임" 과 "이어하기" 도 stage_select 로 라우팅. 기존 battle 직행은 제거.
_BUTTONS: list[tuple[str, str, float, float, float, float]] = [
    # (key, scene_or_action, bx, by, bw, bh)
    ("menu.new_game", "stage_select", 760, 520, 400, 70),
    ("menu.continue", "stage_select", 760, 600, 400, 70),
    ("menu.stage_select", "stage_select", 760, 680, 400, 70),
    ("menu.barracks", "menu", 760, 760, 400, 70),
    ("menu.codex", "menu", 760, 840, 400, 70),
    ("menu.settings", "menu", 760, 920, 400, 70),
    ("menu.credits", "menu", 760, 1000, 400, 50),
    ("menu.quit", "__quit__", 760, 1060, 400, 40),
]


class MenuScene(BaseScene):
    """메인 메뉴 씬."""

    SCENE_TAG = "menu"

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self._button_ids: list[tuple[int, int]] = []
        self._focused_idx: int = 0  # 키보드 포커스 인덱스
        self._btn_rect_ids: list[int] = []

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def build(self) -> None:
        canvas = self.app.canvas
        scaler = self.app.scaler
        w = canvas.winfo_width() or scaler.canvas_w
        h = canvas.winfo_height() or scaler.canvas_h
        tag = self._tag

        # 배경 (TIT-01 대용 단색)
        canvas.create_rectangle(0, 0, w, h, fill="#1a1410", outline="", tags=(tag, "bg"))

        s = scaler

        def sx(bx: float, by: float) -> tuple[float, float]:
            return s.to_screen(bx, by)

        def fpt(pt: int) -> int:
            return s.font_pt(pt)

        def font(pt: int, bold: bool = False) -> tuple[str, int, str]:
            style = "bold" if bold else "normal"
            family = _family_bold() if bold else _family_regular()
            return (family, fpt(pt), style)

        # 타이틀 텍스트 (TIT-02)
        tcx, tcy = sx(960, 320)
        canvas.create_text(
            tcx,
            tcy,
            text=_STRINGS["title.game_title"],
            fill="#e8d6a8",
            font=font(72, bold=True),
            anchor="center",
            tags=(tag, "title"),
        )

        # 부제 (TIT-03)
        scx, scy = sx(960, 410)
        canvas.create_text(
            scx,
            scy,
            text=_STRINGS["title.subtitle"],
            fill="#a89878",
            font=font(26),
            anchor="center",
            tags=(tag, "subtitle"),
        )

        # 버튼들
        self._btn_rect_ids = []
        self._button_ids = []
        for i, (key, dest, bx, by, bw, bh) in enumerate(_BUTTONS):
            label = _STRINGS.get(key, key)
            rect_id, text_id = self._make_button(canvas, bx, by, bw, bh, label, dest, s, tag, i)
            self._button_ids.append((rect_id, text_id))
            self._btn_rect_ids.append(rect_id)

        # 버전 라벨 (TIT-12)
        vx, vy = sx(40, 1060)
        canvas.create_text(
            vx,
            vy,
            text=_STRINGS["title.version"],
            fill="#666655",
            font=font(14),
            anchor="sw",
            tags=(tag, "version"),
        )

        # 카피라이트 (TIT-13)
        cx2, cy2 = sx(1880, 1060)
        canvas.create_text(
            cx2,
            cy2,
            text=_STRINGS["title.copyright"],
            fill="#666655",
            font=font(14),
            anchor="se",
            tags=(tag, "copyright"),
        )

        # 키 바인딩
        self.app.root.bind("<Return>", self._on_enter_key)
        self.app.root.bind("<Up>", self._on_up_key)
        self.app.root.bind("<Down>", self._on_down_key)

    def teardown(self) -> None:
        super().teardown()
        try:
            self.app.root.unbind("<Return>")
            self.app.root.unbind("<Up>")
            self.app.root.unbind("<Down>")
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _make_button(
        self,
        canvas: object,
        bx: float,
        by: float,
        bw: float,
        bh: float,
        label: str,
        dest: str,
        scaler: object,
        tag: str,
        idx: int,
    ) -> tuple[int, int]:
        import tkinter as tk  # 씬 레벨에서 import OK

        assert isinstance(canvas, tk.Canvas)
        from src.core.scaler import Scaler

        assert isinstance(scaler, Scaler)

        x1, y1 = scaler.to_screen(bx, by)
        x2, y2 = scaler.to_screen(bx + bw, by + bh)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        fpt_val = scaler.font_pt(22)

        rect_id = canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="#3a2a1c",
            outline="#a88a5c",
            width=2,
            tags=(tag, "menu_button"),
        )
        text_id = canvas.create_text(
            cx,
            cy,
            text=label,
            fill="#f0e0c0",
            font=(_family_bold(), fpt_val, "bold"),
            anchor="center",
            tags=(tag, "menu_button"),
        )

        def _click_handler(d: str = dest, i: int = idx) -> None:
            self._focused_idx = i
            if d == "__quit__":
                self.app.quit()
            else:
                self.app.goto(d)

        def _hover_enter(_e: object, rid: int = rect_id) -> None:
            canvas.itemconfig(rid, fill="#5a4a2c", outline="#d4a84a")

        def _hover_leave(_e: object, rid: int = rect_id) -> None:
            canvas.itemconfig(rid, fill="#3a2a1c", outline="#a88a5c")

        def _press(_e: object, rid: int = rect_id) -> None:
            canvas.itemconfig(rid, fill="#2a1a0c")

        def _release(_e: object, d: str = dest, i: int = idx) -> None:
            _click_handler(d, i)

        for iid in (rect_id, text_id):
            canvas.tag_bind(iid, "<Enter>", _hover_enter)
            canvas.tag_bind(iid, "<Leave>", _hover_leave)
            canvas.tag_bind(iid, "<ButtonPress-1>", _press)
            canvas.tag_bind(iid, "<ButtonRelease-1>", _release)

        return rect_id, text_id

    # ------------------------------------------------------------------
    # 키보드 핸들러
    # ------------------------------------------------------------------

    def _on_enter_key(self, _event: object) -> None:
        if self._focused_idx < len(_BUTTONS):
            _, dest, *_ = _BUTTONS[self._focused_idx]
            if dest == "__quit__":
                self.app.quit()
            else:
                self.app.goto(dest)

    def _on_up_key(self, _event: object) -> None:
        self._focused_idx = max(0, self._focused_idx - 1)
        self._update_focus()

    def _on_down_key(self, _event: object) -> None:
        self._focused_idx = min(len(_BUTTONS) - 1, self._focused_idx + 1)
        self._update_focus()

    def _update_focus(self) -> None:
        canvas = self.app.canvas
        for i, rect_id in enumerate(self._btn_rect_ids):
            if i == self._focused_idx:
                canvas.itemconfig(rect_id, outline="#d4a84a", width=3)
            else:
                canvas.itemconfig(rect_id, outline="#a88a5c", width=2)
