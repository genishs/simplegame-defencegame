"""Stage 02~05 JSON 로드 검증 테스트 (Issue #11).

- 각 스테이지가 load_stage()를 통해 정상 로드되는지 확인.
- 스키마 검증(validate_stage) + dataclass 매핑까지 포함.
- tk 비의존 단위 테스트.

DECISION-DT1-P3-2-001 ~ 004 참고.
"""

from __future__ import annotations

from src.data.loader import StageDef, StageReward, load_stage


# ---------------------------------------------------------------------------
# 공통 헬퍼
# ---------------------------------------------------------------------------
def _load(stage_id: str) -> StageDef:
    """스테이지 로드 래퍼 — pytest 에러 메시지를 명확히 하기 위해."""
    return load_stage(stage_id)


# ---------------------------------------------------------------------------
# Stage 02 — 백암성의 항복
# ---------------------------------------------------------------------------


class TestStage02:
    """stage_02.json 검증 (DECISION-DT1-P3-2-001)."""

    def test_load_succeeds(self) -> None:
        """load_stage('stage_02') 가 StageSchemaError 없이 성공한다."""
        stage = _load("stage_02")
        assert isinstance(stage, StageDef)

    def test_id(self) -> None:
        stage = _load("stage_02")
        assert stage.id == "stage_02"

    def test_title(self) -> None:
        stage = _load("stage_02")
        assert stage.title == "백암성의 항복"

    def test_wave_count_gte_4(self) -> None:
        """스테이지 02는 stage_01(3웨이브) 대비 웨이브 수가 증가해야 한다."""
        stage = _load("stage_02")
        assert len(stage.waves) >= 4

    def test_reward_grain_gte_stage01(self) -> None:
        """stage_02 grain 보상은 stage_01(50) 보다 크다 (난이도 곡선)."""
        stage = _load("stage_02")
        assert isinstance(stage.reward, StageReward)
        assert stage.reward.grain > 50

    def test_reward_unlock_stage03(self) -> None:
        """stage_02 클리어 시 stage_03가 해금된다."""
        stage = _load("stage_02")
        assert stage.reward.unlock == "stage_03"

    def test_paths_have_waypoints(self) -> None:
        """모든 path가 2개 이상의 waypoint를 가진다."""
        stage = _load("stage_02")
        for path in stage.paths:
            assert len(path.waypoints) >= 2

    def test_all_spawns_have_valid_path_ref(self) -> None:
        """각 웨이브 spawn의 path 값이 stage paths 중 하나를 참조한다."""
        stage = _load("stage_02")
        path_ids = {p.id for p in stage.paths}
        for wave in stage.waves:
            for spawn in wave.spawns:
                assert spawn.path in path_ids, f"spawn.path={spawn.path!r} not in {path_ids}"

    def test_build_zones_non_empty(self) -> None:
        """stage_02는 build_zone을 1개 이상 가진다."""
        stage = _load("stage_02")
        assert len(stage.build_zones) >= 1


# ---------------------------------------------------------------------------
# Stage 03 — 개모성의 횃불
# ---------------------------------------------------------------------------


class TestStage03:
    """stage_03.json 검증 (DECISION-DT1-P3-2-002)."""

    def test_load_succeeds(self) -> None:
        stage = _load("stage_03")
        assert isinstance(stage, StageDef)

    def test_id(self) -> None:
        stage = _load("stage_03")
        assert stage.id == "stage_03"

    def test_title(self) -> None:
        stage = _load("stage_03")
        assert stage.title == "개모성의 횃불"

    def test_multi_path(self) -> None:
        """야간 협곡 스테이지 — 2개 이상의 스폰 경로가 있어야 한다 (DECISION-DT1-P3-2-002)."""
        stage = _load("stage_03")
        assert len(stage.paths) >= 2

    def test_wave_count_gte_stage02(self) -> None:
        """stage_03 웨이브 수 >= stage_02 웨이브 수."""
        s02 = _load("stage_02")
        s03 = _load("stage_03")
        assert len(s03.waves) >= len(s02.waves)

    def test_reward_grain_progression(self) -> None:
        """stage_03 grain > stage_02 grain (난이도 곡선 상승)."""
        s02 = _load("stage_02")
        s03 = _load("stage_03")
        assert s03.reward.grain > s02.reward.grain

    def test_reward_unlock_stage04(self) -> None:
        stage = _load("stage_03")
        assert stage.reward.unlock == "stage_04"

    def test_all_spawns_have_valid_path_ref(self) -> None:
        stage = _load("stage_03")
        path_ids = {p.id for p in stage.paths}
        for wave in stage.waves:
            for spawn in wave.spawns:
                assert spawn.path in path_ids

    def test_boss_wave_exists(self) -> None:
        """stage_03에는 boss 필드가 있는 웨이브가 1개 이상이다."""
        stage = _load("stage_03")
        boss_waves = [w for w in stage.waves if w.boss is not None]
        assert len(boss_waves) >= 1


# ---------------------------------------------------------------------------
# Stage 04 — 안시성 외곽
# ---------------------------------------------------------------------------


class TestStage04:
    """stage_04.json 검증 (DECISION-DT1-P3-2-003)."""

    def test_load_succeeds(self) -> None:
        stage = _load("stage_04")
        assert isinstance(stage, StageDef)

    def test_id(self) -> None:
        stage = _load("stage_04")
        assert stage.id == "stage_04"

    def test_title(self) -> None:
        stage = _load("stage_04")
        assert stage.title == "안시성 외곽"

    def test_multi_lane_paths(self) -> None:
        """중후반 다중 lane — 3개 이상 경로가 있어야 한다 (DECISION-DT1-P3-2-003)."""
        stage = _load("stage_04")
        assert len(stage.paths) >= 3

    def test_build_zones_expanded(self) -> None:
        """stage_04 build_zone >= stage_03 build_zone (확장)."""
        s03 = _load("stage_03")
        s04 = _load("stage_04")
        assert len(s04.build_zones) >= len(s03.build_zones)

    def test_wave_count_7(self) -> None:
        """stage_04(안시성 외곽)는 7 웨이브 (스토리 목표: 7번의 적 진군)."""
        stage = _load("stage_04")
        assert len(stage.waves) == 7

    def test_reward_grain_positive(self) -> None:
        """stage_04 grain 보상은 양수다.

        NOTE: Phase 4 난이도 하향 정책(DECISION-PL-P4-015)으로 stage_03 grain 이
        220으로 상향되어 stage_04(200)보다 커졌다. stage_04~05는 무변경 정책
        (DECISION-PL-P4-013)이므로 "grain 단조 증가" 불변식은 더 이상 성립하지 않음.
        grain 양수 검증으로 대체.
        """
        s04 = _load("stage_04")
        assert s04.reward.grain > 0

    def test_reward_unlock_stage05(self) -> None:
        stage = _load("stage_04")
        assert stage.reward.unlock == "stage_05"

    def test_all_spawns_valid_path(self) -> None:
        stage = _load("stage_04")
        path_ids = {p.id for p in stage.paths}
        for wave in stage.waves:
            for spawn in wave.spawns:
                assert spawn.path in path_ids

    def test_boss_wave_exists(self) -> None:
        stage = _load("stage_04")
        boss_waves = [w for w in stage.waves if w.boss is not None]
        assert len(boss_waves) >= 1

    def test_starting_lives_gte_stage03(self) -> None:
        """안시성 외곽(중후반)은 stage_03보다 lives가 많거나 같다."""
        s03 = _load("stage_03")
        s04 = _load("stage_04")
        assert s04.lives >= s03.lives


# ---------------------------------------------------------------------------
# Stage 05 — 안시성 토산 (최종)
# ---------------------------------------------------------------------------


class TestStage05:
    """stage_05.json 검증 (DECISION-DT1-P3-2-004)."""

    def test_load_succeeds(self) -> None:
        stage = _load("stage_05")
        assert isinstance(stage, StageDef)

    def test_id(self) -> None:
        stage = _load("stage_05")
        assert stage.id == "stage_05"

    def test_title(self) -> None:
        stage = _load("stage_05")
        assert stage.title == "안시성 토산"

    def test_wave_count_10(self) -> None:
        """stage_05는 Phase 1(W1~W6) + Phase 2(W7~W10) = 10웨이브 (스토리 §3.1)."""
        stage = _load("stage_05")
        assert len(stage.waves) == 10

    def test_four_paths(self) -> None:
        """stage_05는 토산 경로를 포함해 4개 이상의 경로를 가진다 (DECISION-DT1-P3-2-004)."""
        stage = _load("stage_05")
        assert len(stage.paths) >= 4

    def test_boss_is_tang_taizong(self) -> None:
        """최종 보스는 tang_taizong (당 태종 친림 — 스토리 §4.9)."""
        stage = _load("stage_05")
        boss_waves = [w for w in stage.waves if w.boss == "tang_taizong"]
        assert len(boss_waves) >= 1

    def test_reward_grain_highest(self) -> None:
        """stage_05 grain 보상이 모든 스테이지 중 가장 높다."""
        grains = [_load(f"stage_0{i}").reward.grain for i in range(1, 6)]
        assert grains[-1] == max(grains)

    def test_no_unlock_field(self) -> None:
        """stage_05 클리어 후 unlock 없음 (최종 스테이지)."""
        stage = _load("stage_05")
        assert stage.reward.unlock is None

    def test_all_spawns_valid_path(self) -> None:
        stage = _load("stage_05")
        path_ids = {p.id for p in stage.paths}
        for wave in stage.waves:
            for spawn in wave.spawns:
                assert spawn.path in path_ids

    def test_max_build_zones(self) -> None:
        """최종 스테이지는 모든 스테이지 중 build_zone이 가장 많다."""
        counts = [len(_load(f"stage_0{i}").build_zones) for i in range(1, 6)]
        assert counts[-1] == max(counts)

    def test_starting_gold_highest(self) -> None:
        """stage_05 starting_gold가 가장 높다 (최종 스테이지 자원)."""
        golds = [_load(f"stage_0{i}").starting_gold for i in range(1, 6)]
        assert golds[-1] == max(golds)
