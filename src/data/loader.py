"""JSON 로더 + dataclass 매핑.

DESIGN: ``frozen=True`` 불변 dataclass(DECISION-5.1). 누락된 필드는
명시적 KeyError로 빠르게 실패시켜 데이터 오류를 조기 발견.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.core.settings import DATA_ROOT


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
    reward: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 로더 함수
# ---------------------------------------------------------------------------
def _read_json(path) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_units(data_root=DATA_ROOT) -> dict[str, UnitDef]:  # type: ignore[no-untyped-def]
    raw = _read_json(data_root / "units.json")
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
    raw = _read_json(data_root / "enemies.json")
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


def load_stage(stage_id: str, data_root=DATA_ROOT) -> StageDef:  # type: ignore[no-untyped-def]
    raw = _read_json(data_root / "stages" / f"{stage_id}.json")
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
        reward=dict(raw.get("reward", {})),
    )
