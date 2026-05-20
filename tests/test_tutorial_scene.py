"""TutorialScene 단위 테스트 (Phase 4, Issue #26).

DESIGN:
- FakeCanvas/FakeApp 으로 tk 비의존 검증 (테스트 패턴은 test_battle_scene_flow 참조).
- 8 단계 흐름, 스킵 다이얼로그, 메뉴 재진입, 자동 진입 조건, save_slot flag.
- tmp_path 픽스처로 save_slot 격리.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.regression_p4

# ---------------------------------------------------------------------------
# Fake 인프라
# ---------------------------------------------------------------------------


class FakeCanvas:
    def __init__(self) -> None:
        self.items: dict[int, Any] = {}
        self._next: int = 1

    def _new_item(self, kind: str, args: Any, kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = (kind, args, kw)
        return i

    def create_rectangle(self, *args: Any, **kw: Any) -> int:
        return self._new_item("rect", args, kw)

    def create_text(self, *args: Any, **kw: Any) -> int:
        return self._new_item("text", args, kw)

    def create_line(self, *args: Any, **kw: Any) -> int:
        return self._new_item("line", args, kw)

    def create_oval(self, *args: Any, **kw: Any) -> int:
        return self._new_item("oval", args, kw)

    def create_polygon(self, *args: Any, **kw: Any) -> int:
        return self._new_item("polygon", args, kw)

    def itemconfig(self, i: int, **kw: Any) -> None:
        pass

    def coords(self, i: int, *args: Any) -> None:
        pass

    def delete(self, i: Any) -> None:
        if isinstance(i, int):
            self.items.pop(i, None)

    def tag_bind(self, *args: Any, **kw: Any) -> None:
        pass

    def winfo_width(self) -> int:
        return 1920

    def winfo_height(self) -> int:
        return 1080


class FakeScaler:
    canvas_w = 1920
    canvas_h = 1080

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return x, y

    def font_pt(self, pt: int) -> int:
        return max(8, pt)


class FakeRoot:
    def __init__(self) -> None:
        self._bindings: dict[str, Any] = {}

    def bind(self, key: str, fn: Any) -> None:
        self._bindings[key] = fn

    def unbind(self, key: str) -> None:
        self._bindings.pop(key, None)


class FakeApp:
    def __init__(self) -> None:
        self.canvas = FakeCanvas()
        self.scaler = FakeScaler()
        self.root = FakeRoot()
        self.goto_calls: list[str] = []

    def goto(self, name: str, **kw: Any) -> None:
        self.goto_calls.append(name)


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_save_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """ANSISEONG_HOME 을 tmp_path 로 격리해 사용자 홈 오염 방지."""
    monkeypatch.setenv("ANSISEONG_HOME", str(tmp_path))
    return tmp_path / "save_slot.json"


@pytest.fixture
def scene(isolated_save_path: Path) -> Any:
    from src.scenes.tutorial_scene import TutorialScene

    app = FakeApp()
    s = TutorialScene(app)
    s.build()
    return s


# ---------------------------------------------------------------------------
# 1. 빌드 / 초기 상태
# ---------------------------------------------------------------------------


def test_tutorial_scene_builds_at_step_1(scene: Any) -> None:
    assert scene.step == 1
    # 단계 1 본문이 그려졌는가 (텍스트 아이템이 1개 이상)
    has_text = any(v[0] == "text" for v in scene.app.canvas.items.values())
    assert has_text


def test_tutorial_scene_has_skip_button(scene: Any) -> None:
    """우상단 스킵 버튼이 존재."""
    # tag 로 등록된 텍스트 중 라벨 "튜토리얼 종료" 포함 여부
    rendered_texts = [kw.get("text") for kind, args, kw in scene.app.canvas.items.values() if kind == "text"]
    assert any("종료" in (t or "") for t in rendered_texts)


# ---------------------------------------------------------------------------
# 2. 단계 진행 (인터랙티브)
# ---------------------------------------------------------------------------


def test_tutorial_step_1_to_2_via_cta(scene: Any) -> None:
    """단계 1 패시브 → CTA 클릭 → 단계 2."""
    assert scene.step == 1
    scene.trigger_cta_click()
    assert scene.step == 2


def test_tutorial_step_2_clickthrough(scene: Any) -> None:
    """단계 2: 곡식 HUD 클릭 → 단계 3."""
    scene.trigger_cta_click()  # 1 → 2
    assert scene.step == 2
    scene.trigger_step2_done()
    assert scene.step == 3


def test_tutorial_step_3_buildzone(scene: Any) -> None:
    """단계 3: 궁수 배치 완료 → 단계 4."""
    for _ in range(2):  # 1 → 2 → 3
        scene.trigger_cta_click() if scene.step == 1 else scene.trigger_step2_done()
    assert scene.step == 3
    scene.trigger_step3_done()
    assert scene.step == 4


def test_tutorial_step_4_cta_disabled_until_mock_wave_ends(scene: Any) -> None:
    """단계 4 진입 직후 CTA 비활성. mock wave 후 활성화."""
    # 1 → 2 → 3 → 4
    scene.trigger_cta_click()
    scene.trigger_step2_done()
    scene.trigger_step3_done()
    assert scene.step == 4
    # 비활성 상태
    assert scene._cta_enabled is False
    # CTA 클릭은 무시
    scene.trigger_cta_click()
    assert scene.step == 4
    # mock wave 진행 (2 spawn × 1.5s = 3초 이상)
    for _ in range(20):
        scene.update(0.2)
    assert scene._mock_wave_done is True
    assert scene._cta_enabled is True
    # 이제 CTA 클릭 → 단계 5
    scene.trigger_cta_click()
    assert scene.step == 5


def test_tutorial_step_5_m_key(scene: Any) -> None:
    """단계 5: M 키 입력 → 단계 6."""
    # 1 → 2 → 3 → 4
    scene.trigger_cta_click()
    scene.trigger_step2_done()
    scene.trigger_step3_done()
    # 4 → 5 via mock wave
    for _ in range(20):
        scene.update(0.2)
    scene.trigger_cta_click()
    assert scene.step == 5
    scene._on_m_key(None)
    assert scene.step == 6


def test_tutorial_step_6_space_toggle_cycle(scene: Any) -> None:
    """단계 6: Space 2회 → 단계 7."""
    # 단계 6 까지 빠르게
    scene.trigger_cta_click()
    scene.trigger_step2_done()
    scene.trigger_step3_done()
    for _ in range(20):
        scene.update(0.2)
    scene.trigger_cta_click()
    scene._on_m_key(None)
    assert scene.step == 6
    scene._on_space(None)
    assert scene.step == 6  # 한 번 만 누름
    scene._on_space(None)
    assert scene.step == 7


def test_tutorial_step_8_complete_to_stage_select(scene: Any) -> None:
    """단계 8 CTA → save_slot.tutorial_completed=True + stage_select 이동."""
    # 전부 진행
    scene.trigger_cta_click()  # 1→2
    scene.trigger_step2_done()  # 2→3
    scene.trigger_step3_done()  # 3→4
    for _ in range(20):
        scene.update(0.2)
    scene.trigger_cta_click()  # 4→5
    scene._on_m_key(None)  # 5→6
    scene._on_space(None)
    scene._on_space(None)  # 6→7
    scene.trigger_cta_click()  # 7→8
    assert scene.step == 8
    scene.trigger_cta_click()  # 8→complete
    assert scene.app.goto_calls == ["stage_select"]

    # save_slot 검증
    from src.core.save_slot import load_save_slot

    slot = load_save_slot()
    assert slot.tutorial_completed is True


# ---------------------------------------------------------------------------
# 3. 표시 시간 상한 fallback
# ---------------------------------------------------------------------------


def test_tutorial_step_2_time_limit_auto_advance(scene: Any) -> None:
    """단계 2 (인터랙티브) 표시 시간 상한 15초 후 자동 진행."""
    scene.trigger_cta_click()  # 1→2
    assert scene.step == 2
    # 16초 시뮬
    for _ in range(80):  # 80 × 0.2 = 16s
        scene.update(0.2)
    assert scene.step == 3


# ---------------------------------------------------------------------------
# 4. 스킵 다이얼로그
# ---------------------------------------------------------------------------


def test_tutorial_escape_opens_skip_dialog(scene: Any) -> None:
    assert scene.skip_dialog_visible is False
    scene._on_escape(None)
    assert scene.skip_dialog_visible is True


def test_tutorial_skip_no_keeps_step(scene: Any) -> None:
    """스킵 다이얼로그에서 '아니오' → 단계 유지."""
    scene._on_escape(None)
    assert scene.skip_dialog_visible is True
    scene._handle_skip_no()
    assert scene.skip_dialog_visible is False
    assert scene.step == 1


def test_tutorial_skip_yes_with_dont_show_again_saves_flag(scene: Any, isolated_save_path: Path) -> None:
    """체크박스 ON + '예' → save_slot.tutorial_dismissed=True."""
    scene._on_escape(None)
    dlg = scene._skip_dialog
    assert dlg is not None
    dlg.toggle_dont_show_again()
    assert dlg.dont_show_again is True
    scene._handle_skip_yes(True)
    assert scene.app.goto_calls == ["stage_select"]

    from src.core.save_slot import load_save_slot

    slot = load_save_slot()
    assert slot.tutorial_dismissed is True


def test_tutorial_skip_yes_without_checkbox_does_not_dismiss(scene: Any, isolated_save_path: Path) -> None:
    """체크박스 OFF + '예' → dismissed 변경 없음 (또는 False 유지)."""
    scene._on_escape(None)
    scene._handle_skip_yes(False)
    assert scene.app.goto_calls == ["stage_select"]

    from src.core.save_slot import load_save_slot

    slot = load_save_slot()
    assert slot.tutorial_dismissed is False


# ---------------------------------------------------------------------------
# 5. save_slot / 자동 진입
# ---------------------------------------------------------------------------


def test_save_slot_empty_triggers_auto_tutorial(isolated_save_path: Path) -> None:
    """저장 슬롯이 비어 있으면 decide_initial_scene → 'tutorial'."""
    from src.scenes.tutorial_scene import decide_initial_scene

    assert decide_initial_scene() == "tutorial"


def test_save_slot_dismissed_skips_tutorial(isolated_save_path: Path) -> None:
    """tutorial_dismissed=True 이면 menu 직행."""
    from src.core.save_slot import SaveSlot, save_save_slot
    from src.scenes.tutorial_scene import decide_initial_scene

    slot = SaveSlot(tutorial_dismissed=True)
    save_save_slot(slot)
    assert decide_initial_scene() == "menu"


def test_save_slot_completed_skips_tutorial(isolated_save_path: Path) -> None:
    """tutorial_completed=True 이면 menu 직행 (자동 진입 안 함)."""
    from src.core.save_slot import SaveSlot, save_save_slot
    from src.scenes.tutorial_scene import decide_initial_scene

    slot = SaveSlot(tutorial_completed=True)
    save_save_slot(slot)
    assert decide_initial_scene() == "menu"


def test_save_slot_json_io_roundtrip(isolated_save_path: Path) -> None:
    """SaveSlot 저장/로드 라운드트립."""
    from src.core.save_slot import SaveSlot, load_save_slot, save_save_slot

    s1 = SaveSlot(tutorial_dismissed=True, tutorial_completed=False, extra={"foo": "bar"})
    save_save_slot(s1)
    assert isolated_save_path.exists()
    raw = json.loads(isolated_save_path.read_text(encoding="utf-8"))
    assert raw["tutorial_dismissed"] is True
    assert raw["foo"] == "bar"

    s2 = load_save_slot()
    assert s2.tutorial_dismissed is True
    assert s2.extra.get("foo") == "bar"


def test_save_slot_corrupted_json_falls_back_to_empty(isolated_save_path: Path) -> None:
    """깨진 JSON 도 빈 슬롯으로 폴백."""
    from src.core.save_slot import load_save_slot

    isolated_save_path.parent.mkdir(parents=True, exist_ok=True)
    isolated_save_path.write_text("{not valid", encoding="utf-8")
    slot = load_save_slot()
    assert slot.tutorial_dismissed is False
    assert slot.tutorial_completed is False


# ---------------------------------------------------------------------------
# 6. 메뉴 재진입 / reset
# ---------------------------------------------------------------------------


def test_tutorial_reset_to_first_step(scene: Any) -> None:
    """reset_to_first_step() — 메뉴 재진입 시 호출 가능."""
    scene.trigger_cta_click()
    scene.trigger_step2_done()
    assert scene.step == 3
    scene.reset_to_first_step()
    assert scene.step == 1


def test_menu_scene_has_tutorial_button() -> None:
    """메뉴 씬 _BUTTONS 에 tutorial 라우팅이 포함되어 있는가."""
    from src.scenes.menu_scene import _BUTTONS

    keys = [b[0] for b in _BUTTONS]
    dests = [b[1] for b in _BUTTONS]
    assert "menu.tutorial" in keys
    assert "tutorial" in dests


# ---------------------------------------------------------------------------
# 7. 도메인 가드 — 의존성
# ---------------------------------------------------------------------------


def test_save_slot_has_no_tkinter_dependency() -> None:
    """save_slot.py 는 tkinter 를 import 하지 않는다 (도메인 가드).

    docstring 에 tkinter 단어가 등장해도 통과해야 하므로 실제 import 문만
    AST 로 검증한다.
    """
    import ast

    import src.core.save_slot as ss

    src_text = Path(ss.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("tkinter"), f"tkinter import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module is None or not node.module.startswith(
                "tkinter"
            ), f"tkinter import from found: {node.module}"


def test_tutorial_scene_teardown_clears_canvas(scene: Any) -> None:
    """teardown() 이 캔버스 아이템을 정리한다."""
    assert len(scene.app.canvas.items) > 0
    scene.teardown()
    # teardown 후 step_ids 비어 있음
    assert scene._step_ids == []


# ---------------------------------------------------------------------------
# 8. Issue #49 — 동그라미 안 콘텐츠 렌더 (DECISION-DL-P4D-001/002)
# ---------------------------------------------------------------------------


def _has_text_value(canvas: Any, value: str) -> bool:
    """canvas.items 에 텍스트 값이 등장하는가 (mock content 검증용)."""
    for kind, _args, kw in canvas.items.values():
        if kind == "text" and kw.get("text") == value:
            return True
    return False


def _items_with_tag(canvas: Any, tag_substr: str) -> list[tuple[str, Any, Any]]:
    """tags kwarg 에 특정 substring 이 포함된 아이템만 추출."""
    out: list[tuple[str, Any, Any]] = []
    for kind, args, kw in canvas.items.values():
        tags = kw.get("tags") or ()
        if any(tag_substr in (t or "") for t in tags):
            out.append((kind, args, kw))
    return out


def test_tutorial_step2_spotlight_has_inner_content(scene: Any) -> None:
    """Issue #49 fix — 단계 2 동그라미 안에 곡식 mock 콘텐츠가 그려져야 한다.

    DECISION-DL-P4D-001: spotlight 가 가리키는 위치가 비어 있으면 사용자는
    "동그라미 안에 아무것도 안 나옴" 으로 인식. mock placeholder 로 해소.
    """
    scene.trigger_cta_click()  # 1 → 2
    assert scene.step == 2

    # spotlight ring 존재
    rings = _items_with_tag(scene.app.canvas, "tutorial_spotlight_ring")
    assert len(rings) == 1, "단계 2 에서 spotlight ring 이 정확히 1개 그려져야 함"

    # mock content (곡식 라벨 + 값) 존재
    mock_items = _items_with_tag(scene.app.canvas, "tutorial_mock_content")
    assert len(mock_items) >= 2, "단계 2 spotlight 안에 mock 콘텐츠가 비어 있음 (Issue #49 회귀)"

    # 곡식 라벨이 텍스트로 등장 + 값 카운터 등장
    assert _has_text_value(scene.app.canvas, "곡식"), "단계 2 mock 콘텐츠에 '곡식' 라벨 누락"
    # 값 카운터 (어떤 숫자라도) 존재
    values = [
        kw.get("text")
        for kind, _a, kw in mock_items
        if kind == "text" and (kw.get("text") or "").isdigit()
    ]
    assert values, "단계 2 mock 콘텐츠에 곡식 값 카운터 누락"


def test_tutorial_step3_spotlight_has_buildzone_placeholder(scene: Any) -> None:
    """Issue #49 fix — 단계 3 buildzone spotlight 안에 빈 배치 칸 + '?' placeholder."""
    scene.trigger_cta_click()  # 1 → 2
    scene.trigger_step2_done()  # 2 → 3
    assert scene.step == 3

    mock_items = _items_with_tag(scene.app.canvas, "tutorial_mock_content")
    assert len(mock_items) >= 2, "단계 3 spotlight 안에 buildzone placeholder 누락"
    assert _has_text_value(scene.app.canvas, "?"), "단계 3 buildzone '?' placeholder 누락"


def test_tutorial_step5_spotlight_has_hero_placeholder(scene: Any) -> None:
    """Issue #49 fix — 단계 5 hero spotlight 안에 영웅 placeholder (원 + 글자)."""
    # 1 → 2 → 3 → 4 → 5
    scene.trigger_cta_click()
    scene.trigger_step2_done()
    scene.trigger_step3_done()
    for _ in range(20):
        scene.update(0.2)
    scene.trigger_cta_click()
    assert scene.step == 5

    mock_items = _items_with_tag(scene.app.canvas, "tutorial_mock_content")
    assert len(mock_items) >= 2, "단계 5 spotlight 안에 hero placeholder 누락"
    # 영웅 글자 "楊" (양만춘 약자) 등장
    assert _has_text_value(scene.app.canvas, "楊"), "단계 5 hero placeholder 글자 누락"


def test_tutorial_spotlight_z_order_mock_under_ring(scene: Any) -> None:
    """Issue #49 fix — Canvas z-order: mask → mock → ring → arrow → label.

    Canvas 의 z-order 는 item id 생성 순서. 단계 2 진입 시 mock content 의
    item id 가 ring item id 보다 작아야 ring 이 mock 위에 그려진다.
    DECISION-DL-P4D-002.
    """
    scene.trigger_cta_click()  # 1 → 2
    mock_items_ids = [
        iid
        for iid, (kind, _a, kw) in scene.app.canvas.items.items()
        if any("tutorial_mock_content" in (t or "") for t in (kw.get("tags") or ()))
    ]
    ring_ids = [
        iid
        for iid, (kind, _a, kw) in scene.app.canvas.items.items()
        if any("tutorial_spotlight_ring" in (t or "") for t in (kw.get("tags") or ()))
    ]
    assert mock_items_ids, "mock content 누락"
    assert ring_ids, "ring 누락"
    assert max(mock_items_ids) < min(ring_ids), (
        "z-order 위반: mock content 가 ring 보다 늦게 그려져 ring 을 가림"
    )


def test_tutorial_step1_no_spotlight_no_mock(scene: Any) -> None:
    """단계 1 은 hud_target=None — spotlight 와 mock content 모두 없어야 한다.

    사용자 보고("동그라미가 있는데 안이 비어")가 단계 1 자체에서 일어나지
    않음을 회귀 가드로 박는다.
    """
    assert scene.step == 1
    rings = _items_with_tag(scene.app.canvas, "tutorial_spotlight_ring")
    mock_items = _items_with_tag(scene.app.canvas, "tutorial_mock_content")
    assert rings == [], "단계 1 에 spotlight ring 이 그려지면 안 됨"
    assert mock_items == [], "단계 1 에 mock content 가 그려지면 안 됨"
