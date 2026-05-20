"""BattleScene을 Canvas mock으로 1틱 굴려서 시스템 호출 순서 검증 (tk 비의존).

실제 캔버스 없이 FakeCanvas + FakeApp으로 BattleScene의 오케스트레이션을
검증한다.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Fake 인프라
# ---------------------------------------------------------------------------


class FakeCanvas:
    def __init__(self) -> None:
        self.items: dict[int, Any] = {}
        self._next: int = 1

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

    def create_oval(self, *args: Any, **kw: Any) -> int:
        # Issue #51: TutorialScene 의 spotlight ring/circle 렌더 지원.
        i = self._next
        self._next += 1
        self.items[i] = ("oval", args, kw)
        return i

    def create_polygon(self, *args: Any, **kw: Any) -> int:
        # Issue #51: TutorialScene 의 spotlight 화살표 polygon 렌더 지원.
        i = self._next
        self._next += 1
        self.items[i] = ("polygon", args, kw)
        return i

    def itemconfig(self, i: int, **kw: Any) -> None:
        """기존 item 의 kw 에 새 kw 를 병합 (Issue #70/#71 가드 지원).

        rc.6 fix: hp 바 state 전환, HUD wave_progress 텍스트 갱신 등
        itemconfig 호출 결과를 테스트가 검증할 수 있도록 kw 를 누적한다.
        없는 item id 는 silently 무시 — 기존 동작 보존.
        """
        if i not in self.items:
            return
        kind, args, existing_kw = self.items[i]
        merged = dict(existing_kw)
        merged.update(kw)
        self.items[i] = (kind, args, merged)

    def coords(self, i: int, *args: Any) -> None:
        """기존 item 의 좌표 (args) 를 갱신 (Issue #71 hp 바 너비 가드 지원)."""
        if i not in self.items:
            return
        kind, _old_args, kw = self.items[i]
        self.items[i] = (kind, args, kw)

    def delete(self, i: Any) -> None:
        if isinstance(i, int):
            self.items.pop(i, None)

    def tag_bind(self, *args: Any, **kw: Any) -> None:
        pass

    def winfo_width(self) -> int:
        return 1920

    def winfo_height(self) -> int:
        return 1080

    def after(self, ms: int, func: Any) -> str:
        return "after_id"


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
    def publish(self, event: str, data: Any) -> None:
        pass


class FakeRoot:
    """tk.Tk mock — bind/unbind만 지원."""

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


class FakeSoundManager:
    """SoundManager stub — Phase 5.1 BGM 통합 후 FakeApp에서 사용."""

    def play_bgm(self, name: str, *, loop: bool = True, fade_in: float = 1.0) -> None:
        pass

    def stop_bgm(self, *, fade_out: float = 1.0) -> None:
        pass

    def set_bgm_volume(self, v: float) -> None:
        pass

    def play_sfx(self, name: str) -> None:
        pass

    def play_ui(self, name: str) -> None:
        pass

    def stop_all(self) -> None:
        pass

    def set_master_volume(self, v: float) -> None:
        pass

    def mute(self) -> None:
        pass

    def unmute(self) -> None:
        pass


class FakeApp:
    def __init__(self) -> None:
        self.canvas = FakeCanvas()
        self.scaler = FakeScaler()
        self.events = FakeEventBus()
        self.root = FakeRoot()
        self.sound = FakeSoundManager()  # Phase 5.1 BGM 통합 대응
        self._goto_calls: list[str] = []

    def goto(self, name: str, **kwargs: Any) -> None:
        self._goto_calls.append(name)

    def quit(self) -> None:
        pass


# ---------------------------------------------------------------------------
# BattleScene 기본 흐름
# ---------------------------------------------------------------------------


def _make_battle_scene(stage_id: str = "stage_01") -> Any:
    """FakeApp으로 BattleScene을 생성하고 build()까지 완료."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id=stage_id)
    scene.build()
    return scene


def test_battle_scene_builds_without_error() -> None:
    """build()가 오류 없이 완료된다."""
    scene = _make_battle_scene()
    assert scene.stage is not None


def test_battle_scene_loads_wave_system() -> None:
    """build() 후 WaveSystem에 웨이브가 로드된다."""
    scene = _make_battle_scene()
    assert len(scene.wave.waves) > 0


def test_battle_scene_update_calls_wave_system() -> None:
    """update(dt)가 WaveSystem.update를 호출한다."""
    scene = _make_battle_scene()

    original_update = scene.wave.update
    call_log: list[float] = []

    def _tracked_update(dt: float, world: Any = None) -> None:
        call_log.append(dt)
        original_update(dt, world)

    scene.wave.update = _tracked_update

    scene.update(0.016)
    assert len(call_log) == 1
    assert abs(call_log[0] - 0.016) < 1e-9


def test_battle_scene_update_calls_pathing_system() -> None:
    """update(dt)가 PathingSystem.update를 호출한다."""
    scene = _make_battle_scene()

    call_log: list[float] = []
    original_update = scene.pathing.update

    def _tracked(dt: float, world: Any = None) -> None:
        call_log.append(dt)
        original_update(dt, world)

    scene.pathing.update = _tracked
    scene.update(0.016)
    assert len(call_log) == 1


def test_battle_scene_update_calls_combat_system() -> None:
    """update(dt)가 CombatSystem.update를 호출한다."""
    scene = _make_battle_scene()

    call_log: list[float] = []
    original_update = scene.combat.update

    def _tracked(dt: float, world: Any = None) -> None:
        call_log.append(dt)
        original_update(dt, world)

    scene.combat.update = _tracked
    scene.update(0.016)
    assert len(call_log) == 1


def test_battle_scene_paused_skips_update() -> None:
    """_paused=True이면 시스템 update가 호출되지 않는다."""
    scene = _make_battle_scene()
    scene._paused = True

    wave_calls: list[float] = []
    scene.wave.update = lambda dt, world=None: wave_calls.append(dt)

    scene.update(0.016)
    assert len(wave_calls) == 0


def test_battle_scene_escape_key_toggles_pause() -> None:
    """Esc 키가 _toggle_pause를 트리거한다."""
    scene = _make_battle_scene()

    assert scene._paused is False
    scene._on_escape(None)
    # PauseDialog가 show() 됐으면 _paused=True
    assert scene._paused is True


def test_battle_scene_m_key_toggles_hero_mode() -> None:
    """M 키가 _hero_direct_mode를 토글한다."""
    scene = _make_battle_scene()

    assert scene._hero_direct_mode is False
    scene._on_m_key(None)
    assert scene._hero_direct_mode is True
    scene._on_m_key(None)
    assert scene._hero_direct_mode is False


def test_battle_scene_wave_all_clear_and_no_enemies_triggers_victory() -> None:
    """wave.all_clear=True이고 enemies가 없으면 승리 판정된다."""
    scene = _make_battle_scene()

    scene.wave.all_clear = True
    scene.world["enemies"] = []
    scene.world["lives"] = 20
    scene.world["goals_reached"] = 0

    scene._check_end_conditions()
    assert scene._game_over is True


def test_battle_scene_goals_reached_triggers_defeat() -> None:
    """goals_reached >= lives이면 패배 판정된다."""
    scene = _make_battle_scene()

    scene.world["goals_reached"] = 20
    scene.world["lives"] = 20

    scene._check_end_conditions()
    assert scene._game_over is True


def test_battle_scene_system_update_order() -> None:
    """update() 내 시스템 호출 순서: wave → pathing → combat."""
    scene = _make_battle_scene()

    call_order: list[str] = []

    original_wave = scene.wave.update
    original_path = scene.pathing.update
    original_comb = scene.combat.update

    scene.wave.update = lambda dt, world=None: (call_order.append("wave"), original_wave(dt, world))
    scene.pathing.update = lambda dt, world=None: (call_order.append("pathing"), original_path(dt, world))
    scene.combat.update = lambda dt, world=None: (call_order.append("combat"), original_comb(dt, world))

    scene.update(0.016)

    assert call_order.index("wave") < call_order.index("pathing")
    assert call_order.index("pathing") < call_order.index("combat")
