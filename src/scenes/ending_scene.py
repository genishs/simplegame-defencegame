"""엔딩 씬 (SCN-10).

DESIGN: 와이어프레임 §13 준수.
- 텍스트 자동 스크롤(엔딩 8패널 순차 표시).
- Space로 다음 패널 / ESC로 스킵.
- 마지막 컷 (향이가 양만춘 활을 든 무음 장면; PM DECISION-E03) 후 메뉴 복귀.
- 실제 이미지 없이 색 패널 + 텍스트로 대체 (아트 미완 상태).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.scenes.base_scene import BaseScene

if TYPE_CHECKING:
    from src.core.app import App

# 엔딩 패널 정의 (docs/story/07_ending.md 기반, 와이어프레임 §13 기준)
_PANELS: list[dict[str, object]] = [
    {
        "bg": "#141820",
        "title": "겨울이 왔다",
        "text": "어느새 서리가 내리고, 당군의 깃발이 사라졌다.",
        "label": "(사실)",
    },
    {
        "bg": "#101418",
        "title": "당 태종의 퇴각",
        "text": "이세민이 직접 거둔 군사를 돌렸다.\n안시성 하나가 30만 대군을 막은 것이다.",
        "label": "(사실)",
    },
    {
        "bg": "#181818",
        "title": "성벽의 침묵",
        "text": "성벽 위에 다시 고구려의 깃발이 펄럭였다.\n아무도 죽지 않은 88일이었다.",
        "label": "(사실)",
    },
    {
        "bg": "#1a1810",
        "title": "양만춘의 절",
        "text": "성주는 퇴각하는 당군을 향해 절했다.\n태종도 성주에게 비단을 하사했다 전한다.",
        "label": "[전승]",
    },
    {
        "bg": "#1c1814",
        "title": "백성들의 미소",
        "text": "성안의 백성들이 서로 손을 잡았다.\n[픽션·승인대기]",
        "label": "[픽션·승인대기]",
    },
    {
        "bg": "#1a160e",
        "title": "비단 한 필",
        "text": "당 태종이 보낸 비단 한 필.\n절개를 지킨 성주에게 바치는 경의였다.",
        "label": "[전승]",
    },
    {
        "bg": "#100c08",
        "title": "향이의 활",
        "text": "향이가 성주의 활을 조용히 들어 올렸다.\n약속은 끝났다. [픽션·승인대기]",
        "label": "[픽션·승인대기]",
        "is_last_cut": True,  # DECISION-E03 마지막 무음 컷
    },
    {
        "bg": "#000000",
        "title": "",
        "text": "안시성: 88일의 약속\n\n645년 ~ 645년",
        "label": "(사실)",
        "is_finale": True,
    },
]


class EndingScene(BaseScene):
    """엔딩 씬 — 텍스트 자동 스크롤."""

    SCENE_TAG = "ending"

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self._current_panel: int = 0
        self._panel_ids: list[int] = []
        self._auto_timer_id: str | None = None

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def build(self) -> None:
        self._current_panel = 0
        self._draw_panel(self._current_panel)
        # 키 바인딩
        self.app.root.bind("<space>", self._on_space)
        self.app.root.bind("<Escape>", self._on_escape)
        # 자동 진행 (5초마다)
        self._schedule_auto()

    def teardown(self) -> None:
        super().teardown()
        if self._auto_timer_id is not None:
            try:
                self.app.root.after_cancel(self._auto_timer_id)
            except Exception:  # noqa: BLE001
                pass
        try:
            self.app.root.unbind("<space>")
            self.app.root.unbind("<Escape>")
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 패널 렌더링
    # ------------------------------------------------------------------

    def _draw_panel(self, idx: int) -> None:
        if idx >= len(_PANELS):
            self._go_to_menu()
            return

        canvas = self.app.canvas
        scaler = self.app.scaler
        tag = self._tag
        panel = _PANELS[idx]

        # 이전 패널 아이템 삭제
        for iid in self._panel_ids:
            try:
                canvas.delete(iid)
            except Exception:  # noqa: BLE001
                pass
        self._panel_ids = []

        w = canvas.winfo_width() or scaler.canvas_w
        h = canvas.winfo_height() or scaler.canvas_h

        bg_fill = str(panel.get("bg", "#000000"))
        bg = canvas.create_rectangle(0, 0, w, h, fill=bg_fill, outline="", tags=(tag,))
        self._panel_ids.append(bg)

        def sx(bx: float, by: float) -> tuple[float, float]:
            return scaler.to_screen(bx, by)

        def fpt(pt: int) -> int:
            return scaler.font_pt(pt)

        def font(pt: int, bold: bool = False) -> tuple[str, int, str]:
            style = "bold" if bold else "normal"
            family = _family_bold() if bold else _family_regular()
            return (family, fpt(pt), style)

        # 제목
        title = str(panel.get("title", ""))
        if title:
            tx, ty = sx(960, 400)
            tid = canvas.create_text(
                tx, ty, text=title, fill="#e8d6a8", font=font(48, bold=True), anchor="center", tags=(tag,)
            )
            self._panel_ids.append(tid)

        # 본문 텍스트
        text = str(panel.get("text", ""))
        if text:
            vx, vy = sx(960, 560)
            vid = canvas.create_text(
                vx,
                vy,
                text=text,
                fill="#c8c0a8",
                font=font(24),
                anchor="center",
                justify="center",
                tags=(tag,),
            )
            self._panel_ids.append(vid)

        # 레이블 칩 ([사실]/[전승]/[픽션·승인대기])
        label = str(panel.get("label", ""))
        if label and "픽션" in label:
            lx, ly = sx(80, 860)
            lid = canvas.create_text(
                lx, ly, text=label, fill="#e8c040", font=font(14), anchor="nw", tags=(tag,)
            )
            self._panel_ids.append(lid)

        # 마지막 컷 특별 처리 (DECISION-E03: 무음 장면)
        if panel.get("is_last_cut"):
            sx2, sy2 = sx(960, 700)
            silent_id = canvas.create_text(
                sx2, sy2, text="—", fill="#555555", font=font(28), anchor="center", tags=(tag,)
            )
            self._panel_ids.append(silent_id)

        # 피날레 특별 처리
        if panel.get("is_finale"):
            fx, fy = sx(960, 700)
            finid = canvas.create_text(
                fx,
                fy,
                text="[Space] 메인 메뉴로",
                fill="#666655",
                font=font(18),
                anchor="center",
                tags=(tag,),
            )
            self._panel_ids.append(finid)
        else:
            # 진행 힌트
            hx, hy = sx(1800, 1040)
            hid = canvas.create_text(
                hx, hy, text="[Space] 다음", fill="#555550", font=font(14), anchor="se", tags=(tag,)
            )
            self._panel_ids.append(hid)

        # 패널 번호 표시 (작게)
        px, py = sx(960, 1060)
        pid = canvas.create_text(
            px,
            py,
            text=f"{idx + 1} / {len(_PANELS)}",
            fill="#333333",
            font=font(12),
            anchor="center",
            tags=(tag,),
        )
        self._panel_ids.append(pid)

    # ------------------------------------------------------------------
    # 이벤트 핸들러
    # ------------------------------------------------------------------

    def _on_space(self, _event: object) -> None:
        if self._auto_timer_id is not None:
            try:
                self.app.root.after_cancel(self._auto_timer_id)
            except Exception:  # noqa: BLE001
                pass
            self._auto_timer_id = None
        self._advance()

    def _on_escape(self, _event: object) -> None:
        self._go_to_menu()

    def _advance(self) -> None:
        self._current_panel += 1
        if self._current_panel >= len(_PANELS):
            self._go_to_menu()
        else:
            self._draw_panel(self._current_panel)
            if not _PANELS[self._current_panel].get("is_finale"):
                self._schedule_auto()

    def _schedule_auto(self) -> None:
        """5초 후 자동으로 다음 패널."""
        panel = _PANELS[self._current_panel] if self._current_panel < len(_PANELS) else {}
        if panel.get("is_finale") or panel.get("is_last_cut"):
            return  # 마지막 컷은 자동 진행 없음
        self._auto_timer_id = self.app.root.after(5000, self._on_auto_advance)

    def _on_auto_advance(self) -> None:
        self._auto_timer_id = None
        self._advance()

    def _go_to_menu(self) -> None:
        self.app.goto("menu")
