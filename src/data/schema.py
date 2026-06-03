"""Stage / Unit / Enemy JSON 스키마 검증 (stdlib only).

DESIGN (DECISION-DL-P3-001):
    - DECISION-P3-005 (Phase 3 계획) 에 따라 ``jsonschema`` / ``pydantic`` 같은
      외부 라이브러리를 도입하지 않는다. 표준 라이브러리 (``typing``,
      ``dataclasses``, 내장 ``isinstance``) 만으로 검증한다.
    - 헬퍼 함수 (``_require_*``) + path 추적 (``"reward.gold"`` 형태) 으로
      누락/타입오류 시 ``StageSchemaError`` 를 명확한 메시지와 함께 raise.
    - 검증 통과 후 ``loader.py`` 의 ``load_stage`` 등이 그대로 dataclass 매핑.

본 모듈은 dataclass 자체를 정의하지 않는다 (``loader.py`` 책임). 순수 검증만 담당.
"""

from __future__ import annotations

from typing import Any


class StageSchemaError(ValueError):
    """Stage / Unit / Enemy JSON 스키마 검증 실패.

    ``ValueError`` 의 하위 클래스이므로 기존 ``except ValueError`` 를 깨지 않는다.
    """

    def __init__(
        self,
        message: str,
        *,
        path: str | None = None,
        source: str | None = None,
    ) -> None:
        parts: list[str] = []
        if source is not None:
            parts.append(f"[{source}]")
        if path is not None:
            parts.append(f"at '{path}':")
        parts.append(message)
        super().__init__(" ".join(parts))
        self.path = path
        self.source = source


# ---------------------------------------------------------------------------
# 검증 헬퍼 (path 추적)
# ---------------------------------------------------------------------------
def _require_key(data: dict[str, Any], key: str, path: str, source: str) -> Any:
    if key not in data:
        raise StageSchemaError(
            f"required key '{key}' is missing",
            path=path,
            source=source,
        )
    return data[key]


def _require_type(
    value: Any,
    expected: type | tuple[type, ...],
    *,
    path: str,
    source: str,
) -> Any:
    if isinstance(expected, tuple):
        names = " | ".join(t.__name__ for t in expected)
    else:
        names = expected.__name__
    # bool 은 int 의 서브클래스이므로, int 를 요구할 때 bool 거부.
    if expected is int and isinstance(value, bool):
        raise StageSchemaError(
            f"expected {names}, got bool",
            path=path,
            source=source,
        )
    if not isinstance(value, expected):
        got = type(value).__name__
        raise StageSchemaError(
            f"expected {names}, got {got}",
            path=path,
            source=source,
        )
    return value


def _require_int(
    data: dict[str, Any],
    key: str,
    *,
    path: str,
    source: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    sub_path = f"{path}.{key}" if path else key
    raw = _require_key(data, key, path, source)
    value = _require_type(raw, int, path=sub_path, source=source)
    if minimum is not None and value < minimum:
        raise StageSchemaError(
            f"value {value} is below minimum {minimum}",
            path=sub_path,
            source=source,
        )
    if maximum is not None and value > maximum:
        raise StageSchemaError(
            f"value {value} is above maximum {maximum}",
            path=sub_path,
            source=source,
        )
    return value


def _require_number(
    data: dict[str, Any],
    key: str,
    *,
    path: str,
    source: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    """int 또는 float 모두 허용. bool 은 거부."""
    sub_path = f"{path}.{key}" if path else key
    raw = _require_key(data, key, path, source)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        got = type(raw).__name__
        raise StageSchemaError(
            f"expected int | float, got {got}",
            path=sub_path,
            source=source,
        )
    value = float(raw)
    if minimum is not None and value < minimum:
        raise StageSchemaError(
            f"value {value} is below minimum {minimum}",
            path=sub_path,
            source=source,
        )
    if maximum is not None and value > maximum:
        raise StageSchemaError(
            f"value {value} is above maximum {maximum}",
            path=sub_path,
            source=source,
        )
    return value


def _require_str(
    data: dict[str, Any],
    key: str,
    *,
    path: str,
    source: str,
    non_empty: bool = True,
) -> str:
    sub_path = f"{path}.{key}" if path else key
    raw = _require_key(data, key, path, source)
    value = _require_type(raw, str, path=sub_path, source=source)
    if non_empty and not value:
        raise StageSchemaError(
            "string must be non-empty",
            path=sub_path,
            source=source,
        )
    return value


def _require_list(
    data: dict[str, Any],
    key: str,
    *,
    path: str,
    source: str,
    min_items: int = 0,
) -> list[Any]:
    sub_path = f"{path}.{key}" if path else key
    raw = _require_key(data, key, path, source)
    value = _require_type(raw, list, path=sub_path, source=source)
    if len(value) < min_items:
        raise StageSchemaError(
            f"list must have >= {min_items} items, got {len(value)}",
            path=sub_path,
            source=source,
        )
    return value


def _require_dict(
    data: dict[str, Any],
    key: str,
    *,
    path: str,
    source: str,
) -> dict[str, Any]:
    sub_path = f"{path}.{key}" if path else key
    raw = _require_key(data, key, path, source)
    return _require_type(raw, dict, path=sub_path, source=source)


def _optional_str(
    data: dict[str, Any],
    key: str,
    *,
    path: str,
    source: str,
) -> str | None:
    if key not in data or data[key] is None:
        return None
    sub_path = f"{path}.{key}" if path else key
    return _require_type(data[key], str, path=sub_path, source=source)


# ---------------------------------------------------------------------------
# 서브 스키마
# ---------------------------------------------------------------------------
def _validate_waypoint(raw: Any, *, path: str, source: str) -> tuple[float, float]:
    if not isinstance(raw, (list, tuple)):
        raise StageSchemaError(
            f"waypoint must be a list/tuple of two numbers, got {type(raw).__name__}",
            path=path,
            source=source,
        )
    if len(raw) != 2:
        raise StageSchemaError(
            f"waypoint must have exactly 2 numbers, got {len(raw)}",
            path=path,
            source=source,
        )
    coords: list[float] = []
    for idx, comp in enumerate(raw):
        comp_path = f"{path}[{idx}]"
        if isinstance(comp, bool) or not isinstance(comp, (int, float)):
            raise StageSchemaError(
                f"waypoint component must be int | float, got {type(comp).__name__}",
                path=comp_path,
                source=source,
            )
        coords.append(float(comp))
    return coords[0], coords[1]


def _validate_path(raw: Any, *, path: str, source: str) -> None:
    _require_type(raw, dict, path=path, source=source)
    assert isinstance(raw, dict)  # for mypy
    _require_str(raw, "id", path=path, source=source)
    wps = _require_list(raw, "waypoints", path=path, source=source, min_items=2)
    for idx, wp in enumerate(wps):
        _validate_waypoint(wp, path=f"{path}.waypoints[{idx}]", source=source)


def _validate_spawn(raw: Any, *, path: str, source: str) -> None:
    _require_type(raw, dict, path=path, source=source)
    assert isinstance(raw, dict)
    _require_str(raw, "type", path=path, source=source)
    _require_int(raw, "count", path=path, source=source, minimum=1)
    _require_number(raw, "interval_s", path=path, source=source, minimum=0.0)
    # interval_s == 0.0 은 엣지 케이스이지만 ``minimum=0.0`` 로 허용.
    # 0 이하의 음수는 거부됨.
    _require_str(raw, "path", path=path, source=source)


def _validate_wave(raw: Any, *, path: str, source: str) -> None:
    _require_type(raw, dict, path=path, source=source)
    assert isinstance(raw, dict)
    _require_number(raw, "delay_s", path=path, source=source, minimum=0.0)
    boss = _optional_str(raw, "boss", path=path, source=source)
    # spawns 는 ``boss`` 가 있을 때 비어 있어도 허용 (현재 stage_01.json 의 3 번째 wave 가 이 형태).
    if "spawns" in raw:
        spawns = _require_list(raw, "spawns", path=path, source=source, min_items=0)
        for idx, sp in enumerate(spawns):
            _validate_spawn(sp, path=f"{path}.spawns[{idx}]", source=source)
        has_spawns = bool(spawns)
    else:
        has_spawns = False
    if not has_spawns and boss is None:
        raise StageSchemaError(
            "wave must have non-empty 'spawns' or a 'boss' field",
            path=path,
            source=source,
        )
    # Issue #43 / DECISION-DL-P5P-001: 옵션 boss_path 필드 (non-empty str).
    # paths 컨텍스트 검증은 WaveSystem 의 _resolve_boss_path() 가 unknown id 시
    # 자동 fallback 처리하므로, schema 단계에서는 형식(str, non-empty)만 검증.
    if "boss_path" in raw and raw["boss_path"] is not None:
        bp_path = f"{path}.boss_path"
        _require_type(raw["boss_path"], str, path=bp_path, source=source)
        if not raw["boss_path"]:
            raise StageSchemaError(
                "string must be non-empty",
                path=bp_path,
                source=source,
            )


def _validate_build_zone(raw: Any, *, path: str, source: str) -> None:
    _require_type(raw, dict, path=path, source=source)
    assert isinstance(raw, dict)
    _require_int(raw, "x", path=path, source=source)
    _require_int(raw, "y", path=path, source=source)
    _require_int(raw, "w", path=path, source=source, minimum=1)
    _require_int(raw, "h", path=path, source=source, minimum=1)


def _validate_reward(raw: Any, *, path: str, source: str) -> None:
    _require_type(raw, dict, path=path, source=source)
    assert isinstance(raw, dict)
    # gold 는 필수.
    _require_int(raw, "gold", path=path, source=source, minimum=0)
    # grain 은 optional (Team1 머지 후 follow-up Issue 로 mandatory 격상 예정).
    if "grain" in raw:
        _require_int(raw, "grain", path=path, source=source, minimum=0)
    # unlock 은 optional.
    if "unlock" in raw:
        sub_path = f"{path}.unlock"
        _require_type(raw["unlock"], str, path=sub_path, source=source)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def validate_stage(raw: Any, *, source: str = "<stage>") -> None:
    """Stage JSON dict 를 검증. 실패 시 ``StageSchemaError`` raise.

    Args:
        raw: ``json.load`` 결과 dict.
        source: 에러 메시지에 노출할 식별자 (보통 파일 경로).

    Notes:
        - ``loader.load_stage`` 에서 dataclass 매핑 전에 호출한다.
        - 본 함수는 비파괴이며 원본 dict 를 수정하지 않는다.
    """
    if not isinstance(raw, dict):
        raise StageSchemaError(
            f"stage root must be a dict, got {type(raw).__name__}",
            source=source,
        )

    _require_str(raw, "id", path="", source=source)
    _require_str(raw, "title", path="", source=source)
    _require_str(raw, "background", path="", source=source)
    _require_str(raw, "music", path="", source=source)
    _require_int(raw, "starting_gold", path="", source=source, minimum=0)
    _require_int(raw, "lives", path="", source=source, minimum=1)
    if "starting_population" in raw:
        _require_int(raw, "starting_population", path="", source=source, minimum=0)

    paths = _require_list(raw, "paths", path="", source=source, min_items=1)
    for idx, p in enumerate(paths):
        _validate_path(p, path=f"paths[{idx}]", source=source)

    waves = _require_list(raw, "waves", path="", source=source, min_items=1)
    for idx, w in enumerate(waves):
        _validate_wave(w, path=f"waves[{idx}]", source=source)

    if "build_zones" in raw:
        zones = _require_list(raw, "build_zones", path="", source=source, min_items=0)
        for idx, z in enumerate(zones):
            _validate_build_zone(z, path=f"build_zones[{idx}]", source=source)

    if "reward" in raw:
        reward = _require_dict(raw, "reward", path="", source=source)
        _validate_reward(reward, path="reward", source=source)

    # history_caption 은 교육 통합(H1) 도입 캡션 옵션 필드.
    # docs/15 §2.2 / docs/16: 스테이지 시작 시 1줄 역사 캡션. 존재할 때만 non-empty str 검증.
    if "history_caption" in raw and raw["history_caption"] is not None:
        _require_str(raw, "history_caption", path="", source=source)

    # endurance 는 교육 통합(H7) 토산 "버티기 승리" 게이지 옵션 메타(스테이지5 전용).
    # docs/15 §2.1 H7 / docs/16 Wave4. 존재할 때만 dict + 옵션 수치 필드 검증(전부 옵션).
    if "endurance" in raw and raw["endurance"] is not None:
        end = _require_dict(raw, "endurance", path="", source=source)
        for fkey in ("duration_s", "time_weight", "wave_weight", "kill_weight"):
            if fkey in end:
                _require_number(end, fkey, path="endurance", source=source, minimum=0.0)
        if "kills_for_full" in end:
            _require_int(end, "kills_for_full", path="endurance", source=source, minimum=1)

    # night_vision_radius_multiplier 는 야간 스테이지 전용 옵션 필드.
    # DECISION-PL-P4-014: 0.5~2.0 범위의 float. 존재할 때만 검증.
    if "night_vision_radius_multiplier" in raw:
        _require_number(
            raw,
            "night_vision_radius_multiplier",
            path="",
            source=source,
            minimum=0.5,
            maximum=2.0,
        )


def validate_units(raw: Any, *, source: str = "<units>") -> None:
    """``units.json`` 검증."""
    if not isinstance(raw, dict):
        raise StageSchemaError(
            f"units root must be a dict, got {type(raw).__name__}",
            source=source,
        )
    units = _require_dict(raw, "units", path="", source=source)
    for uid, u in units.items():
        path = f"units.{uid}"
        if not isinstance(u, dict):
            raise StageSchemaError(
                f"unit entry must be a dict, got {type(u).__name__}",
                path=path,
                source=source,
            )
        _require_str(u, "name", path=path, source=source)
        _require_int(u, "cost", path=path, source=source, minimum=0)
        _require_int(u, "hp", path=path, source=source, minimum=1)
        _require_int(u, "atk", path=path, source=source, minimum=0)
        _require_number(u, "atk_speed", path=path, source=source, minimum=0.0)
        _require_int(u, "range", path=path, source=source, minimum=0)
        _require_str(u, "sprite", path=path, source=source)
        size = _require_list(u, "size", path=path, source=source, min_items=2)
        if len(size) != 2:
            raise StageSchemaError(
                f"size must have exactly 2 ints, got {len(size)}",
                path=f"{path}.size",
                source=source,
            )
        for idx, comp in enumerate(size):
            if isinstance(comp, bool) or not isinstance(comp, int):
                raise StageSchemaError(
                    f"size component must be int, got {type(comp).__name__}",
                    path=f"{path}.size[{idx}]",
                    source=source,
                )
        # history_blurb 는 교육 통합(H3) 사료 한 줄 옵션 필드.
        # docs/15 §6.2 / docs/16. 존재할 때만 non-empty str 검증.
        if "history_blurb" in u and u["history_blurb"] is not None:
            _require_str(u, "history_blurb", path=path, source=source)


def validate_enemies(raw: Any, *, source: str = "<enemies>") -> None:
    """``enemies.json`` 검증."""
    if not isinstance(raw, dict):
        raise StageSchemaError(
            f"enemies root must be a dict, got {type(raw).__name__}",
            source=source,
        )
    enemies = _require_dict(raw, "enemies", path="", source=source)
    for eid, e in enemies.items():
        path = f"enemies.{eid}"
        if not isinstance(e, dict):
            raise StageSchemaError(
                f"enemy entry must be a dict, got {type(e).__name__}",
                path=path,
                source=source,
            )
        _require_str(e, "name", path=path, source=source)
        _require_int(e, "hp", path=path, source=source, minimum=1)
        _require_number(e, "speed", path=path, source=source, minimum=0.0)
        _require_int(e, "damage_to_castle", path=path, source=source, minimum=0)
        _require_int(e, "gold_drop", path=path, source=source, minimum=0)
        _require_str(e, "sprite", path=path, source=source)
        if "armor" in e:
            _require_int(e, "armor", path=path, source=source, minimum=0)
        if "is_boss" in e and not isinstance(e["is_boss"], bool):
            raise StageSchemaError(
                f"expected bool, got {type(e['is_boss']).__name__}",
                path=f"{path}.is_boss",
                source=source,
            )
        # intro_banner 는 교육 통합(H2) 첫 등장 배너 옵션 필드.
        # docs/15 §6.3 / docs/16. 존재할 때만 non-empty str 검증.
        if "intro_banner" in e and e["intro_banner"] is not None:
            _require_str(e, "intro_banner", path=path, source=source)


# ---------------------------------------------------------------------------
# Codex (교육 통합 H4/H5 — docs/15 §6.1, docs/16)
# ---------------------------------------------------------------------------
# 라벨 enum (EP2 라벨 무결성). docs/15 §4.1 + 09_codex.md §4.
#   fact         — (사실) 1차 사료 근거
#   fact_adapted — (사실 + 게임 각색). 별도 4번째 라벨 아님(R5); 배지는 (사실), 본문에 각색 고지
#   legend       — [전승] 후대 야사
#   fiction      — [픽션] 본 게임 창작
CODEX_LABELS: frozenset[str] = frozenset({"fact", "fact_adapted", "legend", "fiction"})

# unlock_condition.type enum. docs/15 §6.1.
#   auto              — 게임 시작 시 자동 해금
#   stage_clear       — 특정 스테이지 클리어 (stage 필드 필수)
#   stage_three_stars — 특정 스테이지 별 3개 (stage 필드 필수)
#   true_ending       — 진엔딩 (5스테이지 모두 별 3개)
CODEX_UNLOCK_TYPES: frozenset[str] = frozenset({"auto", "stage_clear", "stage_three_stars", "true_ending"})
_CODEX_UNLOCK_NEEDS_STAGE: frozenset[str] = frozenset({"stage_clear", "stage_three_stars"})


def _validate_codex_unlock(raw: Any, *, path: str, source: str) -> None:
    _require_type(raw, dict, path=path, source=source)
    assert isinstance(raw, dict)
    utype = _require_str(raw, "type", path=path, source=source)
    if utype not in CODEX_UNLOCK_TYPES:
        allowed = " | ".join(sorted(CODEX_UNLOCK_TYPES))
        raise StageSchemaError(
            f"unlock_condition.type must be one of [{allowed}], got '{utype}'",
            path=f"{path}.type",
            source=source,
        )
    if utype in _CODEX_UNLOCK_NEEDS_STAGE:
        # stage 필드 필수 (1~5).
        _require_int(raw, "stage", path=path, source=source, minimum=1, maximum=5)
    elif "stage" in raw and raw["stage"] is not None:
        # auto / true_ending 에는 stage 가 무의미 — 들어 있으면 타입만 가볍게 검증.
        _require_int(raw, "stage", path=path, source=source, minimum=1, maximum=5)


def validate_codex(raw: Any, *, source: str = "<codex>") -> None:
    """``codex.json`` 검증 (교육 통합 H4/H5).

    검증 항목:
        - root 는 dict, ``cards`` 는 비어있지 않은 list.
        - 각 카드: ``id``/``title``/``label``/``summary``/``body``/``source`` non-empty str.
        - ``label`` 은 :data:`CODEX_LABELS` enum 중 하나 (EP2 라벨 무결성).
        - ``unlock_condition`` 은 dict, ``type`` 은 enum, stage_* 면 ``stage`` (1~5) 필수.
        - 옵션 ``source_original``/``source_reading``/``source_translation`` 은 있으면 non-empty str.
        - 카드 ``id`` 중복 금지.
    """
    if not isinstance(raw, dict):
        raise StageSchemaError(
            f"codex root must be a dict, got {type(raw).__name__}",
            source=source,
        )
    cards = _require_list(raw, "cards", path="", source=source, min_items=1)
    seen_ids: set[str] = set()
    for idx, c in enumerate(cards):
        path = f"cards[{idx}]"
        if not isinstance(c, dict):
            raise StageSchemaError(
                f"card entry must be a dict, got {type(c).__name__}",
                path=path,
                source=source,
            )
        cid = _require_str(c, "id", path=path, source=source)
        if cid in seen_ids:
            raise StageSchemaError(
                f"duplicate card id '{cid}'",
                path=f"{path}.id",
                source=source,
            )
        seen_ids.add(cid)
        _require_str(c, "title", path=path, source=source)
        _require_str(c, "summary", path=path, source=source)
        _require_str(c, "body", path=path, source=source)
        _require_str(c, "source", path=path, source=source)
        label = _require_str(c, "label", path=path, source=source)
        if label not in CODEX_LABELS:
            allowed = " | ".join(sorted(CODEX_LABELS))
            raise StageSchemaError(
                f"label must be one of [{allowed}], got '{label}'",
                path=f"{path}.label",
                source=source,
            )
        unlock = _require_key(c, "unlock_condition", path, source)
        _validate_codex_unlock(unlock, path=f"{path}.unlock_condition", source=source)
        # 옵션 한문 원문 3필드 (H9, DECISION-EDU-003). 있으면 non-empty str.
        for opt_key in ("source_original", "source_reading", "source_translation"):
            if opt_key in c and c[opt_key] is not None:
                _require_str(c, opt_key, path=path, source=source)


__all__ = [
    "CODEX_LABELS",
    "CODEX_UNLOCK_TYPES",
    "StageSchemaError",
    "validate_codex",
    "validate_enemies",
    "validate_stage",
    "validate_units",
]
