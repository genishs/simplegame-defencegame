"""토산 "버티기" 게이지 위젯 (교육 통합 H7 표시부).

DESIGN (docs/15 §2.1 H7, docs/16 Wave4):
- 스테이지5 한정. 화면 상단 중앙(웨이브 HUD 아래)에 "버티기" 게이지를 표시.
- 게이지 채움(0..1)은 systems(EnduranceSystem)이 계산. 본 위젯은 표시만(R-5).
- 가득 차면 "버티면 이긴다 — 당군이 물러갑니다" 메시지로 강조(LO2).
- 비모달. 게임 일시정지 없음(EP1).

베이스 해상도 1920×1080 기준 좌표.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.fonts import family_bold as _family_bold

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler

# 게이지 바 베이스 좌표 (상단 중앙, 웨이브 HUD y=80 아래).
_BAR_X1 = 760.0
_BAR_X2 = 1160.0
_BAR_Y1 = 92.0
_BAR_Y2 = 116.0


class EnduranceGauge:
    """버티기 게이지 표시 (H7).

    Args:
        canvas: 대상 Canvas.
        scaler: 좌표/폰트 Scaler.
        tag: 소속 씬 태그.
    """

    TAG: str = "endurance_gauge"

    def __init__(self, canvas: tk.Canvas, scaler: Scaler | None, *, tag: str | None = None) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._tag = tag or self.TAG
        self._bg_id: int | None = None
        self._bar_id: int | None = None
        self._label_id: int | None = None
        self._msg_id: int | None = None
        self._built = False

    def _sx(self, x: float, y: float) -> tuple[float, float]:
        s = self._scaler
        return s.to_screen(x, y) if s is not None else (x, y)

    def _fpt(self, pt: int) -> int:
        s = self._scaler
        return s.font_pt(pt) if s is not None else pt

    def build(self) -> None:
        if self._built:
            return
        self._built = True
        c = self._canvas
        bx1, by1 = self._sx(_BAR_X1, _BAR_Y1)
        bx2, by2 = self._sx(_BAR_X2, _BAR_Y2)
        # 라벨
        lx, ly = self._sx(_BAR_X1, _BAR_Y1 - 18)
        self._label_id = c.create_text(
            lx,
            ly,
            text="버티기 (적 사기·추위)",
            fill="#9ad0ff",
            font=(_family_bold(), self._fpt(13), "bold"),
            anchor="w",
            tags=(self._tag, self.TAG),
        )
        self._bg_id = c.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#102030",
            outline="#3a6a9a",
            width=2,
            tags=(self._tag, self.TAG),
        )
        self._bar_id = c.create_rectangle(
            bx1,
            by1,
            bx1,
            by2,
            fill="#4a9adf",
            outline="",
            tags=(self._tag, self.TAG),
        )
        mx, my = self._sx((_BAR_X1 + _BAR_X2) / 2, (_BAR_Y1 + _BAR_Y2) / 2)
        self._msg_id = c.create_text(
            mx,
            my,
            text="0%",
            fill="#dceaff",
            font=(_family_bold(), self._fpt(11), "bold"),
            anchor="center",
            tags=(self._tag, self.TAG),
        )

    def update(self, fill: float, *, victory: bool = False) -> None:
        """게이지 채움(0..1) 반영. victory 면 가득 + 강조 메시지."""
        if not self._built:
            return
        c = self._canvas
        ratio = max(0.0, min(1.0, fill))
        bx1, by1 = self._sx(_BAR_X1, _BAR_Y1)
        bx2, by2 = self._sx(_BAR_X2, _BAR_Y2)
        bar_w = (bx2 - bx1) * ratio
        if self._bar_id is not None:
            try:
                c.coords(self._bar_id, bx1, by1, bx1 + bar_w, by2)
                # 70% 이상이면 따뜻한 강조색(임박).
                fill_clr = "#7ad0a0" if ratio >= 0.7 else "#4a9adf"
                c.itemconfig(self._bar_id, fill=fill_clr)
            except Exception:  # noqa: BLE001
                pass
        if self._msg_id is not None:
            try:
                if victory or ratio >= 1.0:
                    c.itemconfig(
                        self._msg_id,
                        text="버티면 이긴다 — 당군이 물러갑니다",
                        fill="#bfffd0",
                    )
                else:
                    c.itemconfig(self._msg_id, text=f"{int(ratio * 100)}%", fill="#dceaff")
            except Exception:  # noqa: BLE001
                pass
