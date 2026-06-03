"""교육 통합(Track A) 데이터 기반 스키마/로더 검증 테스트.

DESIGN: docs/15 (교육 통합 스펙) + docs/16 (구현 계획). stdlib-only 검증
(DECISION-DL-P3-001) 을 유지하며, 신규 데이터 필드/파일을 커버한다.

커버 대상:
    - ``codex.json`` 신설 — 라벨 enum, unlock_condition, 옵션 한문 3필드, 15장 정합.
    - ``units.json`` ``history_blurb`` (H3).
    - ``enemies.json`` ``intro_banner`` (H2).
    - ``stages/stage_0[1-5].json`` ``history_caption`` (H1).
    - 로더 (``load_codex``/``load_units``/``load_enemies``/``load_stage``) 매핑.
"""

from __future__ import annotations

import copy
import json

import pytest

from src.core.settings import DATA_ROOT
from src.data.loader import (
    CodexCard,
    load_codex,
    load_enemies,
    load_stage,
    load_units,
)
from src.data.schema import (
    CODEX_LABELS,
    CODEX_UNLOCK_TYPES,
    StageSchemaError,
    validate_codex,
    validate_enemies,
    validate_stage,
    validate_units,
)


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------
@pytest.fixture()
def valid_codex() -> dict:
    raw = json.loads((DATA_ROOT / "codex.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


@pytest.fixture()
def valid_units() -> dict:
    raw = json.loads((DATA_ROOT / "units.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


@pytest.fixture()
def valid_enemies() -> dict:
    raw = json.loads((DATA_ROOT / "enemies.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


@pytest.fixture()
def valid_stage() -> dict:
    raw = json.loads((DATA_ROOT / "stages" / "stage_01.json").read_text(encoding="utf-8"))
    return copy.deepcopy(raw)


# ---------------------------------------------------------------------------
# Codex — 정상 케이스 + 정합 (QA-EDU-08, EP2)
# ---------------------------------------------------------------------------
def test_codex_file_passes_validation(valid_codex: dict) -> None:
    validate_codex(valid_codex, source="codex.json")


def test_codex_has_exactly_15_cards(valid_codex: dict) -> None:
    """DECISION-C01 / docs/15 §3.4: 총 15장 고정."""
    assert len(valid_codex["cards"]) == 15


def test_codex_all_labels_in_enum(valid_codex: dict) -> None:
    """EP2 라벨 무결성: 모든 카드 라벨이 enum 안에 있어야 한다."""
    for c in valid_codex["cards"]:
        assert c["label"] in CODEX_LABELS, c["id"]


def test_codex_fact_cards_have_source_original(valid_codex: dict) -> None:
    """DECISION-EDU-003: (사실) 라벨 카드는 한문 원문 3필드를 우선 채운다.

    옵션 필드이지만, fact 카드 다수에 채워졌는지(>=8) 회귀 가드.
    """
    fact_with_original = [
        c for c in valid_codex["cards"] if c["label"] == "fact" and c.get("source_original")
    ]
    assert len(fact_with_original) >= 8


def test_codex_legend_fiction_cards_have_no_hanja(valid_codex: dict) -> None:
    """[전승]/[픽션] 카드에는 한문 원문을 달지 않는다 (EP2: 야사를 사료처럼 보이게 금지)."""
    for c in valid_codex["cards"]:
        if c["label"] in ("legend", "fiction"):
            assert not c.get("source_original"), c["id"]


def test_codex_unlock_types_valid(valid_codex: dict) -> None:
    for c in valid_codex["cards"]:
        assert c["unlock_condition"]["type"] in CODEX_UNLOCK_TYPES, c["id"]


def test_codex_true_ending_card_is_card15(valid_codex: dict) -> None:
    true_ending = [c for c in valid_codex["cards"] if c["unlock_condition"]["type"] == "true_ending"]
    assert len(true_ending) == 1
    assert true_ending[0]["id"] == "codex_15"
    assert true_ending[0]["label"] == "fiction"


# ---------------------------------------------------------------------------
# Codex — 비정상 케이스
# ---------------------------------------------------------------------------
def test_codex_rejects_unknown_label(valid_codex: dict) -> None:
    valid_codex["cards"][0]["label"] = "myth"
    with pytest.raises(StageSchemaError) as excinfo:
        validate_codex(valid_codex, source="codex.json")
    assert "label" in str(excinfo.value)


def test_codex_rejects_missing_unlock_condition(valid_codex: dict) -> None:
    del valid_codex["cards"][0]["unlock_condition"]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_codex(valid_codex, source="codex.json")
    assert "unlock_condition" in str(excinfo.value)


def test_codex_rejects_unknown_unlock_type(valid_codex: dict) -> None:
    valid_codex["cards"][0]["unlock_condition"] = {"type": "on_login"}
    with pytest.raises(StageSchemaError) as excinfo:
        validate_codex(valid_codex, source="codex.json")
    assert "type" in str(excinfo.value)


def test_codex_stage_clear_requires_stage(valid_codex: dict) -> None:
    valid_codex["cards"][1]["unlock_condition"] = {"type": "stage_clear"}
    with pytest.raises(StageSchemaError) as excinfo:
        validate_codex(valid_codex, source="codex.json")
    assert "stage" in str(excinfo.value)


def test_codex_rejects_out_of_range_stage(valid_codex: dict) -> None:
    valid_codex["cards"][1]["unlock_condition"] = {"type": "stage_clear", "stage": 9}
    with pytest.raises(StageSchemaError):
        validate_codex(valid_codex, source="codex.json")


def test_codex_rejects_duplicate_ids(valid_codex: dict) -> None:
    valid_codex["cards"][1]["id"] = valid_codex["cards"][0]["id"]
    with pytest.raises(StageSchemaError) as excinfo:
        validate_codex(valid_codex, source="codex.json")
    assert "duplicate" in str(excinfo.value)


def test_codex_rejects_empty_body(valid_codex: dict) -> None:
    valid_codex["cards"][0]["body"] = ""
    with pytest.raises(StageSchemaError):
        validate_codex(valid_codex, source="codex.json")


def test_codex_rejects_non_dict_root() -> None:
    with pytest.raises(StageSchemaError):
        validate_codex(["not", "a", "dict"], source="codex.json")


def test_codex_rejects_empty_cards() -> None:
    with pytest.raises(StageSchemaError):
        validate_codex({"version": 1, "cards": []}, source="codex.json")


# ---------------------------------------------------------------------------
# Codex — 로더 매핑
# ---------------------------------------------------------------------------
def test_load_codex_returns_15_cards() -> None:
    cards = load_codex()
    assert len(cards) == 15
    assert all(isinstance(c, CodexCard) for c in cards)


def test_load_codex_preserves_order_and_unlock() -> None:
    cards = load_codex()
    assert cards[0].id == "codex_01"
    assert cards[0].unlock.type == "auto"
    assert cards[0].unlock.stage is None
    assert cards[1].unlock.type == "stage_clear"
    assert cards[1].unlock.stage == 1
    # codex_13 = 별 3개 해금
    c13 = next(c for c in cards if c.id == "codex_13")
    assert c13.unlock.type == "stage_three_stars"
    assert c13.unlock.stage == 5


# ---------------------------------------------------------------------------
# units.json — history_blurb (H3, QA-EDU-04)
# ---------------------------------------------------------------------------
def test_all_units_have_history_blurb(valid_units: dict) -> None:
    """QA-EDU-04: 모든 유닛 툴팁에 사료 한 줄이 있어야 한다."""
    for uid, u in valid_units["units"].items():
        assert u.get("history_blurb"), uid


def test_units_history_blurb_must_be_non_empty_string(valid_units: dict) -> None:
    valid_units["units"]["archer"]["history_blurb"] = ""
    with pytest.raises(StageSchemaError):
        validate_units(valid_units, source="units.json")


def test_units_history_blurb_optional_when_absent(valid_units: dict) -> None:
    """비파괴: history_blurb 가 없어도 검증 통과 (기존 데이터 호환)."""
    del valid_units["units"]["archer"]["history_blurb"]
    validate_units(valid_units, source="units.json")


def test_load_units_maps_history_blurb() -> None:
    units = load_units()
    assert units["archer"].history_blurb
    assert units["spear"].history_blurb


# ---------------------------------------------------------------------------
# enemies.json — intro_banner (H2, QA-EDU-03)
# ---------------------------------------------------------------------------
def test_all_enemies_have_intro_banner(valid_enemies: dict) -> None:
    for eid, e in valid_enemies["enemies"].items():
        assert e.get("intro_banner"), eid


def test_enemies_intro_banner_must_be_non_empty_string(valid_enemies: dict) -> None:
    valid_enemies["enemies"]["tang_soldier"]["intro_banner"] = ""
    with pytest.raises(StageSchemaError):
        validate_enemies(valid_enemies, source="enemies.json")


def test_enemies_intro_banner_optional_when_absent(valid_enemies: dict) -> None:
    del valid_enemies["enemies"]["tang_soldier"]["intro_banner"]
    validate_enemies(valid_enemies, source="enemies.json")


def test_load_enemies_maps_intro_banner() -> None:
    enemies = load_enemies()
    assert enemies["tang_soldier"].intro_banner


# ---------------------------------------------------------------------------
# stages — history_caption (H1, QA-EDU-01)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("stage_id", ["stage_01", "stage_02", "stage_03", "stage_04", "stage_05"])
def test_every_stage_has_history_caption(stage_id: str) -> None:
    """QA-EDU-01: 스테이지 1~5 모두 도입 캡션을 가진다."""
    stage = load_stage(stage_id)
    assert stage.history_caption, stage_id


def test_stage_history_caption_must_be_non_empty_string(valid_stage: dict) -> None:
    valid_stage["history_caption"] = ""
    with pytest.raises(StageSchemaError):
        validate_stage(valid_stage, source="stage_01.json")


def test_stage_history_caption_optional_when_absent(valid_stage: dict) -> None:
    valid_stage.pop("history_caption", None)
    validate_stage(valid_stage, source="stage_01.json")
