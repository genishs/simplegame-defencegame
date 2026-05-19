"""JSON 로더 + dataclass 매핑.

DESIGN: ``frozen=True`` 불변 dataclass(DECISION-5.1). 누락된 필드는
명시적 KeyError로 빠르게 실패시켜 데이터 오류를 조기 발견.

검증: ``load_*`` 진입점에서 ``src.data.schema`` 의 stdlib-only 검증을
선실행하고, 실패 시 ``StageSchemaError`` (``ValueError`` 하위) 로 즉시
중단한다. dataclass 매핑은 검증 통과 후에만 수행되므로 데이터 사고가
구조 검증 단계에서 캐치된다. (DECISION-DL-P3-001, Issue #10, Phase 3.1)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.core.settings import DATA_ROOT
from src.data.schema import (
    StageSchemaError,
    validate_enemies,
    validate_stage,
    validate_units,
)

# ``loader`` 에서 re-export 하여 호출자가 ``from src.data.loader import
# StageSchemaError`` 형태로도 import 할 수 있게 한다 (ruff F401 회피).
__all__ = [
    "EnemyDef",
    "PathDef",
    "StageDef",
    "StageSchemaError",
    "UnitDef",
    "WaveDef",
    "WaveSpawn",
    "load_enemies",
    "load_stage",
    "load_units",
]


# ---------------------------------------------------------------------------
# dataclass 정의
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class UnitDef:
    id: str
    name: str
    cost: int
    hp: int
    atk: int
    atk_speed: float
    range: int
    sprite: str
    size: tuple[int, int]
    projectile: str | None = None
    splash_radius: int | None = None


@dataclass(frozen=True)
class EnemyDef:
    id: str
    name: str
    hp: int
    speed: float
    armor: int
    damage_to_castle: int
    gold_drop: int
    sprite: str
    is_boss: bool = False


@dataclass(frozen=True)
class PathDef:
    id: str
    waypoints: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class WaveSpawn:
    type: str
    count: int
    interval_s: float
    path: str


@dataclass(frozen=True)
class WaveDef:
    delay_s: float
    spawns: tuple[WaveSpawn, ...]
    boss: str | None = None
    # DECISION-DL-P5P-001 (Issue #43): 보스 spawn path id 옵션 필드.
    # None 이면 WaveSystem._resolve_boss_path() 가 다음 우선순위로 결정한다:
    #   spawns 첫 항목 path → load(paths=...) 첫 path id → world waypoints 첫 키 → "p_main".
    boss_path: str | None = None


@dataclass(frozen=True)
class StageReward:
    """스테이지 클리어 보상 (DECISION-Q-011: grain 필드 추가).

    비파괴 기본값: ``grain=0`` 으로 기존 JSON 에 grain 이 없어도 로드됨.
    신규 스테이지는 반드시 grain 을 명시적으로 채울 것.
    """

    gold: int = 0
    grain: int = 0
    unlock: str | None = None


@dataclass(frozen=True)
class StageDef:
    id: str
    title: str
    background: str
    music: str
    starting_gold: int
    starting_population: int
    lives: int
    paths: tuple[PathDef, ...]
    build_zones: tuple[dict[str, int], ...]
    waves: tuple[WaveDef, ...]
    reward: StageReward = field(default_factory=StageReward)


# ---------------------------------------------------------------------------
# 로더 함수
# ---------------------------------------------------------------------------
def _read_json(path) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_units(data_root=DATA_ROOT) -> dict[str, UnitDef]:  # type: ignore[no-untyped-def]
    src = str(data_root / "units.json")
    raw = _read_json(data_root / "units.json")
    validate_units(raw, source=src)
    out: dict[str, UnitDef] = {}
    for uid, u in raw["units"].items():
        out[uid] = UnitDef(
            id=uid,
            name=u["name"],
            cost=int(u["cost"]),
            hp=int(u["hp"]),
            atk=int(u["atk"]),
            atk_speed=float(u["atk_speed"]),
            range=int(u["range"]),
            sprite=u["sprite"],
            size=(int(u["size"][0]), int(u["size"][1])),
            projectile=u.get("projectile"),
            splash_radius=u.get("splash_radius"),
        )
    return out


def load_enemies(data_root=DATA_ROOT) -> dict[str, EnemyDef]:  # type: ignore[no-untyped-def]
    src = str(data_root / "enemies.json")
    raw = _read_json(data_root / "enemies.json")
    validate_enemies(raw, source=src)
    out: dict[str, EnemyDef] = {}
    for eid, e in raw["enemies"].items():
        out[eid] = EnemyDef(
            id=eid,
            name=e["name"],
            hp=int(e["hp"]),
            speed=float(e["speed"]),
            armor=int(e.get("armor", 0)),
            damage_to_castle=int(e["damage_to_castle"]),
            gold_drop=int(e["gold_drop"]),
            sprite=e["sprite"],
            is_boss=bool(e.get("is_boss", False)),
        )
    return out


def _parse_reward(raw_reward: dict[str, Any]) -> StageReward:
    """reward 딕셔너리를 ``StageReward`` dataclass 로 변환."""
    return StageReward(
        gold=int(raw_reward.get("gold", 0)),
        grain=int(raw_reward.get("grain", 0)),
        unlock=raw_reward.get("unlock"),
    )


def load_stage(stage_id: str, data_root=DATA_ROOT) -> StageDef:  # type: ignore[no-untyped-def]
    stage_path = data_root / "stages" / f"{stage_id}.json"
    src = str(stage_path)
    raw = _read_json(stage_path)
    validate_stage(raw, source=src)
    paths = tuple(
        PathDef(
            id=p["id"],
            waypoints=tuple((float(x), float(y)) for x, y in p["waypoints"]),
        )
        for p in raw["paths"]
    )
    waves = tuple(
        WaveDef(
            delay_s=float(w["delay_s"]),
            spawns=tuple(
                WaveSpawn(
                    type=s["type"],
                    count=int(s["count"]),
                    interval_s=float(s["interval_s"]),
                    path=s["path"],
                )
                for s in w.get("spawns", [])
            ),
            boss=w.get("boss"),
            # Issue #43: 옵션 boss_path 필드 (str 또는 None).
            boss_path=w.get("boss_path"),
        )
        for w in raw["waves"]
    )
    return StageDef(
        id=raw["id"],
        title=raw["title"],
        background=raw["background"],
        music=raw["music"],
        starting_gold=int(raw["starting_gold"]),
        starting_population=int(raw.get("starting_population", 0)),
        lives=int(raw["lives"]),
        paths=paths,
        build_zones=tuple(dict(z) for z in raw.get("build_zones", [])),
        waves=waves,
        reward=_parse_reward(dict(raw.get("reward", {}))),
    )
