"""양만춘 S1/S2/S3 스킬 시스템 회귀 가드 (Issue #61, DECISION-DL-P5S-001).

GDD §3.2:
  S1 일점사   — 단일 강타 200 + 0.5s 기절, 쿨다운 12s
  S2 독려의 함성 — 반경 250px 아군 공속 +30% / 10s, 쿨다운 25s
  S3 화살비   — 지정 지점 반경 180px 5초간 초당 30 데미지, 쿨다운 40s

도메인 가드: 효과 적용은 Hero/도메인에서, Effect/Projectile 스폰은 BattleScene.
본 모듈은 도메인 계층(Hero/Ally/Enemy/PathingSystem)만으로 검증한다.
"""

from __future__ import annotations

import math

import pytest

from src.data.loader import EnemyDef, UnitDef
from src.entities.ally import Ally
from src.entities.enemy import Enemy
from src.entities.hero import Hero
from src.systems.pathing import PathingSystem

pytestmark = pytest.mark.regression_p4


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _enemy(x: float, y: float, hp: int = 500, speed: float = 100.0) -> Enemy:
    edef = EnemyDef(
        id="dummy",
        name="dummy",
        hp=hp,
        speed=speed,
        armor=0,
        damage_to_castle=1,
        gold_drop=1,
        sprite="x",
    )
    return Enemy(x=x, y=y, enemy_def=edef, path_id="p0")


def _ally(x: float, y: float, atk_speed: float = 1.0) -> Ally:
    udef = UnitDef(
        id="archer",
        name="궁수",
        cost=10,
        hp=50,
        atk=10,
        atk_speed=atk_speed,
        range=200,
        sprite="a",
        size=(1, 1),
    )
    return Ally(x=x, y=y, unit_def=udef)


# ---------------------------------------------------------------------------
# S1 일점사
# ---------------------------------------------------------------------------


def test_s1_deals_damage_and_stun_to_nearest_enemy() -> None:
    hero = Hero(x=0.0, y=0.0)
    near = _enemy(100.0, 0.0, hp=500)
    far = _enemy(2000.0, 0.0, hp=500)
    res = hero.cast_s1([near, far])
    assert res["fired"] is True
    assert res["target"] is near
    assert near.hp == 300  # 500 - 200
    assert near.stun_timer == pytest.approx(0.5)
    assert far.hp == 500  # 사거리 밖, 무영향


def test_s1_blocked_during_cooldown() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(100.0, 0.0)
    assert hero.cast_s1([e])["fired"] is True
    # 즉시 재시전 불가
    res2 = hero.cast_s1([e])
    assert res2["fired"] is False
    assert res2["reason"] == "cooldown"
    assert hero.s1_ready is False


def test_s1_cooldown_recovers_after_update() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(100.0, 0.0)
    hero.cast_s1([e])
    assert hero.s1_cooldown == pytest.approx(12.0)
    hero.update(12.0)
    assert hero.s1_ready is True
    assert hero.s1_cooldown == pytest.approx(0.0)


def test_s1_no_target_does_not_fire_or_consume_cooldown() -> None:
    hero = Hero(x=0.0, y=0.0)
    far = _enemy(5000.0, 0.0)
    res = hero.cast_s1([far])
    assert res["fired"] is False
    assert res["reason"] == "no_target"
    assert hero.s1_ready is True  # 쿨다운 소모 안 함


def test_s1_lethal_marks_enemy_dying() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(100.0, 0.0, hp=150)  # 200 데미지 > 150
    hero.cast_s1([e])
    assert e.dying is True


# ---------------------------------------------------------------------------
# S1 기절 → PathingSystem 이동 정지
# ---------------------------------------------------------------------------


def test_stun_stops_pathing_movement() -> None:
    enemy = _enemy(0.0, 0.0, speed=100.0)
    enemy.stun_timer = 0.5
    world = {"enemies": [enemy], "waypoints": {"p0": [(0.0, 0.0), (1000.0, 0.0)]}}
    ps = PathingSystem(world)
    ps.update(0.2)
    # 기절 중 — 이동하지 않음, 타이머 감소
    assert enemy.x == pytest.approx(0.0)
    assert enemy.stun_timer == pytest.approx(0.3)


def test_enemy_moves_after_stun_expires() -> None:
    enemy = _enemy(0.0, 0.0, speed=100.0)
    enemy.stun_timer = 0.1
    world = {"enemies": [enemy], "waypoints": {"p0": [(0.0, 0.0), (1000.0, 0.0)]}}
    ps = PathingSystem(world)
    ps.update(0.1)  # 기절 소진(이동 0)
    assert enemy.x == pytest.approx(0.0)
    assert enemy.stun_timer == pytest.approx(0.0)
    ps.update(0.5)  # 이제 이동 가능
    assert enemy.x > 0.0


# ---------------------------------------------------------------------------
# S2 독려의 함성
# ---------------------------------------------------------------------------


def test_s2_buffs_allies_in_radius_only() -> None:
    hero = Hero(x=0.0, y=0.0)
    near = _ally(100.0, 0.0, atk_speed=1.0)
    far = _ally(400.0, 0.0, atk_speed=1.0)  # 250px 밖
    res = hero.cast_s2([near, far])
    assert res["fired"] is True
    assert near in res["buffed"]
    assert far not in res["buffed"]
    assert near.atk_speed_mult == pytest.approx(1.3)
    assert far.atk_speed_mult == pytest.approx(1.0)


def test_s2_buff_shortens_ally_cooldown() -> None:
    hero = Hero(x=0.0, y=0.0)
    ally = _ally(50.0, 0.0, atk_speed=1.0)
    hero.cast_s2([ally])
    ally.reset_fire()
    # 공속 1.0 * 1.3 = 1.3 → 쿨다운 1/1.3 ≈ 0.769s
    assert ally.cooldown == pytest.approx(1.0 / 1.3, rel=1e-3)
    assert ally.effective_atk_speed == pytest.approx(1.3)


def test_s2_buff_expires_after_duration() -> None:
    hero = Hero(x=0.0, y=0.0)
    ally = _ally(50.0, 0.0)
    hero.cast_s2([ally])
    assert ally.atk_speed_mult == pytest.approx(1.3)
    # attack_tick 으로 10s 경과 → 만료
    ally.attack_tick(10.0)
    assert ally.atk_speed_mult == pytest.approx(1.0)


def test_s2_cooldown_blocks_recast() -> None:
    hero = Hero(x=0.0, y=0.0)
    a = _ally(10.0, 0.0)
    assert hero.cast_s2([a])["fired"] is True
    assert hero.cast_s2([a])["fired"] is False
    assert hero.s2_cooldown == pytest.approx(25.0)


# ---------------------------------------------------------------------------
# S3 화살비
# ---------------------------------------------------------------------------


def test_s3_creates_active_zone() -> None:
    hero = Hero(x=0.0, y=0.0)
    res = hero.cast_s3(300.0, 300.0)
    assert res["fired"] is True
    assert len(hero.active_arrow_rains) == 1
    assert hero.s3_cooldown == pytest.approx(40.0)


def test_s3_dot_damages_enemies_in_radius() -> None:
    hero = Hero(x=0.0, y=0.0)
    inside = _enemy(300.0, 300.0, hp=500)
    outside = _enemy(900.0, 900.0, hp=500)
    hero.cast_s3(300.0, 300.0)
    # 1초 누적 틱(0.1 x 10) → 30 데미지
    for _ in range(10):
        hero.tick_active_skills(0.1, [inside, outside])
    assert inside.hp == pytest.approx(470, abs=1)  # 약 30 감소
    assert outside.hp == 500


def test_s3_zone_expires_after_duration() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(0.0, 0.0, hp=10_000)
    hero.cast_s3(0.0, 0.0)
    # 5초 경과 → 지대 소멸
    for _ in range(50):
        hero.tick_active_skills(0.1, [e])
    assert len(hero.active_arrow_rains) == 0
    # 약 5s * 30 = 150 데미지 누적 (정수 누적기 오차 ±2)
    assert e.hp == pytest.approx(10_000 - 150, abs=3)


def test_s3_total_dot_is_about_30_per_second() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(0.0, 0.0, hp=10_000)
    hero.cast_s3(0.0, 0.0)
    # 정확히 1초 (단일 큰 틱)
    hero.tick_active_skills(1.0, [e])
    assert e.hp == pytest.approx(10_000 - 30, abs=1)


# ---------------------------------------------------------------------------
# 자동 모드 AI (auto_cast)
# ---------------------------------------------------------------------------


def test_auto_cast_uses_s1_on_enemy_in_range() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(100.0, 0.0, hp=500)
    results = hero.auto_cast([], [e])
    skills = {r["skill"] for r in results}
    assert "s1" in skills
    assert e.hp == 300


def test_auto_cast_uses_s3_on_enemy_cluster() -> None:
    hero = Hero(x=0.0, y=0.0)
    # 3명이 한 지점에 군집 + 영웅 교전 사거리(380px) 내 — 방어선 위협으로 반응.
    cluster = [_enemy(300.0, 0.0), _enemy(320.0, 0.0), _enemy(310.0, 20.0)]
    results = hero.auto_cast([], cluster)
    skills = {r["skill"] for r in results}
    assert "s3" in skills
    assert len(hero.active_arrow_rains) == 1


def test_auto_cast_skips_s3_for_distant_cluster() -> None:
    """원거리(스폰 지점) 군집에는 화살비를 쓰지 않는다 — 스폰 캠핑 방지."""
    hero = Hero(x=0.0, y=0.0)
    distant = [_enemy(1000.0, 0.0), _enemy(1020.0, 0.0), _enemy(1010.0, 20.0)]
    results = hero.auto_cast([], distant)
    skills = {r["skill"] for r in results}
    assert "s3" not in skills
    assert len(hero.active_arrow_rains) == 0


def test_auto_cast_uses_s2_when_allies_grouped() -> None:
    hero = Hero(x=0.0, y=0.0)
    allies = [_ally(50.0, 0.0), _ally(60.0, 0.0)]  # 2명 250px 내
    results = hero.auto_cast(allies, [])
    skills = {r["skill"] for r in results}
    assert "s2" in skills
    assert all(a.atk_speed_mult == pytest.approx(1.3) for a in allies)


def test_auto_cast_no_skill_when_conditions_unmet() -> None:
    hero = Hero(x=0.0, y=0.0)
    # 적/아군 모두 없음 → 아무 스킬도 발동 안 함
    assert hero.auto_cast([], []) == []
    # 아군 1명(임계 2 미만) + 적 1명이 사거리 밖 → S1/S2/S3 모두 미발동
    lone_ally = _ally(50.0, 0.0)
    far_enemy = _enemy(5000.0, 0.0)
    assert hero.auto_cast([lone_ally], [far_enemy]) == []


def test_densest_cluster_returns_none_below_threshold() -> None:
    hero = Hero(x=0.0, y=0.0)
    # 멀리 떨어진 적 2명 — 군집 3 미만
    scattered = [_enemy(0.0, 0.0), _enemy(1000.0, 1000.0)]
    assert hero._densest_enemy_cluster(scattered, 180.0, 3) is None


def test_densest_cluster_finds_center() -> None:
    hero = Hero(x=0.0, y=0.0)
    cluster = [_enemy(500.0, 500.0), _enemy(510.0, 505.0), _enemy(495.0, 510.0)]
    center = hero._densest_enemy_cluster(cluster, 180.0, 3)
    assert center is not None
    assert math.isclose(center[0], 500.0, abs_tol=20.0)


# ---------------------------------------------------------------------------
# 쿨다운 통합 — update 가 3종 모두 감소
# ---------------------------------------------------------------------------


def test_update_decrements_all_skill_cooldowns() -> None:
    hero = Hero(x=0.0, y=0.0)
    e = _enemy(100.0, 0.0)
    a = _ally(50.0, 0.0)
    hero.cast_s1([e])
    hero.cast_s2([a])
    hero.cast_s3(0.0, 0.0)
    hero.update(5.0)
    assert hero.s1_cooldown == pytest.approx(7.0)
    assert hero.s2_cooldown == pytest.approx(20.0)
    assert hero.s3_cooldown == pytest.approx(35.0)


# ---------------------------------------------------------------------------
# BattleScene 통합 — 키 바인딩 + 시각 스폰 (Issue #61)
# ---------------------------------------------------------------------------


def _key_event(keysym: str):
    import types

    return types.SimpleNamespace(keysym=keysym)


def _placed_enemy_in_hero_range(scene):
    """영웅 사거리 안에 적 1마리 배치 후 반환."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy

    edef = EnemyDef(id="x", name="x", hp=500, speed=0, armor=0, damage_to_castle=1, gold_drop=8, sprite="x")
    hero = scene.world["hero"]
    e = Enemy(x=hero.x + 100.0, y=hero.y, enemy_def=edef, path_id="p_main")
    scene.world["enemies"].append(e)
    return e


def test_battlescene_q_key_casts_s1() -> None:
    from tests.battle_scene_simulator import BattleSceneSimulator

    scene = BattleSceneSimulator("stage_01").build_scene()
    enemy = _placed_enemy_in_hero_range(scene)
    n_fx = len(scene._skill_fx)
    scene._on_skill_key(_key_event("q"))
    assert enemy.hp == 300  # 500 - 200 (S1)
    assert enemy.stun_timer == pytest.approx(0.5)
    # 강타 transient FX 등록 (빔+임팩트)
    assert len(scene._skill_fx) > n_fx
    assert any(fx["kind"] == "s1" for fx in scene._skill_fx)
    assert scene.world["hero"].s1_cooldown == pytest.approx(12.0)


def test_battlescene_e_key_casts_s3() -> None:
    from tests.battle_scene_simulator import BattleSceneSimulator

    scene = BattleSceneSimulator("stage_01").build_scene()
    _placed_enemy_in_hero_range(scene)
    scene._on_skill_key(_key_event("e"))
    hero = scene.world["hero"]
    assert len(hero.active_arrow_rains) == 1
    assert hero.s3_cooldown == pytest.approx(40.0)


def test_battlescene_w_key_casts_s2() -> None:
    from tests.battle_scene_simulator import BattleSceneSimulator

    scene = BattleSceneSimulator("stage_01").build_scene()
    hero = scene.world["hero"]
    ally = _ally(hero.x + 30.0, hero.y)
    scene.world["allies"].append(ally)
    scene._on_skill_key(_key_event("w"))  # 이제 W 는 스킬 전용
    assert ally.atk_speed_mult == pytest.approx(1.3)
    assert hero.s2_cooldown == pytest.approx(25.0)


def test_battlescene_wasd_does_not_move_hero_in_manual_mode() -> None:
    """W/A/S/D 는 이동이 아니라 스킬 전용 — 수동 모드에서도 이동시키지 않는다."""
    from tests.battle_scene_simulator import BattleSceneSimulator

    scene = BattleSceneSimulator("stage_01").build_scene()
    scene._hero_direct_mode = True
    hero = scene.world["hero"]
    x0, y0 = hero.x, hero.y
    scene._on_hero_dir_key(_key_event("d"))
    scene._on_hero_dir_key(_key_event("w"))
    scene._apply_hero_manual_move(hero, 0.1)
    assert hero.x == pytest.approx(x0)
    assert hero.y == pytest.approx(y0)


def test_battlescene_render_draws_skill_overlay() -> None:
    """스킬 발동 후 render 가 오버레이(빔/임팩트/텍스트) 캔버스 아이템을 그린다."""
    from tests.battle_scene_simulator import BattleSceneSimulator

    sim = BattleSceneSimulator("stage_01")
    scene = sim.build_scene()
    _placed_enemy_in_hero_range(scene)
    scene._on_skill_key(_key_event("q"))  # S1 → transient FX 등록
    scene.render()
    canvas = scene.app.canvas
    texts = [kw.get("text") for (kind, _args, kw) in canvas.items.values() if kind == "text"]
    assert "일점사!" in texts  # S1 발동 라벨이 실제로 그려짐


def test_battlescene_render_draws_arrow_rain_zone() -> None:
    """S3 화살비 지대가 render 에서 채움 원 + 라벨로 표시된다."""
    from tests.battle_scene_simulator import BattleSceneSimulator

    sim = BattleSceneSimulator("stage_01")
    scene = sim.build_scene()
    _placed_enemy_in_hero_range(scene)
    scene._on_skill_key(_key_event("e"))  # S3 지대 생성
    scene.render()
    canvas = scene.app.canvas
    texts = [kw.get("text") for (kind, _args, kw) in canvas.items.values() if kind == "text"]
    assert "화살비" in texts


def test_battlescene_skill_keys_ignored_when_paused() -> None:
    from tests.battle_scene_simulator import BattleSceneSimulator

    scene = BattleSceneSimulator("stage_01").build_scene()
    enemy = _placed_enemy_in_hero_range(scene)
    scene._paused = True
    scene._on_skill_key(_key_event("q"))
    assert enemy.hp == 500  # 일시정지 중 발동 안 함
    assert scene.world["hero"].s1_ready is True


# ---------------------------------------------------------------------------
# HUD Q/W/E 스킬 슬롯 (Issue #61)
# ---------------------------------------------------------------------------


def test_hud_registers_skill_slots() -> None:
    from src.ui.hud import HUD
    from tests.test_hud_state_model import FakeCanvas, FakeScaler

    hud = HUD()
    hud.build(FakeCanvas(), FakeScaler())
    for skey in ("s1", "s2", "s3"):
        assert f"{skey}_slot_bg" in hud._ids
        assert f"{skey}_cooldown" in hud._ids


def test_hud_update_renders_skill_cooldowns() -> None:
    from src.ui.hud import HUD
    from tests.test_hud_state_model import FakeCanvas, FakeScaler

    canvas = FakeCanvas()
    hud = HUD()
    hud.build(canvas, FakeScaler())
    hud.update(
        {
            "s1_cooldown_s": 8.0,
            "s2_cooldown_s": 0.0,
            "s3_cooldown_s": 40.0,
        }
    )
    # s1: "8s" 표기, s2: "준비"
    assert canvas._configs[hud._ids["s1_cooldown"]]["text"] == "8s"
    assert canvas._configs[hud._ids["s2_cooldown"]]["text"] == "준비"
    assert canvas._configs[hud._ids["s3_cooldown"]]["text"] == "40s"
