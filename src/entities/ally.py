"""아군 유닛(궁수/창병/투석병 등).

``find_target``으로 사거리 내 최근접 적을 찾고,
``attack_tick``으로 쿨다운을 관리한다.
쿨다운이 0에 도달하면 ``ready_to_fire=True``로 플래그를 세운다.
CombatSystem이 이 플래그를 읽어 projectile을 스폰한 후 플래그를 리셋한다.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler
    from src.data.loader import UnitDef


class Ally(Entity):
    """배치 가능한 아군 유닛.

    Attributes:
        unit_def: 유닛 정의 (공격력/사거리/공속 등).
        cooldown: 남은 공격 쿨다운(초). 0이 되면 ``ready_to_fire`` 세팅.
        ready_to_fire: CombatSystem이 projectile을 스폰해야 할 때 True.
        target: 현재 타겟 엔티티 (없으면 None).
    """

    def __init__(self, x: float, y: float, unit_def: UnitDef) -> None:
        super().__init__(x, y, hp=unit_def.hp)
        self.unit_def = unit_def
        self.cooldown: float = 0.0
        self.ready_to_fire: bool = False
        self.target: Entity | None = None

        # Issue #61 (DECISION-DL-P5S-001): 양만춘 S2 독려의 함성 버프.
        # 공속 배수(>=1.0). reset_fire 가 쿨다운 산정에 곱한다. 버프 지속시간이
        # 끝나면 1.0 으로 복원. unit_def(공유 정의) 를 변형하지 않고 인스턴스에만
        # 적용해 같은 유닛 종류라도 버프 대상만 빨라지게 한다.
        self.atk_speed_mult: float = 1.0
        self._buff_timer: float = 0.0

    # ------------------------------------------------------------------
    # 타겟팅
    # ------------------------------------------------------------------

    def find_target(self, enemies: list[Any], range_px: float) -> Any | None:
        """살아있는 적 중 자신과 가장 가까운 적을 반환.

        Args:
            enemies: 적 엔티티 리스트.
            range_px: 유효 사거리(픽셀). 이 거리 밖이면 None 반환.

        Returns:
            사거리 내 최근접 Enemy 인스턴스, 없으면 None.
        """
        best: Any | None = None
        best_dist_sq = range_px * range_px  # 사거리² 초과는 제외

        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= best_dist_sq:
                best_dist_sq = dist_sq
                best = enemy

        return best

    # ------------------------------------------------------------------
    # 공격 틱
    # ------------------------------------------------------------------

    def apply_atk_speed_buff(self, mult: float, duration_s: float) -> None:
        """S2 독려의 함성 — 공속 버프 적용/갱신 (Issue #61).

        재시전 시 더 강한 배수와 더 긴 잔여 시간으로 갱신한다(약화 없음).

        Args:
            mult: 공속 배수 (예: 1.3 = +30%).
            duration_s: 지속 시간(초).
        """
        self.atk_speed_mult = max(self.atk_speed_mult, float(mult))
        self._buff_timer = max(self._buff_timer, float(duration_s))

    def attack_tick(self, dt: float) -> None:
        """쿨다운을 dt만큼 감소. 0 도달 시 ``ready_to_fire=True``.

        Args:
            dt: 경과 시간(초).
        """
        # Issue #61: S2 공속 버프 만료 처리 (CombatSystem 이 매 틱 호출).
        if self._buff_timer > 0.0:
            self._buff_timer -= dt
            if self._buff_timer <= 0.0:
                self._buff_timer = 0.0
                self.atk_speed_mult = 1.0
        if self.cooldown > 0.0:
            self.cooldown -= dt
            if self.cooldown <= 0.0:
                self.cooldown = 0.0
                self.ready_to_fire = True
        # 쿨다운이 이미 0이고 타겟이 있으면 즉시 발사 준비
        elif self.target is not None and not self.ready_to_fire:
            self.ready_to_fire = True

    def reset_fire(self) -> None:
        """발사 완료 후 쿨다운 재설정."""
        self.ready_to_fire = False
        # atk_speed: 초당 공격 횟수 → 쿨다운 = 1/atk_speed.
        # Issue #61: S2 버프 시 atk_speed_mult 만큼 공속 증가(쿨다운 단축).
        spd = self.unit_def.atk_speed * self.atk_speed_mult
        self.cooldown = (1.0 / spd) if spd > 0 else 1.0

    @property
    def effective_atk_speed(self) -> float:
        """현재 버프 반영 공속(초당 공격 횟수). 테스트/UI 공개 API (Issue #61)."""
        return float(self.unit_def.atk_speed) * self.atk_speed_mult

    # ------------------------------------------------------------------
    # Entity 오버라이드
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """쿨다운 감소. 타겟팅·발사는 CombatSystem이 담당."""
        if self.cooldown > 0.0:
            self.cooldown -= dt
            if self.cooldown <= 0.0:
                self.cooldown = 0.0

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """coords 동기화 + 사거리 미리보기 (렌더러가 호출)."""
        return

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _distance_to(self, other: Any) -> float:
        return math.hypot(other.x - self.x, other.y - self.y)
