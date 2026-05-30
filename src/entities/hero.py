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

# GDD §3.2 스킬 3종 (Issue #61, DECISION-DL-P5S-001)
# S1. 일점사 — 단일 강타 200 + 0.5s 기절, 쿨다운 12s
_S1_COOLDOWN = 12.0
_S1_DAMAGE = 200
_S1_STUN_S = 0.5
# S2. 독려의 함성 — 반경 250px 아군 공속 +30% / 10s, 쿨다운 25s
_S2_COOLDOWN = 25.0
_S2_RADIUS = 250.0
_S2_ATK_SPEED_MULT = 1.3
_S2_DURATION = 10.0
# S3. 화살비 — 지정 지점 반경 180px 5초간 초당 30 데미지, 쿨다운 40s
_S3_COOLDOWN = 40.0
_S3_RADIUS = 180.0
_S3_DPS = 30
_S3_DURATION = 5.0
# 자동 모드 AI 발동 임계값
_AUTO_S2_MIN_ALLIES = 2  # 250px 내 아군 N명 이상이면 함성
_AUTO_S3_MIN_CLUSTER = 3  # 180px 내 적 N명 이상 군집이면 화살비


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

        # Issue #61 (DECISION-DL-P5S-001): S1/S2/S3 스킬 쿨다운(0이면 발동 가능).
        self._s1_timer: float = 0.0
        self._s2_timer: float = 0.0
        self._s3_timer: float = 0.0
        # 활성 화살비(S3) 지대 목록. 각 dict: x/y/radius/dps/remaining/_accum.
        # BattleScene 이 ``tick_active_skills`` 로 DoT 를 적용하고 render 로 표시.
        self._arrow_rains: list[dict[str, Any]] = []

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

        # S1/S2/S3 스킬 쿨다운 감소 (Issue #61)
        if self._s1_timer > 0.0:
            self._s1_timer = max(0.0, self._s1_timer - dt)
        if self._s2_timer > 0.0:
            self._s2_timer = max(0.0, self._s2_timer - dt)
        if self._s3_timer > 0.0:
            self._s3_timer = max(0.0, self._s3_timer - dt)

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

    # ------------------------------------------------------------------
    # S1/S2/S3 스킬 (GDD §3.2, Issue #61, DECISION-DL-P5S-001)
    #
    # 도메인 가드: 스킬 효과(데미지/기절/버프/DoT) 는 도메인에서 적용하되,
    # 시각(Effect/Projectile 스폰)·키 바인딩은 BattleScene 이 담당한다.
    # 각 cast_* 는 발동 결과 dict 를 반환하며 ``fired`` 가 False 면 쿨다운 중.
    # ------------------------------------------------------------------

    @property
    def s1_ready(self) -> bool:
        """S1 일점사 발동 가능 여부."""
        return self._s1_timer <= 0.0

    @property
    def s2_ready(self) -> bool:
        """S2 독려의 함성 발동 가능 여부."""
        return self._s2_timer <= 0.0

    @property
    def s3_ready(self) -> bool:
        """S3 화살비 발동 가능 여부."""
        return self._s3_timer <= 0.0

    @property
    def s1_cooldown(self) -> float:
        """S1 잔여 쿨다운(초)."""
        return self._s1_timer

    @property
    def s2_cooldown(self) -> float:
        """S2 잔여 쿨다운(초)."""
        return self._s2_timer

    @property
    def s3_cooldown(self) -> float:
        """S3 잔여 쿨다운(초)."""
        return self._s3_timer

    @property
    def active_arrow_rains(self) -> list[dict[str, Any]]:
        """현재 활성 화살비(S3) 지대 목록 (BattleScene render/테스트용)."""
        return self._arrow_rains

    def cast_s1(self, enemies: list[Any]) -> dict[str, Any]:
        """S1 일점사 — 사거리 내 최근접 적에게 단일 강타 200 + 0.5s 기절.

        Args:
            enemies: 적 엔티티 리스트.

        Returns:
            발동 결과 dict. ``fired`` True 시 ``target``/``damage``/``stun_s``
            포함. 쿨다운 중이거나 사거리 내 적이 없으면 ``fired=False``.
        """
        if not self.s1_ready:
            return {"fired": False, "skill": "s1", "reason": "cooldown"}
        target = self.find_target_in_range(enemies)
        if target is None:
            return {"fired": False, "skill": "s1", "reason": "no_target"}
        # 데미지 + 기절 적용 (궁극기와 동일하게 도메인에서 직접 적용해 명중 보장).
        if hasattr(target, "take_damage"):
            target.take_damage(_S1_DAMAGE)
        else:
            target.hp -= _S1_DAMAGE
            if target.hp <= 0 and hasattr(target, "dying"):
                target.dying = True
        if hasattr(target, "stun_timer"):
            target.stun_timer = max(float(getattr(target, "stun_timer", 0.0)), _S1_STUN_S)
        self._s1_timer = _S1_COOLDOWN
        return {
            "fired": True,
            "skill": "s1",
            "target": target,
            "damage": _S1_DAMAGE,
            "stun_s": _S1_STUN_S,
            "x": self.x,
            "y": self.y,
        }

    def cast_s2(self, allies: list[Any]) -> dict[str, Any]:
        """S2 독려의 함성 — 반경 250px 아군 공속 +30% / 10s.

        Args:
            allies: 아군 엔티티 리스트.

        Returns:
            발동 결과 dict. ``fired`` True 시 ``buffed``(대상 리스트)/``radius``/
            ``mult``/``duration`` 포함. 쿨다운 중이면 ``fired=False``.
        """
        if not self.s2_ready:
            return {"fired": False, "skill": "s2", "reason": "cooldown"}
        buffed: list[Any] = []
        r_sq = _S2_RADIUS * _S2_RADIUS
        for ally in allies:
            if not getattr(ally, "alive", True):
                continue
            dx = ally.x - self.x
            dy = ally.y - self.y
            if dx * dx + dy * dy <= r_sq:
                if hasattr(ally, "apply_atk_speed_buff"):
                    ally.apply_atk_speed_buff(_S2_ATK_SPEED_MULT, _S2_DURATION)
                buffed.append(ally)
        self._s2_timer = _S2_COOLDOWN
        return {
            "fired": True,
            "skill": "s2",
            "buffed": buffed,
            "radius": _S2_RADIUS,
            "mult": _S2_ATK_SPEED_MULT,
            "duration": _S2_DURATION,
            "x": self.x,
            "y": self.y,
        }

    def cast_s3(self, target_x: float, target_y: float) -> dict[str, Any]:
        """S3 화살비 — 지정 지점 반경 180px 에 5초간 초당 30 데미지 지대 생성.

        지대는 ``tick_active_skills`` 가 매 틱 DoT 를 적용하고 5초 후 소멸한다.

        Args:
            target_x: 지대 중심 x(베이스 좌표).
            target_y: 지대 중심 y(베이스 좌표).

        Returns:
            발동 결과 dict. 쿨다운 중이면 ``fired=False``.
        """
        if not self.s3_ready:
            return {"fired": False, "skill": "s3", "reason": "cooldown"}
        self._arrow_rains.append(
            {
                "x": float(target_x),
                "y": float(target_y),
                "radius": _S3_RADIUS,
                "dps": _S3_DPS,
                "remaining": _S3_DURATION,
                "_accum": 0.0,
            }
        )
        self._s3_timer = _S3_COOLDOWN
        return {
            "fired": True,
            "skill": "s3",
            "x": float(target_x),
            "y": float(target_y),
            "radius": _S3_RADIUS,
            "dps": _S3_DPS,
            "duration": _S3_DURATION,
        }

    def tick_active_skills(self, dt: float, enemies: list[Any]) -> None:
        """활성 화살비(S3) 지대의 DoT 적용 + 만료 처리 (BattleScene 이 매 틱 호출).

        지대별 누적기(``_accum``)에 ``dps * dt`` 를 더하고 정수 단위가 차면
        지대 반경 내 살아있는 적 전원에게 그만큼 데미지를 가한다(초당 30 수렴).

        Args:
            dt: 경과 시간(초).
            enemies: 적 엔티티 리스트.
        """
        if not self._arrow_rains:
            return
        still_active: list[dict[str, Any]] = []
        for zone in self._arrow_rains:
            zone["_accum"] += zone["dps"] * dt
            dmg_chunk = int(zone["_accum"])
            if dmg_chunk > 0:
                zone["_accum"] -= dmg_chunk
                r_sq = zone["radius"] * zone["radius"]
                zx = zone["x"]
                zy = zone["y"]
                for e in enemies:
                    if not getattr(e, "alive", False) or getattr(e, "dying", False):
                        continue
                    dx = e.x - zx
                    dy = e.y - zy
                    if dx * dx + dy * dy <= r_sq:
                        if hasattr(e, "take_damage"):
                            e.take_damage(dmg_chunk)
                        else:
                            e.hp -= dmg_chunk
            zone["remaining"] -= dt
            if zone["remaining"] > 1e-9:  # 부동소수 잔차로 인한 1틱 연장 방지
                still_active.append(zone)
        self._arrow_rains = still_active

    def auto_cast(self, allies: list[Any], enemies: list[Any]) -> list[dict[str, Any]]:
        """자동 모드 AI — 발동 조건이 맞는 스킬을 사용하고 결과 리스트 반환.

        - S1: 쿨다운 준비 + 사거리 내 적 존재 → 최근접 적 일점사.
        - S3: 쿨다운 준비 + 반경 180px 내 적 3명 이상 군집 → 군집 중심 화살비.
        - S2: 쿨다운 준비 + 반경 250px 내 아군 2명 이상 → 함성.

        Args:
            allies: 아군 리스트.
            enemies: 적 리스트.

        Returns:
            발동된 스킬 결과 dict 리스트(BattleScene 이 시각화).
        """
        results: list[dict[str, Any]] = []

        if self.s1_ready and self.find_target_in_range(enemies) is not None:
            r = self.cast_s1(enemies)
            if r.get("fired"):
                results.append(r)

        if self.s3_ready:
            # 영웅 교전 사거리 내 적만 군집 후보로 삼는다 — 멀리 스폰 지점에
            # 화살비를 퍼붓는 "스폰 캠핑"을 방지하고 방어선 위협에만 반응.
            r_sq = self.range_px * self.range_px
            engaged = [
                e
                for e in enemies
                if getattr(e, "alive", False)
                and not getattr(e, "dying", False)
                and (e.x - self.x) ** 2 + (e.y - self.y) ** 2 <= r_sq
            ]
            cluster = self._densest_enemy_cluster(engaged, _S3_RADIUS, _AUTO_S3_MIN_CLUSTER)
            if cluster is not None:
                r = self.cast_s3(cluster[0], cluster[1])
                if r.get("fired"):
                    results.append(r)

        if self.s2_ready:
            r_sq = _S2_RADIUS * _S2_RADIUS
            nearby = sum(
                1
                for a in allies
                if getattr(a, "alive", True) and (a.x - self.x) ** 2 + (a.y - self.y) ** 2 <= r_sq
            )
            if nearby >= _AUTO_S2_MIN_ALLIES:
                r = self.cast_s2(allies)
                if r.get("fired"):
                    results.append(r)

        return results

    @staticmethod
    def _densest_enemy_cluster(
        enemies: list[Any], radius: float, min_count: int
    ) -> tuple[float, float] | None:
        """반경 ``radius`` 안에 가장 많은 적이 모인 중심(적 좌표)을 찾는다.

        각 살아있는 적을 후보 중심으로 보고 반경 내 적 수를 센 뒤 최다 군집을
        반환한다. 최다 군집이 ``min_count`` 미만이면 None.

        Returns:
            (x, y) 중심 좌표 또는 None.
        """
        r_sq = radius * radius
        alive = [e for e in enemies if getattr(e, "alive", False) and not getattr(e, "dying", False)]
        best_center: tuple[float, float] | None = None
        best_count = 0
        for center in alive:
            count = 0
            for other in alive:
                dx = other.x - center.x
                dy = other.y - center.y
                if dx * dx + dy * dy <= r_sq:
                    count += 1
            if count > best_count:
                best_count = count
                best_center = (float(center.x), float(center.y))
        if best_count >= min_count:
            return best_center
        return None

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
