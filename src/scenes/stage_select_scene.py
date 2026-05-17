"""스테이지 선택 씬 (placeholder).

EXPECTED: team-member-2가 5개 스테이지 카드 + 잠금/해금 표시 + 별 표시 구현.
"""
from __future__ import annotations

from src.scenes.base_scene import BaseScene


class StageSelectScene(BaseScene):
    SCENE_TAG = "stage_select"

    def build(self) -> None:
        canvas = self.app.canvas
        w = canvas.winfo_width() or self.app.scaler.canvas_w
        h = canvas.winfo_height() or self.app.scaler.canvas_h
        canvas.create_rectangle(
            0, 0, w, h, fill="#101820", outline="", tags=(self._tag, "bg")
        )
        canvas.create_text(
            w / 2,
            h * 0.3,
            text="스테이지 선택 (Phase 2 골격 — 구현 예정)",
            fill="#cccccc",
            font=("Malgun Gothic", 18),
            tags=(self._tag,),
        )

        # 임시 메뉴 복귀 버튼.
        back_id = canvas.create_text(
            w / 2,
            h * 0.7,
            text="[ 메뉴로 ]",
            fill="#88aaff",
            font=("Malgun Gothic", 14, "underline"),
            tags=(self._tag, "back"),
        )
        canvas.tag_bind(back_id, "<Button-1>", lambda _e: self.app.goto("menu"))
        # ESC로도 메뉴 복귀.
        self.app.root.bind("<Escape>", lambda _e: self.app.goto("menu"))

    def teardown(self) -> None:
        super().teardown()
        self.app.root.unbind("<Escape>")
