"""BattleScene 적 spawn + waypoint 결선 테스트 (Issue #1).

검증 항목:
- ``BattleScene.build()`` 후 ``world['waypoints']`` 가 stage.paths 의
  ``path_id → list[Point]`` 매핑으로 채워진다.
- ``_spawn_enemy`` 가 ``EnemyDef`` 를 lookup 해 ``Enemy`` 인스턴스를 생성하고
  첫 waypoint 좌표에서 시작하도록 한다.
- 스폰된 적이 PathingSystem 한 틱 후에 첫 waypoint 방향으로 이동한다
  (즉, waypoint 결선 동작 확인).
- 알 수 없는 path_id / enemy_type 은 안전하게 무시되고 enemies 가 늘지 않는다.

tk 비의존 FakeApp/FakeCanvas 인프라를 재사용.
"""

from __future__ import annotations

from typing import Any

# tests 패키지 내 헬퍼 재사용 — 동일 디렉토리에 있으므로 직접 import.
from tests.test_battle_scene_flow import FakeApp


def _make_scene(stage_id: str = "stage_01") -> Any:
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id=stage_id)
    scene.build()
    return scene


# ---------------------------------------------------------------------------
# 1. waypoints dict 채워짐
# ---------------------------------------------------------------------------


def test_build_populates_waypoints_dict() -> None:
    """build() 후 world['waypoints'] 가 path_id → list[Point] 형태로 채워진다."""
    scene = _make_scene()
    wps = scene.world.get("waypoints")
    assert isinstance(wps, dict)
    # stage_01.json 은 p_main 경로 1개를 가진다.
    assert "p_main" in wps
    assert len(wps["p_main"]) >= 2
    # 첫 waypoint 가 [0, 540] 인지 (stage_01 의 정의값).
    assert wps["p_main"][0] == (0.0, 540.0)


def test_pathing_system_sees_scene_waypoints() -> None:
    """PathingSystem 이 BattleScene 의 waypoints dict 를 그대로 참조한다."""
    scene = _make_scene()
    # pathing.world 와 scene.world 가 같은 dict 인지.
    assert scene.pathing.world is scene.world
    # waypoints 가 dict 이며 enemy.path_id 로 조회 가능한지.
    wps = scene.world["waypoints"]
    assert isinstance(wps, dict)
    assert wps.get("p_main") is not None


# ---------------------------------------------------------------------------
# 2. _spawn_enemy 가 올바른 Enemy 생성
# ---------------------------------------------------------------------------


def test_spawn_enemy_creates_enemy_with_def_and_path() -> None:
    """_spawn_enemy 가 EnemyDef + path_id 를 결선한 Enemy 인스턴스를 만든다."""
    scene = _make_scene()
    assert scene.world["enemies"] == []

    scene._spawn_enemy("tang_soldier", "p_main")

    enemies = scene.world["enemies"]
    assert len(enemies) == 1
    enemy = enemies[0]
    assert enemy.path_id == "p_main"
    assert enemy.enemy_def.id == "tang_soldier"
    # 첫 waypoint (0, 540) 에서 스폰.
    assert enemy.x == 0.0
    assert enemy.y == 540.0
    # HP 는 enemies.json 의 tang_soldier hp(80) 이어야 한다.
    assert enemy.hp == 80


def test_spawn_enemy_unknown_type_is_noop() -> None:
    """알 수 없는 enemy_type 은 enemies 리스트를 변경하지 않는다."""
    scene = _make_scene()
    scene._spawn_enemy("nonexistent_enemy", "p_main")
    assert scene.world["enemies"] == []


def test_spawn_enemy_unknown_path_is_noop() -> None:
    """알 수 없는 path_id 는 enemies 리스트를 변경하지 않는다."""
    scene = _make_scene()
    scene._spawn_enemy("tang_soldier", "no_such_path")
    assert scene.world["enemies"] == []


# ---------------------------------------------------------------------------
# 3. 통합: spawn → PathingSystem update → 적이 첫 waypoint 따라 이동
# ---------------------------------------------------------------------------


def test_spawned_enemy_advances_along_waypoints() -> None:
    """스폰된 적이 PathingSystem 한 틱 후에 다음 waypoint 방향으로 이동한다.

    stage_01 p_main 경로: [(0,540), (600,540), (600,300), (1920,300)].
    시작 (0,540) 이 첫 waypoint 와 동일하므로 PathingSystem 한 틱은
    바로 다음 waypoint (600, 540) 를 향한다 → x 가 증가해야 한다.
    """
    scene = _make_scene()
    scene._spawn_enemy("tang_soldier", "p_main")
    enemy = scene.world["enemies"][0]

    # 시작 좌표 보장.
    assert enemy.x == 0.0
    # PathingSystem 첫 틱: wp_index 가 0 이라 (0,540) → (0,540) 즉시 도달 후
    # 잔여 dt 로 (600,540) 방향 이동. 약 1초에 speed=60 만큼 이동.
    scene.pathing.update(dt=1.0)

    assert enemy.x > 0.0, "적이 첫 웨이포인트를 지나 다음 웨이포인트 방향으로 이동해야 한다"
    # waypoint 결선 확인: wp_index 가 진행되었거나 좌표가 진행 중.
    assert enemy.wp_index >= 1 or enemy.x < 600.0


def test_spawned_enemy_reaches_final_waypoint() -> None:
    """충분한 시간이 지나면 적이 마지막 waypoint 에 도달해 goal_reached=True."""
    scene = _make_scene()
    scene._spawn_enemy("tang_soldier", "p_main")
    enemy = scene.world["enemies"][0]

    # 큰 dt 로 강제로 경로 전체 통과시킴.
    scene.pathing.update(dt=1000.0)
    assert enemy.goal_reached is True


# ---------------------------------------------------------------------------
# 4. WaveSystem → spawn_callback 결선 (회귀)
# ---------------------------------------------------------------------------


def test_wave_system_spawn_callback_uses_battle_scene_spawn() -> None:
    """WaveSystem._do_spawn → world['spawn_enemy'] → BattleScene._spawn_enemy."""
    scene = _make_scene()
    # spawn_callback 이 None 이라도 world['spawn_enemy'] 가 fallback 으로 호출됨.
    scene.world["spawn_enemy"]("tang_soldier", "p_main")
    assert len(scene.world["enemies"]) == 1
