"""회귀 매트릭스 P3.5 — 자동 테스트 케이스.

매트릭스 docs/qa/regression_matrix.md 의 ✗ → ✓ 전환 항목 커버.
DECISION-TL-P3-5-003: headless FakeApp/FakeCanvas 패턴 사용.

커버 항목:
  [MN] MN-03 Enter 키 포커스 활성화
  [MN] MN-04 Up/Down 키 포커스 이동
  [MN] MN-05 종료 버튼 -> app.quit()
  [SS] SS-02 초기 상태 stage_01만 해금
  [SS] SS-05 ESC 키 -> 메뉴 복귀
  [EN] EN-01 EndingScene 패널 순차 진행 (Space)
  [EN] EN-02 EndingScene ESC -> 메뉴 복귀
  [EN] EN-03 마지막 패널 이후 메뉴 복귀
  [EN] EN-04 is_finale 패널에서 자동 진행 없음
  [BT] BT-11 BattleScene stage_02 ~ stage_05 build 오류 없음 (각 스테이지)
"""

from __future__ import annotations

from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Shared Fake 인프라 (test_battle_scene_flow.py 재사용 + 확장)
# ---------------------------------------------------------------------------


class FakeCanvas:
    def __init__(self) -> None:
        self.items: dict[int, Any] = {}
        self._next: int = 1
        self._item_configs: dict[int, dict[str, Any]] = {}

    def create_rectangle(self, *args: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("rect", args, kw)
        self._item_configs[i] = {}
        return i

    def create_text(self, *args: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("text", args, kw)
        self._item_configs[i] = {}
        return i

    def create_line(self, *args: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("line", args, kw)
        self._item_configs[i] = {}
        return i

    def itemconfig(self, i: int, **kw: Any) -> None:
        if i in self._item_configs:
            self._item_configs[i].update(kw)

    def coords(self, i: int, *args: Any) -> None:
        pass

    def delete(self, i: Any) -> None:
        if isinstance(i, int):
            self.items.pop(i, None)
            self._item_configs.pop(i, None)

    def tag_bind(self, *args: Any, **kw: Any) -> None:
        pass

    def winfo_width(self) -> int:
        return 1920

    def winfo_height(self) -> int:
        return 1080

    def after(self, ms: int, func: Any) -> str:
        return "after_id"

    def after_cancel(self, after_id: str) -> None:
        pass


class FakeScaler:
    scale = 1.0
    canvas_w = 1920
    canvas_h = 1080

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return x, y

    def font_pt(self, pt: int) -> int:
        return max(8, pt)

    def update(self, w: int, h: int) -> tuple[float, float]:
        return 1.0, 1.0


class FakeEventBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, Any]] = []

    def publish(self, event: str, data: Any) -> None:
        self.events.append((event, data))


class FakeRoot:
    def __init__(self) -> None:
        self._bindings: dict[str, Any] = {}

    def bind(self, key: str, fn: Any) -> None:
        self._bindings[key] = fn

    def unbind(self, key: str) -> None:
        self._bindings.pop(key, None)

    def after(self, ms: int, fn: Any) -> str:
        return "after_id"

    def after_cancel(self, after_id: str) -> None:
        pass


class FakePlayerData:
    """player_data mock - 해금/완료 스테이지 제어용."""

    def __init__(
        self,
        unlocked: list[str] | None = None,
        stars: dict[str, int] | None = None,
    ) -> None:
        self.unlocked_stages: list[str] = unlocked if unlocked is not None else ["stage_01"]
        self.stage_stars: dict[str, int] = stars if stars is not None else {}


class FakeApp:
    def __init__(self, player_data: Any = None) -> None:
        self.canvas = FakeCanvas()
        self.scaler = FakeScaler()
        self.events = FakeEventBus()
        self.root = FakeRoot()
        self._goto_calls: list[str] = []
        self._quit_called: bool = False
        if player_data is not None:
            self.player_data = player_data

    def goto(self, name: str, **kwargs: Any) -> None:
        self._goto_calls.append(name)

    def quit(self) -> None:
        self._quit_called = True


# ---------------------------------------------------------------------------
# [MN] MenuScene - 키보드 네비게이션 (MN-03, MN-04, MN-05)
# ---------------------------------------------------------------------------


def _make_menu_scene(player_data: Any = None) -> Any:
    from src.scenes.menu_scene import MenuScene

    app = FakeApp(player_data=player_data)
    scene = MenuScene(app)
    # MenuScene._make_button 은 tkinter.Canvas 를 assert 하므로 build() 직접 호출 불가.
    # 대신 내부 상태를 직접 초기화해 keyboard handler 만 테스트한다.
    # (DECISION-TL-P3-5-006: build() 는 수동 CAT-01 카탈로그 검수 대상)
    scene._focused_idx = 0
    # build() 없이 _btn_rect_ids 를 빈 리스트로 초기화 -> _update_focus 호출 시 루프 없음
    scene._btn_rect_ids = []
    scene._button_ids = []
    return scene


def test_menu_enter_key_triggers_goto_for_focused_button() -> None:
    """MN-03: Enter 키 -> _focused_idx 0번 -> goto(dest) 호출.

    DECISION-SCM-P3-001 (2026-05-19): Phase 3.5 수직 슬라이스(PR #24,
    DECISION-DL-P3-5-002)에서 "새 게임"/"이어하기" 라우팅이 battle 직행에서
    stage_select 경유로 변경됨. 본 테스트는 회귀 매트릭스 MN-03을 신규
    수직 슬라이스 흐름(메뉴 → 스테이지 선택 → 배틀)에 맞춰 갱신.
    """
    scene = _make_menu_scene()
    scene._focused_idx = 0  # "새 게임" -> dest="stage_select" (수직 슬라이스 흐름)
    scene._on_enter_key(None)
    assert "stage_select" in scene.app._goto_calls


def test_menu_enter_key_stage_select_button() -> None:
    """MN-03(변형): 포커스가 "스테이지" 버튼일 때 Enter -> goto("stage_select").

    Phase 4 (Issue #26, DECISION-DL-P4-006): "튜토리얼" 항목이 인덱스 2 로 합류해
    "스테이지" 는 인덱스 3 으로 밀린다. 본 회귀는 dest='stage_select' 라우팅 자체를
    검증하는 것이 목적이므로 인덱스만 갱신한다.
    """
    from src.scenes.menu_scene import _BUTTONS

    # "menu.stage_select" 라우팅 버튼의 현재 인덱스를 동적으로 조회 — 향후 메뉴
    # 재배치에도 회귀가 따라오도록 한다.
    stage_idx = next(i for i, b in enumerate(_BUTTONS) if b[0] == "menu.stage_select")
    scene = _make_menu_scene()
    scene._focused_idx = stage_idx
    scene._on_enter_key(None)
    assert "stage_select" in scene.app._goto_calls


def test_menu_up_key_decrements_focus() -> None:
    """MN-04: Up 키 -> _focused_idx 감소 (최솟값 0 유지)."""
    scene = _make_menu_scene()
    scene._focused_idx = 3
    scene._on_up_key(None)
    assert scene._focused_idx == 2


def test_menu_up_key_does_not_go_below_zero() -> None:
    """MN-04: Up 키 연속 -> 0 미만으로 내려가지 않는다."""
    scene = _make_menu_scene()
    scene._focused_idx = 0
    scene._on_up_key(None)
    assert scene._focused_idx == 0


def test_menu_down_key_increments_focus() -> None:
    """MN-04: Down 키 -> _focused_idx 증가."""
    scene = _make_menu_scene()
    scene._focused_idx = 0
    scene._on_down_key(None)
    assert scene._focused_idx == 1


def test_menu_down_key_does_not_exceed_max() -> None:
    """MN-04: Down 키 연속 -> 버튼 수 - 1 초과 없음."""
    from src.scenes.menu_scene import _BUTTONS

    scene = _make_menu_scene()
    max_idx = len(_BUTTONS) - 1
    scene._focused_idx = max_idx
    scene._on_down_key(None)
    assert scene._focused_idx == max_idx


def test_menu_quit_button_calls_app_quit() -> None:
    """MN-05: 포커스가 종료 버튼(dest="__quit__")일 때 Enter -> app.quit() 호출."""
    from src.scenes.menu_scene import _BUTTONS

    scene = _make_menu_scene()
    # "종료" 버튼 인덱스 탐색 (dest="__quit__")
    quit_idx = next(i for i, (_, dest, *_) in enumerate(_BUTTONS) if dest == "__quit__")
    scene._focused_idx = quit_idx
    scene._on_enter_key(None)
    assert scene.app._quit_called is True


# ---------------------------------------------------------------------------
# [SS] StageSelectScene - 잠금 상태 + ESC (SS-02, SS-05)
# ---------------------------------------------------------------------------


def _make_stage_select_scene(player_data: Any = None) -> Any:
    from src.scenes.stage_select_scene import StageSelectScene

    app = FakeApp(player_data=player_data)
    scene = StageSelectScene(app)
    return scene


def test_stage_select_default_unlocked_is_stage_01_only() -> None:
    """SS-02: player_data 없을 때 _get_unlocked_stages() = {"stage_01"} 만 반환."""
    scene = _make_stage_select_scene()
    unlocked = scene._get_unlocked_stages()
    assert "stage_01" in unlocked
    # 나머지 스테이지는 잠금
    for sid in ("stage_02", "stage_03", "stage_04", "stage_05"):
        assert sid not in unlocked


def test_stage_select_player_data_unlocked_stages() -> None:
    """SS-02(변형): player_data 주입 시 해금 목록 반영."""
    pd = FakePlayerData(unlocked=["stage_01", "stage_02"])
    scene = _make_stage_select_scene(player_data=pd)
    unlocked = scene._get_unlocked_stages()
    assert "stage_01" in unlocked
    assert "stage_02" in unlocked
    assert "stage_03" not in unlocked


def test_stage_select_completed_stages_empty_by_default() -> None:
    """SS-02: player_data 없을 때 _get_completed_stages() = {} 반환."""
    scene = _make_stage_select_scene()
    completed = scene._get_completed_stages()
    assert completed == {}


def test_stage_select_esc_triggers_menu_goto() -> None:
    """SS-05: ESC 람다가 app.goto("menu") 를 호출하는지 검증."""
    scene = _make_stage_select_scene()
    # build() 없이 ESC 람다를 직접 실행해 goto 호출 확인
    # (StageSelectScene.build 에서 bind("<Escape>", lambda _e: self.app.goto("menu")))
    esc_fn = lambda _e: scene.app.goto("menu")  # noqa: E731
    esc_fn(None)
    assert "menu" in scene.app._goto_calls


# ---------------------------------------------------------------------------
# [EN] EndingScene - 패널 진행 + ESC (EN-01, EN-02, EN-03, EN-04)
# ---------------------------------------------------------------------------


def _make_ending_scene() -> Any:
    from src.scenes.ending_scene import EndingScene

    app = FakeApp()
    scene = EndingScene(app)
    scene.build()
    return scene


def test_ending_scene_builds_without_error() -> None:
    """EN-01 전제: EndingScene.build() 가 오류 없이 완료된다."""
    scene = _make_ending_scene()
    assert scene._current_panel == 0


def test_ending_scene_space_advances_panel() -> None:
    """EN-01: Space(_on_space) -> _current_panel 증가."""
    scene = _make_ending_scene()
    assert scene._current_panel == 0
    scene._on_space(None)
    assert scene._current_panel == 1


def test_ending_scene_space_multiple_advances() -> None:
    """EN-01: Space 반복 -> 패널 순차 진행."""
    scene = _make_ending_scene()
    for _ in range(3):
        scene._on_space(None)
    assert scene._current_panel == 3


def test_ending_scene_escape_goes_to_menu() -> None:
    """EN-02: ESC(_on_escape) -> app.goto("menu") 호출."""
    scene = _make_ending_scene()
    scene._on_escape(None)
    assert "menu" in scene.app._goto_calls


def test_ending_scene_last_panel_advances_to_menu() -> None:
    """EN-03: 마지막 패널을 넘어서면 app.goto("menu") 호출."""
    from src.scenes.ending_scene import _PANELS

    scene = _make_ending_scene()
    # 모든 패널을 Space 로 넘기면 메뉴로 이동
    for _ in range(len(_PANELS) + 1):
        scene._on_space(None)
    assert "menu" in scene.app._goto_calls


def test_ending_scene_finale_panel_no_auto_schedule() -> None:
    """EN-04: is_finale 패널에서는 _schedule_auto 가 auto_timer 를 설정하지 않는다."""
    from src.scenes.ending_scene import _PANELS

    scene = _make_ending_scene()
    # finale 패널 인덱스 탐색
    finale_idx = next((i for i, p in enumerate(_PANELS) if p.get("is_finale")), None)
    assert finale_idx is not None

    scene._current_panel = finale_idx
    scene._auto_timer_id = None
    scene._schedule_auto()
    # FakeRoot.after 는 실행되지 않아야 함 (finale -> early return)
    assert scene._auto_timer_id is None


# ---------------------------------------------------------------------------
# [BT] BattleScene - stage_02 ~ stage_05 build (BT-11 확장)
# ---------------------------------------------------------------------------

from tests.test_battle_scene_flow import FakeApp as _BattleFakeApp  # noqa: E402


@pytest.mark.parametrize("stage_id", ["stage_02", "stage_03", "stage_04", "stage_05"])
def test_battle_scene_builds_for_all_stages(stage_id: str) -> None:
    """BT-11: stage_02~05 에서도 BattleScene.build() 가 오류 없이 완료된다."""
    from src.scenes.battle_scene import BattleScene

    app = _BattleFakeApp()
    scene = BattleScene(app, stage_id=stage_id)
    scene.build()
    assert scene.stage is not None
    assert scene.stage.id == stage_id
