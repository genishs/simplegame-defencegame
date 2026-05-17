"""전투 시스템 (데미지 계산 + 타겟팅, tk 비의존).

DESIGN: ``calc_damage(atk, armor)``는 순수 함수로 단위 테스트 핵심.
GDD: 방어력 1당 1 데미지 감쇄. 최소 1 데미지 보장(0 데미지는 게임성 저해).

``CombatSystem.update(dt, world)``는 다음 순서로 동작한다:
  1. 각 ally: find_target → attack_tick → ready_to_fire이면 projectile 스폰
  2. 각 projectile: update; hit이면 enemy.take_damage + effect 스폰 + release
  3. 각 enemy: fade_tick; alive==False && _was_dying이면 on_enemy_defeated 콜백
"""

from __future__ import annotations

from typing import Any

from src.entities.effect import Effect
from src.entities.projectile import Projectile


def calc_damage(atk: int, armor: int = 0) -> int:
    """기본 데미지 공식.

    Args:
        atk: 공격력(>= 0).
        armor: 방어력(>= 0).

    Returns:
        최종 데미지. 최소 1 보장.
    """
    if atk < 0:
        raise ValueError(f"atk must be >= 0, got {atk}")
    if armor < 0:
        raise ValueError(f"armor must be >= 0, got {armor}")
    return max(1, atk - armor)


def in_range(ax: float, ay: float, bx: float, by: float, radius: float) -> bool:
    """A의 사거리 ``radius`` 안에 B가 있는가."""
    dx = bx - ax
    dy = by - ay
    return (dx * dx + dy * dy) <= (radius * radius)


class CombatSystem:
    """매 틱 ``world['allies']``의 타겟팅과 발사 트리거.

    world 키:
        allies: list[Ally]
        enemies: list[Enemy]
        projectiles: list[Projectile]
        effects: list[Effect]
        pools: dict (선택 — 있으면 풀에서 acquire, 없으면 직접 생성)
        on_enemy_defeated: callable(enemy) (선택)
    """

    def __init__(self, world: dict[str, Any]) -> None:
        self.world = world

    def update(self, dt: float, world: dict[str, Any] | None = None) -> None:
        """전투 한 틱 처리.

        Args:
            dt: 경과 시간(초).
            world: 이 호출에서 사용할 world dict.
                   None이면 생성자에서 받은 ``self.world``를 사용.
        """
        w = world if world is not None else self.world

        allies: list[Any] = w.get("allies", [])
        enemies: list[Any] = w.get("enemies", [])
        projectiles: list[Any] = w.get("projectiles", [])
        effects: list[Any] = w.get("effects", [])
        pools: dict[str, Any] = w.get("pools", {})
        on_defeated: Any = w.get("on_enemy_defeated")

        # ------------------------------------------------------------------
        # 1. Ally: 타겟 찾기 → 공격 틱 → 발사
        # ------------------------------------------------------------------
        for ally in allies:
            if not ally.alive:
                continue

            range_px = float(ally.unit_def.range)
            target = ally.find_target(enemies, range_px)
            ally.target = target

            # attack_tick 호출 (ready_to_fire 갱신)
            ally.attack_tick(dt)

            if ally.ready_to_fire and target is not None and target.alive:
                proj = self._spawn_projectile(pools, projectiles, ally, target)
                if proj is not None:
                    projectiles.append(proj)
                ally.reset_fire()

        # ------------------------------------------------------------------
        # 2. Projectile: 이동 + 명중 판정
        # ------------------------------------------------------------------
        for proj in list(projectiles):
            if not proj.alive:
                continue

            proj.update(dt)

            if proj.hit:
                # 타겟에 데미지
                target = proj.target
                if target is not None and target.alive and not target.dying:
                    armor = getattr(target, "enemy_def", None)
                    armor_val = armor.armor if armor is not None else 0
                    dmg = calc_damage(proj.damage, armor_val)
                    target.take_damage(dmg)

                # 이펙트 스폰
                eff = self._spawn_effect(pools, effects, proj.x, proj.y)
                if eff is not None:
                    effects.append(eff)

                # 발사체 제거
                proj.alive = False
                proj.should_release = True

            elif proj.should_release:
                proj.alive = False

        # 죽은 발사체를 풀에 반환 + 리스트에서 제거
        to_remove: list[Any] = []
        for proj in projectiles:
            if not proj.alive:
                proj_pool = pools.get("projectile")
                if proj_pool is not None:
                    try:
                        proj_pool.release(proj)
                    except Exception:
                        pass
                to_remove.append(proj)
        for proj in to_remove:
            if proj in projectiles:
                projectiles.remove(proj)

        # ------------------------------------------------------------------
        # 3. Enemy: fade_tick + 사망 콜백
        # ------------------------------------------------------------------
        for enemy in list(enemies):
            if not enemy.alive:
                continue
            # fade_tick은 Enemy.update 또는 직접 호출
            if hasattr(enemy, "fade_tick"):
                enemy.fade_tick(dt)

            if not enemy.alive and getattr(enemy, "_was_dying", False):
                enemy._was_dying = False  # 콜백 1회만
                if callable(on_defeated):
                    on_defeated(enemy)

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _spawn_projectile(
        self,
        pools: dict[str, Any],
        projectiles: list[Any],
        ally: Any,
        target: Any,
    ) -> Any | None:
        """projectile 풀 또는 직접 생성으로 발사체를 만들어 반환."""
        proj_pool = pools.get("projectile")
        if proj_pool is not None:
            try:
                proj = proj_pool.acquire()
            except Exception:
                # 풀 고갈 시 그레이스풀 디그레이드: 직접 생성
                proj = None
        else:
            proj = None

        damage = ally.unit_def.atk
        speed = 400.0  # 기본 발사체 속도 (px/s)

        if proj is not None and hasattr(proj, "reset"):
            proj.reset(
                x=ally.x,
                y=ally.y,
                target_x=target.x,
                target_y=target.y,
                damage=damage,
                speed=speed,
                target=target,
            )
        else:
            proj = Projectile(
                x=ally.x,
                y=ally.y,
                target_x=target.x,
                target_y=target.y,
                damage=damage,
                speed=speed,
                target=target,
            )

        return proj

    def _spawn_effect(
        self,
        pools: dict[str, Any],
        effects: list[Any],
        x: float,
        y: float,
    ) -> Any | None:
        """effect 풀 또는 직접 생성으로 이펙트를 만들어 반환."""
        eff_pool = pools.get("effect")
        if eff_pool is not None:
            try:
                eff = eff_pool.acquire()
                eff.x = x
                eff.y = y
                eff.elapsed_s = 0.0
                eff.alpha = 1.0
                eff.alive = True
                return eff
            except Exception:
                pass  # 풀 고갈 시 이펙트 생략

        return Effect(x=x, y=y, kind="hit")
