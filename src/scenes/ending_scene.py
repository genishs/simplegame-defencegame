"""엔딩 씬 (placeholder).

EXPECTED: team-member-2가 결과 화면(승리/패배), 별 평가, 메타 보상 노출 구현.
"""
from __future__ import annotations

from src.scenes.base_scene import BaseScene


class EndingScene(BaseScene):
    SCENE_TAG = "ending"

    def build(self) -> None:
        canvas = self.app.canvas
        w = canvas.winfo_width() or self.app.scaler.canvas_w
        h = canvas.winfo_height() or self.app.scaler.canvas_h
        canvas.create_rectangle(
            0, 0, w, h, fill="#080808", outline="", tags=(self._tag, "bg")
        )
        canvas.create_text(
            w / 2,
            h / 2,
            text="엔딩 — Phase 2 골격 — 구현 예정",
            fill="#f0d090",
            font=("Malgun Gothic", 20, "bold"),
            tags=(self._tag,),
        )
        back_id = canvas.create_text(
            w / 2,
            h * 0.75,
            text="[ 메뉴로 ]",
            fill="#88aaff",
            font=("Malgun Gothic", 14, "underline"),
            tags=(self._tag, "back"),
        )
        canvas.tag_bind(back_id, "<Button-1>", lambda _e: self.app.goto("menu"))
