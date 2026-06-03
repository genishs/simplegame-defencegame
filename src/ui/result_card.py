"""L2 결과 카드 — 클리어 시 해금 코덱스 카드 앞면 연출 (교육 통합 H4).

DESIGN (docs/15 §3.2, DECISION-EDU-001, docs/16 Wave2 2-1):
- 클리어 결과 화면에 **앞면만 자동** 노출: 라벨 칩 + 제목 + NEW + 1줄 요약.
- 본문은 강제하지 않는다(EP1). "도감에서 읽기" 버튼이 L3(도감)로 연결.
- 본 위젯은 ResultDialog 위에 얹히는 캔버스 패널. 비모달 강제 없음(결과 화면
  자체가 게임 종료 후 화면이라 흐름 단절 아님).

라벨 칩 색/표기는 ``src.ui.edu_strings`` SSOT(R2) 를 사용한다.
베이스 해상도 1920×1080 기준 좌표.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.ui.edu_strings import STRINGS, label_color, label_text

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler
    from src.data.loader import CodexCard


class ResultCard:
    """결과 화면 해금 카드 앞면(H4).

    Args:
        canvas: 대상 Canvas.
        scaler: 좌표/폰트 Scaler.
        card: 해금된 ``CodexCard`` (앞면 메타).
        on_read: "도감에서 읽기" 콜백 (없으면 버튼 생략).
        tag: 소속 씬/다이얼로그 태그.
    """

    TAG: str = "result_card"

    def __init__(
        self,
        canvas: tk.Canvas,
        scaler: Scaler | None,
        card: CodexCard,
        *,
        on_read: Callable[[], None] | None = None,
        tag: str | None = None,
    ) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._card = card
        self._on_read = on_read
        self._tag = tag or self.TAG
        self._ids: list[int] = []
        self._visible = False

    @property
    def visible(self) -> bool:
        return self._visible

    def show(self) -> None:
        if self._visible:
            return
        self._visible = True
        c = self._canvas
        s = self._scaler

        def sx(x: float, y: float) -> tuple[float, float]:
            return s.to_screen(x, y) if s is not None else (x, y)

        def fpt(pt: int) -> int:
            return s.font_pt(pt) if s is not None else pt

        # 카드 패널 (우측 하단 영역, 결과 패널 안쪽 아래).
        px1, py1 = sx(1180, 380)
        px2, py2 = sx(1410, 660)
        panel = c.create_rectangle(
            px1,
            py1,
            px2,
            py2,
            fill="#241a10",
            outline="#c8a060",
            width=3,
            tags=(self._tag, self.TAG),
        )
        self._ids.append(panel)

        # 섹션 제목 "새 역사 노트"
        st_x, st_y = sx(1295, 400)
        title_sec = c.create_text(
            st_x,
            st_y,
            text=STRINGS["result.card.title"],
            fill="#e8d080",
            font=(_family_bold(), fpt(16), "bold"),
            anchor="center",
            tags=(self._tag, self.TAG),
        )
        self._ids.append(title_sec)

        # 라벨 칩 (색 + 표기). fact_adapted 도 (사실) 표기(R5).
        chip_x1, chip_y1 = sx(1200, 422)
        chip_x2, chip_y2 = sx(1290, 450)
        chip = c.create_rectangle(
            chip_x1,
            chip_y1,
            chip_x2,
            chip_y2,
            fill=label_color(self._card.label),
            outline="",
            tags=(self._tag, self.TAG),
        )
        self._ids.append(chip)
        chip_cx, chip_cy = sx(1245, 436)
        chip_text = c.create_text(
            chip_cx,
            chip_cy,
            text=label_text(self._card.label),
            fill="#ffffff",
            font=(_family_bold(), fpt(12), "bold"),
            anchor="center",
            tags=(self._tag, self.TAG),
        )
        self._ids.append(chip_text)

        # NEW 뱃지
        new_x, new_y = sx(1380, 436)
        new_badge = c.create_text(
            new_x,
            new_y,
            text=STRINGS["result.card.new_badge"],
            fill="#ff6a4a",
            font=(_family_bold(), fpt(14), "bold"),
            anchor="e",
            tags=(self._tag, self.TAG),
        )
        self._ids.append(new_badge)

        # 카드 제목
        ct_x, ct_y = sx(1295, 478)
        card_title = c.create_text(
            ct_x,
            ct_y,
            text=self._card.title,
            fill="#f0e0c0",
            font=(_family_bold(), fpt(18), "bold"),
            anchor="center",
            justify="center",
            width=int(px2 - px1 - 28),
            tags=(self._tag, self.TAG),
        )
        self._ids.append(card_title)

        # 1줄 요약 (앞면 — 본문 강제 금지 DECISION-EDU-001)
        sm_x, sm_y = sx(1295, 530)
        summary = c.create_text(
            sm_x,
            sm_y,
            text=self._card.summary,
            fill="#c8b890",
            font=(_family_regular(), fpt(13)),
            anchor="center",
            justify="center",
            width=int(px2 - px1 - 28),
            tags=(self._tag, self.TAG),
        )
        self._ids.append(summary)

        # "도감에서 읽기" 버튼 (선택)
        if self._on_read is not None:
            self._add_read_button(sx, fpt)

    def _add_read_button(self, sx, fpt) -> None:  # type: ignore[no-untyped-def]
        c = self._canvas
        bx1, by1 = sx(1200, 600)
        bx2, by2 = sx(1390, 644)
        rect = c.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#3a2a1c",
            outline="#a88a5c",
            width=2,
            tags=(self._tag, self.TAG),
        )
        cx = (bx1 + bx2) / 2
        cy = (by1 + by2) / 2
        label = c.create_text(
            cx,
            cy,
            text=STRINGS["result.card.read_in_codex"],
            fill="#f0e0c0",
            font=(_family_bold(), fpt(14), "bold"),
            anchor="center",
            tags=(self._tag, self.TAG),
        )
        self._ids.extend([rect, label])
        for iid in (rect, label):
            try:
                c.tag_bind(iid, "<ButtonRelease-1>", lambda _e: self._on_read())  # type: ignore[misc]
            except Exception:  # noqa: BLE001
                pass

    def hide(self) -> None:
        if not self._visible:
            return
        self._visible = False
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []
