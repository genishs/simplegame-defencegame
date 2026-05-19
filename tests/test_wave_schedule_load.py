"""stage_01.json 로딩 → WaveSystem 구성 검증 (tk 비의존)."""

from __future__ import annotations

from src.data.loader import WaveDef, WaveSpawn, load_stage
from src.systems.wave import WaveSystem


def test_load_stage_returns_waves() -> None:
    """stage_01.json에 웨이브 정의가 있다."""
    stage = load_stage("stage_01")
    assert len(stage.waves) > 0


def test_wave_def_has_spawns() -> None:
    """각 웨이브에 스폰이 있다."""
    stage = load_stage("stage_01")
    for wave in stage.waves:
        assert isinstance(wave, WaveDef)
        assert len(wave.spawns) > 0 or wave.boss is not None


def test_wave_spawn_fields() -> None:
    """WaveSpawn의 모든 필드가 유효하다."""
    stage = load_stage("stage_01")
    for wave in stage.waves:
        for spawn in wave.spawns:
            assert isinstance(spawn, WaveSpawn)
            assert spawn.count > 0
            assert spawn.interval_s > 0
            assert spawn.type
            assert spawn.path


def test_wave_system_load_from_stage() -> None:
    """WaveSystem.load()에 stage.waves를 주입할 수 있다."""
    stage = load_stage("stage_01")
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(stage.waves)

    assert len(ws.waves) == len(stage.waves)
    assert ws.current_wave == 0
    assert ws.all_clear is False


def test_wave_system_update_starts_first_wave() -> None:
    """delay_s 이후 첫 웨이브가 시작된다."""
    stage = load_stage("stage_01")
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(stage.waves)

    first_delay = stage.waves[0].delay_s
    ws.update(first_delay + 0.1)
    assert ws.current_wave == 1


def test_wave_system_spawn_callback_called() -> None:
    """WaveSystem이 spawn_callback을 호출한다."""
    stage = load_stage("stage_01")
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(stage.waves)

    spawned: list[tuple[str, str]] = []
    ws.spawn_callback = lambda t, p: spawned.append((t, p))

    first_delay = stage.waves[0].delay_s
    first_interval = stage.waves[0].spawns[0].interval_s

    ws.update(first_delay + first_interval + 0.1)
    assert len(spawned) >= 1


def test_wave_with_boss_field() -> None:
    """boss 필드가 있는 웨이브를 파싱한다."""
    stage = load_stage("stage_01")
    boss_waves = [w for w in stage.waves if w.boss is not None]
    assert len(boss_waves) >= 1
    for w in boss_waves:
        assert isinstance(w.boss, str)


def test_all_clear_after_all_waves() -> None:
    """빠른 dt로 모든 웨이브를 완주하면 all_clear=True."""
    stage = load_stage("stage_01")
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(stage.waves)

    # 충분히 긴 dt를 여러 번 줘서 모든 웨이브 완주
    for _ in range(200):
        if ws.all_clear:
            break
        ws.update(1.0)

    assert ws.all_clear is True
