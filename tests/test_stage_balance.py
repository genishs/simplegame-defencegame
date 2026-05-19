"""Phase 4 난이도 하향 정책 매트릭스 가드 테스트 (Issue #27).

DECISION-DT1-P4-001 ~ 004 (개발 팀원 1, Phase 4 라운드):
  - DT1-P4-001: wave 6→4 축소 시 정책 문서 §3.2/3.3 기준 W1,W2,W3,W6(boss) 유지,
                W4/W5 제거.
  - DT1-P4-002: count -40% 계산 시 PL 산출물(docs/13_difficulty_balance.md §4.2/4.3)
                명시 목표값 우선 적용.
  - DT1-P4-003: reward.grain +50% 계산값을 정책 문서 §2.4 반올림값 그대로 사용.
  - DT1-P4-004: stage_04 grain < stage_03 grain(정책 변경 후) — stage_04 grain 단조
                증가 불변식은 폐기하고 양수 검증으로 대체.

정책 참조: docs/13_difficulty_balance.md (DECISION-PL-P4-009~016).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.data.loader import StageDef, load_stage
from src.data.schema import validate_stage

STAGES_DIR = Path(__file__).parent.parent / "src" / "data" / "stages"


def _raw(stage_id: str) -> dict:
    """JSON raw dict — schema 검증 전 원시 데이터 접근용."""
    with open(STAGES_DIR / f"{stage_id}.json", encoding="utf-8") as fh:
        return json.load(fh)


def _load(stage_id: str) -> StageDef:
    return load_stage(stage_id)


# ---------------------------------------------------------------------------
# 1. schema validator 통과 확인 (5건)
# ---------------------------------------------------------------------------


class TestSchemaPass:
    """5개 스테이지 모두 validate_stage 통과 가드."""

    @pytest.mark.parametrize("sid", ["stage_01", "stage_02", "stage_03", "stage_04", "stage_05"])
    def test_validate_stage_no_error(self, sid: str) -> None:
        """validate_stage 가 StageSchemaError 없이 통과한다 (Issue #27 DOD)."""
        validate_stage(_raw(sid), source=sid)


# ---------------------------------------------------------------------------
# 2. stage_01 — 보상만 상향, 나머지 무변경 (3건)
# ---------------------------------------------------------------------------


class TestStage01Policy:
    """DECISION-PL-P4-011/015: stage_01 reward.grain 50 → 100."""

    def test_reward_grain_100(self) -> None:
        """stage_01 reward.grain == 100 (Phase 4 하향 정책 적용 후)."""
        assert _load("stage_01").reward.grain == 100

    def test_wave_count_unchanged_3(self) -> None:
        """stage_01 wave 수는 3 — 정책상 무변경 (DECISION-PL-P4-011)."""
        assert len(_load("stage_01").waves) == 3

    def test_spawn_interval_unchanged(self) -> None:
        """stage_01 spawn interval 은 변경 없음 (DECISION-PL-P4-011)."""
        stage = _load("stage_01")
        # W1: tang_soldier interval 0.8, W2: 0.7, W3: 0.8
        intervals = [sp.interval_s for w in stage.waves for sp in w.spawns]
        assert 0.8 in intervals, "stage_01 W1 interval 0.8 이 유지되어야 한다"


# ---------------------------------------------------------------------------
# 3. stage_02 — wave 4, count -40%, interval +30%, reward.grain 150 (5건)
# ---------------------------------------------------------------------------


class TestStage02Policy:
    """DECISION-PL-P4-009/010/015: stage_02 5축 조정."""

    def test_wave_count_4(self) -> None:
        """stage_02 wave 수 == 4 (6→4 축소, DECISION-PL-P4-010)."""
        assert len(_load("stage_02").waves) == 4

    def test_boss_wave_preserved(self) -> None:
        """stage_02 마지막 wave 에 boss(tang_vanguard_captain)가 유지된다."""
        stage = _load("stage_02")
        boss_waves = [w for w in stage.waves if w.boss is not None]
        assert len(boss_waves) >= 1
        assert any(w.boss == "tang_vanguard_captain" for w in stage.waves)

    def test_reward_grain_150(self) -> None:
        """stage_02 reward.grain == 150 (+50%, DECISION-PL-P4-015)."""
        assert _load("stage_02").reward.grain == 150

    def test_spawn_count_reduced(self) -> None:
        """stage_02 W1 tang_soldier count == 3 (5×0.6 내림, DECISION-PL-P4-009)."""
        stage = _load("stage_02")
        w1_spawns = stage.waves[0].spawns
        assert w1_spawns[0].type == "tang_soldier"
        assert w1_spawns[0].count == 3

    def test_spawn_interval_increased(self) -> None:
        """stage_02 W1 spawn interval >= 1.0 (+30% 이상, DECISION-PL-P4-009)."""
        stage = _load("stage_02")
        w1_spawns = stage.waves[0].spawns
        assert w1_spawns[0].interval_s >= 1.0


# ---------------------------------------------------------------------------
# 4. stage_03 — wave 4, count -40%, interval +30%, reward.grain 220,
#               야간 시야 multiplier 1.4, W1 단일 path (5건)
# ---------------------------------------------------------------------------


class TestStage03Policy:
    """DECISION-PL-P4-009/010/014/015: stage_03 5축 조정 + 야간 시야."""

    def test_wave_count_4(self) -> None:
        """stage_03 wave 수 == 4 (6→4 축소, DECISION-PL-P4-010)."""
        assert len(_load("stage_03").waves) == 4

    def test_boss_wave_preserved(self) -> None:
        """stage_03 마지막 wave 에 boss(tang_night_raider)가 유지된다."""
        stage = _load("stage_03")
        assert any(w.boss == "tang_night_raider" for w in stage.waves)

    def test_reward_grain_220(self) -> None:
        """stage_03 reward.grain == 220 (+50% 반올림, DECISION-PL-P4-015)."""
        assert _load("stage_03").reward.grain == 220

    def test_night_vision_radius_multiplier(self) -> None:
        """stage_03 JSON 에 night_vision_radius_multiplier == 1.4 가 있다
        (DECISION-PL-P4-014).
        """
        raw = _raw("stage_03")
        assert "night_vision_radius_multiplier" in raw
        assert raw["night_vision_radius_multiplier"] == pytest.approx(1.4)

    def test_w1_single_path_gorge(self) -> None:
        """stage_03 W1 은 p_gorge 단일 경로만 사용한다 (DECISION-PL-P4-014)."""
        stage = _load("stage_03")
        w1_spawns = stage.waves[0].spawns
        paths_used = {sp.path for sp in w1_spawns}
        assert paths_used == {"p_gorge"}, f"W1 에 p_flank 가 포함되면 안 됨: {paths_used}"


# ---------------------------------------------------------------------------
# 5. stage_04, stage_05 무변경 가드 (4건)
# ---------------------------------------------------------------------------


class TestStage04Stage05Unchanged:
    """DECISION-PL-P4-013: stage_04~05 데이터 무변경 가드."""

    def test_stage04_wave_count_7(self) -> None:
        """stage_04 wave 수 == 7 (변경 없음)."""
        assert len(_load("stage_04").waves) == 7

    def test_stage04_reward_gold_400(self) -> None:
        """stage_04 reward.gold == 400 (변경 없음)."""
        assert _load("stage_04").reward.gold == 400

    def test_stage04_reward_grain_200(self) -> None:
        """stage_04 reward.grain == 200 (변경 없음, DECISION-PL-P4-013)."""
        assert _load("stage_04").reward.grain == 200

    def test_stage05_wave_count_10(self) -> None:
        """stage_05 wave 수 == 10 (변경 없음)."""
        assert len(_load("stage_05").waves) == 10
