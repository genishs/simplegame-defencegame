"""BattleSceneSimulator 자동 가드 (Issue #60).

DECISION-DL-P5C-001:

  v0.4.0-rc.1~rc.5 누적 사용자 검수 결함 5건 (#51/#53/#55/#56/#57+58) 이 모두
  기존 BL-07 시뮬레이터를 통과한 뒤 사용자 시각 검수에서야 발견됨. 본 모듈은
  실 BattleScene 사슬을 거치는 ``BattleSceneSimulator`` 가 **그러한 결함들을
  사전 자동 감지하는 능력을 갖췄음** 을 회귀 가드한다.

각 테스트는 사용자 검수에서 발견된 결함 카테고리와 매핑된다::

  test_*_spec_datas_loaded            -- Issue #51 / #52  spec datas 누락
  test_*_render_creates_canvas_items  -- Issue #53        render pass
  test_*_placement_ui_*               -- Issue #56        배치 UI
  test_*_hero_auto_attack_*           -- Issue #57/#58    영웅 평타
  test_*_full_chain_*                 -- 통합             update+render+UI 사슬

도메인 가드: ``tkinter`` import 전혀 없음 (FakeApp + FakeCanvas 사용).
외부 패키지 추가 없음 (stdlib + 기존 fakes 재사용).

DECISION-DL-P5C-002: stage_03 만 cleared 검증 대상으로 선정.
  - stage_01: 신규 결함 (DECISION-DL-P5C-003) 으로 BattleScene 이 적의
    castle 도달을 ``world['goals_reached']`` 로 반영하지 않아 클리어/패배
    판정 자체가 발생하지 않음. 해당 결함은 별도 이슈 후속 처리.
  - stage_02: 신규 결함 (DECISION-DL-P5C-004) 으로 ``enemies.json`` 에
    ``tang_archer`` 정의가 누락되어 BattleScene 의 ``_spawn_enemy`` 가
    wave 진행을 막음. 별도 이슈 후속 처리.
  - stage_03: 신규 결함 영향 회피 (path 다중 + 충분한 build_zones) — 정합
    검증 대상.
"""

from __future__ import annotations

import pytest

from tests.battle_scene_simulator import BattleSceneSimulator

pytestmark = pytest.mark.regression_p4


# ---------------------------------------------------------------------------
# 1. spec datas 로드 가드 (Issue #51 / #52)
# ---------------------------------------------------------------------------


class TestSpecDatas:
    """Issue #51/#52 패밀리: stage_01.json / units.json / enemies.json 실 로드."""

    def test_stage01_spec_datas_loaded(self) -> None:
        """stage_01 build 후 stage + units_db + enemies_db 가 모두 로드된다."""
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()
        assert scene.stage is not None, "stage_01.json 이 로드되어야 한다 (Issue #52)"
        assert scene._units_db, "units.json 이 로드되어 _units_db 가 채워져야 한다"
        assert scene._enemy_defs, "enemies.json 이 로드되어 _enemy_defs 가 채워져야 한다"
        # 결함 #51 사례: stage_01 진입 자체가 실패하지 않아야 한다.
        assert scene._stage_load_error is None

    def test_stage_load_error_propagates_to_result(self) -> None:
        """존재하지 않는 stage_id 는 stage_load_error + cleared=False 로 noisy fail."""
        sim = BattleSceneSimulator("stage_does_not_exist_99")
        result = sim.run()
        assert result.cleared is False
        assert result.extra.get("reason") == "stage_load_failed"


# ---------------------------------------------------------------------------
# 2. render() 사슬 가드 (Issue #53)
# ---------------------------------------------------------------------------


class TestRenderChain:
    """Issue #53 패밀리: BattleScene.render() 가 entity 캔버스 아이템을 생성."""

    def test_build_then_render_creates_hero_canvas_item(self) -> None:
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()
        assert scene.world["hero"] is not None
        assert scene.world["hero"].canvas_id is None
        scene.render()
        assert (
            scene.world["hero"].canvas_id is not None
        ), "render() 후 영웅 canvas_id 가 할당되어야 한다 (Issue #53)"

    def test_run_invokes_render_many_times(self) -> None:
        """run() 은 update 와 render 를 동등 횟수로 호출한다."""
        sim = BattleSceneSimulator("stage_01")
        sim.MAX_SIM_TIME = 5.0  # 짧은 cap
        result = sim.run()
        # render 와 update 는 1:1 매칭 (App._tick 정합).
        assert result.render_calls == result.update_ticks
        assert result.render_calls > 0, "render() 가 한 번도 호출되지 않으면 결함 #53 재발"

    def test_canvas_items_grow_when_enemies_spawn(self) -> None:
        """wave 시작 후 적이 spawn 되면 캔버스 아이템 수가 증가한다."""
        sim = BattleSceneSimulator("stage_01")
        sim.MAX_SIM_TIME = 8.0  # wave 1 delay 통과 충분
        result = sim.run()
        assert result.enemies_spawned >= 1, "wave 1 동안 적이 1체 이상 spawn 되어야 한다"
        # 캔버스 아이템 peak 가 build 직후 + entity 분만큼 증가.
        assert (
            result.canvas_items_peak > 10
        ), "render 사슬 정합 — entities 가 캔버스에 그려져야 한다 (Issue #53)"


# ---------------------------------------------------------------------------
# 3. 배치 UI 사슬 가드 (Issue #56)
# ---------------------------------------------------------------------------


class TestPlacementUI:
    """Issue #56 패밀리: 유닛 선택 + build_zone 클릭 사슬."""

    def test_placement_ui_places_units_in_all_zones(self) -> None:
        """자동 배치 정책은 모든 build_zone 을 점유한다 (UI 클릭 사슬 검증)."""
        sim = BattleSceneSimulator("stage_01")
        sim.build_scene()
        placed = sim.auto_place_strongest_unit()
        assert sim.scene is not None
        zone_count = len(sim.scene.stage.build_zones)
        assert placed == zone_count, f"build_zone {zone_count}개 모두 배치 기대, 실제 {placed}"
        assert len(sim.scene.world["allies"]) == zone_count

    def test_placement_ui_persists_through_run(self) -> None:
        """run() 시작 시 배치된 ally 는 시뮬 종료까지 world['allies'] 에 남는다."""
        sim = BattleSceneSimulator("stage_01")
        sim.MAX_SIM_TIME = 5.0
        result = sim.run()
        assert result.allies_placed > 0
        assert sim.scene is not None
        # 종료 시 ally 가 사라지지 않아야 함 (살아있다는 가정).
        assert len(sim.scene.world["allies"]) == result.allies_placed

    def test_units_db_keys_match_clickable_buttons(self) -> None:
        """_units_db 의 모든 유닛이 _placement_btn_state 에 버튼이 있다."""
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()
        for uid in scene._units_db:
            assert (
                uid in scene._placement_btn_state
            ), f"유닛 {uid} 에 대응하는 클릭 버튼이 패널에 없음 (Issue #56)"


# ---------------------------------------------------------------------------
# 4. 영웅 평타 사슬 가드 (Issue #57 / #58)
# ---------------------------------------------------------------------------


class TestHeroAutoAttack:
    """Issue #57/#58 패밀리: BattleScene.update 가 매 틱 영웅 평타를 트리거."""

    def test_hero_spawns_projectiles_during_run(self) -> None:
        """run() 중 적이 사거리 내에 들어오면 hero 가 projectile 을 스폰한다."""
        sim = BattleSceneSimulator("stage_01")
        sim.MAX_SIM_TIME = 15.0  # wave 1 진입 + 영웅 사거리 진입 충분
        result = sim.run()
        assert (
            result.hero_projectiles_spawned > 0
        ), "BattleScene 이 영웅 평타로 projectile 을 스폰해야 한다 (Issue #57/#58)"

    def test_hero_attack_works_with_zero_allies(self) -> None:
        """영웅만으로도 (ally 없이) 평타가 시동된다 — 수동 모드 회귀."""
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()
        # 배치 단계를 건너뛰고 직접 update 사슬만 호출.
        from src.data.loader import EnemyDef
        from src.entities.enemy import Enemy

        edef = EnemyDef(
            id="x",
            name="x",
            hp=50,
            speed=0,
            armor=0,
            damage_to_castle=1,
            gold_drop=8,
            sprite="x",
        )
        hero = scene.world["hero"]
        scene.world["enemies"].append(Enemy(x=hero.x + 100.0, y=hero.y, enemy_def=edef, path_id="p_main"))
        before = len(scene.world["projectiles"])
        scene.update(0.016)
        after = len(scene.world["projectiles"])
        assert after == before + 1, "영웅 평타가 1 projectile 스폰해야 함"


# ---------------------------------------------------------------------------
# 5. 통합 사슬 가드 (update + render + UI + clear)
# ---------------------------------------------------------------------------


class TestFullChain:
    """통합: stage_01/02/03 을 BattleScene 사슬로 굴려 cleared=True 까지 도달.

    DECISION-DL-P5C-006 (Issue #62 + #64 종합 cleanup):
        stage_01 lives 차감 (#62) + stage_02/03 enemies.json (#64) 결함 해소
        후, 본 통합 가드는 3개 스테이지 모두 BattleScene 사슬만으로 클리어
        가능함을 보장한다. 기존 DECISION-DL-P5C-002 (stage_03 only) 가드를
        승격 — 후속 결함 사전 감지망 확장.
    """

    @pytest.mark.parametrize("stage_id", ["stage_01", "stage_02", "stage_03"])
    def test_stages_clear_via_battle_scene_chain(self, stage_id: str) -> None:
        """stage_01/02/03 모두 BattleScene 사슬만으로 클리어 (DECISION-DL-P5C-006).

        BL-07 시뮬레이터(`src/systems/auto_mode_simulator.py`) 와 별개로,
        실 BattleScene + UI + render 사슬을 그대로 사용해도 클리어가 도달
        해야 한다 (Issue #62/#64 회귀 가드).
        """
        sim = BattleSceneSimulator(stage_id)
        result = sim.run()
        assert result.cleared is True, (
            f"{stage_id} BattleScene 사슬 클리어 실패: "
            f"elapsed={result.elapsed_sim_seconds:.1f}s "
            f"spawned={result.enemies_spawned} defeated={result.enemies_defeated} "
            f"allies={result.allies_placed} hero_proj={result.hero_projectiles_spawned}"
        )
        # 사슬 통합 메트릭 모두 양수여야 한다.
        assert result.update_ticks > 0
        assert result.render_calls > 0
        assert result.allies_placed > 0
        assert result.hero_projectiles_spawned > 0
        assert result.enemies_spawned > 0
        assert result.canvas_items_peak > 0
        assert result.units_db_loaded is True
        assert result.enemies_db_loaded is True


# ---------------------------------------------------------------------------
# 6. Castle breach (lives 차감) 가드 — Issue #62, DECISION-DL-P5C-005
# ---------------------------------------------------------------------------


class TestCastleBreach:
    """Issue #62 패밀리: BattleScene 이 enemy.goal_reached 를 lives 차감으로 반영."""

    def test_goal_reached_triggers_goals_reached_increment(self) -> None:
        """단일 적이 castle 도달 → goals_reached 가 damage_to_castle 만큼 증가."""
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()

        from src.data.loader import EnemyDef
        from src.entities.enemy import Enemy

        edef = EnemyDef(
            id="x",
            name="x",
            hp=50,
            speed=0,
            armor=0,
            damage_to_castle=3,
            gold_drop=8,
            sprite="x",
        )
        enemy = Enemy(x=0.0, y=0.0, enemy_def=edef, path_id="p_main")
        enemy.goal_reached = True  # PathingSystem 결과 모사.
        scene.world["enemies"].append(enemy)

        before = int(scene.world.get("goals_reached", 0))
        scene.update(0.016)
        after = int(scene.world.get("goals_reached", 0))
        assert after == before + 3, "damage_to_castle=3 만큼 증가해야 함 (DECISION-DL-P5C-005)"
        # breach 후 enemy 는 cleanup 으로 enemies 리스트에서 제거되어야 한다.
        assert enemy not in scene.world["enemies"]

    def test_castle_breach_does_not_double_count_dying_enemy(self) -> None:
        """이미 사망 페이드 중인 적은 castle breach 로 lives 차감하지 않는다."""
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()

        from src.data.loader import EnemyDef
        from src.entities.enemy import Enemy

        edef = EnemyDef(
            id="x",
            name="x",
            hp=50,
            speed=0,
            armor=0,
            damage_to_castle=5,
            gold_drop=8,
            sprite="x",
        )
        enemy = Enemy(x=0.0, y=0.0, enemy_def=edef, path_id="p_main")
        enemy.goal_reached = True
        enemy.dying = True  # 이미 처치되어 페이드 중 — breach 무시되어야 함.
        scene.world["enemies"].append(enemy)

        before = int(scene.world.get("goals_reached", 0))
        scene.update(0.016)
        after = int(scene.world.get("goals_reached", 0))
        assert after == before, "dying 상태 적은 castle breach 누적에서 제외 (이중 카운트 방지)"

    def test_stage01_eventually_terminates_when_unguarded(self) -> None:
        """stage_01 에서 ally 없이 영웅만으로 굴려도 결국 게임이 종료된다 (defeat).

        Issue #62 fix 전에는 적이 castle 에 멈춰 영원히 cleared 도 defeat 도 안
        나왔다. 본 가드는 게임이 무한 루프에 빠지지 않음을 검증한다.
        """
        sim = BattleSceneSimulator("stage_01")
        scene = sim.build_scene()
        # ally 배치 단계를 건너뛴다 — 영웅만으로는 stage_01 의 모든 wave 를
        # 막을 수 없으므로 결국 defeat 또는 cleared 종료가 나야 한다.
        sim.MAX_SIM_TIME = 120.0  # 2분이면 wave 3 까지 충분히 지남.

        elapsed = 0.0
        update_ticks = 0
        while elapsed < sim.MAX_SIM_TIME and not scene._game_over:
            scene.update(sim.DT)
            update_ticks += 1
            if scene._game_over:
                break
            elapsed += sim.DT

        assert (
            scene._game_over
        ), f"stage_01 이 ally 없이도 종료되어야 함 (elapsed={elapsed:.1f}s ticks={update_ticks})"
        # goals_reached 가 0 이상으로 누적되었어야 (영웅만으로는 막기 부족 — defeat).
        assert int(scene.world.get("goals_reached", 0)) > 0


# ---------------------------------------------------------------------------
# 7. enemies.json 데이터 정합 가드 — Issue #64, DECISION-DL-P5C-005
# ---------------------------------------------------------------------------


class TestEnemiesDataIntegrity:
    """Issue #64 패밀리: 모든 stage 의 enemy type 이 enemies.json 에 존재."""

    @pytest.mark.parametrize("stage_id", ["stage_01", "stage_02", "stage_03"])
    def test_all_spawn_types_in_enemies_db(self, stage_id: str) -> None:
        """stage_NN 의 모든 wave spawn type 이 enemies.json 에 정의되어 있다.

        보스(`wave.boss`) 도 enemies.json 에 정의되어야 spawn fallback 이 없다.
        """
        from src.data.loader import load_enemies, load_stage

        db = load_enemies()
        stage = load_stage(stage_id)
        missing: list[str] = []
        for w in stage.waves:
            for sp in w.spawns:
                if sp.type not in db:
                    missing.append(sp.type)
            if w.boss and w.boss not in db:
                missing.append(w.boss)
        assert not missing, (
            f"{stage_id} 의 enemy type 누락: {missing} (DECISION-DL-P5C-005, Issue #64)"
        )

    def test_archer_and_scout_defined(self) -> None:
        """Issue #64 회귀: tang_archer, tang_scout 가 enemies.json 에 존재."""
        from src.data.loader import load_enemies

        db = load_enemies()
        assert "tang_archer" in db, "tang_archer 가 enemies.json 에 정의되어야 한다 (Issue #64)"
        assert "tang_scout" in db, "tang_scout 가 enemies.json 에 정의되어야 한다 (Issue #64)"

    def test_stage_02_03_bosses_defined(self) -> None:
        """stage_02/03 보스 정의도 enemies.json 에 존재 (통합 가드 통과 조건)."""
        from src.data.loader import load_enemies

        db = load_enemies()
        assert "tang_vanguard_captain" in db, "stage_02 보스 정의 필요"
        assert "tang_night_raider" in db, "stage_03 보스 정의 필요"
