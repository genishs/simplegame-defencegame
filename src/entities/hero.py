"""양만춘 영웅 엔티티.

4단계 페이즈는 hp 비율로 자동 결정된다:
  Phase 1: hp_ratio >= 0.70
  Phase 2: hp_ratio >= 0.40
  Phase 3: hp_ratio >= 0.15
  Phase 4: hp_ratio <  0.15

궁극기(ultimate)는 ``ultimate_cooldown_s`` 쿨다운과 페이즈별 스칼라로 동작한다.
페이즈 전환 시 ``phase_changed`` 플래그가 True로 1회 세팅된다.
외부에서 이 플래그를 읽은 뒤 False로 초기화해야 다음 전환을 감지할 수 있다.

DECISION-DL-P4D-007 (Issue #57/#58):
  Hero는 평타(활) 자동 공격을 가진다. GDD §3.1: atk 35 / range 380px /
  공속 1.0/s. ``find_target_in_range`` 로 사거리 내 최근접 적을 찾고,
  ``auto_attack(enemies)`` 가 쿨다운을 갱신해 발사 가능 시 (target, damage,
  cooldown) 을 반환한다. 발사체 스폰은 BattleScene 이 책임 (도메인 가드
  tkinter-free 유지). 수동 모드에서도 발사 트리거는 동일하게 작동해
  영웅이 적과 전투할 수 있게 한다 (Issue #58).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler

# GDD §3.1 기본 능력치
_DEFAULT_HP = 800
_DEFAULT_ATK = 35
_DEFAULT_ATK_SPEED = 1.0  # 초당 공격 횟수
_DEFAULT_RANGE_PX = 380.0
_DEFAULT_MOVE_SPEED = 150.0

# 궁극기 쿨다운 (GDD §3.3 U. 결사항전 180s)
_DEFAULT_ULT_COOLDOWN = 180.0

# 페이즈별 궁극기 데미지·범위 스칼라
# Phase 1: 기본, Phase 2: 강화, Phase 3: 위기, Phase 4: 필사
_PHASE_DMG_SCALAR = {1: 1.0, 2: 1.4, 3: 1.8, 4: 2.5}
_PHASE_RANGE_SCALAR = {1: 1.0, 2: 1.2, 3: 1.4, 4: 1.8}
_BASE_ULT_DMG = 150
_BASE_ULT_RANGE = 250.0


class Hero(Entity):
    """양만춘 영웅.

    Attributes:
        max_hp: 최대 체력 (페이즈 계산 기준).
        ultimate_cooldown_s: 궁극기 쿨다운(초).
        _ult_timer: 현재 남은 쿨다운.
        phase_changed: 이번 틱에 페이즈가 바뀌었으면 True.
        _prev_phase: 이전 틱의 페이즈 값.
    """

    def __init__(
        self,
        x: float = 960.0,
        y: float = 540.0,
        hp: int = _DEFAULT_HP,
        ultimate_cooldown_s: float = _DEFAULT_ULT_COOLDOWN,
    ) -> None:
        super().__init__(x, y, hp)
        self.max_hp: int = hp
        self.atk: int = _DEFAULT_ATK
        self.atk_speed: float = _DEFAULT_ATK_SPEED
        self.range_px: float = _DEFAULT_RANGE_PX
        self.move_speed: float = _DEFAULT_MOVE_SPEED
        self.ultimate_cooldown_s: float = ultimate_cooldown_s
        self._ult_timer: float = 0.0  # 0이면 즉시 발동 가능
        self.phase_changed: bool = False
        self._prev_phase: int = 1
        # DECISION-DL-P4D-007 (Issue #57/#58): 평타 자동 공격 쿨다운.
        # 0이면 즉시 발사 가능. ``auto_attack`` 이 1/atk_speed 로 재설정.
        self._atk_cooldown: float = 0.0
        # 현재 평타 타겟 (UI 디버그/테스트용. CombatSystem 의존성 없음).
        self.target: Any = None

    # ------------------------------------------------------------------
    # 페이즈 프로퍼티
    # ------------------------------------------------------------------

    @property
    def current_phase(self) -> int:
        """HP 비율 기반 페이즈 (1~4).

        hp_ratio >= 0.70 → Phase 1
        hp_ratio >= 0.40 → Phase 2
        hp_ratio >= 0.15 → Phase 3
        hp_ratio <  0.15 → Phase 4
        """
        ratio = self.hp / self.max_hp if self.max_hp > 0 else 0.0
        if ratio >= 0.70:
            return 1
        if ratio >= 0.40:
            return 2
        if ratio >= 0.15:
            return 3
        return 4

    # ------------------------------------------------------------------
    # 업데이트
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """매 틱 쿨다운 감소 및 페이즈 전환 감지."""
        # 쿨다운 감소
        if self._ult_timer > 0.0:
            self._ult_timer = max(0.0, self._ult_timer - dt)
        # 평타 쿨다운 감소 (Issue #57/#58, DECISION-DL-P4D-007)
        if self._atk_cooldown > 0.0:
            self._atk_cooldown = max(0.0, self._atk_cooldown - dt)

        # 페이즈 전환 감지
        new_phase = self.current_phase
        if new_phase != self._prev_phase:
            self.phase_changed = True
            self._prev_phase = new_phase
        else:
            # 외부에서 아직 읽지 않았으면 True 유지, 읽고 나서 False로 초기화
            pass  # phase_changed는 외부에서 직접 False로 리셋

    # ------------------------------------------------------------------
    # 평타 자동 공격 (DECISION-DL-P4D-007, Issue #57/#58)
    # ------------------------------------------------------------------

    def find_target_in_range(self, enemies: list[Any]) -> Any | None:
        """사거리 ``self.range_px`` 내 최근접 살아있는 적을 반환.

        Args:
            enemies: 적 엔티티 리스트.

        Returns:
            가장 가까운 Enemy, 없으면 None.
        """
        import math

        best: Any | None = None
        best_dist_sq = self.range_px * self.range_px
        for e in enemies:
            if not getattr(e, "alive", False):
                continue
            if getattr(e, "dying", False):
                continue
            dx = e.x - self.x
            dy = e.y - self.y
            dsq = dx * dx + dy * dy
            if dsq <= best_dist_sq:
                best_dist_sq = dsq
                best = e
        return best

    def auto_attack(self, enemies: list[Any]) -> dict[str, Any] | None:
        """평타 자동 공격 트리거.

        쿨다운이 0이고 사거리 내 적이 있으면 발사 정보를 반환한다.
        반환된 dict 는 BattleScene 이 받아 Projectile 을 스폰한다 (도메인 가드).

        Returns:
            발사 정보 dict (``{"target", "damage", "x", "y"}``) 또는 None.
        """
        if self._atk_cooldown > 0.0:
            return None
        target = self.find_target_in_range(enemies)
        if target is None:
            self.target = None
            return None
        self.target = target
        # 쿨다운 재설정 (atk_speed = 초당 공격 횟수)
        self._atk_cooldown = (1.0 / self.atk_speed) if self.atk_speed > 0 else 1.0
        return {
            "target": target,
            "damage": self.atk,
            "x": self.x,
            "y": self.y,
        }

    @property
    def atk_cooldown(self) -> float:
        """평타 쿨다운 잔여 시간 (테스트/UI 공개 API)."""
        return self._atk_cooldown

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """canvas_id의 coords 갱신 (렌더러가 호출)."""
        return

    # ------------------------------------------------------------------
    # 궁극기
    # ------------------------------------------------------------------

    @property
    def ult_ready(self) -> bool:
        """궁극기 발동 가능 여부."""
        return self._ult_timer <= 0.0

    def ultimate(self, targets: list[Any]) -> dict[str, Any]:
        """페이즈별 궁극기 발동.

        Args:
            targets: 데미지를 입힐 후보 엔티티 리스트.

        Returns:
            발동 결과 dict::

                {
                    "fired": bool,          # 발동 여부
                    "phase": int,           # 발동 당시 페이즈
                    "damage": int,          # 적용 데미지
                    "range_px": float,      # 유효 범위
                    "hit_targets": list,    # 실제 데미지 적용된 엔티티
                }

        쿨다운 중이면 ``fired=False``를 반환하고 데미지를 적용하지 않는다.
        """
        if not self.ult_ready:
            return {
                "fired": False,
                "phase": self.current_phase,
                "damage": 0,
                "range_px": 0.0,
                "hit_targets": [],
            }

        phase = self.current_phase
        dmg = int(_BASE_ULT_DMG * _PHASE_DMG_SCALAR[phase])
        eff_range = _BASE_ULT_RANGE * _PHASE_RANGE_SCALAR[phase]

        import math

        hit: list[Any] = []
        for t in targets:
            if not t.alive:
                continue
            dist = math.hypot(t.x - self.x, t.y - self.y)
            if dist <= eff_range:
                t.hp -= dmg
                if t.hp <= 0:
                    if hasattr(t, "dying"):
                        t.dying = True
                    else:
                        t.alive = False
                hit.append(t)

        self._ult_timer = self.ultimate_cooldown_s
        return {
            "fired": True,
            "phase": phase,
            "damage": dmg,
            "range_px": eff_range,
            "hit_targets": hit,
        }

    # ------------------------------------------------------------------
    # 하위 호환 (이전 스텁 유지)
    # ------------------------------------------------------------------

    def cast_ult(self) -> bool:
        """궁극기 발동 (타겟 없는 단순 트리거). 발동 가능하면 True."""
        result = self.ultimate([])
        return result["fired"]
