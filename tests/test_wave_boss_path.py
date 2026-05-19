"""WaveSystem 보스 path resolution 테스트 (Issue #43, DECISION-DL-P5P-001).

과거: 보스 spawn 시 path_id 가 ``"p_main"`` 으로 하드코딩되어, stage_03/04/05
처럼 ``p_main`` 이 존재하지 않는 다중-경로 스테이지에서는 spawn 실패.

현재 우선순위 (DECISION-DL-P5P-001):
  (1) ``wave_def.boss_path`` 명시
  (2) 같은 wave 의 ``spawns`` 첫 항목 ``path``
  (3) ``load(paths=...)`` 로 주입된 첫 path id
  (4) ``world['waypoints']`` (dict) 의 첫 키
  (5) 기존 호환 ``"p_main"`` fallback

본 모듈은 5 가지 우선순위 + 실제 stage_01~05 보스 wave 가 정상 spawn 되는지
가드한다. WV-01~04 회귀 매트릭스 시나리오 자동화.
"""

from __future__ import annotations

from typing import Any

from src.data.loader import PathDef, WaveDef, WaveSpawn, load_stage
from src.systems.wave import WaveSystem

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _make_wave(
    delay_s: float = 0.0,
    boss: str | None = "tang_boss",
    boss_path: str | None = None,
    spawn_path: str | None = None,
) -> WaveDef:
    """보스 wave 생성. spawn_path 가 None 이면 spawns 비어 있음."""
    spawns: tuple[WaveSpawn, ...]
    if spawn_path is None:
        spawns = ()
    else:
        spawns = (WaveSpawn(type="tang_soldier", count=1, interval_s=1.0, path=spawn_path),)
    return WaveDef(delay_s=delay_s, spawns=spawns, boss=boss, boss_path=boss_path)


def _drive_to_spawn(ws: WaveSystem, dt_step: float = 0.05, max_steps: int = 100) -> None:
    """첫 wave 시작이 트리거될 때까지 update 반복."""
    for _ in range(max_steps):
        if ws._wave_started or ws.all_clear:
            return
        ws.update(dt_step)


# ---------------------------------------------------------------------------
# WV-01: boss_path 명시 (옵션 a)
# ---------------------------------------------------------------------------


def test_wv01_boss_path_explicit_used() -> None:
    """wave_def.boss_path 가 명시되면 그 값을 그대로 사용."""
    spawned: list[tuple[str, str]] = []
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(
        (_make_wave(boss="tang_boss", boss_path="p_explicit", spawn_path="p_other"),),
        paths=(PathDef(id="p_other", waypoints=((0.0, 0.0), (1.0, 1.0))),),
    )
    _drive_to_spawn(ws)
    assert ("tang_boss", "p_explicit") in spawned


# ---------------------------------------------------------------------------
# WV-02: boss_path 미지정 + spawns 첫 path 차용
# ---------------------------------------------------------------------------


def test_wv02_boss_uses_first_spawn_path_when_boss_path_missing() -> None:
    """boss_path 가 None 이면 같은 wave 의 첫 spawn path 를 사용."""
    spawned: list[tuple[str, str]] = []
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(
        (_make_wave(boss="tang_boss", boss_path=None, spawn_path="p_gorge"),),
        paths=(PathDef(id="p_gorge", waypoints=((0.0, 0.0), (10.0, 10.0))),),
    )
    _drive_to_spawn(ws)
    assert ("tang_boss", "p_gorge") in spawned


# ---------------------------------------------------------------------------
# WV-03: boss_path & spawns 모두 미지정 → load(paths=) 첫 path
# ---------------------------------------------------------------------------


def test_wv03_boss_uses_load_paths_first_when_no_spawns() -> None:
    """boss-only wave (spawns 비어 있음) 일 때 load(paths=) 첫 path id 사용."""
    spawned: list[tuple[str, str]] = []
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(
        (_make_wave(boss="tang_boss", boss_path=None, spawn_path=None),),
        paths=(
            PathDef(id="p_first", waypoints=((0.0, 0.0), (1.0, 1.0))),
            PathDef(id="p_second", waypoints=((0.0, 100.0), (1.0, 101.0))),
        ),
    )
    _drive_to_spawn(ws)
    assert ("tang_boss", "p_first") in spawned


# ---------------------------------------------------------------------------
# WV-04: paths 미주입 + world['waypoints'] dict 첫 키
# ---------------------------------------------------------------------------


def test_wv04_boss_uses_world_waypoints_first_key_when_no_paths() -> None:
    """load 에 paths 가 주입되지 않았고 spawns 도 비어 있을 때 world dict 첫 키 사용."""
    spawned: list[tuple[str, str]] = []
    world: dict[str, Any] = {
        "events": None,
        "waypoints": {"p_world_first": [(0.0, 0.0), (1.0, 1.0)], "p_world_second": [(0.0, 100.0)]},
    }
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load((_make_wave(boss="tang_boss", boss_path=None, spawn_path=None),))  # paths 주입 안 함
    _drive_to_spawn(ws)
    assert ("tang_boss", "p_world_first") in spawned


# ---------------------------------------------------------------------------
# WV-05: 완전 미지정 → "p_main" 호환 fallback
# ---------------------------------------------------------------------------


def test_wv05_boss_falls_back_to_p_main_legacy() -> None:
    """모든 컨텍스트가 없으면 "p_main" 으로 fallback (기존 동작 보존)."""
    spawned: list[tuple[str, str]] = []
    world: dict[str, Any] = {"events": None}  # waypoints 키조차 없음
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load((_make_wave(boss="tang_boss", boss_path=None, spawn_path=None),))
    _drive_to_spawn(ws)
    assert ("tang_boss", "p_main") in spawned


# ---------------------------------------------------------------------------
# 실 stage 01~05 보스 wave 가 path 존재 확인
# ---------------------------------------------------------------------------


def _last_wave_boss(stage_id: str) -> tuple[Any, ...]:
    """주어진 stage 의 마지막 wave 의 (boss, resolved_path, paths_ids) 반환."""
    stage = load_stage(stage_id)
    # 보스 wave 를 찾는다 (마지막 wave 가 보통 보스).
    boss_wave = None
    for w in stage.waves:
        if w.boss:
            boss_wave = w
    return stage, boss_wave


def test_stage_01_boss_spawns_on_valid_path() -> None:
    """stage_01: 보스 wave 가 정상 spawn (단일 경로 p_main 유지)."""
    spawned: list[tuple[str, str]] = []
    stage, _ = _last_wave_boss("stage_01")
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(stage.waves, paths=stage.paths)
    # 모든 wave 를 진행
    for _ in range(2000):
        ws.update(0.05)
        if ws.all_clear:
            break
    path_ids = {p.id for p in stage.paths}
    boss_spawns = [(t, p) for t, p in spawned if t.startswith("tang_") and "boss" not in t]  # any non-soldier
    # 정확히는 stage_01 의 보스인 tang_scout_captain 으로 확인.
    boss_calls = [c for c in spawned if c[0] == "tang_scout_captain"]
    assert len(boss_calls) == 1
    assert boss_calls[0][1] in path_ids
    _ = boss_spawns  # silence linter


def test_stage_03_boss_spawns_on_valid_path() -> None:
    """stage_03: 보스 wave 가 정상 spawn (다중 경로, p_main 미정의)."""
    spawned: list[tuple[str, str]] = []
    stage, _ = _last_wave_boss("stage_03")
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(stage.waves, paths=stage.paths)
    for _ in range(2000):
        ws.update(0.05)
        if ws.all_clear:
            break
    path_ids = {p.id for p in stage.paths}
    boss_calls = [c for c in spawned if c[0] == "tang_night_raider"]
    assert len(boss_calls) == 1, f"stage_03 보스 spawn 누락: spawns={spawned[:5]}..."
    assert boss_calls[0][1] in path_ids, f"stage_03 보스 path={boss_calls[0][1]} 가 paths={path_ids} 에 없음"
    # 호환: "p_main" 이 결과로 나와선 안 됨 — stage_03 에는 p_main 이 없음.
    assert boss_calls[0][1] != "p_main"


def test_stage_04_boss_spawns_on_valid_path() -> None:
    """stage_04: 보스 wave 가 정상 spawn (3 경로, p_main 미정의)."""
    spawned: list[tuple[str, str]] = []
    stage, _ = _last_wave_boss("stage_04")
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(stage.waves, paths=stage.paths)
    for _ in range(3000):
        ws.update(0.05)
        if ws.all_clear:
            break
    path_ids = {p.id for p in stage.paths}
    boss_calls = [c for c in spawned if c[0] == "tang_elite_battering_ram"]
    assert len(boss_calls) == 1
    assert boss_calls[0][1] in path_ids
    assert boss_calls[0][1] != "p_main"


def test_stage_05_boss_spawns_on_valid_path() -> None:
    """stage_05: 보스 wave 가 정상 spawn (4 경로, p_main 미정의)."""
    spawned: list[tuple[str, str]] = []
    stage, _ = _last_wave_boss("stage_05")
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(stage.waves, paths=stage.paths)
    for _ in range(4000):
        ws.update(0.05)
        if ws.all_clear:
            break
    path_ids = {p.id for p in stage.paths}
    boss_calls = [c for c in spawned if c[0] == "tang_taizong"]
    assert len(boss_calls) == 1
    assert boss_calls[0][1] in path_ids
    assert boss_calls[0][1] != "p_main"


# ---------------------------------------------------------------------------
# 안전 fallback: load(paths=) 빈 튜플 / None
# ---------------------------------------------------------------------------


def test_load_paths_none_does_not_break_legacy() -> None:
    """load(paths=None) 호출 시 기존 동작 보존 (paths 없이도 load 가능)."""
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.load((_make_wave(boss="tang_boss", boss_path=None, spawn_path="p_old"),))
    assert ws.waves != ()  # 정상 로드


def test_load_paths_empty_tuple_falls_back_safely() -> None:
    """load(paths=()) 도 graceful — 보스 path 가 다른 우선순위로 결정됨."""
    spawned: list[tuple[str, str]] = []
    world: dict[str, Any] = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load(
        (_make_wave(boss="tang_boss", boss_path=None, spawn_path="p_safe"),),
        paths=(),
    )
    _drive_to_spawn(ws)
    # spawns 첫 path 가 사용됨.
    assert ("tang_boss", "p_safe") in spawned


# ---------------------------------------------------------------------------
# WaveDef 데이터클래스 기본값 보존 (boss_path 옵션)
# ---------------------------------------------------------------------------


def test_wave_def_boss_path_defaults_to_none() -> None:
    """WaveDef 기본 boss_path=None — 기존 코드 호환."""
    wave = WaveDef(delay_s=0.0, spawns=(), boss="tang_boss")
    assert wave.boss_path is None


def test_wave_def_boss_path_explicit() -> None:
    """WaveDef boss_path 명시 시 그대로 저장."""
    wave = WaveDef(delay_s=0.0, spawns=(), boss="tang_boss", boss_path="p_custom")
    assert wave.boss_path == "p_custom"
