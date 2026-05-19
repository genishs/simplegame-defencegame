"""Enemy 페이드 사망 단위 테스트 (tk 비의존)."""

from __future__ import annotations

from dataclasses import dataclass

from src.entities.enemy import Enemy

# ---------------------------------------------------------------------------
# 테스트용 EnemyDef 스텁
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _EnemyDef:
    id: str = "tang_soldier"
    name: str = "당군 보병"
    hp: int = 80
    speed: float = 60.0
    armor: int = 0
    damage_to_castle: int = 1
    gold_drop: int = 8
    sprite: str = "enemy_soldier"
    is_boss: bool = False


def make_enemy(hp: int = 80) -> Enemy:
    def_ = _EnemyDef(hp=hp)
    return Enemy(x=100.0, y=200.0, enemy_def=def_, path_id="p_main")


# ---------------------------------------------------------------------------
# 기본 생성
# ---------------------------------------------------------------------------


def test_enemy_initial_state() -> None:
    enemy = make_enemy()
    assert enemy.alive is True
    assert enemy.dying is False
    assert enemy.fade_alpha == 1.0
    assert enemy.hp == 80


# ---------------------------------------------------------------------------
# take_damage → dying 전환
# ---------------------------------------------------------------------------


def test_take_damage_reduces_hp() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(20)
    assert enemy.hp == 60
    assert enemy.dying is False


def test_take_damage_zero_hp_sets_dying() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(80)
    assert enemy.hp == 0
    assert enemy.dying is True


def test_take_damage_overkill_clamps_hp() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(200)
    assert enemy.hp == 0
    assert enemy.dying is True


def test_take_damage_ignored_when_already_dying() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(80)  # dying=True
    initial_hp = enemy.hp
    enemy.take_damage(50)  # 무시돼야 함
    assert enemy.hp == initial_hp


def test_take_damage_ignored_when_not_alive() -> None:
    enemy = make_enemy(hp=80)
    enemy.alive = False
    enemy.take_damage(80)
    assert enemy.dying is False


# ---------------------------------------------------------------------------
# fade_tick → fade_alpha 감소
# ---------------------------------------------------------------------------


def test_fade_tick_not_dying_no_change() -> None:
    enemy = make_enemy()
    enemy.fade_tick(0.1)
    assert enemy.fade_alpha == 1.0
    assert enemy.alive is True


def test_fade_tick_reduces_alpha() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(80)  # dying=True
    # fade_duration_s=0.6, dt=0.3 → alpha = 1 - 0.3/0.6 = 0.5
    enemy.fade_tick(0.3)
    assert abs(enemy.fade_alpha - 0.5) < 1e-6


def test_fade_tick_sets_alive_false_when_complete() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(80)
    # 완전 페이드: dt >= fade_duration_s
    enemy.fade_tick(0.6)
    assert enemy.fade_alpha == 0.0
    assert enemy.alive is False


def test_fade_tick_gradual_steps() -> None:
    enemy = make_enemy(hp=80)
    enemy.take_damage(80)
    # 0.2s씩 3회 → 총 0.6s (fade_duration_s)
    enemy.fade_tick(0.2)
    assert enemy.alive is True
    enemy.fade_tick(0.2)
    assert enemy.alive is True
    enemy.fade_tick(0.2)
    assert enemy.alive is False


# ---------------------------------------------------------------------------
# 보상값
# ---------------------------------------------------------------------------


def test_reward_food_matches_gold_drop() -> None:
    enemy = make_enemy()
    # gold_drop=8 → reward_food=8
    assert enemy.reward_food == 8


def test_reward_arrows_is_positive() -> None:
    enemy = make_enemy()
    assert enemy.reward_arrows >= 1


# ---------------------------------------------------------------------------
# _was_dying 플래그 (CombatSystem 보상 콜백용)
# ---------------------------------------------------------------------------


def test_was_dying_set_on_death() -> None:
    enemy = make_enemy(hp=80)
    assert enemy._was_dying is False
    enemy.take_damage(80)
    assert enemy._was_dying is True
