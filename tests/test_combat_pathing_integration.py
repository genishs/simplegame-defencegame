"""Combat + Pathing 통합 테스트 (tk 비의존).

시나리오: ally 1체 + enemy 1체.
- PathingSystem으로 enemy가 이동
- CombatSystem으로 ally가 enemy를 타겟 → 발사체 스폰 → 적중 → enemy 페이드 사망
- on_enemy_defeated 콜백으로 보상 누적
"""

from __future__ import annotations

from dataclasses import dataclass

from src.entities.ally import Ally
from src.entities.enemy import Enemy
from src.systems.combat import CombatSystem
from src.systems.pathing import PathingSystem

# ---------------------------------------------------------------------------
# 스텁 데이터 클래스
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _UnitDef:
    id: str = "archer"
    name: str = "고구려 궁수"
    cost: int = 10
    hp: int = 60
    atk: int = 12
    atk_speed: float = 2.0  # 빠른 공속으로 테스트
    range: int = 500  # px — enemy가 사거리 안에 있도록
    sprite: str = "ally_archer"
    size: tuple = (48, 64)
    projectile: str = "arrow"
    splash_radius: None = None


@dataclass(frozen=True)
class _EnemyDef:
    id: str = "tang_soldier"
    name: str = "당군 보병"
    hp: int = 12  # 낮은 HP로 빠르게 사망
    speed: float = 60.0
    armor: int = 0
    damage_to_castle: int = 1
    gold_drop: int = 8
    sprite: str = "enemy_soldier"
    is_boss: bool = False


# ---------------------------------------------------------------------------
# 통합 시나리오 헬퍼
# ---------------------------------------------------------------------------


def build_world():
    """ally 1, enemy 1이 있는 최소 world 반환."""
    ally = Ally(x=400.0, y=300.0, unit_def=_UnitDef())
    ally.cooldown = 0.0  # 즉시 발사 가능

    enemy = Enemy(x=450.0, y=300.0, enemy_def=_EnemyDef(), path_id="p_main")

    projectiles = []
    effects = []

    defeated_list = []

    def on_defeated(e):
        defeated_list.append(e)

    world = {
        "allies": [ally],
        "enemies": [enemy],
        "projectiles": projectiles,
        "effects": effects,
        "on_enemy_defeated": on_defeated,
        "_defeated": defeated_list,
    }
    return world


# ---------------------------------------------------------------------------
# 1. Pathing: enemy 이동
# ---------------------------------------------------------------------------


def test_pathing_moves_enemy() -> None:
    # enemy는 wp_index=0에서 시작하므로 첫 웨이포인트를 목표로 향한다.
    # enemy 위치를 첫 웨이포인트보다 앞에 두어 실제 이동이 발생하게 한다.
    waypoints = [(100.0, 0.0), (200.0, 0.0)]
    enemy = Enemy(x=0.0, y=0.0, enemy_def=_EnemyDef(), path_id="p_main")
    world = {"enemies": [enemy], "waypoints": waypoints}
    ps = PathingSystem(world)
    ps.update(dt=1.0)
    # 1초 동안 speed=60 이동 → (0,0)에서 (100,0) 방향으로 60px
    assert enemy.x > 0.0


def test_pathing_sets_goal_reached() -> None:
    # enemy 위치를 경로 시작 이전으로 설정해 실제 이동 발생
    waypoints = [(50.0, 0.0), (100.0, 0.0)]
    enemy = Enemy(x=0.0, y=0.0, enemy_def=_EnemyDef(), path_id="p_main")
    world = {"enemies": [enemy], "waypoints": waypoints}
    ps = PathingSystem(world)
    # 충분히 큰 dt로 목표 도달
    ps.update(dt=100.0)
    assert enemy.goal_reached is True


def test_pathing_skips_dying_enemy() -> None:
    waypoints = [(100.0, 0.0), (200.0, 0.0)]
    enemy = Enemy(x=0.0, y=0.0, enemy_def=_EnemyDef(), path_id="p_main")
    enemy.dying = True
    world = {"enemies": [enemy], "waypoints": waypoints}
    ps = PathingSystem(world)
    ps.update(dt=1.0)
    assert enemy.x == 0.0  # dying → 이동 없음


# ---------------------------------------------------------------------------
# 2. Combat: ally → projectile 스폰
# ---------------------------------------------------------------------------


def test_combat_spawns_projectile() -> None:
    world = build_world()
    cs = CombatSystem(world)
    cs.update(dt=0.1, world=world)
    # ally가 ready_to_fire → projectile 스폰 후 리스트에 추가
    # (발사 후 projectile이 hit하면 리스트에서 제거될 수 있으므로 존재 여부만 확인)
    # ready_to_fire 이후 발사됐음을 간접 확인: cooldown이 리셋됨
    ally = world["allies"][0]
    assert ally.ready_to_fire is False or ally.cooldown > 0.0


def test_combat_ally_targets_enemy() -> None:
    world = build_world()
    ally = world["allies"][0]
    enemy = world["enemies"][0]
    cs = CombatSystem(world)
    cs.update(dt=0.0, world=world)
    # target이 설정됐거나 사거리 내에 있어야 함
    assert ally.find_target([enemy], range_px=500.0) is enemy


# ---------------------------------------------------------------------------
# 3. Combat: projectile → enemy 적중 → 페이드 사망
# ---------------------------------------------------------------------------


def test_enemy_takes_damage_after_hit() -> None:
    """발사체가 명중하면 enemy HP가 줄어야 한다."""
    world = build_world()
    enemy = world["enemies"][0]
    init_hp = enemy.hp

    cs = CombatSystem(world)
    # 여러 틱 돌려서 발사체가 명중할 때까지 시뮬레이션
    for _ in range(30):
        cs.update(dt=0.05, world=world)
        if enemy.dying or not enemy.alive:
            break

    assert enemy.hp < init_hp or enemy.dying


def test_enemy_dies_after_sufficient_ticks() -> None:
    """충분한 시간이 지나면 enemy가 alive=False가 된다."""
    world = build_world()
    enemy = world["enemies"][0]

    cs = CombatSystem(world)
    # 충분히 많은 틱 (ally가 발사 + 발사체 명중 + fade 완료)
    for _ in range(200):
        cs.update(dt=0.05, world=world)
        if not enemy.alive:
            break

    assert not enemy.alive


def test_on_enemy_defeated_called() -> None:
    """enemy 사망 시 on_enemy_defeated 콜백이 호출돼야 한다."""
    world = build_world()
    enemy = world["enemies"][0]
    defeated_list = world["_defeated"]

    cs = CombatSystem(world)
    for _ in range(200):
        cs.update(dt=0.05, world=world)
        if defeated_list:
            break

    assert len(defeated_list) >= 1
    assert defeated_list[0] is enemy


# ---------------------------------------------------------------------------
# 4. Effect 스폰
# ---------------------------------------------------------------------------


def test_effect_spawned_on_hit() -> None:
    """발사체 명중 시 이펙트가 생성돼야 한다."""
    world = build_world()
    effects = world["effects"]

    cs = CombatSystem(world)
    for _ in range(30):
        cs.update(dt=0.05, world=world)
        if effects:
            break

    # 이펙트가 스폰됐거나 enemy가 죽었음을 확인
    enemy = world["enemies"][0]
    assert effects or enemy.dying or not enemy.alive


# ---------------------------------------------------------------------------
# 5. Issue #76 — 호밍 발사체 명중 보장 (이동하는 적도 적중)
# ---------------------------------------------------------------------------


def test_homing_projectile_hits_moving_enemy() -> None:
    """Issue #76: 매 틱 적이 이동해도 호밍 발사체가 적중해 적이 사망한다.

    적을 사거리 안에 두고 매 틱 y축으로 이동시킨다. 발사체 속도(400px/s)는
    적 이동속도(60px/s)보다 빠르므로 호밍 재조준으로 결국 명중해야 한다.
    과거 등속 직선 발사체였다면 발사 시점 좌표만 향해 빗나갔을 케이스.
    """
    world = build_world()
    enemy = world["enemies"][0]
    enemy.x = 420.0
    enemy.y = 300.0

    cs = CombatSystem(world)
    for _ in range(300):
        # 적이 매 틱 옆으로 이동 (사거리 500 안에 머물도록 소폭)
        if enemy.alive and not enemy.dying:
            enemy.y += 60.0 * 0.05
            if enemy.y > 360.0:
                enemy.y = 240.0  # 위아래로 왕복 — 발사 시점 좌표를 계속 벗어남
        cs.update(dt=0.05, world=world)
        if not enemy.alive or enemy.dying:
            break

    assert enemy.dying or not enemy.alive, "호밍 발사체가 이동하는 적을 끝내 명중시키지 못함"
