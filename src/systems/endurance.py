"""토산 "버티기 승리" 게이지 (적 사기·추위) — tkinter 비의존 (교육 통합 H7).

DESIGN (docs/15 §2.1 H7·§3.4·LO2, docs/16 Wave4 4-1):
- 스테이지5 한정. 사료(자치통감/삼국사기)의 "추위·보급 부족·토산 붕괴 → 당군
  철수" 를 메커닉화: 플레이어가 **버틸수록** 적 사기/추위 게이지가 차오르고,
  가득 차면 "버티기 승리"(적 자멸/철수). 공격만이 승리가 아니라는 메시지(LO2).
- 게이지 충전 동력(0..1):
    * 시간 경과(추위가 다가옴) — 가장 큰 축.
    * 웨이브 진행도(공방 장기화).
    * 적 처치 누적(당군 피로) — 보조 가산.
  세 축의 가중합을 0..1 로 클램프. 100% 도달 시 ``victory`` True.
- 본 모듈은 순수 상태 전이. 렌더(ui)·승리 처리(scene)는 호출자가 결합.

비파괴: 스테이지 메타(``endurance``)가 없으면 보수적 기본값으로 동작하며,
H7 비활성(스테이지5 외)에서는 씬이 본 시스템을 아예 생성하지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EnduranceConfig:
    """버티기 게이지 튜닝값 (stage_05.json ``endurance`` 블록에서 주입 가능).

    Attributes:
        duration_s: 시간 축이 단독으로 게이지를 가득 채우는 데 걸리는 초.
            추위가 다가오는 속도. 기본 180초(3분, 시뮬레이터 MAX 와 정합).
        time_weight: 시간 축 가중치.
        wave_weight: 웨이브 진행 축 가중치.
        kill_weight: 적 처치 축 가중치.
        kills_for_full: 처치 축이 가득 차는 누적 처치 수.
    """

    duration_s: float = 180.0
    time_weight: float = 0.6
    wave_weight: float = 0.3
    kill_weight: float = 0.1
    kills_for_full: int = 80

    @classmethod
    def from_meta(cls, meta: dict | None) -> EnduranceConfig:
        """stage JSON 의 ``endurance`` dict 로부터 설정 생성(없으면 기본)."""
        if not isinstance(meta, dict):
            return cls()

        def _f(key: str, default: float) -> float:
            v = meta.get(key, default)
            try:
                return float(v)
            except (TypeError, ValueError):
                return default

        def _i(key: str, default: int) -> int:
            v = meta.get(key, default)
            try:
                return int(v)
            except (TypeError, ValueError):
                return default

        return cls(
            duration_s=max(1.0, _f("duration_s", 180.0)),
            time_weight=_f("time_weight", 0.6),
            wave_weight=_f("wave_weight", 0.3),
            kill_weight=_f("kill_weight", 0.1),
            kills_for_full=max(1, _i("kills_for_full", 80)),
        )


class EnduranceSystem:
    """버티기 게이지 상태기 (H7). tk-free.

    호출자가 매 틱 ``update(dt, wave_progress, kills)`` 를 호출한다.

    Attributes:
        fill: 현재 게이지 0.0~1.0.
        victory: 게이지가 가득 차 "버티기 승리" 가 성립했는가(래치 — 한 번 True 면 유지).
    """

    def __init__(self, config: EnduranceConfig | None = None) -> None:
        self.config = config or EnduranceConfig()
        self._elapsed: float = 0.0
        self.fill: float = 0.0
        self.victory: bool = False

    def update(self, dt: float, *, wave_progress: float = 0.0, kills: int = 0) -> bool:
        """게이지 갱신. 이번 갱신으로 승리가 **새로** 성립하면 True 반환.

        Args:
            dt: 경과 시간(초).
            wave_progress: 0.0~1.0 웨이브 진행도(현재 웨이브/전체).
            kills: 누적 적 처치 수.

        Returns:
            이번 호출에서 처음 victory 가 성립했으면 True(엣지). 이미 승리 상태였거나
            아직 미달이면 False.
        """
        if self.victory:
            return False
        self._elapsed += max(0.0, dt)
        cfg = self.config

        time_axis = min(1.0, self._elapsed / cfg.duration_s) if cfg.duration_s > 0 else 1.0
        wave_axis = max(0.0, min(1.0, wave_progress))
        kill_axis = min(1.0, kills / cfg.kills_for_full) if cfg.kills_for_full > 0 else 0.0

        total_w = cfg.time_weight + cfg.wave_weight + cfg.kill_weight
        if total_w <= 0:
            self.fill = 0.0
        else:
            weighted = time_axis * cfg.time_weight + wave_axis * cfg.wave_weight + kill_axis * cfg.kill_weight
            self.fill = max(0.0, min(1.0, weighted / total_w))

        if self.fill >= 1.0 and not self.victory:
            self.victory = True
            return True
        return False
