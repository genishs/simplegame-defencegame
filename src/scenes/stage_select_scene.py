"""스테이지 선택 씬 (SCN-02).

DESIGN: 와이어프레임 §5 준수.
- 5스테이지 카드 가로 배치 (1열×5개, x=80+360n).
- 잠금 상태: app.player_data.unlocked_stages (없으면 stage_01만 해금).
- 클릭 → app.goto("battle", stage_id=N).
- ESC → 메인 메뉴.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.scenes.base_scene import BaseScene

if TYPE_CHECKING:
    from src.core.app import App

# 스테이지 메타데이터 (docs/story/08_ui_strings.md §2.1)
_STAGES: list[dict[str, Any]] = [
    {
        "id": "stage_01",
        "name": "1. 요동성의 첫눈",
        "subtitle": "함락 직전의 한 시간",
        "bg_color": "#3a5030",
    },
    {
        "id": "stage_02",
        "name": "2. 백암성의 항복",
        "subtitle": "사람을 살리는 길",
        "bg_color": "#305050",
    },
    {
        "id": "stage_03",
        "name": "3. 개모성의 횃불",
        "subtitle": "어둠을 견딘 자",
        "bg_color": "#201828",
    },
    {
        "id": "stage_04",
        "name": "4. 안시성 외곽",
        "subtitle": "외성은 내어준다",
        "bg_color": "#503820",
    },
    {
        "id": "stage_05",
        "name": "5. 안시성 토산",
        "subtitle": "88일의 약속",
        "bg_color": "#3a3028",
    },
]

_STRINGS: dict[str, str] = {
    "stage_select.title": "스테이지 선택",
    "stage_select.back": "돌아가기",
    "stage_select.play": "도전하기",
    "stage_select.locked": "잠금",
    "stage_select.cleared": "클리어",
}

# 와이어프레임 §5 카드 레이아웃
_CARD_W = 320.0
_CARD_H = 700.0
_CARD_Y = 160.0
_CARD_SPACING = 360.0
_CARD_X0 = 80.0


class StageSelectScene(BaseScene):
    """스테이지 선택 씬."""

    SCENE_TAG = "stage_select"

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self._selected_idx: int = 0

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def build(self) -> None:
        canvas = self.app.canvas
        scaler = self.app.scaler
        w = canvas.winfo_width() or scaler.canvas_w
        h = canvas.winfo_height() or scaler.canvas_h
        tag = self._tag
        s = scaler

        def sx(bx: float, by: float) -> tuple[float, float]:
            return s.to_screen(bx, by)

        def fpt(pt: int) -> int:
            return s.font_pt(pt)

        def font(pt: int, bold: bool = False) -> tuple[str, int, str]:
            style = "bold" if bold else "normal"
            family = _family_bold() if bold else _family_regular()
            return (family, fpt(pt), style)

        # 배경
        canvas.create_rectangle(0, 0, w, h, fill="#101820", outline="", tags=(tag, "bg"))

        # 헤더 배경 (STS-01)
        hx1, hy1 = sx(0, 0)
        hx2, hy2 = sx(1920, 120)
        canvas.create_rectangle(hx1, hy1, hx2, hy2, fill="#0a0c14", outline="#2a3040", tags=(tag, "header"))

        # 돌아가기 버튼 (STS-02)
        bk_rect, bk_text = self._make_button(
            canvas,
            40,
            30,
            160,
            60,
            _STRINGS["stage_select.back"],
            lambda: self.app.goto("menu"),
            s,
            tag,
            font(18),
        )

        # 화면 제목 (STS-03)
        tx, ty = sx(960, 60)
        canvas.create_text(
            tx,
            ty,
            text=_STRINGS["stage_select.title"],
            fill="#e8d6a8",
            font=font(36, bold=True),
            anchor="center",
            tags=(tag,),
        )

        # 해금 상태 조회
        unlocked = self._get_unlocked_stages()
        completed = self._get_completed_stages()

        # 5개 스테이지 카드 (STS-06)
        for i, stage in enumerate(_STAGES):
            cx = _CARD_X0 + i * _CARD_SPACING
            self._draw_stage_card(canvas, cx, _CARD_Y, stage, i, unlocked, completed, s, tag)

        # ESC 바인딩
        self.app.root.bind("<Escape>", lambda _e: self.app.goto("menu"))

    def teardown(self) -> None:
        super().teardown()
        try:
            self.app.root.unbind("<Escape>")
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 카드 그리기
    # ------------------------------------------------------------------

    def _draw_stage_card(
        self,
        canvas: Any,
        bx: float,
        by: float,
        stage: dict[str, Any],
        idx: int,
        unlocked: set[str],
        completed: dict[str, int],
        scaler: Any,
        tag: str,
    ) -> None:
        is_locked = stage["id"] not in unlocked
        is_cleared = stage["id"] in completed
        stars = completed.get(stage["id"], 0)

        def sx(x: float, y: float) -> tuple[float, float]:
            return scaler.to_screen(x, y)

        def font(pt: int, bold: bool = False) -> tuple[str, int, str]:
            style = "bold" if bold else "normal"
            family = _family_bold() if bold else _family_regular()
            return (family, scaler.font_pt(pt), style)

        card_fill = "#0e1018" if is_locked else "#1c1810"
        card_outline = "#333333" if is_locked else "#5a4a30"

        # 카드 배경 (STC-a)
        cx1, cy1 = sx(bx, by)
        cx2, cy2 = sx(bx + _CARD_W, by + _CARD_H)
        canvas.create_rectangle(
            cx1, cy1, cx2, cy2, fill=card_fill, outline=card_outline, width=2, tags=(tag,)
        )

        # 썸네일 영역 (STC-b) - 색상 박스로 대체
        thumb_fill = "#222222" if is_locked else stage["bg_color"]
        tx1, ty1 = sx(bx + 16, by + 16)
        tx2, ty2 = sx(bx + _CARD_W - 16, by + 216)
        canvas.create_rectangle(tx1, ty1, tx2, ty2, fill=thumb_fill, outline="#3a3030", tags=(tag,))

        # 썸네일 위 번호
        tnx, tny = sx(bx + _CARD_W / 2, by + 116)
        canvas.create_text(
            tnx,
            tny,
            text=str(idx + 1),
            fill="#ffffff" if not is_locked else "#444444",
            font=font(48, bold=True),
            anchor="center",
            tags=(tag,),
        )

        # 스테이지 이름 (STC-c)
        nmx, nmy = sx(bx + 16, by + 250)
        canvas.create_text(
            nmx,
            nmy,
            text=stage["name"],
            fill="#e8d6a8" if not is_locked else "#555555",
            font=font(20, bold=True),
            anchor="nw",
            tags=(tag,),
        )

        # 부제 (STC-d)
        sbx, sby = sx(bx + 16, by + 320)
        canvas.create_text(
            sbx,
            sby,
            text=stage["subtitle"],
            fill="#a89878" if not is_locked else "#444444",
            font=font(15),
            anchor="nw",
            tags=(tag,),
        )

        # 별 평가 (STC-e)
        for star_i in range(3):
            star_bx = bx + 30 + star_i * 90
            star_x, star_y = sx(star_bx, by + 440)
            star_fill = "#e8c040" if (star_i < stars) else "#333333"
            canvas.create_text(
                star_x,
                star_y,
                text="★",
                fill=star_fill,
                font=font(28, bold=True),
                anchor="center",
                tags=(tag,),
            )

        # 클리어/잠금 라벨 (STC-f)
        if is_locked:
            lbl_text = _STRINGS["stage_select.locked"]
            lbl_clr = "#cc4444"
        elif is_cleared:
            lbl_text = _STRINGS["stage_select.cleared"]
            lbl_clr = "#44cc88"
        else:
            lbl_text = ""
            lbl_clr = "#888888"

        if lbl_text:
            lx, ly = sx(bx + _CARD_W / 2, by + 510)
            canvas.create_text(
                lx, ly, text=lbl_text, fill=lbl_clr, font=font(16, bold=True), anchor="center", tags=(tag,)
            )

        # 도전하기 버튼 (STC-g)
        if not is_locked:
            stage_id = stage["id"]
            self._make_button(
                canvas,
                bx + 16,
                by + 600,
                _CARD_W - 32,
                60,
                _STRINGS["stage_select.play"],
                lambda sid=stage_id: self.app.goto("battle"),
                scaler,
                tag,
                font(18),
            )
        else:
            # 잠금 버튼 (비활성)
            lbx1, lby1 = scaler.to_screen(bx + 16, by + 600)
            lbx2, lby2 = scaler.to_screen(bx + _CARD_W - 16, by + 660)
            canvas.create_rectangle(
                lbx1, lby1, lbx2, lby2, fill="#222222", outline="#444444", width=2, tags=(tag,)
            )
            lcx, lcy = ((lbx1 + lbx2) / 2, (lby1 + lby2) / 2)
            canvas.create_text(
                lcx, lcy, text="🔒 잠금", fill="#666666", font=font(16), anchor="center", tags=(tag,)
            )

    # ------------------------------------------------------------------
    # 헬퍼
    # ------------------------------------------------------------------

    def _get_unlocked_stages(self) -> set[str]:
        """해금된 스테이지 ID 집합. player_data가 없으면 stage_01만."""
        try:
            pd = getattr(self.app, "player_data", None)
            if pd is not None:
                return set(pd.unlocked_stages)
        except Exception:  # noqa: BLE001
            pass
        return {"stage_01"}

    def _get_completed_stages(self) -> dict[str, int]:
        """완료된 스테이지별 별 수 dict. player_data가 없으면 빈 dict."""
        try:
            pd = getattr(self.app, "player_data", None)
            if pd is not None and hasattr(pd, "stage_stars"):
                return dict(pd.stage_stars)
        except Exception:  # noqa: BLE001
            pass
        return {}

    def _make_button(
        self,
        canvas: Any,
        bx: float,
        by: float,
        bw: float,
        bh: float,
        label: str,
        on_click: Any,
        scaler: Any,
        tag: str,
        font_tuple: tuple[str, int, str],
    ) -> tuple[int, int]:
        x1, y1 = scaler.to_screen(bx, by)
        x2, y2 = scaler.to_screen(bx + bw, by + bh)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        rect_id = canvas.create_rectangle(
            x1, y1, x2, y2, fill="#3a2a1c", outline="#a88a5c", width=2, tags=(tag,)
        )
        text_id = canvas.create_text(
            cx, cy, text=label, fill="#f0e0c0", font=font_tuple, anchor="center", tags=(tag,)
        )

        def _hover_enter(_e: Any, rid: int = rect_id) -> None:
            canvas.itemconfig(rid, fill="#5a4a2c", outline="#d4a84a")

        def _hover_leave(_e: Any, rid: int = rect_id) -> None:
            canvas.itemconfig(rid, fill="#3a2a1c", outline="#a88a5c")

        def _press(_e: Any, rid: int = rect_id) -> None:
            canvas.itemconfig(rid, fill="#2a1a0c")

        def _release(_e: Any) -> None:
            on_click()

        for iid in (rect_id, text_id):
            canvas.tag_bind(iid, "<Enter>", _hover_enter)
            canvas.tag_bind(iid, "<Leave>", _hover_leave)
            canvas.tag_bind(iid, "<ButtonPress-1>", _press)
            canvas.tag_bind(iid, "<ButtonRelease-1>", _release)

        return rect_id, text_id
