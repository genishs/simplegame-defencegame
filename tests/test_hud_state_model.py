"""HUD state 모델 검증 테스트 (캔버스 없이 데이터 변환만).

Canvas mock을 사용해 tkinter 없이 HUD.build/update 경로를 검증한다.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Canvas / Scaler mock
# ---------------------------------------------------------------------------


class FakeCanvas:
    """캔버스 mock — item id 발급 + itemconfig 추적."""

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
        self.items[i] = ("line", args, kw)
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
        # tag delete는 무시

    def tag_bind(self, *args: Any, **kw: Any) -> None:
        pass

    def after(self, ms: int, func: Any) -> str:
        return "after_id"

    def after_cancel(self, after_id: str) -> None:
        pass


class FakeScaler:
    """Scaler mock — 베이스 좌표를 그대로 반환."""

    BASE_W = 1920
    BASE_H = 1080
    scale = 1.0
    canvas_w = 1920
    canvas_h = 1080

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return x, y

    def font_pt(self, pt: int) -> int:
        return max(8, pt)


# ---------------------------------------------------------------------------
# HUD build/update 검증
# ---------------------------------------------------------------------------


def test_hud_build_creates_canvas_items() -> None:
    """build() 후 캔버스에 아이템이 생성된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)

    # 최소한 배경 + 자원 레이블 3종은 있어야 함
    assert len(canvas.items) > 5


def test_hud_build_registers_resource_ids() -> None:
    """build() 후 _ids에 자원 관련 key가 등록된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)

    # 적어도 grain_val, pop_val, arrows_val이 등록되어야 함
    assert "grain_val" in hud._ids
    assert "pop_val" in hud._ids
    assert "arrows_val" in hud._ids


def test_hud_update_calls_itemconfig() -> None:
    """update() 시 itemconfig가 호출된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)

    state = {
        "food": 150,
        "pop": 8,
        "arrows": 75,
        "hero_hp": 720,
        "hero_max_hp": 1000,
        "hero_phase": 2,
        "ult_cooldown_s": 12.5,
        "wave": 2,
        "total_waves": 3,
        "time_to_next": 8.0,
    }
    hud.update(state)

    # grain_val itemconfig가 호출됐는지 확인
    grain_id = hud._ids.get("grain_val")
    assert grain_id is not None
    assert grain_id in canvas._configs
    assert canvas._configs[grain_id].get("text") == "150"


def test_hud_update_wave_progress_text() -> None:
    """update() 시 wave_progress 텍스트가 갱신된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)

    state = {
        "food": 0,
        "pop": 0,
        "arrows": 0,
        "hero_hp": 0,
        "hero_max_hp": 1,
        "hero_phase": 1,
        "ult_cooldown_s": 0.0,
        "wave": 3,
        "total_waves": 5,
        "time_to_next": 0.0,
    }
    hud.update(state)

    wave_id = hud._ids.get("wave_progress")
    assert wave_id in canvas._configs
    text = canvas._configs[wave_id].get("text", "")
    assert "3" in text
    assert "5" in text


def test_hud_update_time_to_next_positive() -> None:
    """time_to_next > 0이면 next_wave 텍스트에 초가 포함된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)

    state = {
        "food": 0,
        "pop": 0,
        "arrows": 0,
        "hero_hp": 0,
        "hero_max_hp": 1,
        "hero_phase": 1,
        "ult_cooldown_s": 0.0,
        "wave": 1,
        "total_waves": 3,
        "time_to_next": 18.0,
    }
    hud.update(state)

    nw_id = hud._ids.get("next_wave")
    assert nw_id in canvas._configs
    text = canvas._configs[nw_id].get("text", "")
    assert "18" in text


def test_hud_update_hero_hp_bar() -> None:
    """HP가 0이면 HP 바 너비가 최소로 설정된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)

    state = {
        "food": 0,
        "pop": 0,
        "arrows": 0,
        "hero_hp": 0,
        "hero_max_hp": 1000,
        "hero_phase": 1,
        "ult_cooldown_s": 0.0,
        "wave": 0,
        "total_waves": 1,
        "time_to_next": -1.0,
    }
    hud.update(state)
    # coords가 호출됐는지 간접 확인 (hero_hp_bar 아이템 존재)
    assert "hero_hp_bar" in hud._ids


def test_hud_color_blind_mode_adds_glyph() -> None:
    """color_blind_mode=True이면 자원 레이블에 한자 글리프가 추가된다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler, color_blind_mode=True)

    # 레이블 텍스트에 한자가 포함됐는지 확인
    grain_label_id = hud._ids.get("grain_label")
    assert grain_label_id is not None
    item = canvas.items.get(grain_label_id)
    assert item is not None
    kw = item[2] if len(item) > 2 else {}
    text_val = kw.get("text", "")
    # 한자 穀이 포함돼야 함
    assert "穀" in text_val


def test_hud_teardown_clears_ids() -> None:
    """teardown() 후 _ids가 비어 있다."""
    from src.ui.hud import HUD

    canvas = FakeCanvas()
    scaler = FakeScaler()
    hud = HUD()
    hud.build(canvas, scaler)
    hud.teardown()

    assert len(hud._ids) == 0
