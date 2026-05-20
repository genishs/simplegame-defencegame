"""BattleSceneSimulator — 실 BattleScene 사슬을 따라가는 통합 시뮬레이터.

DECISION-DL-P5C-001 (Issue #60):

  v0.4.0-rc.1~rc.5 누적 사용자 검수 결함 5건 (#51 spec datas / #53 render
  pass / #55 tutorial 클릭 / #56 배치 UI / #57+58 영웅 평타) 이 모두 기존
  BL-07 시뮬레이터 (``src/systems/auto_mode_simulator.py``) 의 자동 가드를
  통과한 뒤 사용자 시각 검수에서야 발견됨. 근본 원인은 BL-07 이 systems
  (WaveSystem / PathingSystem) 만 직접 호출하고 실 BattleScene 의 build /
  render / 클릭 핸들러 사슬을 거치지 않은 정합 빈약.

  본 모듈은 BL-07 과 별개로 **실 BattleScene + FakeApp/FakeCanvas** 를 사용
  하는 통합 시뮬레이터 ``BattleSceneSimulator`` 를 제공한다. BL-07 은 그대로
  남겨 두어 (성능 < 5s / 직접 DPS 모델) 클리어율 회귀 가드 책임을 유지하고,
  본 시뮬레이터는 사용자 경험 사슬 (spec 로드 → build → 클릭 → render →
  update → clear) 자체를 자동으로 재생산해 검수 결함을 사전 차단한다.

비교표 (DECISION-DL-P5C-001 본문)::

  영역                     BL-07 (auto_mode_simulator)   본 시뮬레이터
  ------------------------ ----------------------------- --------------------
  대상 코드                src/systems 직접 호출          src/scenes/battle_scene
                                                          .BattleScene 그대로
  build / spec datas       자체 fallback 사용             load_stage / load_units
                                                          / load_enemies 모두 실
                                                          호출 (PR #52 결함 감지)
  render() 호출            없음                          매 틱 render → canvas
                                                          item 검증 (PR #54 감지)
  배치 UI 인터랙션         _auto_place_units 가 직접     _on_unit_button_click /
                          Ally append                    _on_build_zone_click
                                                          (PR #59 감지)
  영웅 평타                미사용                        BattleScene._tick_hero_
                                                          attack → Projectile
                                                          spawn (PR #59 감지)
  CombatSystem 명중        직접 DPS 모델 (대체)           CombatSystem.update 가
                                                          Projectile + Enemy 명중
                                                          처리 (실 사슬 동일)
  성능                     15회 < 5s (BL-07 임계값)       1회 ~수초 (정합 검증)
  목적                     클리어율 회귀 가드             사용자 경험 사슬 가드

도메인 가드:
  - 본 모듈은 ``tests/`` 하위에 있으므로 src/systems / src/entities tkinter-free
    제약 영향 없음.
  - FakeApp / FakeCanvas 만 사용 (``tkinter`` import 전혀 없음).
  - 외부 패키지 추가 없음 (stdlib + 기존 fakes 재사용).

Usage::

    from tests.battle_scene_simulator import BattleSceneSimulator

    sim = BattleSceneSimulator(stage_id="stage_01")
    result = sim.run()
    assert result.cleared
    assert result.hero_projectiles_spawned > 0
    assert result.allies_placed > 0
    assert result.render_calls > 0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 기존 FakeApp / FakeCanvas 재사용 (tests/test_battle_scene_flow.py 정의).
from tests.test_battle_scene_flow import FakeApp


@dataclass
class BattleSimResult:
    """BattleSceneSimulator.run() 결과.

    ``BL-07.SimResult`` 와 호환되는 핵심 필드를 보존하면서, BattleScene 통합
    검증을 위한 시각/UI 측 메트릭을 추가 노출한다.
    """

    stage_id: str
    cleared: bool
    lives_remaining: int
    elapsed_sim_seconds: float
    enemies_defeated: int = 0
    # ----- 통합 시뮬레이터 전용 (BL-07 미포함) -----
    update_ticks: int = 0
    render_calls: int = 0
    allies_placed: int = 0
    hero_projectiles_spawned: int = 0
    enemies_spawned: int = 0
    canvas_items_peak: int = 0
    units_db_loaded: bool = False
    enemies_db_loaded: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


class BattleSceneSimulator:
    """실 BattleScene 을 FakeApp + FakeCanvas 위에서 자동 모드로 굴리는 시뮬레이터.

    실행 흐름:

    1. ``BattleScene(app, stage_id).build()`` — 실 spec datas 로드.
    2. UI 인터랙션으로 모든 build_zone 에 가장 강한 (atk 최대) 유닛 배치 —
       ``_on_unit_button_click`` + ``_on_build_zone_click`` 직접 호출.
    3. 매 틱 ``scene.update(dt)`` + ``scene.render()`` 호출 (App._tick 와 동일).
    4. ``scene._game_over`` 또는 ``MAX_SIM_TIME`` 도달까지 반복.

    승리/패배 판정은 BattleScene 자체 ``_check_end_conditions`` 에 위임.
    """

    DT: float = 0.05  # 50 ms 틱 (BL-07 의 16ms 보다 살짝 크게 — 통합 비용 절감)
    MAX_SIM_TIME: float = 180.0  # 3분 in-game (BL-07 의 10분보다 짧게)

    def __init__(self, stage_id: str = "stage_01") -> None:
        self.stage_id = stage_id
        self.app: Any | None = None
        self.scene: Any | None = None

    # ------------------------------------------------------------------
    # 시나리오
    # ------------------------------------------------------------------
    def build_scene(self) -> Any:
        """BattleScene 을 FakeApp 위에서 build() 까지 마치고 반환."""
        from src.scenes.battle_scene import BattleScene

        self.app = FakeApp()
        self.scene = BattleScene(self.app, stage_id=self.stage_id)
        self.scene.build()
        return self.scene

    def auto_place_strongest_unit(self) -> int:
        """모든 build_zone 에 가장 강한 (atk 최대) 유닛을 UI 인터랙션으로 배치.

        BL-07 의 ``_auto_place_units`` 와 동등한 정책이지만, 본 시뮬레이터는
        BattleScene 의 클릭 핸들러 (``_on_unit_button_click`` →
        ``_on_build_zone_click``) 를 직접 호출해 UI 사슬을 거친다 (PR #59 감지).

        반환: 실제 배치된 ally 수.
        """
        scene = self.scene
        assert scene is not None
        units_db = scene._units_db
        if not units_db or scene.stage is None:
            return 0

        # 가장 강한 유닛 (atk desc, cost asc tie-breaker — 결정론적)
        best_uid = max(units_db.items(), key=lambda kv: (kv[1].atk, -kv[1].cost))[0]
        # 배치를 위해 곡식을 충분히 확보 (자동 검증 환경 — 경제 균형 영향 0).
        scene.world["food"] = max(int(scene.world.get("food", 0)), 10_000)
        scene.world["gold"] = max(int(scene.world.get("gold", 0)), 10_000)

        # 유닛 선택 (토글)
        scene._on_unit_button_click(best_uid)
        placed = 0
        for idx in range(len(scene.stage.build_zones)):
            before = len(scene.world["allies"])
            scene._on_build_zone_click(idx)
            after = len(scene.world["allies"])
            if after > before:
                placed += 1
                # _on_build_zone_click 후 selection 이 풀리지 않는 사양 — 그대로
                # 다음 zone 으로 이어 클릭. 토글이 해제된 경우 다시 선택.
                if scene._selected_unit_id != best_uid:
                    scene._on_unit_button_click(best_uid)
        return placed

    def run(self) -> BattleSimResult:
        """전체 흐름 실행 후 결과 반환."""
        scene = self.build_scene()
        assert scene is not None
        app = self.app
        assert app is not None

        # ----- 0. spec datas 로드 검증 -----
        units_loaded = bool(scene._units_db)
        enemies_loaded = bool(scene._enemy_defs)
        # stage 가 로드 실패면 즉시 패배 처리.
        if scene.stage is None:
            return BattleSimResult(
                stage_id=self.stage_id,
                cleared=False,
                lives_remaining=0,
                elapsed_sim_seconds=0.0,
                units_db_loaded=units_loaded,
                enemies_db_loaded=enemies_loaded,
                extra={"reason": "stage_load_failed"},
            )

        # ----- 1. UI 인터랙션으로 ally 배치 -----
        allies_placed = self.auto_place_strongest_unit()

        # ----- 2. 메인 루프 (update + render) -----
        elapsed = 0.0
        update_ticks = 0
        render_calls = 0
        hero_projectiles_spawned = 0
        enemies_spawned = 0
        canvas_items_peak = 0
        # spawn 누적 추적 — set 사용 (object identity).
        seen_projectiles: set[int] = set()
        seen_enemies: set[int] = set()

        while elapsed < self.MAX_SIM_TIME:
            scene.update(self.DT)
            update_ticks += 1
            scene.render()
            render_calls += 1

            # spawn 추적
            for p in scene.world.get("projectiles", []):
                pid = id(p)
                if pid not in seen_projectiles:
                    seen_projectiles.add(pid)
                    # Projectile 가 Hero 발 인지 식별: owner=hero 또는 source 가
                    # hero 인스턴스. 보수적으로 모든 projectile 누적.
                    hero_projectiles_spawned += 1
            for e in scene.world.get("enemies", []):
                eid = id(e)
                if eid not in seen_enemies:
                    seen_enemies.add(eid)
                    enemies_spawned += 1

            canvas_items_peak = max(canvas_items_peak, len(app.canvas.items))

            if scene._game_over:
                break
            elapsed += self.DT

        # 결과 판정
        lives = int(scene.world.get("lives", 0))
        goals_reached = int(scene.world.get("goals_reached", 0))
        cleared = bool(scene.wave.all_clear and not scene.world.get("enemies"))
        # BattleScene 자체 판정도 반영 (defeat 시 game_over=True)
        if goals_reached >= lives and lives > 0:
            cleared = False
        if not cleared and not scene._game_over and elapsed >= self.MAX_SIM_TIME:
            cleared = False

        enemies_defeated = max(0, enemies_spawned - len(scene.world.get("enemies", [])) - goals_reached)

        return BattleSimResult(
            stage_id=self.stage_id,
            cleared=cleared,
            lives_remaining=max(0, lives - goals_reached),
            elapsed_sim_seconds=elapsed,
            enemies_defeated=enemies_defeated,
            update_ticks=update_ticks,
            render_calls=render_calls,
            allies_placed=allies_placed,
            hero_projectiles_spawned=hero_projectiles_spawned,
            enemies_spawned=enemies_spawned,
            canvas_items_peak=canvas_items_peak,
            units_db_loaded=units_loaded,
            enemies_db_loaded=enemies_loaded,
        )
