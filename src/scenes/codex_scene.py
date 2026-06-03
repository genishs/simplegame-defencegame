"""도감 화면 (역사 노트 백과) — 교육 통합 H5 / L3.

DESIGN (docs/15 §3.3·§3.4, docs/16 Wave3 3-1·3-2·3-3):
- 3×5 그리드(15장) + 카드 상세 토글(같은 씬 내 view 전환).
- 상단 완성도 게이지("역사 노트 N/15") + 라벨 분포 + 칭호(5/10/15).
- 카드 상세: 라벨 칩 + 제목 + 본문 + 출처 + (사실 카드) 한문 원문 토글(H9).
- 잠금 카드: 회색 + 자물쇠 + codex.locked. 해금 카드만 상세 진입.
- 진행도(획득 카드 집합)는 세이브 슬롯 연동, 없으면 graceful(auto 해금분만).

진행도/해금 계산은 tk-free systems(codex_progress), 렌더는 본 씬. 라벨 칩 색/표기는
edu_strings SSOT(R2). ESC/뒤로 → 메뉴.

베이스 해상도 1920×1080 기준 좌표.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.data.loader import CodexCard, load_codex
from src.scenes.base_scene import BaseScene
from src.systems.codex_progress import (
    auto_unlocked_ids,
    compute_progress,
    load_unlocked_ids,
)
from src.ui.edu_strings import STRINGS, label_color, label_text

if TYPE_CHECKING:
    from src.core.app import App


class CodexScene(BaseScene):
    """도감 씬 (H5). 그리드 ↔ 상세 view 전환."""

    SCENE_TAG = "codex"

    _GRID_TAG = "codex_grid"
    _DETAIL_TAG = "codex_detail"

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self._cards: tuple[CodexCard, ...] = ()
        self._owned: set[str] = set()
        self._detail_card: CodexCard | None = None
        self._hanmun_open: bool = False

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------
    def build(self) -> None:
        try:
            self.app.sound.play_bgm("bgm.menu", loop=True, fade_in=1.0)
        except Exception:  # noqa: BLE001
            pass

        # 데이터 로드 (graceful).
        try:
            self._cards = load_codex()
        except Exception:  # noqa: BLE001
            self._cards = ()
        self._owned = self._load_owned()

        canvas = self.app.canvas
        scaler = self.app.scaler
        w = canvas.winfo_width() or scaler.canvas_w
        h = canvas.winfo_height() or scaler.canvas_h
        canvas.create_rectangle(0, 0, w, h, fill="#16110a", outline="", tags=(self._tag, "bg"))

        self._render_grid_view()

        self.app.root.bind("<Escape>", self._on_escape)

    def teardown(self) -> None:
        super().teardown()
        try:
            self.app.root.unbind("<Escape>")
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 진행도 로드
    # ------------------------------------------------------------------
    def _load_owned(self) -> set[str]:
        """획득 카드 집합 = auto 해금 ∪ 세이브 저장분. 세이브 없으면 auto 만(graceful)."""
        owned = auto_unlocked_ids(self._cards)
        try:
            from src.core.save_slot import load_save_slot

            owned |= load_unlocked_ids(load_save_slot())
        except Exception:  # noqa: BLE001
            pass
        return owned

    # ------------------------------------------------------------------
    # 그리드 view
    # ------------------------------------------------------------------
    def _sx(self, x: float, y: float) -> tuple[float, float]:
        s = self.app.scaler
        return s.to_screen(x, y) if s is not None else (x, y)

    def _fpt(self, pt: int) -> int:
        s = self.app.scaler
        return s.font_pt(pt) if s is not None else pt

    def _font(self, pt: int, bold: bool = False) -> tuple[str, int, str]:
        family = _family_bold() if bold else _family_regular()
        return (family, self._fpt(pt), "bold" if bold else "normal")

    def _render_grid_view(self) -> None:
        canvas = self.app.canvas
        self._detail_card = None

        # 타이틀
        tx, ty = self._sx(960, 70)
        canvas.create_text(
            tx,
            ty,
            text=STRINGS["codex.title"],
            fill="#e8d6a8",
            font=self._font(40, bold=True),
            anchor="center",
            tags=(self._tag, self._GRID_TAG),
        )

        self._render_progress_header()

        # 3×5 그리드. 카드 184×120, 간격 30. 시작 (300, 230).
        cols, rows = 5, 3
        cw, ch, gap = 240, 150, 28
        start_x, start_y = 320, 230
        for idx, card in enumerate(self._cards[: cols * rows]):
            r = idx // cols
            col = idx % cols
            bx = start_x + col * (cw + gap)
            by = start_y + r * (ch + gap)
            self._render_grid_cell(card, bx, by, cw, ch)

        self._render_back_button(self._GRID_TAG)

    def _render_progress_header(self) -> None:
        canvas = self.app.canvas
        prog = compute_progress(self._cards, self._owned)
        # 완성도 라벨
        px, py = self._sx(320, 150)
        canvas.create_text(
            px,
            py,
            text=STRINGS["codex.progress.label"].format(current=prog.unlocked),
            fill="#f0d080",
            font=self._font(22, bold=True),
            anchor="w",
            tags=(self._tag, self._GRID_TAG),
        )
        # 라벨 분포
        bx, by = self._sx(620, 150)
        canvas.create_text(
            bx,
            by,
            text=STRINGS["codex.progress.label_breakdown"].format(
                fact=prog.fact, legend=prog.legend, fiction=prog.fiction
            ),
            fill="#b8a878",
            font=self._font(16),
            anchor="w",
            tags=(self._tag, self._GRID_TAG),
        )
        # 칭호 (도달 시)
        milestone = prog.milestone_reached()
        if milestone is not None:
            key = f"codex.progress.milestone_{milestone}"
            mx, my = self._sx(1100, 150)
            canvas.create_text(
                mx,
                my,
                text=STRINGS.get(key, ""),
                fill="#8fd0a0",
                font=self._font(15),
                anchor="w",
                tags=(self._tag, self._GRID_TAG),
            )

    def _render_grid_cell(self, card: CodexCard, bx: float, by: float, cw: float, ch: float) -> None:
        canvas = self.app.canvas
        unlocked = card.id in self._owned
        x1, y1 = self._sx(bx, by)
        x2, y2 = self._sx(bx + cw, by + ch)
        fill = "#241a10" if unlocked else "#1a1a1a"
        outline = label_color(card.label) if unlocked else "#444444"
        rect = canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=fill,
            outline=outline,
            width=2,
            tags=(self._tag, self._GRID_TAG, "codex_cell"),
        )
        if unlocked:
            # 라벨 칩
            chx, chy = self._sx(bx + 12, by + 12)
            chx2, chy2 = self._sx(bx + 92, by + 38)
            canvas.create_rectangle(
                chx,
                chy,
                chx2,
                chy2,
                fill=label_color(card.label),
                outline="",
                tags=(self._tag, self._GRID_TAG),
            )
            ccx, ccy = self._sx(bx + 52, by + 25)
            canvas.create_text(
                ccx,
                ccy,
                text=label_text(card.label),
                fill="#ffffff",
                font=self._font(11, bold=True),
                anchor="center",
                tags=(self._tag, self._GRID_TAG),
            )
            # 제목
            ttx, tty = self._sx(bx + cw / 2, by + ch / 2 + 8)
            canvas.create_text(
                ttx,
                tty,
                text=card.title,
                fill="#f0e0c0",
                font=self._font(15, bold=True),
                anchor="center",
                justify="center",
                width=int(x2 - x1 - 24),
                tags=(self._tag, self._GRID_TAG),
            )

            def _open(_e: Any, c: CodexCard = card) -> None:
                self._open_detail(c)

            try:
                canvas.tag_bind(rect, "<ButtonRelease-1>", _open)
            except Exception:  # noqa: BLE001
                pass
        else:
            # 잠금: 자물쇠 + 안내
            lx, ly = self._sx(bx + cw / 2, by + ch / 2 - 6)
            canvas.create_text(
                lx,
                ly,
                text="🔒",
                fill="#777777",
                font=self._font(24, bold=True),
                anchor="center",
                tags=(self._tag, self._GRID_TAG),
            )
            l2x, l2y = self._sx(bx + cw / 2, by + ch / 2 + 26)
            canvas.create_text(
                l2x,
                l2y,
                text=STRINGS["codex.locked"],
                fill="#888888",
                font=self._font(11),
                anchor="center",
                justify="center",
                width=int(x2 - x1 - 24),
                tags=(self._tag, self._GRID_TAG),
            )

    # ------------------------------------------------------------------
    # 상세 view
    # ------------------------------------------------------------------
    def _open_detail(self, card: CodexCard) -> None:
        self._clear_tag(self._GRID_TAG)
        self._detail_card = card
        self._hanmun_open = False
        self._render_detail_view()

    def _back_to_grid(self) -> None:
        self._clear_tag(self._DETAIL_TAG)
        self._render_grid_view()

    def _render_detail_view(self) -> None:
        card = self._detail_card
        if card is None:
            return
        canvas = self.app.canvas

        # 패널 배경
        px1, py1 = self._sx(360, 140)
        px2, py2 = self._sx(1560, 900)
        canvas.create_rectangle(
            px1,
            py1,
            px2,
            py2,
            fill="#1e1610",
            outline="#7a5c3a",
            width=2,
            tags=(self._tag, self._DETAIL_TAG),
        )
        # 라벨 칩
        chx1, chy1 = self._sx(400, 180)
        chx2, chy2 = self._sx(500, 214)
        canvas.create_rectangle(
            chx1,
            chy1,
            chx2,
            chy2,
            fill=label_color(card.label),
            outline="",
            tags=(self._tag, self._DETAIL_TAG),
        )
        ccx, ccy = self._sx(450, 197)
        canvas.create_text(
            ccx,
            ccy,
            text=label_text(card.label),
            fill="#ffffff",
            font=self._font(14, bold=True),
            anchor="center",
            tags=(self._tag, self._DETAIL_TAG),
        )
        # 제목
        tx, ty = self._sx(540, 197)
        canvas.create_text(
            tx,
            ty,
            text=card.title,
            fill="#f0d080",
            font=self._font(28, bold=True),
            anchor="w",
            tags=(self._tag, self._DETAIL_TAG),
        )
        # 본문
        bx, by = self._sx(400, 250)
        canvas.create_text(
            bx,
            by,
            text=card.body,
            fill="#e8d8b8",
            font=self._font(16),
            anchor="nw",
            justify="left",
            width=int(self._sx(1120, 0)[0]),
            tags=(self._tag, self._DETAIL_TAG),
        )
        # 출처 (EP5)
        sx_, sy_ = self._sx(400, 720)
        canvas.create_text(
            sx_,
            sy_,
            text=f"출처: {card.source}",
            fill="#9a8a60",
            font=self._font(13),
            anchor="nw",
            justify="left",
            width=int(self._sx(1120, 0)[0]),
            tags=(self._tag, self._DETAIL_TAG),
        )

        # 한문 원문 토글 (H9) — source_original 이 있는 카드만.
        if card.source_original:
            self._render_hanmun_section(card)

        # 뒤로(그리드) 버튼
        self._render_back_button(self._DETAIL_TAG, on_click=self._back_to_grid)

    def _render_hanmun_section(self, card: CodexCard) -> None:
        canvas = self.app.canvas
        # 토글 버튼
        bx1, by1 = self._sx(400, 780)
        bx2, by2 = self._sx(620, 820)
        rect = canvas.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#2a2010",
            outline="#a88a5c",
            width=2,
            tags=(self._tag, self._DETAIL_TAG),
        )
        lcx, lcy = self._sx(510, 800)
        label = canvas.create_text(
            lcx,
            lcy,
            text=STRINGS["codex.source.original_toggle"],
            fill="#e0c878",
            font=self._font(14, bold=True),
            anchor="center",
            tags=(self._tag, self._DETAIL_TAG),
        )

        def _toggle(_e: Any) -> None:
            self._hanmun_open = not self._hanmun_open
            self._refresh_hanmun_body(card)

        for iid in (rect, label):
            try:
                canvas.tag_bind(iid, "<ButtonRelease-1>", _toggle)
            except Exception:  # noqa: BLE001
                pass
        self._refresh_hanmun_body(card)

    _HANMUN_TAG = "codex_hanmun_body"

    def _refresh_hanmun_body(self, card: CodexCard) -> None:
        canvas = self.app.canvas
        self._clear_tag(self._HANMUN_TAG)
        if not self._hanmun_open:
            return
        parts = [card.source_original or ""]
        if card.source_reading:
            parts.append(f"({card.source_reading})")
        if card.source_translation:
            parts.append(f"— {card.source_translation}")
        text = "  ".join(p for p in parts if p)
        hx, hy = self._sx(640, 800)
        canvas.create_text(
            hx,
            hy,
            text=text,
            fill="#f0e0b0",
            font=self._font(15),
            anchor="w",
            tags=(self._tag, self._DETAIL_TAG, self._HANMUN_TAG),
        )

    # ------------------------------------------------------------------
    # 공통
    # ------------------------------------------------------------------
    def _render_back_button(self, view_tag: str, on_click: Any = None) -> None:
        canvas = self.app.canvas
        bx1, by1 = self._sx(60, 60)
        bx2, by2 = self._sx(220, 110)
        rect = canvas.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#3a2a1c",
            outline="#a88a5c",
            width=2,
            tags=(self._tag, view_tag),
        )
        cx = (bx1 + bx2) / 2
        cy = (by1 + by2) / 2
        label = canvas.create_text(
            cx,
            cy,
            text=STRINGS["codex.back"],
            fill="#f0e0c0",
            font=self._font(18, bold=True),
            anchor="center",
            tags=(self._tag, view_tag),
        )
        handler = on_click or (lambda: self.app.goto("menu"))

        def _click(_e: Any) -> None:
            handler()

        for iid in (rect, label):
            try:
                canvas.tag_bind(iid, "<ButtonRelease-1>", _click)
            except Exception:  # noqa: BLE001
                pass

    def _clear_tag(self, tag: str) -> None:
        try:
            self.app.canvas.delete(tag)
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 키
    # ------------------------------------------------------------------
    def _on_escape(self, _event: Any) -> None:
        if self._detail_card is not None:
            self._back_to_grid()
        else:
            self.app.goto("menu")
