"""메인 메뉴 씬.

DESIGN: 골격 단계에서는 단순 텍스트 + 두 개의 클릭 가능 텍스트 버튼.
EXPECTED: team-member-2가 ``ui/widgets.py``의 Button을 적용하여 리뉴얼.
"""
from __future__ import annotations

from src.core.settings import APP_TITLE
from src.scenes.base_scene import BaseScene


class MenuScene(BaseScene):
    SCENE_TAG = "menu"

    def __init__(self, app):  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._button_ids: list[int] = []

    # ------------------------------------------------------------------
    def build(self) -> None:
        canvas = self.app.canvas
        w = canvas.winfo_width() or self.app.scaler.canvas_w
        h = canvas.winfo_height() or self.app.scaler.canvas_h

        canvas.create_rectangle(
            0, 0, w, h, fill="#1a1410", outline="", tags=(self._tag, "bg")
        )
        canvas.create_text(
            w / 2,
            h * 0.25,
            text=APP_TITLE,
            fill="#e8d6a8",
            font=("Malgun Gothic", 36, "bold"),
            tags=(self._tag, "title"),
        )
        canvas.create_text(
            w / 2,
            h * 0.35,
            text="Phase 2 — 엔진 골격",
            fill="#a89878",
            font=("Malgun Gothic", 16),
            tags=(self._tag, "subtitle"),
        )

        # 단순 텍스트 버튼.
        self._make_button(w / 2, h * 0.55, "전투 시작", lambda: self.app.goto("battle"))
        self._make_button(w / 2, h * 0.65, "스테이지 선택", lambda: self.app.goto("stage_select"))
        self._make_button(w / 2, h * 0.75, "종료", self.app.quit)

    # ------------------------------------------------------------------
    def _make_button(  # type: ignore[no-untyped-def]
        self, cx: float, cy: float, label: str, on_click
    ) -> None:
        canvas = self.app.canvas
        pad_x, pad_y = 120, 22
        rect_id = canvas.create_rectangle(
            cx - pad_x,
            cy - pad_y,
            cx + pad_x,
            cy + pad_y,
            fill="#3a2a1c",
            outline="#a88a5c",
            width=2,
            tags=(self._tag, "menu_button"),
        )
        text_id = canvas.create_text(
            cx,
            cy,
            text=label,
            fill="#f0e0c0",
            font=("Malgun Gothic", 18, "bold"),
            tags=(self._tag, "menu_button"),
        )

        def _hit(_event) -> None:  # type: ignore[no-untyped-def]
            on_click()

        canvas.tag_bind(rect_id, "<Button-1>", _hit)
        canvas.tag_bind(text_id, "<Button-1>", _hit)
        self._button_ids.extend([rect_id, text_id])
