"""영웅 직접조작 모드 (M키 토글) 테스트 — Issue #4.

검증 항목:
- M키로 ``_hero_direct_mode`` 가 토글된다.
- 수동 모드에서 방향키/WASD 입력이 hero.x/y 를 변경한다.
- 자동 모드에서는 방향키 입력이 hero 좌표를 변경하지 않는다.
- 수동 모드에서 ``BattleScene.update`` 가 ``hero.update`` 자동 AI 를
  호출하지 않는다 (직접 이동 분기로 들어간다).
- 모드 토글 시 ``hero.manual_mode.toggled`` 이벤트가 publish 된다.
- 모드 토글 시 캔버스 상태 라벨 텍스트가 갱신된다.

tk 비의존 FakeApp/FakeCanvas 인프라 재사용.
"""

from __future__ import annotations

from typing import Any

from tests.test_battle_scene_flow import FakeApp


class _RecordingEventBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def publish(self, event: str, data: Any) -> None:
        self.events.append((event, data))


def _make_scene_with_bus() -> Any:
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    app.events = _RecordingEventBus()
    scene = BattleScene(app, stage_id="stage_01")
    # world 가 이미 init 에서 events 를 복사했으므로 동기화.
    scene.world["events"] = app.events
    scene.build()
    return scene


def _key_event(keysym: str) -> Any:
    """간단한 keysym 보유 이벤트 모의."""

    class _E:
        pass

    e = _E()
    e.keysym = keysym  # type: ignore[attr-defined]
    return e


# ---------------------------------------------------------------------------
# 1. M키 토글
# ---------------------------------------------------------------------------


def test_m_key_toggles_direct_mode() -> None:
    scene = _make_scene_with_bus()
    assert scene._hero_direct_mode is False
    scene._on_m_key(None)
    assert scene._hero_direct_mode is True
    scene._on_m_key(None)
    assert scene._hero_direct_mode is False


def test_m_key_publishes_toggle_event() -> None:
    scene = _make_scene_with_bus()
    bus = scene.world["events"]
    scene._on_m_key(None)
    scene._on_m_key(None)
    events = [e for e in bus.events if e[0] == "hero.manual_mode.toggled"]
    assert len(events) == 2
    assert events[0][1] == {"on": True}
    assert events[1][1] == {"on": False}


def test_m_key_updates_status_label() -> None:
    """모드 토글 시 캔버스 상태 라벨 텍스트가 갱신된다 (itemconfig 호출 예외 무).

    FakeCanvas.itemconfig 는 no-op 이므로 텍스트 변경을 직접 관측할 수 없으나,
    토글 흐름이 예외 없이 통과하고 _manual_mode_label_id 가 유지되는지 확인.
    """
    scene = _make_scene_with_bus()
    assert scene._manual_mode_label_id is not None
    assert scene._manual_mode_label_id in scene.app.canvas.items

    scene._on_m_key(None)
    scene._on_m_key(None)
    # 라벨 id 는 그대로 유지.
    assert scene._manual_mode_label_id in scene.app.canvas.items


# ---------------------------------------------------------------------------
# 2. 수동 모드에서 방향키/WASD 이동
# ---------------------------------------------------------------------------


def test_arrow_right_moves_hero_in_manual_mode() -> None:
    from src.entities.hero import Hero

    scene = _make_scene_with_bus()
    hero = Hero(x=100.0, y=100.0, hp=800)
    scene.world["hero"] = hero
    scene._on_m_key(None)  # 모드 ON.
    assert scene._hero_direct_mode is True

    scene._on_hero_dir_key(_key_event("Right"))
    # update 한 틱 → 이동 적용.
    scene.update(0.1)
    assert hero.x > 100.0


def test_wasd_moves_hero_in_manual_mode() -> None:
    from src.entities.hero import Hero

    scene = _make_scene_with_bus()
    hero = Hero(x=500.0, y=500.0, hp=800)
    scene.world["hero"] = hero
    scene._on_m_key(None)  # 모드 ON.

    # d → 우측 이동.
    scene._on_hero_dir_key(_key_event("d"))
    scene.update(0.1)
    assert hero.x > 500.0
    x_after_d = hero.x

    # w → 위로 이동 (y 감소).
    scene._on_hero_dir_key(_key_event("w"))
    scene.update(0.1)
    assert hero.y < 500.0
    assert hero.x == x_after_d  # x 는 이번 틱에 변하지 않음.


def test_diagonal_input_normalizes_speed() -> None:
    """대각선 입력에서도 속도가 일정 (대각선이 1.41배 빠르지 않게)."""
    from src.entities.hero import Hero

    scene = _make_scene_with_bus()
    hero = Hero(x=0.0, y=0.0, hp=800)
    scene.world["hero"] = hero
    scene._on_m_key(None)

    scene._on_hero_dir_key(_key_event("Right"))
    scene._on_hero_dir_key(_key_event("Up"))
    scene.update(1.0)
    # speed=150, 1초 → 거리 약 150 (정규화 적용 시).
    dist = (hero.x**2 + hero.y**2) ** 0.5
    assert abs(dist - 150.0) < 1e-6


# ---------------------------------------------------------------------------
# 3. 자동 모드에서 방향키 무시
# ---------------------------------------------------------------------------


def test_arrow_key_ignored_in_auto_mode() -> None:
    from src.entities.hero import Hero

    scene = _make_scene_with_bus()
    hero = Hero(x=100.0, y=100.0, hp=800)
    scene.world["hero"] = hero
    # 자동 모드 그대로.
    assert scene._hero_direct_mode is False

    scene._on_hero_dir_key(_key_event("Right"))
    scene.update(0.1)
    assert hero.x == 100.0


# ---------------------------------------------------------------------------
# 4. 수동 모드에서는 자동 AI(Hero.update) 가 호출되지 않는다
# ---------------------------------------------------------------------------


def test_manual_mode_still_ticks_hero_cooldowns() -> None:
    """수동 모드에서도 hero.update 는 호출되어 쿨다운/페이즈가 흐른다.

    Issue #58 / DECISION-DL-P4D-007: 수동 모드에서도 영웅 평타 자동 공격이
    작동해야 하므로 hero.update(쿨다운 감소) 호출은 유지된다. 자동 AI 분기는
    auto_attack 의 사거리 검사로 자체 제어된다.

    이전 정책 (DECISION-DL-P3-3-003): 수동 모드에서는 hero.update 미호출 →
    평타 쿨다운이 멈춰 영웅이 적과 전투 불가 (검수 결함 #58). 본 결정으로 갱신.
    """
    from src.entities.hero import Hero

    scene = _make_scene_with_bus()
    hero = Hero(x=100.0, y=100.0, hp=800)
    scene.world["hero"] = hero

    call_log: list[float] = []
    original_update = hero.update

    def _tracked(dt: float) -> None:
        call_log.append(dt)
        original_update(dt)

    hero.update = _tracked  # type: ignore[method-assign]

    # 자동 모드: update 호출됨.
    scene.update(0.05)
    assert len(call_log) == 1

    # 수동 모드: update 도 호출됨 (Issue #58 fix).
    scene._on_m_key(None)
    scene.update(0.05)
    assert len(call_log) == 2, "수동 모드에서도 평타 쿨다운을 위해 hero.update 호출 필요"


def test_manual_mode_ignores_input_when_paused() -> None:
    """일시정지 상태에서는 방향 입력이 영웅을 이동시키지 않는다."""
    from src.entities.hero import Hero

    scene = _make_scene_with_bus()
    hero = Hero(x=100.0, y=100.0, hp=800)
    scene.world["hero"] = hero
    scene._on_m_key(None)  # 모드 ON.
    scene._paused = True

    scene._on_hero_dir_key(_key_event("Right"))
    scene.update(0.1)  # paused 이므로 update 본체가 일찍 return.
    assert hero.x == 100.0
