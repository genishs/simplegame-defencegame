"""auto_mode_simulator -- BattleScene auto-mode headless simulator.

DECISION-DT1-P4B-001 (dev team1, Phase 4 cleanup):
  - tkinter-free domain modules only (WaveSystem, PathingSystem).
  - Missing enemy types fall back to inline EnemyDef.
  - Auto-placement: strongest unit (highest atk) placed in all build_zones.
  - DT=0.016s steps compress real wave timing to milliseconds.

DECISION-DT1-P4B-005: Direct DPS damage model instead of CombatSystem
  projectile physics. The simulator runs at compressed time (DT=0.016s) which
  causes projectile overshoot relative to hit_radius (12 px). Direct damage
  preserves identical DPS while avoiding floating-point trajectory artifacts.

  Phase 5 후속 (DECISION-DL-P5P-002, Issue #44): 실 발사체에는 swept-circle
  collision (Projectile + Enemy 양쪽 이동 보정) 이 도입됐으나, 시뮬레이터는
  본격 클리어율 재검증 비용 (15 회 × 3 stage = 45 시드) 을 회피하기 위해
  DPS 모델을 유지한다. 두 모델은 동일 DPS 를 보장하므로 클리어율 결과 일치.

Usage::

    from src.systems.auto_mode_simulator import StageSimulator, SimResult
    result = StageSimulator("stage_01", rng_seed=42).run()
    assert result.cleared

tkinter import prohibited (DECISION-4.1).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from src.data.loader import EnemyDef, StageDef, UnitDef, load_enemies, load_stage, load_units
from src.entities.ally import Ally
from src.entities.enemy import Enemy
from src.systems.pathing import PathingSystem
from src.systems.wave import WaveSystem

# ---------------------------------------------------------------------------
# Fallback enemy stats for types not in enemies.json
# ---------------------------------------------------------------------------
_FALLBACK_ENEMY_STATS: dict[str, dict[str, Any]] = {
    "tang_archer": {
        "name": "당군 궁수",
        "hp": 60,
        "speed": 70,
        "armor": 0,
        "damage_to_castle": 1,
        "gold_drop": 10,
        "sprite": "enemy_archer",
        "is_boss": False,
    },
    "tang_scout": {
        "name": "당군 척후병",
        "hp": 50,
        "speed": 90,
        "armor": 0,
        "damage_to_castle": 1,
        "gold_drop": 8,
        "sprite": "enemy_scout",
        "is_boss": False,
    },
    "tang_vanguard_captain": {
        "name": "당군 선봉대장",
        "hp": 250,
        "speed": 50,
        "armor": 3,
        "damage_to_castle": 5,
        "gold_drop": 50,
        "sprite": "enemy_vanguard_captain",
        "is_boss": True,
    },
    "tang_night_raider": {
        "name": "당군 야간 기습대",
        "hp": 300,
        "speed": 55,
        "armor": 2,
        "damage_to_castle": 6,
        "gold_drop": 60,
        "sprite": "enemy_night_raider",
        "is_boss": True,
    },
}


def _get_enemy_def(enemy_id: str, enemies_db: dict[str, EnemyDef]) -> EnemyDef:
    """Look up enemy_id in enemies_db; create fallback EnemyDef if missing."""
    if enemy_id in enemies_db:
        return enemies_db[enemy_id]
    stats = _FALLBACK_ENEMY_STATS.get(enemy_id)
    if stats is None:
        base = enemies_db.get("tang_soldier")
        if base is not None:
            return EnemyDef(
                id=enemy_id,
                name=enemy_id,
                hp=base.hp,
                speed=base.speed,
                armor=base.armor,
                damage_to_castle=base.damage_to_castle,
                gold_drop=base.gold_drop,
                sprite=base.sprite,
            )
        return EnemyDef(
            id=enemy_id,
            name=enemy_id,
            hp=80,
            speed=60,
            armor=0,
            damage_to_castle=1,
            gold_drop=8,
            sprite="enemy_default",
        )
    return EnemyDef(
        id=enemy_id,
        name=stats["name"],
        hp=stats["hp"],
        speed=stats["speed"],
        armor=stats["armor"],
        damage_to_castle=stats["damage_to_castle"],
        gold_drop=stats["gold_drop"],
        sprite=stats["sprite"],
        is_boss=stats.get("is_boss", False),
    )


@dataclass
class SimResult:
    """Result of a single simulation run.

    Attributes:
        stage_id: Stage that was simulated.
        seed: RNG seed used.
        cleared: True if player cleared, False if lives reached 0.
        lives_remaining: Lives left at end.
        elapsed_sim_seconds: In-game time elapsed (seconds).
        enemies_defeated: Number of enemies defeated.
    """

    stage_id: str
    seed: int
    cleared: bool
    lives_remaining: int
    elapsed_sim_seconds: float
    enemies_defeated: int
    extra: dict[str, Any] = field(default_factory=dict)


class StageSimulator:
    """Single-stage auto-mode simulator.

    Call ``run()`` to execute the game loop at compressed speed and receive
    a ``SimResult``.

    Auto-mode policy:
    - Allies: strongest unit (atk descending) placed in every build_zone.
    - No gold check -- optimal placement assumed for new-player simulation.
    - Combat: direct DPS model (DECISION-DT1-P4B-005). Each ally deals
      ``atk * atk_speed`` damage-per-second to the nearest enemy in range,
      distributed evenly across time. Armor reduces each attack's damage
      by the enemy's armor value (min 1 per hit).
    - Defeat condition: lives <= 0.
    - Clear condition: WaveSystem.all_clear == True and enemies list empty.
    """

    DT: float = 0.016  # simulation step size in seconds (~60 fps)
    MAX_SIM_TIME: float = 600.0  # safety cutoff (10 min in-game)

    def __init__(self, stage_id: str, rng_seed: int = 0) -> None:
        self.stage_id = stage_id
        self.rng_seed = rng_seed
        self._rng = random.Random(rng_seed)

        self._stage: StageDef = load_stage(stage_id)
        self._units_db: dict[str, UnitDef] = load_units()
        self._enemies_db: dict[str, EnemyDef] = load_enemies()

    def run(self) -> SimResult:
        """Execute simulation and return result."""
        stage = self._stage

        lives = stage.lives
        allies: list[Ally] = []
        enemies: list[Enemy] = []
        enemies_defeated = 0
        elapsed = 0.0

        waypoints_map: dict[str, list[tuple[float, float]]] = {p.id: list(p.waypoints) for p in stage.paths}

        default_path_id = stage.paths[0].id if stage.paths else "p_main"

        allies = self._auto_place_units(stage, allies)

        # ally cooldown accumulators (direct DPS model)
        # cooldown_acc[i] tracks accumulated time since last attack for ally i
        cooldown_acc: list[float] = [0.0] * len(allies)

        world: dict[str, Any] = {
            "allies": allies,
            "enemies": enemies,
            "waypoints": waypoints_map,
        }

        pathing_sys = PathingSystem(world)
        wave_sys = WaveSystem(world)

        def spawn_enemy(enemy_type: str, path_id: str) -> None:
            edef = _get_enemy_def(enemy_type, self._enemies_db)
            # Resolve effective path: fall back to first valid path if path_id not in map.
            # This handles the hard-coded "p_main" boss spawn in WaveSystem when the
            # stage uses a different path id (e.g. stage_03 uses p_gorge/p_flank).
            effective_path_id = path_id if path_id in waypoints_map else default_path_id
            wps = waypoints_map.get(effective_path_id, [])
            sx, sy = wps[0] if wps else (0.0, 540.0)
            e = Enemy(x=sx, y=sy, enemy_def=edef, path_id=effective_path_id)
            enemies.append(e)

        wave_sys.spawn_callback = spawn_enemy
        # Issue #43 / DECISION-DL-P5P-001: paths 주입으로 WaveSystem 자체가 보스 path
        # fallback 처리. 시뮬레이터의 spawn_enemy fallback (effective_path_id) 은
        # 안전망으로 유지 — 미래 stage 변형 시 graceful degradation 확보.
        wave_sys.load(stage.waves, paths=stage.paths)

        while elapsed < self.MAX_SIM_TIME:
            dt = self.DT

            # 1. Spawn
            wave_sys.update(dt)

            # 2. Move enemies
            pathing_sys.update(dt, enemies=enemies, waypoints=waypoints_map)

            # 3. Castle-reach check
            for enemy in list(enemies):
                if not enemy.alive:
                    continue
                if enemy.goal_reached or enemy.reached_castle:
                    lives -= enemy.enemy_def.damage_to_castle
                    enemy.alive = False
                    enemy.dying = True

            # 4. Direct DPS combat (DECISION-DT1-P4B-005)
            # Each ally attacks the nearest in-range enemy; cooldown-based.
            alive_enemies = [e for e in enemies if e.alive and not e.dying]
            for i, ally in enumerate(allies):
                if not ally.alive:
                    continue
                # Find nearest enemy in range
                target: Enemy | None = None
                best_dist_sq = float(ally.unit_def.range) ** 2
                for e in alive_enemies:
                    dx = e.x - ally.x
                    dy = e.y - ally.y
                    dsq = dx * dx + dy * dy
                    if dsq <= best_dist_sq:
                        best_dist_sq = dsq
                        target = e

                if target is None:
                    cooldown_acc[i] = 0.0
                    continue

                # Accumulate attack time; fire when cooldown period elapsed
                atk_speed = ally.unit_def.atk_speed  # attacks per second
                cooldown_period = 1.0 / atk_speed if atk_speed > 0 else 1.0
                cooldown_acc[i] += dt
                while cooldown_acc[i] >= cooldown_period and target is not None:
                    cooldown_acc[i] -= cooldown_period
                    # Apply direct damage (min 1 per hit)
                    armor = target.enemy_def.armor
                    dmg = max(1, ally.unit_def.atk - armor)
                    target.hp -= dmg
                    if target.hp <= 0:
                        target.hp = 0
                        target.dying = True
                        target.alive = False
                        enemies_defeated += 1
                        # Pick next target for remaining cooldown budget
                        alive_enemies = [e for e in enemies if e.alive and not e.dying]
                        target = None
                        for e in alive_enemies:
                            dx = e.x - ally.x
                            dy = e.y - ally.y
                            dsq = dx * dx + dy * dy
                            if dsq <= float(ally.unit_def.range) ** 2:
                                if target is None or dsq < (
                                    (target.x - ally.x) ** 2 + (target.y - ally.y) ** 2
                                ):
                                    target = e

            # 5. Prune dead
            enemies[:] = [e for e in enemies if e.alive]
            alive_enemies = [e for e in enemies if not e.dying]

            # 6. Defeat check
            if lives <= 0:
                return SimResult(
                    stage_id=self.stage_id,
                    seed=self.rng_seed,
                    cleared=False,
                    lives_remaining=0,
                    elapsed_sim_seconds=elapsed,
                    enemies_defeated=enemies_defeated,
                )

            # 7. Clear check
            if wave_sys.all_clear and not enemies:
                return SimResult(
                    stage_id=self.stage_id,
                    seed=self.rng_seed,
                    cleared=True,
                    lives_remaining=lives,
                    elapsed_sim_seconds=elapsed,
                    enemies_defeated=enemies_defeated,
                )

            elapsed += dt

        # Timeout = defeat
        return SimResult(
            stage_id=self.stage_id,
            seed=self.rng_seed,
            cleared=False,
            lives_remaining=lives,
            elapsed_sim_seconds=elapsed,
            enemies_defeated=enemies_defeated,
            extra={"reason": "timeout"},
        )

    def _auto_place_units(self, stage: StageDef, allies: list[Ally]) -> list[Ally]:
        """Place strongest unit in every build_zone (greedy, no gold check)."""
        if not self._units_db:
            return allies

        sorted_units = sorted(self._units_db.values(), key=lambda u: u.atk, reverse=True)
        best_unit = sorted_units[0]

        for zone in stage.build_zones:
            cx = float(zone["x"]) + float(zone.get("w", 80)) / 2.0
            cy = float(zone["y"]) + float(zone.get("h", 80)) / 2.0
            ally = Ally(x=cx, y=cy, unit_def=best_unit)
            allies.append(ally)

        return allies
