"""``src/data/schema.py`` stage JSON 스키마 검증 단위 테스트.

DESIGN: Issue #10 / Phase 3.1 / DECISION-P3-005 (stdlib only).
정상 케이스 (실제 ``stage_01.json``) + 다양한 비정상 케이스를 커버한다.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.core.settings import DATA_ROOT
from src.data.loader import load_stage
from src.data.schema import (
    StageSchemaError,
    validate_enemies,
    validate_stage,
    validate_units,
)


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------
@pytest.fixture()
def valid_stage() -> dict:
    """파일에서 읽은 stage_01.json 사본 (테스트마다 독립 수정 가능)."""
    raw = json.loads((DATA_ROOT / "stages" / "stage_01.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


@pytest.fixture()
def valid_units() -> dict:
    raw = json.loads((DATA_ROOT / "units.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


@pytest.fixture()
def valid_enemies() -> dict:
    raw = json.loads((DATA_ROOT / "enemies.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


# ---------------------------------------------------------------------------
# 정상 케이스
# ---------------------------------------------------------------------------
def test_validate_stage_accepts_current_stage_01(valid_stage: dict) -> None:
    """현재 stage_01.json 은 새 검증을 통과해야 한다 (회귀 방지)."""
    # 예외가 발생하지 않으면 OK.
    validate_stage(valid_stage, source="stage_01.json")


def test_load_stage_still_works() -> None:
    """검증 도입 후에도 ``load_stage`` 가 정상 동작."""
    stage = load_stage("stage_01")
    assert stage.id == "stage_01"
    assert len(stage.paths) >= 1
    assert len(stage.waves) >= 1


def test_validate_units_accepts_current_units(valid_units: dict) -> None:
    validate_units(valid_units, source="units.json")


def test_validate_enemies_accepts_current_enemies(valid_enemies: dict) -> None:
    validate_enemies(valid_enemies, source="enemies.json")


# ---------------------------------------------------------------------------
# 비정상 — 누락
# ---------------------------------------------------------------------------
def test_missing_required_id(valid_stage: dict) -> None:
    del valid_stage["id"]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    msg = str(excinfo.value)
    assert "stage_01.json" in msg
    assert "id" in msg


def test_missing_required_paths(valid_stage: dict) -> None:
    del valid_stage["paths"]
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


def test_missing_required_waves(valid_stage: dict) -> None:
    del valid_stage["waves"]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "waves" in str(excinfo.value)


def test_missing_lives(valid_stage: dict) -> None:
    del valid_stage["lives"]
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


# ---------------------------------------------------------------------------
# 비정상 — 타입 오류
# ---------------------------------------------------------------------------
def test_waves_must_be_list_not_dict(valid_stage: dict) -> None:
    valid_stage["waves"] = {"not": "a list"}
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "expected list" in str(excinfo.value)


def test_starting_gold_must_be_int_not_str(valid_stage: dict) -> None:
    valid_stage["starting_gold"] = "300"
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "expected int" in str(excinfo.value)


def test_starting_gold_rejects_bool(valid_stage: dict) -> None:
    """bool 은 int 의 서브클래스이지만 거부해야 한다 (DESIGN intent)."""
    valid_stage["starting_gold"] = True
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "bool" in str(excinfo.value)


def test_id_must_be_str(valid_stage: dict) -> None:
    valid_stage["id"] = 42
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


# ---------------------------------------------------------------------------
# 비정상 — 값 범위
# ---------------------------------------------------------------------------
def test_starting_gold_must_be_non_negative(valid_stage: dict) -> None:
    valid_stage["starting_gold"] = -10
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "below minimum" in str(excinfo.value)


def test_lives_must_be_positive(valid_stage: dict) -> None:
    valid_stage["lives"] = 0
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


def test_id_must_be_non_empty(valid_stage: dict) -> None:
    valid_stage["id"] = ""
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "non-empty" in str(excinfo.value)


def test_empty_paths_rejected(valid_stage: dict) -> None:
    valid_stage["paths"] = []
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


def test_empty_waves_rejected(valid_stage: dict) -> None:
    valid_stage["waves"] = []
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


# ---------------------------------------------------------------------------
# 비정상 — 중첩 구조
# ---------------------------------------------------------------------------
def test_waypoint_must_have_two_components(valid_stage: dict) -> None:
    valid_stage["paths"][0]["waypoints"][0] = [10, 20, 30]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "exactly 2" in str(excinfo.value)


def test_path_needs_at_least_two_waypoints(valid_stage: dict) -> None:
    valid_stage["paths"][0]["waypoints"] = [[0, 0]]
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


def test_spawn_count_must_be_positive(valid_stage: dict) -> None:
    valid_stage["waves"][0]["spawns"][0]["count"] = 0
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "below minimum" in str(excinfo.value)


def test_wave_without_spawns_and_boss_is_rejected(valid_stage: dict) -> None:
    """spawns 도 비어있고 boss 도 없는 wave 는 거부."""
    valid_stage["waves"][0]["spawns"] = []
    valid_stage["waves"][0].pop("boss", None)
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "spawns" in str(excinfo.value) or "boss" in str(excinfo.value)


def test_wave_with_only_boss_no_spawns_is_accepted(valid_stage: dict) -> None:
    """spawns 비었어도 boss 있으면 통과 (현 stage_01 의 wave 3 형태)."""
    valid_stage["waves"][0]["spawns"] = []
    valid_stage["waves"][0]["boss"] = "tang_scout_captain"
    validate_stage(valid_stage, source="stage_01.json")  # 통과


# ---------------------------------------------------------------------------
# Reward
# ---------------------------------------------------------------------------
def test_reward_gold_is_required_when_reward_present(valid_stage: dict) -> None:
    valid_stage["reward"] = {"unlock": "stage_02"}
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    assert "gold" in str(excinfo.value)


def test_reward_grain_is_optional(valid_stage: dict) -> None:
    """Team1 머지 전이므로 grain 은 optional. 없어도 통과."""
    valid_stage["reward"] = {"gold": 200, "unlock": "stage_02"}
    validate_stage(valid_stage, source="stage_01.json")


def test_reward_grain_accepted_when_present(valid_stage: dict) -> None:
    """Team1 머지 후를 대비 — grain 이 추가되면 통과."""
    valid_stage["reward"] = {"gold": 200, "grain": 50, "unlock": "stage_02"}
    validate_stage(valid_stage, source="stage_01.json")


def test_reward_grain_must_be_non_negative(valid_stage: dict) -> None:
    valid_stage["reward"] = {"gold": 200, "grain": -5}
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


def test_reward_optional_when_missing(valid_stage: dict) -> None:
    """reward 자체가 없어도 통과."""
    valid_stage.pop("reward", None)
    validate_stage(valid_stage, source="stage_01.json")


# ---------------------------------------------------------------------------
# 에러 메시지 품질
# ---------------------------------------------------------------------------
def test_error_message_includes_path(valid_stage: dict) -> None:
    valid_stage["waves"][1]["spawns"][0]["count"] = -1
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="stage_01.json")
    msg = str(excinfo.value)
    assert "waves[1].spawns[0]" in msg
    assert "count" in msg


def test_error_message_includes_source_filename(valid_stage: dict) -> None:
    del valid_stage["id"]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_stage(valid_stage, source="my_custom_stage.json")
    assert "my_custom_stage.json" in str(excinfo.value)


def test_stage_schema_error_is_value_error() -> None:
    """``except ValueError`` 호환성 보장."""
    assert issubclass(StageSchemaError, ValueError)


# ---------------------------------------------------------------------------
# Load wrapper — 파일 경로가 메시지에 노출되는지
# ---------------------------------------------------------------------------
def test_load_stage_raises_with_file_path(tmp_path: Path) -> None:
    """잘못된 stage JSON 파일 → 에러 메시지에 파일 경로가 포함."""
    stages_dir = tmp_path / "stages"
    stages_dir.mkdir()
    broken = stages_dir / "broken.json"
    # title 누락.
    broken.write_text(
        json.dumps(
            {
                "id": "broken",
                "background": "bg",
                "music": "m",
                "starting_gold": 100,
                "lives": 10,
                "paths": [{"id": "p", "waypoints": [[0, 0], [1, 1]]}],
                "waves": [
                    {
                        "delay_s": 1.0,
                        "spawns": [
                            {
                                "type": "x",
                                "count": 1,
                                "interval_s": 1.0,
                                "path": "p",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(StageSchemaError) as excinfo:
        load_stage("broken", data_root=tmp_path)
    msg = str(excinfo.value)
    assert "broken.json" in msg
    assert "title" in msg


# ---------------------------------------------------------------------------
# Units / Enemies
# ---------------------------------------------------------------------------
def test_units_missing_cost_rejected(valid_units: dict) -> None:
    del valid_units["units"]["archer"]["cost"]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_units(valid_units, source="units.json")
    assert "cost" in str(excinfo.value)


def test_enemies_negative_hp_rejected(valid_enemies: dict) -> None:
    valid_enemies["enemies"]["tang_soldier"]["hp"] = -10
    with pytest.raises(StageSchemaError):
        validate_enemies(valid_enemies, source="enemies.json")
