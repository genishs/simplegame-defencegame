"""PauseDialog / ResultDialog 상태머신 테스트 (Canvas mock 사용)."""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# FakeCanvas (공통)
# ---------------------------------------------------------------------------


class FakeCanvas:
    def __init__(self) -> None:
        self.items: dict[int, tuple[Any, ...]] = {}
        self._next: int = 1
        self._configs: dict[int, dict[str, Any]] = {}

    def create_rectangle(self, *args: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("rect", args, kw)
        return i

    def create_text(self, *args: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("text", args, kw)
        return i

    def create_line(self, *args: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        return i

    def itemconfig(self, i: int, **kw: Any) -> None:
        if i not in self._configs:
            self._configs[i] = {}
        self._configs[i].update(kw)

    def coords(self, i: int, *args: Any) -> None:
        pass

    def delete(self, i: Any) -> None:
        if isinstance(i, int):
            self.items.pop(i, None)

    def tag_bind(self, *args: Any, **kw: Any) -> None:
        pass

    def after(self, ms: int, func: Any) -> str:
        return "after_id"


# ---------------------------------------------------------------------------
# PauseDialog 상태머신
# ---------------------------------------------------------------------------


def test_pause_dialog_starts_not_visible() -> None:
    """PauseDialog는 생성 직후 visible=False."""
    from src.ui.dialog import PauseDialog

    c = FakeCanvas()
    pd = PauseDialog(c, None, on_resume=lambda: None, on_quit=lambda: None)
    assert pd.visible is False


def test_pause_dialog_show_makes_visible() -> None:
    """show() 후 visible=True, 캔버스 아이템 생성됨."""
    from src.ui.dialog import PauseDialog

    c = FakeCanvas()
    pd = PauseDialog(c, None, on_resume=lambda: None, on_quit=lambda: None)
    pd.show()
    assert pd.visible is True
    assert len(c.items) > 0


def test_pause_dialog_hide_removes_items() -> None:
    """hide() 후 visible=False, _ids가 비어 있음."""
    from src.ui.dialog import PauseDialog

    c = FakeCanvas()
    pd = PauseDialog(c, None, on_resume=lambda: None, on_quit=lambda: None)
    pd.show()
    initial_count = len(c.items)
    assert initial_count > 0

    pd.hide()
    assert pd.visible is False
    assert len(pd._ids) == 0


def test_pause_dialog_double_show_no_duplicate() -> None:
    """show()를 두 번 호출해도 중복 생성되지 않는다."""
    from src.ui.dialog import PauseDialog

    c = FakeCanvas()
    pd = PauseDialog(c, None, on_resume=lambda: None, on_quit=lambda: None)
    pd.show()
    count_after_first = len(c.items)
    pd.show()  # 두 번째 호출 — 이미 visible이므로 무시
    assert len(c.items) == count_after_first


def test_pause_dialog_resume_callback_called() -> None:
    """on_resume 콜백이 _on_resume에 저장된다."""
    from src.ui.dialog import PauseDialog

    called: list[bool] = []
    c = FakeCanvas()
    pd = PauseDialog(c, None, on_resume=lambda: called.append(True), on_quit=lambda: None)
    pd.show()
    pd._on_resume()
    assert called == [True]


def test_pause_dialog_hide_before_show_is_safe() -> None:
    """show() 없이 hide()를 호출해도 오류 없음."""
    from src.ui.dialog import PauseDialog

    c = FakeCanvas()
    pd = PauseDialog(c, None, on_resume=lambda: None, on_quit=lambda: None)
    pd.hide()  # 안전해야 함
    assert pd.visible is False


# ---------------------------------------------------------------------------
# ResultDialog 상태머신
# ---------------------------------------------------------------------------


def test_result_dialog_victory_visible() -> None:
    """ResultDialog(victory=True).show() → visible=True + 아이템 생성."""
    from src.ui.dialog import ResultDialog

    c = FakeCanvas()
    rd = ResultDialog(
        c,
        None,
        victory=True,
        stats={"stars": 3, "fame": 9, "grain": 200, "waves_survived": 3},
        on_next=lambda: None,
        on_retry=lambda: None,
        on_menu=lambda: None,
    )
    rd.show()
    assert rd.visible is True
    assert len(c.items) > 0


def test_result_dialog_defeat_visible() -> None:
    """ResultDialog(victory=False).show() → visible=True."""
    from src.ui.dialog import ResultDialog

    c = FakeCanvas()
    rd = ResultDialog(
        c,
        None,
        victory=False,
        stats={"waves_survived": 2},
        on_next=lambda: None,
        on_retry=lambda: None,
        on_menu=lambda: None,
    )
    rd.show()
    assert rd.visible is True


def test_result_dialog_hide_clears_ids() -> None:
    """ResultDialog.hide() 후 _ids 비어 있음."""
    from src.ui.dialog import ResultDialog

    c = FakeCanvas()
    rd = ResultDialog(
        c,
        None,
        victory=True,
        stats={"stars": 2, "fame": 6, "grain": 100, "waves_survived": 2},
        on_next=lambda: None,
        on_retry=lambda: None,
        on_menu=lambda: None,
    )
    rd.show()
    rd.hide()
    assert rd.visible is False
    assert len(rd._ids) == 0


def test_result_dialog_callbacks_stored() -> None:
    """on_next/on_retry/on_menu 콜백이 저장된다."""
    from src.ui.dialog import ResultDialog

    nxt: list[int] = []
    rty: list[int] = []
    mnu: list[int] = []

    c = FakeCanvas()
    rd = ResultDialog(
        c,
        None,
        victory=True,
        stats={"stars": 1, "fame": 3, "grain": 50, "waves_survived": 1},
        on_next=lambda: nxt.append(1),
        on_retry=lambda: rty.append(1),
        on_menu=lambda: mnu.append(1),
    )
    rd._on_next()
    rd._on_retry()
    rd._on_menu()
    assert nxt == [1]
    assert rty == [1]
    assert mnu == [1]


def test_result_dialog_stars_0_to_3() -> None:
    """stars 0~3 모두 오류 없이 show()된다."""
    from src.ui.dialog import ResultDialog

    for stars in range(4):
        c = FakeCanvas()
        rd = ResultDialog(
            c,
            None,
            victory=True,
            stats={"stars": stars, "fame": stars * 3, "grain": 100, "waves_survived": 1},
            on_next=lambda: None,
            on_retry=lambda: None,
            on_menu=lambda: None,
        )
        rd.show()
        assert rd.visible is True
        rd.hide()
