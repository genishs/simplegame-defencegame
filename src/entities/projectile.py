"""발사체(화살/돌).

타겟을 향해 이동한다.
타겟까지 거리 < hit_radius이면 ``hit=True``.
타겟이 dying이면 fly-through 후 ``should_release=True``로 자동 회수.

DECISION-DL-P5P-002 (Issue #44): swept-circle 충돌 판정.
  과거: 발사체 line-segment vs 타겟 현재 좌표(점) 최단거리. 타겟이 같은 dt 동안
        반대 방향으로 이동하면 발사체가 hit_radius 를 통과하면서도 명중 누락.
  현재: 발사체와 타겟 양쪽의 동시 이동을 고려한 swept-circle distance — 타겟에
        ``_prev_x/_prev_y`` (이전 틱 좌표 스냅샷) 이 있으면 양 선분의 최소 거리,
        없으면 기존 단일-선분 검사로 fallback (하위 호환).

DECISION-DL-P5C-007 (Issue #76): 호밍(추적) 발사체.
  과거: 발사 시점 타겟 위치로 향하는 등속 직선 운동. 자동 평타인데도 적이
        이동하면 빗나가, 발사체가 적을 영영 못 맞히고 화면 밖으로 사라짐.
  현재: ``target`` 엔티티가 살아있는 동안 매 틱 속도 벡터를 타겟 현재 위치로
        재조준한다 (homing). swept-circle 충돌과 결합해 자동 평타 명중을
        보장한다. target 이 없는 발사체(좌표 고정)는 종전대로 직선 운동.
        GDD §3.1 영웅 평타는 회피 메커니즘을 명시하지 않으므로(자동 공격)
        명중 보장이 자연스럽다.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler

# 명중 판정 기본 반경 (px)
_DEFAULT_HIT_RADIUS = 12.0


class Projectile(Entity):
    """발사체.

    Attributes:
        vx, vy: 속도 벡터(px/s).
        damage: 명중 시 적용 데미지.
        hit_radius: 명중 판정 반경(px).
        hit: 타겟 명중 플래그 (CombatSystem이 읽고 처리).
        should_release: 풀에 반환해야 할 때 True (타겟 dying 등).
        target: 추적 대상 엔티티 (optional).
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        target_x: float = 0.0,
        target_y: float = 0.0,
        damage: int = 10,
        speed: float = 400.0,
        hit_radius: float = _DEFAULT_HIT_RADIUS,
        target: Any = None,
    ) -> None:
        super().__init__(x, y, hp=1)
        self.damage = damage
        self.speed = speed
        self.hit_radius = hit_radius
        self.target: Any = target
        self.hit: bool = False
        self.should_release: bool = False

        # 속도 벡터 계산
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = 0.0
            self.vy = 0.0

        # 발사 시 타겟 좌표 스냅샷 (target이 없으면 이 좌표로 명중 판정)
        self._target_x = target_x
        self._target_y = target_y

    # ------------------------------------------------------------------
    # 업데이트
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """등속 직선 이동 + swept-circle 명중 판정.

        타겟이 같은 dt 동안 이동할 수 있으므로 발사체 선분 [proj_old → proj_new]
        과 타겟 선분 [tgt_old → tgt_new] 사이의 최소 거리 < hit_radius 이면 명중.
        타겟에 ``_prev_x/_prev_y`` 가 없으면 점(현재 좌표)으로 fallback.

        DECISION-DL-P5P-002 (Issue #44): swept-circle 충돌 — Enemy 가 같은 틱에
        반대 방향으로 빠르게 이동하는 케이스에서도 hit_radius 통과 감지.

        Args:
            dt: 경과 시간(초).
        """
        if not self.alive or self.hit or self.should_release:
            return

        # 타겟이 dying 상태이면 fly-through → should_release
        if self.target is not None and getattr(self.target, "dying", False):
            self.should_release = True
            return

        # DECISION-DL-P5C-007 (Issue #76): 호밍 재조준.
        # 살아있는 타겟 엔티티가 있으면 매 틱 속도 벡터를 타겟 현재 위치로 다시
        # 맞춰, 적이 이동해도 발사체가 빗나가지 않게 한다 (자동 평타 명중 보장).
        if self.target is not None and getattr(self.target, "alive", False):
            self._reaim()

        # 명중 좌표 결정 (이동 전)
        # 타겟 엔티티의 prev 좌표가 있으면 이를 사용해 swept-circle 평가.
        # CombatSystem 이 매 틱 시작 시 _prev_x/_prev_y 를 갱신한다.
        if self.target is not None:
            tx_new = self.target.x
            ty_new = self.target.y
            tx_old = float(getattr(self.target, "_prev_x", tx_new))
            ty_old = float(getattr(self.target, "_prev_y", ty_new))
        else:
            tx_new = self._target_x
            ty_new = self._target_y
            tx_old = tx_new
            ty_old = ty_new

        # 이동 전 거리 확인
        dist_before = math.hypot(tx_old - self.x, ty_old - self.y)
        if dist_before < self.hit_radius:
            self.hit = True
            return

        # 이동 전 위치 저장
        old_x, old_y = self.x, self.y

        # 발사체 이동
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 이동 후 거리 확인 (발사체 new vs 타겟 new)
        dist_after = math.hypot(tx_new - self.x, ty_new - self.y)
        if dist_after < self.hit_radius:
            self.hit = True
            return

        # Swept-circle: 두 선분의 최단 거리.
        # 발사체 위치: P(t) = proj_old + t * (proj_new - proj_old), t in [0,1]
        # 타겟 위치:   T(t) = tgt_old + t * (tgt_new - tgt_old),   t in [0,1]
        # 둘 사이 거리 vector: D(t) = (proj_old - tgt_old) + t * ((proj_new - tgt_new) - (proj_old - tgt_old))
        # |D(t)|^2 가 t in [0,1] 에서 최소가 되는 t* 를 구한 뒤 거리 < hit_radius 검증.
        dx0 = old_x - tx_old
        dy0 = old_y - ty_old
        dvx = (self.x - tx_new) - dx0
        dvy = (self.y - ty_new) - dy0
        denom = dvx * dvx + dvy * dvy
        if denom <= 1e-12:
            # 두 entity 가 동일 속도로 평행 이동 → 거리 일정. 이미 dist_before 로 처리됨.
            return
        t_star = -(dx0 * dvx + dy0 * dvy) / denom
        t_star = max(0.0, min(1.0, t_star))
        closest_dx = dx0 + t_star * dvx
        closest_dy = dy0 + t_star * dvy
        closest_dist = math.hypot(closest_dx, closest_dy)
        if closest_dist < self.hit_radius:
            self.hit = True

    def _reaim(self) -> None:
        """타겟 현재 위치로 속도 벡터 재조준 (homing, DECISION-DL-P5C-007).

        속력(``self.speed``)은 유지하고 방향만 타겟 쪽으로 돌린다. 거리가 0이면
        (이미 겹침) 기존 벡터를 유지 — 다음 거리 판정에서 명중 처리된다.
        """
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed

    # ------------------------------------------------------------------
    # 초기화 (풀에서 재사용 시)
    # ------------------------------------------------------------------

    def reset(
        self,
        x: float,
        y: float,
        target_x: float,
        target_y: float,
        damage: int,
        speed: float,
        target: Any = None,
        hit_radius: float = _DEFAULT_HIT_RADIUS,
    ) -> None:
        """풀에서 재사용할 때 상태 초기화."""
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.speed = speed
        self.hit_radius = hit_radius
        self.target = target
        self.hit = False
        self.should_release = False
        self.alive = True
        self._target_x = target_x
        self._target_y = target_y

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = 0.0
            self.vy = 0.0

    # ------------------------------------------------------------------
    # Entity 오버라이드
    # ------------------------------------------------------------------

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """coords 갱신 (렌더러가 호출)."""
        return
