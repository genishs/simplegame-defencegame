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


__all__ = [
    "StageSchemaError",
    "validate_stage",
    "validate_units",
    "validate_enemies",
]
