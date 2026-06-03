"""튜토리얼 씬 (Phase 4, Issue #26).

DESIGN:
- 8 단계 인터랙티브 튜토리얼 (DECISION-PL-P4-001).
- 단계별 build()/teardown() 분리, ``self._step`` 으로 상태 머신 관리.
- 인터랙티브 단계(2,3,5,6): 사용자 입력 대기 + 표시 시간 상한 후 자동 진행.
- 패시브 단계(1,4,7,8): 자동/수동 "다음" 버튼 진행.
- 단계 4: mock spawn (``tang_soldier × 2 @ 1.5s``, DECISION-PL-P4-007) —
  실제 stage_01 JSON 을 변형하지 않고 단순 콜백 카운트만.
- ESC 또는 우상단 종료 버튼 → 스킵 확인 다이얼로그.
- 단계 8 완주 → ``save_slot.tutorial_completed = True`` 기록 후 stage_select.

DECISION (Dev Lead, P4):
- HUD 강조 오버레이는 별도 widget 클래스 미사용 — Canvas item 직접 (DL-P4-002).
- mock wave 는 self._mock_wave_dt 누적으로 단순 spawn 콜백 호출
  (전투 시스템 통합 없음 — 인지 부하 우선).
- ui_strings placeholder 는 키와 같은 한글 한 줄 (Design Lead 라운드가 채움).

DECISION (Dev Lead, P4 디버그, 2026-05-20 — Issue #49 fix):
- **DECISION-DL-P4D-001**: 동그라미 안 콘텐츠 비어 있는 결함. 튜토리얼 씬이
  BattleScene 을 통합하지 않아 spotlight 가 가리키는 HUD 대상이 실제로 존재하지
  않았다. 사용자가 "여기를 누르시오" 안내만 보고 동그라미 안에 아무것도 없는
  현상을 보고. 인지부하 우선 원칙(DECISION-DL-P4-002) 을 유지하면서, 각 spotlight
  위치에 **mock placeholder 콘텐츠**(곡식 카운터·배치 빈 칸·영웅 placeholder·
  일시정지 버튼) 를 직접 그려 동그라미가 의미를 가지도록 한다.
- **DECISION-DL-P4D-002**: Canvas z-order 는 생성 순서 = 그리기 순서. 마스크가
  먼저 그려지고 mock 콘텐츠가 그 위에 그려져 spotlight 영역에 "컷아웃" 효과를
  내며, ring/arrow/label 은 마지막에 그려져 최상단에 위치한다.
- 게임플레이 균형 영향 0: stage_01 데이터 변형 없음, mock wave 카운트 그대로,
  save_slot 스키마 변경 없음.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.core.logger import get_logger
from src.core.save_slot import (
    load_save_slot,
    mark_tutorial_completed,
    mark_tutorial_dismissed,
    save_save_slot,
)
from src.scenes.base_scene import BaseScene

if TYPE_CHECKING:
    from src.core.app import App


# ---------------------------------------------------------------------------
# UI 문자열 (placeholder)
# ---------------------------------------------------------------------------
# Design Lead 라운드가 같은 키를 한국어 텍스트로 채운다. 머지 시 SCM 정리.
_STRINGS: dict[str, str] = {
    # §20.1 메뉴 / 스킵 / 완료
    "menu.tutorial.button": "튜토리얼",
    "tutorial.skip.button": "튜토리얼 종료",
    "tutorial.skip.confirm.title": "튜토리얼을 종료하시겠소?",
    "tutorial.skip.confirm.body": "지금 종료하면 스테이지 선택 화면으로 이동합니다.",
    "tutorial.skip.confirm.yes": "예, 종료",
    "tutorial.skip.confirm.no": "아니오, 계속",
    "tutorial.skip.dont_show_again": "다시 보지 않기",
    "tutorial.complete.cta": "Stage 1로 가기",
    # §20.2 단계별 본문
    "tutorial.intro.title": "튜토리얼",
    "tutorial.intro.body": "8단계로 익혀 봅시다",
    "tutorial.step1.title": "1. 88일의 약속",
    "tutorial.step1.body": ("645년 봄, 당의 깃발이 요동으로 향했소. " "양만춘과 함께 88일을 견디시오."),
    "tutorial.step1.cta": "다음",
    "tutorial.step2.title": "2. 곡식",
    "tutorial.step2.body": "위에 곡식이 있소. 이걸로 병사를 모집하시오.",
    "tutorial.step2.cta": "상단의 곡식을 누르시오",
    "tutorial.step3.title": "3. 아군 배치",
    "tutorial.step3.body": "왼쪽 패널에서 궁수를 고른 뒤 녹색 빈 칸에 배치하시오.",
    "tutorial.step3.cta": "좌측 궁수 패널을 누르고, 녹색 칸을 누르시오",
    "tutorial.step4.title": "4. 첫 진군",
    "tutorial.step4.body": "당군이 옵니다. 양만춘과 병사들이 막을 것이오.",
    "tutorial.step4.cta": "다음",
    "tutorial.step5.title": "5. 영웅",
    "tutorial.step5.body": "양만춘은 자동입니다. M 키를 누르면 직접 조작 모드로 전환됩니다.",
    "tutorial.step5.cta": "M 키를 누르시오 (영웅 컨트롤 모드 토글)",
    "tutorial.step6.title": "6. 일시정지",
    "tutorial.step6.body": "Space 키로 잠시 멈출 수 있소. 다시 누르면 재개됩니다.",
    "tutorial.step6.cta": "Space 를 한 번 누르면 정지, 다시 누르면 재개",
    "tutorial.step7.title": "7. 보상",
    "tutorial.step7.body": "진군을 막아내면 곡식과 명성을 얻습니다.",
    "tutorial.step7.cta": "다음",
    "tutorial.step8.title": "8. 출정",
    "tutorial.step8.body": "이제 안시성으로 가는 첫 걸음, 요동성에서 시작합시다.",
    # §20.3 HUD 화살표 보조 라벨
    "tutorial.hud_arrow.resource": "여기",
    "tutorial.hud_arrow.buildzone": "여기에 배치",
    "tutorial.hud_arrow.hero": "양만춘",
    # Issue #67/#68/#69 (DECISION-DL-P4D-012/013/014): 인터랙티브 단계 추가 안내.
    "tutorial.step3.archer_panel": "고구려 궁수\n곡식 50",
    "tutorial.step5.manual_on": "직접 조작 모드 ON\n(2초 뒤 다음으로 진행)",
    "tutorial.step5.manual_off": "자동 모드",
    "tutorial.step6.paused_overlay": "■ 일시정지 ■\n(Space 를 다시 누르면 재개)",
    "tutorial.step6.resumed": "재개됨",
}


# ---------------------------------------------------------------------------
# 색상 팔레트 (dialog.py 와 일치)
# ---------------------------------------------------------------------------
_CLR_DIM = "#000000"
_CLR_BG = "#0c0a08"
_CLR_PANEL = "#1e1610"
_CLR_PANEL_OUTLINE = "#7a5c3a"
_CLR_BTN_NORMAL = "#3a2a1c"
_CLR_BTN_HOVER = "#5a4a2c"
_CLR_BTN_PRESS = "#2a1a0c"
_CLR_BTN_OUTLINE = "#a88a5c"
_CLR_BTN_HOVER_OUTLINE = "#d4a84a"
_CLR_BTN_DISABLED = "#252018"
_CLR_BTN_DISABLED_OUTLINE = "#4a4030"
_CLR_BTN_DISABLED_TEXT = "#666052"
_CLR_TEXT = "#f0e0c0"
_CLR_TEXT_BODY = "#d8c8a0"
_CLR_TITLE = "#e8d080"
_CLR_ARROW = "#f0c040"
_CLR_SPOT_OUTLINE = "#f0c040"

# Issue #73 (DECISION-DL-P5C-009): 정적 전장 backdrop 팔레트.
_CLR_BD_SKY = "#2a2030"  # 상단 하늘(야영 분위기)
_CLR_BD_FIELD = "#1d2418"  # 평지(적 진군 라인)
_CLR_BD_WALL = "#3a2c1c"  # 성벽
_CLR_BD_WALL_TOP = "#4a3826"  # 성벽 상단 테두리
_CLR_BD_GATE = "#5a3a1a"  # 성문(코어)
_CLR_BD_ALLY = "#3a6a8c"  # 아군 placeholder(청)
_CLR_BD_ENEMY = "#7a2a22"  # 적 placeholder(적·흑)

# 단계 모드.
MODE_PASSIVE = "P"
MODE_INTERACTIVE = "I"

# 단계 정의: (step_no, mode, key_prefix, time_limit_s, hud_target_key)
# hud_target_key 는 _HUD_TARGETS 의 키. None 이면 강조 없음.
# Issue #67/#68/#69 (DECISION-DL-P4D-012/013/014): 인터랙티브 단계의 자동
# 진행 시간 상한을 inf 로 변경 — 사용자가 실제로 입력할 때까지 대기. fallback
# 자동 진행이 결함 #67/#68/#69 의 "누르지 않아도 넘어감" 현상을 일으켰다.
_STEP_DEFS: list[tuple[int, str, str, float, str | None]] = [
    (1, MODE_PASSIVE, "tutorial.step1", float("inf"), None),
    (2, MODE_INTERACTIVE, "tutorial.step2", float("inf"), "resource"),
    (3, MODE_INTERACTIVE, "tutorial.step3", float("inf"), "buildzone"),
    (4, MODE_PASSIVE, "tutorial.step4", 45.0, None),
    (5, MODE_INTERACTIVE, "tutorial.step5", float("inf"), "hero"),
    (6, MODE_INTERACTIVE, "tutorial.step6", float("inf"), "pause"),
    (7, MODE_PASSIVE, "tutorial.step7", float("inf"), None),
    (8, MODE_PASSIVE, "tutorial.step8", float("inf"), None),
]

# HUD 강조 좌표 (베이스 1920×1080, §5.2 권고치)
_HUD_TARGETS: dict[str, tuple[float, float, float]] = {
    # name -> (cx, cy, radius)
    "resource": (200.0, 50.0, 80.0),
    "buildzone": (740.0, 640.0, 100.0),
    "hero": (960.0, 540.0, 90.0),
    "pause": (1720.0, 50.0, 60.0),
}

# 단계 4 mock wave (DECISION-PL-P4-007).
_MOCK_WAVE_COUNT = 2
_MOCK_WAVE_INTERVAL = 1.5

# 단계 5 영웅 이동 시연 (Issue #74 / DECISION-DL-P5C-010).
_STEP5_DEMO_DURATION_S = 2.2  # M 키 후 시연 + 인지 시간 (이후 자동 진행)
_STEP5_DEMO_AMPLITUDE = 70.0  # 좌우 왕복 진폭 (베이스 px)
_STEP5_DEMO_PERIOD_S = 1.1  # 왕복 1주기 시간 (초)


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _font(scaler: Any, pt: int, bold: bool = False) -> tuple[str, int, str]:
    style = "bold" if bold else "normal"
    family = _family_bold() if bold else _family_regular()
    size = scaler.font_pt(pt) if scaler is not None else pt
    return (family, size, style)


def _sx(scaler: Any, x: float, y: float) -> tuple[float, float]:
    if scaler is None:
        return x, y
    return scaler.to_screen(x, y)


# ---------------------------------------------------------------------------
# SkipConfirmDialog
# ---------------------------------------------------------------------------


class SkipConfirmDialog:
    """튜토리얼 스킵 확인 다이얼로그 (§3.2).

    체크박스 "다시 보지 않기" + 예/아니오 버튼.
    ``ResultDialog`` 패턴을 따르되 구성 요소가 적어 자체 구현.
    """

    TAG = "tutorial_skip_dialog"

    def __init__(
        self,
        canvas: Any,
        scaler: Any,
        on_yes: Callable[[bool], None],
        on_no: Callable[[], None],
    ) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._on_yes = on_yes
        self._on_no = on_no
        self._ids: list[int] = []
        self._visible: bool = False
        self._dont_show_again: bool = False
        self._checkbox_rect_id: int | None = None
        self._checkbox_mark_id: int | None = None

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def dont_show_again(self) -> bool:
        return self._dont_show_again

    def show(self) -> None:
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

        # 패널
        px1, py1 = sx(560, 340)
        px2, py2 = sx(1360, 740)
        panel = c.create_rectangle(
            px1, py1, px2, py2, fill=_CLR_PANEL, outline=_CLR_PANEL_OUTLINE, width=3, tags=(tag,)
        )
        self._ids.append(panel)

        # 타이틀
        tcx, tcy = sx(960, 400)
        title = c.create_text(
            tcx,
            tcy,
            text=_STRINGS["tutorial.skip.confirm.title"],
            fill=_CLR_TITLE,
            font=_font(s, 32, bold=True),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(title)

        # 본문
        bcx, bcy = sx(960, 470)
        body = c.create_text(
            bcx,
            bcy,
            text=_STRINGS["tutorial.skip.confirm.body"],
            fill=_CLR_TEXT_BODY,
            font=_font(s, 18),
            anchor="center",
            tags=(tag,),
        )
        self._ids.append(body)

        # 체크박스
        self._draw_checkbox(620, 560, s, tag)

        # 버튼들
        self._add_button(660, 640, 240, 56, _STRINGS["tutorial.skip.confirm.yes"], self._handle_yes, s, tag)
        self._add_button(1020, 640, 240, 56, _STRINGS["tutorial.skip.confirm.no"], self._handle_no, s, tag)

    def hide(self) -> None:
        if not self._visible:
            return
        self._visible = False
        for i in self._ids:
            try:
                self._canvas.delete(i)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []
        self._checkbox_rect_id = None
        self._checkbox_mark_id = None

    # ------------------------------------------------------------------

    def _draw_checkbox(self, bx: float, by: float, s: Any, tag: str) -> None:
        c = self._canvas
        x1, y1 = _sx(s, bx, by)
        x2, y2 = _sx(s, bx + 30, by + 30)
        rect_id = c.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="#2a1a0c",
            outline=_CLR_BTN_OUTLINE,
            width=2,
            tags=(tag, "checkbox_rect"),
        )
        self._ids.append(rect_id)
        self._checkbox_rect_id = rect_id

        # 체크 표시 (초기 hidden)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        mark_id = c.create_text(cx, cy, text="✔", fill=_CLR_TITLE, font=_font(s, 22, bold=True), tags=(tag,))
        self._ids.append(mark_id)
        self._checkbox_mark_id = mark_id
        try:
            c.itemconfig(mark_id, state="hidden")
        except Exception:  # noqa: BLE001
            pass

        # 라벨
        lx, ly = _sx(s, bx + 50, by + 15)
        label_id = c.create_text(
            lx,
            ly,
            text=_STRINGS["tutorial.skip.dont_show_again"],
            fill=_CLR_TEXT_BODY,
            font=_font(s, 18),
            anchor="w",
            tags=(tag,),
        )
        self._ids.append(label_id)

        def _toggle(_e: Any) -> None:
            self.toggle_dont_show_again()

        try:
            c.tag_bind(rect_id, "<ButtonRelease-1>", _toggle)
            c.tag_bind(label_id, "<ButtonRelease-1>", _toggle)
        except Exception:  # noqa: BLE001
            pass

    def toggle_dont_show_again(self) -> None:
        """체크박스 토글 — 테스트 친화 공개 API."""
        self._dont_show_again = not self._dont_show_again
        if self._checkbox_mark_id is not None:
            try:
                self._canvas.itemconfig(
                    self._checkbox_mark_id,
                    state="normal" if self._dont_show_again else "hidden",
                )
            except Exception:  # noqa: BLE001
                pass

    def _add_button(
        self,
        bx: float,
        by: float,
        bw: float,
        bh: float,
        label: str,
        on_click: Callable[[], None],
        s: Any,
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
            cx,
            cy,
            text=label,
            fill=_CLR_TEXT,
            font=_font(s, 20, bold=True),
            anchor="center",
            tags=(tag,),
        )
        self._ids.extend([rect_id, text_id])

        def _enter(_e: Any) -> None:
            try:
                c.itemconfig(rect_id, fill=_CLR_BTN_HOVER, outline=_CLR_BTN_HOVER_OUTLINE)
            except Exception:  # noqa: BLE001
                pass

        def _leave(_e: Any) -> None:
            try:
                c.itemconfig(rect_id, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE)
            except Exception:  # noqa: BLE001
                pass

        def _press(_e: Any) -> None:
            try:
                c.itemconfig(rect_id, fill=_CLR_BTN_PRESS)
            except Exception:  # noqa: BLE001
                pass

        def _release(_e: Any) -> None:
            on_click()

        for iid in (rect_id, text_id):
            try:
                c.tag_bind(iid, "<Enter>", _enter)
                c.tag_bind(iid, "<Leave>", _leave)
                c.tag_bind(iid, "<ButtonPress-1>", _press)
                c.tag_bind(iid, "<ButtonRelease-1>", _release)
            except Exception:  # noqa: BLE001
                pass

    def _handle_yes(self) -> None:
        self._on_yes(self._dont_show_again)

    def _handle_no(self) -> None:
        self._on_no()


# ---------------------------------------------------------------------------
# TutorialScene
# ---------------------------------------------------------------------------


class TutorialScene(BaseScene):
    """8 단계 인터랙티브 튜토리얼 (Issue #26)."""

    SCENE_TAG = "tutorial"

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self._log = get_logger(__name__)

        # 상태 머신
        self._step: int = 1  # 1 ~ 8
        self._step_elapsed: float = 0.0  # 현재 단계 누적 표시 시간
        self._step_ids: list[int] = []  # 현재 단계 전용 캔버스 아이템
        self._cta_enabled: bool = False  # 단계 4 같은 조건부 CTA 활성화 플래그
        self._step_completed: bool = False  # 한 단계의 진행 조건 충족 표시

        # 단계 6 — Space 토글 사이클 (한 번 누름 + 다시 누름)
        self._pause_toggle_count: int = 0

        # 단계 4 mock wave
        self._mock_wave_dt: float = 0.0
        self._mock_spawn_count: int = 0
        self._mock_wave_done: bool = False

        # 스킵 다이얼로그
        self._skip_dialog: SkipConfirmDialog | None = None

        # 영구 상태
        self._save_slot_path: Any = None  # 테스트 override 용
        # M 키 토글 검증 — 메뉴 진입 시 False 로 초기화
        self._m_pressed: bool = False

        # Issue #68 (DECISION-DL-P4D-013): 단계 5 M 키 인터랙션 — 토글 ON 표시
        # 후 짧은 지연 뒤 자동 진행 (사용자가 토글 결과를 인지하도록).
        self._step5_manual_on: bool = False
        self._step5_manual_on_at: float = -1.0  # M 키 누른 시각 (step_elapsed 기준)
        # Issue #74 (DECISION-DL-P5C-010): M 키 후 영웅 placeholder 이동 시연.
        # 좌우로 짧게 왕복하는 데모 애니메이션을 보여준 뒤 다음 단계로 진행.
        self._step5_hero_ids: list[int] = []  # 이동시킬 placeholder 아이템(원/이름/링)
        self._step5_hero_base_cx: float = 0.0  # 영웅 기준 x (베이스 좌표)
        self._step5_hero_cy: float = 0.0  # 영웅 y (베이스 좌표)

        # Issue #69 (DECISION-DL-P4D-014): 단계 6 Space 일시정지 — 첫 Space 시
        # paused overlay 표시, 두 번째 Space 에 다음 단계로 진행.
        self._step6_paused: bool = False
        self._step6_overlay_ids: list[int] = []

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def build(self) -> None:
        # BGM — 튜토리얼 진입 시 재생 (Phase 5.1, Issue #30)
        self.app.sound.play_bgm("bgm.tutorial", loop=True, fade_in=1.0)

        canvas = self.app.canvas
        scaler = self.app.scaler
        w = canvas.winfo_width() if hasattr(canvas, "winfo_width") else getattr(scaler, "canvas_w", 1920)
        h = canvas.winfo_height() if hasattr(canvas, "winfo_height") else getattr(scaler, "canvas_h", 1080)

        # 배경 (단계 공유)
        canvas.create_rectangle(0, 0, w, h, fill=_CLR_BG, outline="", tags=(self._tag, "bg"))

        # Issue #73 (DECISION-DL-P5C-009): 실 전장 컨텍스트 배경.
        # rc.7 검수 결함: "튜토리얼 대상만 보이고 나머지는 깜깜해 게임 맥락을 알 수
        # 없다". 전체 BattleScene 통합은 과도하므로, 정적 전장 backdrop(지형 밴드 +
        # 성벽/성문 + 아군·적 placeholder)을 한 번 그려 게임 컨텍스트를 보여준다.
        # 각 단계의 spotlight dim 마스크가 이 위에 덮여 강조 대상만 밝게 남는다.
        self._draw_battle_backdrop(scaler)

        # 우상단 "튜토리얼 종료" 버튼 (단계 공유)
        self._draw_skip_button(scaler)

        # 첫 단계 진입
        self._enter_step(self._step)

        # 키 바인딩
        try:
            self.app.root.bind("<Escape>", self._on_escape)
            self.app.root.bind("<space>", self._on_space)
            self.app.root.bind("m", self._on_m_key)
            self.app.root.bind("M", self._on_m_key)
        except Exception:  # noqa: BLE001
            pass

    def teardown(self) -> None:
        # 스킵 다이얼로그 정리
        if self._skip_dialog is not None and self._skip_dialog.visible:
            self._skip_dialog.hide()
        # 단계 전용 아이템 청소
        for i in self._step_ids:
            try:
                self.app.canvas.delete(i)
            except Exception:  # noqa: BLE001
                pass
        self._step_ids = []
        # 키 바인딩 해제
        try:
            self.app.root.unbind("<Escape>")
            self.app.root.unbind("<space>")
            self.app.root.unbind("m")
            self.app.root.unbind("M")
        except Exception:  # noqa: BLE001
            pass
        super().teardown()

    def update(self, dt: float) -> None:
        # 스킵 다이얼로그가 떠 있으면 진행 정지
        if self._skip_dialog is not None and self._skip_dialog.visible:
            return

        # Issue #69 (DECISION-DL-P4D-014): 단계 6 일시정지 중에는 시간 흐름 정지
        # → "Space 안 눌러도 넘어감" 결함 방지. 사용자 두번째 Space 가 진행 트리거.
        if self._step == 6 and self._step6_paused:
            return

        self._step_elapsed += dt

        # 단계 4 mock wave 진행
        if self._step == 4 and not self._mock_wave_done:
            self._tick_mock_wave(dt)

        # Issue #68/#74 (DECISION-DL-P4D-013 / DECISION-DL-P5C-010): 단계 5 M 키 후
        # 영웅 placeholder 가 좌우로 짧게 왕복 이동하는 데모를 보여준 뒤 자동 진행.
        # 사용자가 "직접 조작 → 움직임" 을 시각적으로 인지하도록 한다.
        if (
            self._step == 5
            and self._step5_manual_on
            and not self._step_completed
            and self._step5_manual_on_at >= 0.0
        ):
            since_m = self._step_elapsed - self._step5_manual_on_at
            self._tick_step5_hero_demo(since_m)
            if since_m >= _STEP5_DEMO_DURATION_S:
                self.trigger_step5_done()

        # 표시 시간 상한 → 자동 진행 (인터랙티브 단계 fallback)
        time_limit = self._current_time_limit()
        if self._step_elapsed >= time_limit and time_limit != float("inf") and not self._step_completed:
            self._log.info("tutorial step %d auto-advanced (time limit)", self._step)
            self._step_completed = True

        # 단계 완료 + CTA 자동 진행 단계는 즉시 다음
        if self._step_completed and self._is_auto_advance_step():
            self._advance_step()

    def render(self) -> None:
        # 현 구현은 build/event 기반 갱신 — render no-op
        pass

    # ------------------------------------------------------------------
    # 단계 진입 / 진행
    # ------------------------------------------------------------------

    def _enter_step(self, step: int) -> None:
        """단계 N 으로 진입. 이전 단계의 캔버스 아이템을 청소하고 새로 그린다."""
        # 청소
        canvas = self.app.canvas
        for i in self._step_ids:
            try:
                canvas.delete(i)
            except Exception:  # noqa: BLE001
                pass
        self._step_ids = []
        # Issue #69: step 6 overlay 정리 (다른 단계 진입 시).
        for i in self._step6_overlay_ids:
            try:
                canvas.delete(i)
            except Exception:  # noqa: BLE001
                pass
        self._step6_overlay_ids = []

        # 상태 리셋
        self._step = step
        self._step_elapsed = 0.0
        self._cta_enabled = False
        self._step_completed = False
        self._pause_toggle_count = 0
        self._m_pressed = False
        self._mock_wave_dt = 0.0
        self._mock_spawn_count = 0
        self._mock_wave_done = False
        # Issue #68/#69 리셋
        self._step5_manual_on = False
        self._step5_manual_on_at = -1.0
        # Issue #74: 영웅 이동 시연 추적 상태 리셋 (이전 단계 잔존 id 방지).
        self._step5_hero_ids = []
        self._step5_hero_base_cx = 0.0
        self._step5_hero_cy = 0.0
        self._step6_paused = False
        # Issue #67: 단계 3 mock 패널 상태 리셋
        self._step3_archer_selected = False
        # Issue #67/#68/#69: cta hint id 리셋 (이전 단계의 잔존 참조 방지)
        self._cta_hint_id = None

        # 단계별 build
        self._build_step(step)
        self._log.info("tutorial enter step %d", step)

    def _build_step(self, step: int) -> None:
        defs = _STEP_DEFS[step - 1]
        _, mode, key_prefix, _time_limit, hud_target = defs
        scaler = self.app.scaler

        title = _STRINGS.get(f"{key_prefix}.title", key_prefix)
        body = _STRINGS.get(f"{key_prefix}.body", "")
        cta = _STRINGS.get(f"{key_prefix}.cta", _STRINGS.get("tutorial.complete.cta", "다음"))

        # HUD 강조 (인터랙티브 단계 중 hud_target 지정 시)
        if hud_target is not None and hud_target in _HUD_TARGETS:
            self._draw_spotlight(scaler, hud_target)

        # Issue #67 (DECISION-DL-P4D-012): 단계 3 좌측에 mock 궁수 선택 패널.
        # rc.6 결함 #67: 사용자가 "왼편에 궁수가 나타나지 않는다" 고 보고.
        # 튜토리얼 단계 3 는 실 BattleScene 을 통합하지 않으므로 spotlight 만으로
        # 는 좌측 유닛 패널을 인지할 수 없다. 본 단계에 직접 mock 패널을 그려
        # "패널 클릭 → buildzone 클릭" 흐름을 시뮬레이션한다.
        if step == 3:
            self._draw_step3_unit_panel(scaler)

        # 본문 텍스트 박스
        self._draw_text_box(scaler, title, body)

        # CTA 버튼 (패시브 단계 또는 인터랙티브 단계의 안내)
        if mode == MODE_PASSIVE:
            # 패시브 단계: 활성 CTA 버튼 (단계 4 는 wave 끝날 때까지 비활성)
            enabled = step != 4
            self._cta_enabled = enabled
            cta_label = _STRINGS["tutorial.complete.cta"] if step == 8 else cta
            self._draw_cta_button(scaler, cta_label, enabled=enabled)
        else:
            # 인터랙티브 단계: cta 텍스트는 안내만, 버튼 없음
            self._draw_cta_hint(scaler, cta)

    def _advance_step(self) -> None:
        """현재 단계 완료 → 다음 단계로 또는 종료 처리."""
        if self._step >= 8:
            self._complete_tutorial()
            return
        next_step = self._step + 1
        self._enter_step(next_step)

    def _complete_tutorial(self) -> None:
        """단계 8 완료 — tutorial_completed=True 저장 + stage_select 이동."""
        try:
            mark_tutorial_completed(True, path=self._save_slot_path)
        except Exception:  # noqa: BLE001
            self._log.exception("tutorial: save completed flag failed")
        self._goto("stage_select")

    # ------------------------------------------------------------------
    # 단계별 진행 조건 (인터랙티브 단계)
    # ------------------------------------------------------------------

    def trigger_step2_done(self) -> None:
        """단계 2: 곡식 HUD 클릭. 공개 API (테스트/실제 입력 공용)."""
        if self._step == 2 and not self._step_completed:
            self._step_completed = True
            self._advance_step()

    # Issue #67 (DECISION-DL-P4D-012): trigger_step3_done 은 mock 궁수 패널
    # 선택을 검증하는 새 구현으로 아래쪽에 재정의되었다. 기존 단순 trigger 는
    # "패널 클릭 없이도 buildzone 만 누르면 진행" 결함을 일으켜 제거.

    def _is_auto_advance_step(self) -> bool:
        """완료 조건 충족 시 자동으로 다음 단계로 가는 단계인가."""
        # 패시브 단계 4 (mock wave 끝나면 다음 버튼 활성화)는 사용자 클릭 대기.
        # 패시브 단계 1/7/8 도 사용자 클릭 대기.
        # 인터랙티브 단계 2/3/5/6 은 입력 받으면 즉시 다음.
        if self._step in (2, 3, 5, 6):
            return True
        return False

    # ------------------------------------------------------------------
    # 단계 4 — mock wave
    # ------------------------------------------------------------------

    def _tick_mock_wave(self, dt: float) -> None:
        if self._mock_wave_done:
            return
        self._mock_wave_dt += dt
        while self._mock_spawn_count < _MOCK_WAVE_COUNT and self._mock_wave_dt >= _MOCK_WAVE_INTERVAL:
            self._mock_wave_dt -= _MOCK_WAVE_INTERVAL
            self._mock_spawn_count += 1
            self._log.debug(
                "tutorial mock wave spawn %d/%d (tang_soldier)",
                self._mock_spawn_count,
                _MOCK_WAVE_COUNT,
            )
        if self._mock_spawn_count >= _MOCK_WAVE_COUNT:
            self._mock_wave_done = True
            # CTA 활성화
            self._cta_enabled = True
            self._refresh_cta_state()

    # ------------------------------------------------------------------
    # 입력 핸들러
    # ------------------------------------------------------------------

    def _on_escape(self, _event: Any) -> None:
        self._show_skip_dialog()

    def _on_space(self, _event: Any) -> None:
        """Issue #69 (DECISION-DL-P4D-014): 단계 6 Space 인터랙션.

        rc.6 검수 결함 #69: "Space 를 누르면 정지되고 메뉴가 나올 것을 기대
        했는데 그냥 다음 단계로 넘어간다 / 누르지 않아도 시간이 지나면 넘어간다".

        본 fix:
          - 첫 Space → 일시정지 placeholder overlay 표시 + 안내 텍스트 갱신.
          - 두 번째 Space → overlay 제거 + 단계 진행.
          - 자동 시간 상한은 inf 로 해제 (_STEP_DEFS) — 사용자 입력 대기.
        """
        # 스킵 다이얼로그 떠 있으면 닫기 (아니오 효과)
        if self._skip_dialog is not None and self._skip_dialog.visible:
            return
        if self._step == 6 and not self._step_completed:
            self._pause_toggle_count += 1
            if self._pause_toggle_count == 1:
                # 첫 Space — paused overlay 표시.
                self._step6_paused = True
                self._draw_step6_paused_overlay()
            elif self._pause_toggle_count >= 2:
                # 두 번째 Space — overlay 제거 + 단계 진행.
                self._step6_paused = False
                self._clear_step6_paused_overlay()
                self.trigger_step6_done()

    def _on_m_key(self, _event: Any) -> None:
        """Issue #68 (DECISION-DL-P4D-013): 단계 5 M 키 인터랙션.

        rc.6 검수 결함 #68: "M 키를 누르면 컨트롤이 되는 게 아니라 다음으로
        이동해 버린다".

        본 fix:
          - M 누름 → 영웅 placeholder 색상 변경 + "직접 조작 모드 ON" 표시.
          - 1.5초 후 update 루프가 자동으로 다음 단계 진행 (인지 시간 확보).
          - 자동 시간 상한은 inf 로 해제 (_STEP_DEFS) — 사용자 입력 대기.
        """
        if self._step == 5 and not self._step_completed and not self._step5_manual_on:
            self._m_pressed = True
            self._step5_manual_on = True
            self._step5_manual_on_at = self._step_elapsed
            self._show_step5_manual_on()
            # trigger_step5_done 는 update() 에서 일정 시간 후 호출.

    def trigger_step5_done(self) -> None:
        if self._step == 5 and not self._step_completed:
            self._step_completed = True
            self._advance_step()

    def trigger_step6_done(self) -> None:
        if self._step == 6 and not self._step_completed:
            self._step_completed = True
            self._advance_step()

    def trigger_cta_click(self) -> None:
        """패시브 단계 CTA 버튼 클릭 — 단계 1/4/7/8 진행."""
        if not self._cta_enabled:
            return
        if self._step in (1, 4, 7):
            self._advance_step()
        elif self._step == 8:
            self._complete_tutorial()

    # ------------------------------------------------------------------
    # 스킵
    # ------------------------------------------------------------------

    def _show_skip_dialog(self) -> None:
        if self._skip_dialog is not None and self._skip_dialog.visible:
            return
        self._skip_dialog = SkipConfirmDialog(
            self.app.canvas,
            self.app.scaler,
            on_yes=self._handle_skip_yes,
            on_no=self._handle_skip_no,
        )
        self._skip_dialog.show()

    def _handle_skip_yes(self, dont_show_again: bool) -> None:
        try:
            if dont_show_again:
                mark_tutorial_dismissed(True, path=self._save_slot_path)
            else:
                # 슬롯 자체는 보존 (다른 필드가 있을 수 있음). 단순히 dismissed 안 건드림.
                # 단, 슬롯 파일이 아예 없으면 빈 슬롯이라도 만들지 않는다.
                pass
        except Exception:  # noqa: BLE001
            self._log.exception("tutorial: skip yes save failed")
        if self._skip_dialog is not None:
            self._skip_dialog.hide()
            self._skip_dialog = None
        self._goto("stage_select")

    def _handle_skip_no(self) -> None:
        if self._skip_dialog is not None:
            self._skip_dialog.hide()
            self._skip_dialog = None

    # ------------------------------------------------------------------
    # 그리기 헬퍼
    # ------------------------------------------------------------------

    def _draw_battle_backdrop(self, scaler: Any) -> None:
        """정적 전장 backdrop (Issue #73 / DECISION-DL-P5C-009).

        실 BattleScene 을 통합하지 않고, 게임 맥락을 보여주는 정적 레이어를 한 번
        그린다 (단계 공유, teardown 시 tag 로 일괄 삭제). 레이어 z-order:
          하늘 → 평지 → 성벽 → 성문 → 아군 placeholder → 적 placeholder.
        각 단계의 spotlight dim 마스크가 이 위에 덮여 강조 대상만 밝게 남는다.
        모든 좌표는 베이스 1920×1080 기준 → scaler.to_screen 변환.
        """
        canvas = self.app.canvas
        tag = (self._tag, "tutorial_backdrop")

        def rect(bx1: float, by1: float, bx2: float, by2: float, **kw: Any) -> None:
            x1, y1 = _sx(scaler, bx1, by1)
            x2, y2 = _sx(scaler, bx2, by2)
            canvas.create_rectangle(x1, y1, x2, y2, tags=tag, **kw)

        def oval(cx: float, cy: float, r: float, **kw: Any) -> None:
            x1, y1 = _sx(scaler, cx - r, cy - r)
            x2, y2 = _sx(scaler, cx + r, cy + r)
            canvas.create_oval(x1, y1, x2, y2, tags=tag, **kw)

        # 하늘(상단) + 평지(중단, 적 진군 라인)
        rect(0, 80, 1920, 560, fill=_CLR_BD_SKY, outline="")
        rect(0, 560, 1920, 1080, fill=_CLR_BD_FIELD, outline="")

        # 성벽(하단 가로 밴드) + 상단 테두리
        rect(0, 700, 1920, 780, fill=_CLR_BD_WALL, outline="")
        rect(0, 700, 1920, 712, fill=_CLR_BD_WALL_TOP, outline="")
        # 성벽 흉벽(凸) 패턴 — 일정 간격 사각형
        for gx in range(60, 1920, 160):
            rect(gx, 684, gx + 80, 700, fill=_CLR_BD_WALL_TOP, outline="")

        # 성문(코어) — buildzone spotlight(740,640) 아래쪽 중앙
        rect(820, 700, 1100, 800, fill=_CLR_BD_GATE, outline="#7a5224", width=2)

        # 아군 placeholder (성벽 위 청색 유닛 몇 체)
        for ax in (360, 560, 1160, 1360):
            oval(ax, 672, 22, fill=_CLR_BD_ALLY, outline="#a8d0e8", width=2)

        # 적 placeholder (평지에서 진군 중인 적색 유닛 몇 체)
        for ex, ey in ((300, 360), (640, 300), (980, 340), (1320, 300), (1600, 380)):
            oval(ex, ey, 20, fill=_CLR_BD_ENEMY, outline="#d88078", width=2)

    def _draw_skip_button(self, scaler: Any) -> None:
        """우상단 "튜토리얼 종료" 버튼 (씬 공유)."""
        canvas = self.app.canvas
        x1, y1 = _sx(scaler, 1700, 30)
        x2, y2 = _sx(scaler, 1880, 80)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        rect_id = canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=_CLR_BTN_NORMAL,
            outline=_CLR_BTN_OUTLINE,
            width=2,
            tags=(self._tag, "skip_button"),
        )
        text_id = canvas.create_text(
            cx,
            cy,
            text=_STRINGS["tutorial.skip.button"],
            fill=_CLR_TEXT,
            font=_font(scaler, 16, bold=True),
            anchor="center",
            tags=(self._tag, "skip_button"),
        )

        def _enter(_e: Any) -> None:
            try:
                canvas.itemconfig(rect_id, fill=_CLR_BTN_HOVER, outline=_CLR_BTN_HOVER_OUTLINE)
            except Exception:  # noqa: BLE001
                pass

        def _leave(_e: Any) -> None:
            try:
                canvas.itemconfig(rect_id, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE)
            except Exception:  # noqa: BLE001
                pass

        def _release(_e: Any) -> None:
            self._show_skip_dialog()

        for iid in (rect_id, text_id):
            try:
                canvas.tag_bind(iid, "<Enter>", _enter)
                canvas.tag_bind(iid, "<Leave>", _leave)
                canvas.tag_bind(iid, "<ButtonRelease-1>", _release)
            except Exception:  # noqa: BLE001
                pass

    def _draw_spotlight(self, scaler: Any, target_key: str) -> None:
        """HUD 강조 — 반투명 마스크 + mock 콘텐츠 + 노란 원형 outline + 화살표 + 라벨.

        Canvas 의 alpha 가 제한적이므로 stipple ``gray50`` 으로 근사.
        spotlight 원형 컷아웃은 진정한 컷아웃이 아니라 노란 원형 outline 으로 표현
        (마스크 위에 그려진다).

        Issue #49 (DECISION-DL-P4D-001): spotlight 가 가리키는 HUD 대상의
        **mock placeholder** 를 마스크 위에 직접 그려, 동그라미 안이 비어 있는
        현상을 해소한다. z-order = mask → mock content → ring → arrow → label.

        Issue #55 (DECISION-DL-P4D-009): 인터랙티브 단계의 spotlight 영역에
        클릭 핸들러를 binding 한다. 단계 2(resource) → trigger_step2_done,
        단계 3(buildzone) → trigger_step3_done. mask 는 hit-target 가로채지
        못하도록 z-order 아래에, mock content/ring 에 직접 binding 한다.
        """
        canvas = self.app.canvas
        cx, cy, radius = _HUD_TARGETS[target_key]

        # Issue #55 (DECISION-DL-P4D-009): mock content 가 그려지기 전에
        # click handler 를 미리 설정해 _draw_mock_target_content 가 각 mock 아이템에
        # binding 할 수 있도록 한다.
        self._spotlight_click_handler = None
        if target_key == "resource":
            self._spotlight_click_handler = lambda _e: self.trigger_step2_done()
        elif target_key == "buildzone":
            self._spotlight_click_handler = lambda _e: self.trigger_step3_done()

        # 반투명 마스크 (전체 화면)
        # Issue #55: 마스크에 클릭 binding 없음 → spotlight 안 콘텐츠가 우선.
        mx1, my1 = _sx(scaler, 0, 0)
        mx2, my2 = _sx(scaler, 1920, 1080)
        mask = canvas.create_rectangle(
            mx1,
            my1,
            mx2,
            my2,
            fill=_CLR_DIM,
            outline="",
            stipple="gray50",
            tags=(self._tag, "tutorial_spotlight_mask"),
        )
        self._step_ids.append(mask)

        # mock HUD placeholder (마스크 위, ring 아래) — Issue #49 fix
        # Issue #55: mock content 에 단계별 클릭 핸들러 binding.
        self._draw_mock_target_content(scaler, target_key)

        # spotlight ring — Issue #55: filled transparent area 추가
        # 원형 영역 자체에 클릭 binding 을 가능하게 하기 위해 fill 을 stipple 로 채운다.
        # outline-only ring 은 영역이 아니라 윤곽선만 hit area 가 되므로 클릭이 어렵다.
        sx1, sy1 = _sx(scaler, cx - radius, cy - radius)
        sx2, sy2 = _sx(scaler, cx + radius, cy + radius)
        # 투명한 내부 hit area (transparent 표시이지만 클릭 받음)
        ring_fill = canvas.create_oval(
            sx1,
            sy1,
            sx2,
            sy2,
            fill="",
            outline="",
            tags=(self._tag, "tutorial_spotlight_hit"),
        )
        self._step_ids.append(ring_fill)
        # 외곽선 ring
        ring = canvas.create_oval(
            sx1,
            sy1,
            sx2,
            sy2,
            outline=_CLR_SPOT_OUTLINE,
            width=4,
            tags=(self._tag, "tutorial_spotlight_ring"),
        )
        self._step_ids.append(ring)

        # Issue #55 (DECISION-DL-P4D-009): 인터랙티브 단계의 spotlight 영역 클릭 핸들러.
        # ring 자체는 outline-only 라 클릭이 어려우니 ring_fill 과 mock content 에
        # 모두 바인딩. ring_fill 은 fill="" 라 clear 영역으로 z-order 위 콘텐츠를 안 가린다.
        self._bind_spotlight_click(target_key, ring_fill, ring)

        # 화살표 (단순 polygon)
        arrow_origin_x = cx + radius + 20
        arrow_tip_x = cx + radius + 4
        ax1, ay1 = _sx(scaler, arrow_origin_x, cy - 12)
        ax2, ay2 = _sx(scaler, arrow_tip_x, cy)
        ax3, ay3 = _sx(scaler, arrow_origin_x, cy + 12)
        arrow = canvas.create_polygon(
            ax1,
            ay1,
            ax2,
            ay2,
            ax3,
            ay3,
            fill=_CLR_ARROW,
            outline="",
            tags=(self._tag, "tutorial_arrow"),
        )
        self._step_ids.append(arrow)

        # 라벨 (옆에 작은 한국어)
        label_key_map = {
            "resource": "tutorial.hud_arrow.resource",
            "buildzone": "tutorial.hud_arrow.buildzone",
            "hero": "tutorial.hud_arrow.hero",
        }
        if target_key in label_key_map:
            label = _STRINGS.get(label_key_map[target_key], "")
            lx, ly = _sx(scaler, cx + radius + 50, cy)
            label_id = canvas.create_text(
                lx,
                ly,
                text=label,
                fill=_CLR_ARROW,
                font=_font(scaler, 16, bold=True),
                anchor="w",
                tags=(self._tag, "tutorial_arrow_label"),
            )
            self._step_ids.append(label_id)

    def _bind_spotlight_click(self, target_key: str, *canvas_ids: int) -> None:
        """spotlight ring/hit-area 에 단계 진행 클릭 핸들러 binding (Issue #55).

        ``_draw_spotlight`` 에서 미리 set 된 ``self._spotlight_click_handler`` 를 사용.
        target_key 별 trigger 매핑은 _draw_spotlight 에서 결정한다.
        """
        canvas = self.app.canvas
        handler = getattr(self, "_spotlight_click_handler", None)
        if handler is None:
            return
        for cid in canvas_ids:
            try:
                canvas.tag_bind(cid, "<ButtonRelease-1>", handler)
            except Exception:  # noqa: BLE001
                pass

    def _draw_mock_target_content(self, scaler: Any, target_key: str) -> None:
        """spotlight 가 가리키는 HUD 대상의 mock placeholder (Issue #49, DECISION-DL-P4D-001).

        실제 BattleScene HUD 를 통합하지 않고, spotlight 안에 의미 있는
        콘텐츠를 직접 그려 동그라미가 가리키는 대상을 사용자가 인식할 수 있게 한다.
        - resource: 곡식 라벨 + 값 카운터
        - buildzone: 빈 배치 칸 사각형 + "?" 표시
        - hero: 영웅 placeholder 원 + 이름 글자
        - pause: 일시정지 버튼 placeholder (||)

        Issue #55 (DECISION-DL-P4D-009): 인터랙티브 단계의 mock content 에 단계
        진행 클릭 핸들러를 추가 — 사용자가 시각적으로 가리킨 위치를 직접 클릭할
        수 있게 한다.
        """
        canvas = self.app.canvas
        cx, cy, _radius = _HUD_TARGETS[target_key]
        # _draw_spotlight 에서 set 됐을 수도 있고, 단독 호출 시 없음
        click_handler = getattr(self, "_spotlight_click_handler", None)

        def _bind_if(iid: int) -> None:
            if click_handler is None:
                return
            try:
                canvas.tag_bind(iid, "<ButtonRelease-1>", click_handler)
            except Exception:  # noqa: BLE001
                pass

        if target_key == "resource":
            # 상단 곡식 HUD placeholder — battle_scene.hud 와 같은 라벨/값
            # Issue #55: 라벨 + 값 카운터 영역을 덮는 투명 hit-area 사각형 추가.
            # 단일 텍스트 anchor 만 클릭 받으면 hit area 가 좁아 사용자가 놓침.
            hit_x1, hit_y1 = _sx(scaler, cx - 36, cy - 32)
            hit_x2, hit_y2 = _sx(scaler, cx + 36, cy + 32)
            hit_id = canvas.create_rectangle(
                hit_x1,
                hit_y1,
                hit_x2,
                hit_y2,
                fill="",
                outline="",
                tags=(self._tag, "tutorial_mock_content", "tutorial_mock_hit"),
            )
            self._step_ids.append(hit_id)
            _bind_if(hit_id)
            # 곡식 라벨 (상단)
            lx, ly = _sx(scaler, cx, cy - 18)
            label_id = canvas.create_text(
                lx,
                ly,
                text="곡식",
                fill="#e8c860",
                font=_font(scaler, 14, bold=True),
                anchor="center",
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(label_id)
            _bind_if(label_id)
            # 값 카운터 (큰 숫자)
            vx, vy = _sx(scaler, cx, cy + 12)
            val_id = canvas.create_text(
                vx,
                vy,
                text="100",
                fill="#f0e0c0",
                font=_font(scaler, 22, bold=True),
                anchor="center",
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(val_id)
            _bind_if(val_id)
        elif target_key == "buildzone":
            # 빈 배치 칸 placeholder — 점선 박스 + "?"
            half = 40.0
            x1, y1 = _sx(scaler, cx - half, cy - half)
            x2, y2 = _sx(scaler, cx + half, cy + half)
            rect_id = canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#1a2a1a",
                outline="#88aa88",
                width=2,
                dash=(6, 4),
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(rect_id)
            _bind_if(rect_id)
            qx, qy = _sx(scaler, cx, cy)
            q_id = canvas.create_text(
                qx,
                qy,
                text="?",
                fill="#aaccaa",
                font=_font(scaler, 36, bold=True),
                anchor="center",
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(q_id)
            _bind_if(q_id)
        elif target_key == "hero":
            # 영웅 placeholder — 원 + 이름
            r = 36.0
            x1, y1 = _sx(scaler, cx - r, cy - r)
            x2, y2 = _sx(scaler, cx + r, cy + r)
            circ_id = canvas.create_oval(
                x1,
                y1,
                x2,
                y2,
                fill="#3a2a8c",
                outline="#a8a0d8",
                width=2,
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(circ_id)
            nx, ny = _sx(scaler, cx, cy)
            name_id = canvas.create_text(
                nx,
                ny,
                text="楊",
                fill="#f0e8d0",
                font=_font(scaler, 28, bold=True),
                anchor="center",
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(name_id)
            # Issue #74 (DECISION-DL-P5C-010): M 키 후 이동 시연 대상으로 추적.
            self._step5_hero_ids = [circ_id, name_id]
            self._step5_hero_base_cx = cx
            self._step5_hero_cy = cy
        elif target_key == "pause":
            # 일시정지 버튼 placeholder — battle_scene.hud 의 pause_btn 모방
            half_w = 30.0
            half_h = 24.0
            x1, y1 = _sx(scaler, cx - half_w, cy - half_h)
            x2, y2 = _sx(scaler, cx + half_w, cy + half_h)
            rect_id = canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#2a2010",
                outline="#8a7040",
                width=2,
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(rect_id)
            px, py = _sx(scaler, cx, cy)
            p_id = canvas.create_text(
                px,
                py,
                text="||",
                fill="#e0d0a0",
                font=_font(scaler, 18, bold=True),
                anchor="center",
                tags=(self._tag, "tutorial_mock_content"),
            )
            self._step_ids.append(p_id)
        # 다른 target_key 는 mock 콘텐츠 없음 (의도).

    def _draw_text_box(self, scaler: Any, title: str, body: str) -> None:
        """본문 텍스트 박스 (하단 중앙)."""
        canvas = self.app.canvas
        bx1, by1 = _sx(scaler, 360, 800)
        bx2, by2 = _sx(scaler, 1560, 980)
        box = canvas.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill=_CLR_PANEL,
            outline=_CLR_PANEL_OUTLINE,
            width=2,
            tags=(self._tag, "tutorial_text_box"),
        )
        self._step_ids.append(box)

        tcx, tcy = _sx(scaler, 960, 840)
        title_id = canvas.create_text(
            tcx,
            tcy,
            text=title,
            fill=_CLR_TITLE,
            font=_font(scaler, 28, bold=True),
            anchor="center",
            tags=(self._tag, "tutorial_text_title"),
        )
        self._step_ids.append(title_id)

        body_cx, body_cy = _sx(scaler, 960, 910)
        body_id = canvas.create_text(
            body_cx,
            body_cy,
            text=body,
            fill=_CLR_TEXT_BODY,
            font=_font(scaler, 18),
            anchor="center",
            justify="center",
            width=1100,
            tags=(self._tag, "tutorial_text_body"),
        )
        self._step_ids.append(body_id)

    def _draw_cta_button(self, scaler: Any, label: str, enabled: bool = True) -> None:
        """패시브 단계의 CTA 버튼 (화면 하단 우측 또는 중앙 하단)."""
        canvas = self.app.canvas
        x1, y1 = _sx(scaler, 840, 1000)
        x2, y2 = _sx(scaler, 1080, 1060)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        fill = _CLR_BTN_NORMAL if enabled else _CLR_BTN_DISABLED
        outline = _CLR_BTN_OUTLINE if enabled else _CLR_BTN_DISABLED_OUTLINE
        text_fill = _CLR_TEXT if enabled else _CLR_BTN_DISABLED_TEXT

        rect_id = canvas.create_rectangle(
            x1, y1, x2, y2, fill=fill, outline=outline, width=2, tags=(self._tag, "tutorial_cta_btn")
        )
        text_id = canvas.create_text(
            cx,
            cy,
            text=label,
            fill=text_fill,
            font=_font(scaler, 20, bold=True),
            anchor="center",
            tags=(self._tag, "tutorial_cta_btn"),
        )
        self._step_ids.append(rect_id)
        self._step_ids.append(text_id)
        # state ref
        self._cta_rect_id = rect_id
        self._cta_text_id = text_id
        self._cta_label = label

        def _release(_e: Any) -> None:
            self.trigger_cta_click()

        for iid in (rect_id, text_id):
            try:
                canvas.tag_bind(iid, "<ButtonRelease-1>", _release)
            except Exception:  # noqa: BLE001
                pass

    def _draw_cta_hint(self, scaler: Any, hint: str) -> None:
        """인터랙티브 단계 안내 텍스트 (CTA 버튼 대신).

        Issue #67/#68/#69 (DECISION-DL-P4D-012/013/014): hint id 를 인스턴스
        속성으로 보관해 단계 진행 중 텍스트/색상을 갱신 가능하도록 한다.
        """
        canvas = self.app.canvas
        hx, hy = _sx(scaler, 960, 1020)
        hint_id = canvas.create_text(
            hx,
            hy,
            text=hint,
            fill=_CLR_ARROW,
            font=_font(scaler, 18, bold=True),
            anchor="center",
            tags=(self._tag, "tutorial_cta_hint"),
        )
        self._step_ids.append(hint_id)
        # Issue #67/#68/#69: 단계 진행 중 갱신용 참조.
        self._cta_hint_id = hint_id

    # ------------------------------------------------------------------
    # Issue #67 (DECISION-DL-P4D-012): 단계 3 mock 궁수 선택 패널
    # ------------------------------------------------------------------

    def _draw_step3_unit_panel(self, scaler: Any) -> None:
        """단계 3 — 좌측 mock 궁수 선택 패널.

        rc.6 결함 #67 fix: BattleScene 의 ``_draw_unit_selection_panel`` 모방.
        실 ally 배치는 발생하지 않고 클릭 → 선택 표시 → buildzone 클릭으로
        진행 트리거. 인지 부하 우선 원칙(DECISION-DL-P4-002) 유지.
        """
        canvas = self.app.canvas
        # 패널 박스 (베이스 1920×1080 좌측 하단)
        px1, py1 = _sx(scaler, 28, 814)
        px2, py2 = _sx(scaler, 252, 932)
        panel_id = canvas.create_rectangle(
            px1,
            py1,
            px2,
            py2,
            fill="#1a1208",
            outline=_CLR_PANEL_OUTLINE,
            width=2,
            tags=(self._tag, "tutorial_step3_panel"),
        )
        self._step_ids.append(panel_id)

        # 타이틀
        title_x, title_y = _sx(scaler, 40, 832)
        title_id = canvas.create_text(
            title_x,
            title_y,
            text="아군 배치",
            fill="#f0d080",
            font=_font(scaler, 14, bold=True),
            anchor="w",
            tags=(self._tag, "tutorial_step3_panel"),
        )
        self._step_ids.append(title_id)

        # 궁수 버튼 (clickable)
        bx1, by1 = _sx(scaler, 40, 850)
        bx2, by2 = _sx(scaler, 240, 920)
        btn_rect = canvas.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#3a2a1c",
            outline="#a88a5c",
            width=2,
            tags=(self._tag, "tutorial_step3_archer_btn"),
        )
        self._step_ids.append(btn_rect)
        self._step3_archer_btn_rect = btn_rect
        nx, ny = _sx(scaler, 52, 862)
        name_id = canvas.create_text(
            nx,
            ny,
            text="고구려 궁수",
            fill="#f0e0c0",
            font=_font(scaler, 14, bold=True),
            anchor="nw",
            tags=(self._tag, "tutorial_step3_archer_btn"),
        )
        self._step_ids.append(name_id)
        cx, cy = _sx(scaler, 52, 892)
        cost_id = canvas.create_text(
            cx,
            cy,
            text="곡식 50",
            fill="#e8c860",
            font=_font(scaler, 12),
            anchor="nw",
            tags=(self._tag, "tutorial_step3_archer_btn"),
        )
        self._step_ids.append(cost_id)

        # 선택 상태 플래그 (튜토리얼 mock — 실 ally 생성 X)
        self._step3_archer_selected: bool = False

        def _select_archer(_e: Any) -> None:
            if self._step != 3 or self._step_completed:
                return
            self._step3_archer_selected = True
            # 버튼 강조
            try:
                canvas.itemconfig(btn_rect, fill="#5a4a2c", outline="#d4a84a")
            except Exception:  # noqa: BLE001
                pass
            # 안내 텍스트 갱신
            self._refresh_cta_hint_step3()

        for iid in (btn_rect, name_id, cost_id):
            try:
                canvas.tag_bind(iid, "<ButtonRelease-1>", _select_archer)
            except Exception:  # noqa: BLE001
                pass

    def _refresh_cta_hint_step3(self) -> None:
        """단계 3 hint 갱신 — 궁수 선택 후 buildzone 안내 강조."""
        hint_id = getattr(self, "_cta_hint_id", None)
        if hint_id is None:
            return
        try:
            self.app.canvas.itemconfig(
                hint_id,
                text="궁수 선택됨 — 녹색 칸을 누르시오",
                fill="#3fbf6f",
            )
        except Exception:  # noqa: BLE001
            pass

    # Issue #67: step3 buildzone(spotlight) 클릭은 _draw_spotlight 의
    # _spotlight_click_handler 가 trigger_step3_done 으로 라우팅. 선택 없이
    # buildzone 만 누르면 hint 갱신만, 양쪽 다 누르면 진행.
    def trigger_step3_done(self) -> None:  # type: ignore[no-redef]
        """단계 3 진행 트리거 — 궁수 선택 + buildzone 클릭 모두 필요.

        Issue #55 의 단순 trigger 와 달리 ``self._step3_archer_selected`` 가
        True 일 때만 진행. False 면 hint 만 갱신해 사용자가 패널을 누르도록
        유도. 본 메서드는 ``_spotlight_click_handler`` (buildzone) 에서 호출.
        """
        if self._step != 3 or self._step_completed:
            return
        if not getattr(self, "_step3_archer_selected", False):
            # 궁수 선택 안 됨 — 안내만 갱신.
            hint_id = getattr(self, "_cta_hint_id", None)
            if hint_id is not None:
                try:
                    self.app.canvas.itemconfig(
                        hint_id,
                        text="먼저 좌측 궁수 패널을 누르시오",
                        fill="#e08840",
                    )
                except Exception:  # noqa: BLE001
                    pass
            return
        self._step_completed = True
        self._advance_step()

    # ------------------------------------------------------------------
    # Issue #68 (DECISION-DL-P4D-013): 단계 5 영웅 컨트롤 시각화
    # ------------------------------------------------------------------

    def _show_step5_manual_on(self) -> None:
        """단계 5 — M 키 누름 후 영웅 placeholder + 모드 라벨 갱신."""
        canvas = self.app.canvas
        scaler = self.app.scaler
        # 영웅 placeholder 색상 강조 (자동 → 직접 조작) — _HUD_TARGETS["hero"] 좌표 사용.
        cx, cy, _r = _HUD_TARGETS["hero"]
        r = 36.0
        x1, y1 = _sx(scaler, cx - r, cy - r)
        x2, y2 = _sx(scaler, cx + r, cy + r)
        ring_id = canvas.create_oval(
            x1,
            y1,
            x2,
            y2,
            outline="#f0c040",
            width=5,
            tags=(self._tag, "tutorial_step5_manual_ring"),
        )
        self._step_ids.append(ring_id)
        # Issue #74: 이동 시연 시 링도 영웅과 함께 움직이도록 추적 목록에 추가.
        self._step5_hero_ids.append(ring_id)
        # 모드 라벨 (영웅 옆)
        lx, ly = _sx(scaler, cx, cy - r - 24)
        label_id = canvas.create_text(
            lx,
            ly,
            text=_STRINGS["tutorial.step5.manual_on"],
            fill="#f0c040",
            font=_font(scaler, 16, bold=True),
            anchor="center",
            justify="center",
            tags=(self._tag, "tutorial_step5_manual_label"),
        )
        self._step_ids.append(label_id)
        # hint 갱신
        hint_id = getattr(self, "_cta_hint_id", None)
        if hint_id is not None:
            try:
                canvas.itemconfig(hint_id, text="직접 조작 모드 ON — 영웅이 움직입니다", fill="#3fbf6f")
            except Exception:  # noqa: BLE001
                pass

    def _tick_step5_hero_demo(self, since_m: float) -> None:
        """단계 5 — M 키 후 영웅 placeholder 좌우 왕복 이동 시연 (Issue #74).

        ``since_m`` (M 키 누른 뒤 경과 시간) 으로 sine 왕복 오프셋을 계산해
        추적 중인 placeholder 아이템(원/이름/링)을 같은 만큼 평행 이동한다.
        canvas.coords 로 기존 아이템을 옮기므로 재생성/깜빡임이 없다.
        DECISION-DL-P5C-010: 인지부하 최소화를 위해 짧은 왕복(진폭 70px)만.
        """
        if not self._step5_hero_ids:
            return
        canvas = self.app.canvas
        scaler = self.app.scaler
        import math

        # sine 왕복 — 시작점에서 오른쪽 → 왼쪽 → 복귀.
        phase = (since_m / _STEP5_DEMO_PERIOD_S) * 2.0 * math.pi
        offset = _STEP5_DEMO_AMPLITUDE * math.sin(phase)
        cx = self._step5_hero_base_cx + offset
        cy = self._step5_hero_cy
        r = 36.0
        # 원 + 링: bbox 갱신.
        x1, y1 = _sx(scaler, cx - r, cy - r)
        x2, y2 = _sx(scaler, cx + r, cy + r)
        nx, ny = _sx(scaler, cx, cy)
        for iid in self._step5_hero_ids:
            try:
                kind = canvas.type(iid) if hasattr(canvas, "type") else "oval"
            except Exception:  # noqa: BLE001
                kind = "oval"
            try:
                if kind == "text":
                    canvas.coords(iid, nx, ny)
                else:
                    canvas.coords(iid, x1, y1, x2, y2)
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # Issue #69 (DECISION-DL-P4D-014): 단계 6 일시정지 시각화
    # ------------------------------------------------------------------

    def _draw_step6_paused_overlay(self) -> None:
        """단계 6 — 첫 Space 시 paused overlay (반투명 dim + 안내)."""
        canvas = self.app.canvas
        scaler = self.app.scaler
        # 반투명 dim — 전체 화면. 이미 step_ids 의 spotlight mask 가 있어도
        # 별도로 추가해 "일시정지" 명확화.
        mx1, my1 = _sx(scaler, 0, 0)
        mx2, my2 = _sx(scaler, 1920, 1080)
        dim_id = canvas.create_rectangle(
            mx1,
            my1,
            mx2,
            my2,
            fill=_CLR_DIM,
            outline="",
            stipple="gray50",
            tags=(self._tag, "tutorial_step6_dim"),
        )
        self._step6_overlay_ids.append(dim_id)
        # 중앙 안내 텍스트
        tcx, tcy = _sx(scaler, 960, 480)
        text_id = canvas.create_text(
            tcx,
            tcy,
            text=_STRINGS["tutorial.step6.paused_overlay"],
            fill="#f0c040",
            font=_font(scaler, 36, bold=True),
            anchor="center",
            justify="center",
            tags=(self._tag, "tutorial_step6_paused_text"),
        )
        self._step6_overlay_ids.append(text_id)
        # hint 갱신
        hint_id = getattr(self, "_cta_hint_id", None)
        if hint_id is not None:
            try:
                canvas.itemconfig(hint_id, text="일시정지됨 — Space 다시 누르면 재개", fill="#f0c040")
            except Exception:  # noqa: BLE001
                pass

    def _clear_step6_paused_overlay(self) -> None:
        """단계 6 — 두 번째 Space 시 overlay 제거."""
        canvas = self.app.canvas
        for iid in self._step6_overlay_ids:
            try:
                canvas.delete(iid)
            except Exception:  # noqa: BLE001
                pass
        self._step6_overlay_ids = []

    def _refresh_cta_state(self) -> None:
        """단계 4: mock wave 종료 시 CTA 활성화로 전환."""
        rect_id = getattr(self, "_cta_rect_id", None)
        text_id = getattr(self, "_cta_text_id", None)
        if rect_id is None or text_id is None:
            return
        try:
            self.app.canvas.itemconfig(rect_id, fill=_CLR_BTN_NORMAL, outline=_CLR_BTN_OUTLINE)
            self.app.canvas.itemconfig(text_id, fill=_CLR_TEXT)
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 유틸
    # ------------------------------------------------------------------

    def _current_time_limit(self) -> float:
        return _STEP_DEFS[self._step - 1][3]

    def _current_mode(self) -> str:
        return _STEP_DEFS[self._step - 1][1]

    def _goto(self, scene_name: str) -> None:
        """``app.goto`` 래핑. 테스트 시 FakeApp 도 정상 라우팅 가능."""
        try:
            self.app.goto(scene_name)
        except Exception:  # noqa: BLE001
            self._log.exception("tutorial: goto %s failed", scene_name)

    # ------------------------------------------------------------------
    # 테스트 친화 API
    # ------------------------------------------------------------------

    @property
    def step(self) -> int:
        """현재 단계 (1~8). 테스트용."""
        return self._step

    @property
    def skip_dialog_visible(self) -> bool:
        return self._skip_dialog is not None and self._skip_dialog.visible

    def force_set_save_slot_path(self, path: Any) -> None:
        """테스트에서 save_slot.json 위치를 override 한다."""
        self._save_slot_path = path

    # 명시 호출 진입점 (메뉴에서) — 외부 보장
    def reset_to_first_step(self) -> None:
        """단계 1부터 다시 시작 — 메뉴 재진입 시 사용."""
        self._enter_step(1)


# ---------------------------------------------------------------------------
# 자동 진입 분기 헬퍼
# ---------------------------------------------------------------------------


def decide_initial_scene(default_scene: str = "menu") -> str:
    """저장 슬롯 검사 후 첫 씬 결정 — main.py 에서 사용 (DECISION-DL-P4-003)."""
    try:
        slot = load_save_slot()
    except Exception:  # noqa: BLE001
        return default_scene
    if slot.should_auto_enter_tutorial():
        return "tutorial"
    return default_scene


# 외부에서 save_slot 호출 시 silent 보존 (직접 import 노출용)
__all__ = [
    "SkipConfirmDialog",
    "TutorialScene",
    "decide_initial_scene",
    "load_save_slot",
    "save_save_slot",
]
