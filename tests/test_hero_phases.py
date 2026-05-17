"""Hero 페이즈 전환 및 ultimate 단위 테스트 (tk 비의존)."""

from __future__ import annotations

from src.entities.hero import Hero

# ---------------------------------------------------------------------------
# 페이즈 계산
# ---------------------------------------------------------------------------


def test_phase_1_at_full_hp() -> None:
    hero = Hero(hp=800)
    assert hero.current_phase == 1


def test_phase_1_at_70_percent() -> None:
    hero = Hero(hp=800)
    hero.hp = 560  # 70%
    assert hero.current_phase == 1


def test_phase_2_just_below_70() -> None:
    hero = Hero(hp=800)
    hero.hp = 559  # < 70%
    assert hero.current_phase == 2


def test_phase_2_at_40_percent() -> None:
    hero = Hero(hp=800)
    hero.hp = 320  # 40%
    assert hero.current_phase == 2


def test_phase_3_just_below_40() -> None:
    hero = Hero(hp=800)
    hero.hp = 319  # < 40%
    assert hero.current_phase == 3


def test_phase_3_at_15_percent() -> None:
    hero = Hero(hp=800)
    hero.hp = 120  # 15%
    assert hero.current_phase == 3


def test_phase_4_just_below_15() -> None:
    hero = Hero(hp=800)
    hero.hp = 119  # < 15%
    assert hero.current_phase == 4


def test_phase_4_at_zero_hp() -> None:
    hero = Hero(hp=800)
    hero.hp = 0
    assert hero.current_phase == 4


# ---------------------------------------------------------------------------
# 페이즈 전환 플래그
# ---------------------------------------------------------------------------


def test_phase_changed_flag_set_on_transition() -> None:
    hero = Hero(hp=800)
    hero.hp = 800  # Phase 1
    hero.update(0.016)
    # 아직 Phase 1 → 플래그 False
    assert hero.phase_changed is False

    hero.hp = 400  # Phase 2 (ratio=0.50, 0.40 <= 0.50 < 0.70)
    hero.update(0.016)
    assert hero.phase_changed is True


def test_phase_changed_flag_stays_until_reset() -> None:
    hero = Hero(hp=800)
    hero.hp = 300  # Phase 2
    hero.update(0.016)
    assert hero.phase_changed is True
    # 외부에서 False로 초기화
    hero.phase_changed = False
    hero.update(0.016)
    # 페이즈 변화 없음 → False 유지
    assert hero.phase_changed is False


def test_phase_changed_each_transition() -> None:
    hero = Hero(hp=800)
    # Phase 1 (hp=800) → Phase 2: hp 400 (ratio=0.50 → Phase 2)
    hero.hp = 400
    hero.update(0.016)
    assert hero.phase_changed is True
    assert hero.current_phase == 2
    hero.phase_changed = False

    # Phase 2 → Phase 3: hp 200 (ratio=0.25 → Phase 3)
    hero.hp = 200
    hero.update(0.016)
    assert hero.phase_changed is True
    assert hero.current_phase == 3
    hero.phase_changed = False

    # Phase 3 → Phase 4: hp 60 (ratio=0.075 → Phase 4)
    hero.hp = 60
    hero.update(0.016)
    assert hero.phase_changed is True
    assert hero.current_phase == 4


# ---------------------------------------------------------------------------
# 쿨다운 감소
# ---------------------------------------------------------------------------


def test_ult_timer_decreases_with_update() -> None:
    hero = Hero(hp=800, ultimate_cooldown_s=10.0)
    hero._ult_timer = 10.0
    hero.update(3.0)
    assert abs(hero._ult_timer - 7.0) < 1e-9


def test_ult_timer_does_not_go_below_zero() -> None:
    hero = Hero(hp=800)
    hero._ult_timer = 1.0
    hero.update(5.0)
    assert hero._ult_timer == 0.0


# ---------------------------------------------------------------------------
# ultimate: 쿨다운 중 발동 불가
# ---------------------------------------------------------------------------


def test_ultimate_blocked_during_cooldown() -> None:
    hero = Hero(hp=800)
    hero._ult_timer = 5.0
    result = hero.ultimate([])
    assert result["fired"] is False


def test_ultimate_fires_when_ready() -> None:
    hero = Hero(hp=800)
    hero._ult_timer = 0.0
    result = hero.ultimate([])
    assert result["fired"] is True


# ---------------------------------------------------------------------------
# ultimate: 페이즈별 스칼라 차이
# ---------------------------------------------------------------------------


class _DummyTarget:
    def __init__(self, x: float, y: float, hp: int = 200) -> None:
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.dying = False


def test_ultimate_phase1_vs_phase4_damage() -> None:
    """Phase 4 궁극기 데미지 > Phase 1."""
    hero_p1 = Hero(hp=800)
    hero_p1.hp = 800  # Phase 1

    hero_p4 = Hero(hp=800)
    hero_p4.hp = 10  # Phase 4

    target_p1 = _DummyTarget(x=800.0 + 10, y=540.0, hp=2000)
    target_p4 = _DummyTarget(x=800.0 + 10, y=540.0, hp=2000)

    hero_p1.x = 800.0
    hero_p1.y = 540.0
    hero_p4.x = 800.0
    hero_p4.y = 540.0

    hero_p1._ult_timer = 0.0
    hero_p4._ult_timer = 0.0

    res1 = hero_p1.ultimate([target_p1])
    res4 = hero_p4.ultimate([target_p4])

    assert res4["damage"] > res1["damage"]


def test_ultimate_hits_targets_in_range() -> None:
    hero = Hero(hp=800)
    hero.x = 500.0
    hero.y = 500.0
    hero._ult_timer = 0.0

    close = _DummyTarget(x=510.0, y=500.0, hp=9999)
    far = _DummyTarget(x=5000.0, y=5000.0, hp=9999)

    result = hero.ultimate([close, far])
    assert close in result["hit_targets"]
    assert far not in result["hit_targets"]


def test_ultimate_resets_cooldown() -> None:
    hero = Hero(hp=800, ultimate_cooldown_s=180.0)
    hero._ult_timer = 0.0
    hero.ultimate([])
    assert hero._ult_timer == 180.0


def test_ultimate_ult_ready_property() -> None:
    hero = Hero(hp=800)
    hero._ult_timer = 0.0
    assert hero.ult_ready is True
    hero._ult_timer = 5.0
    assert hero.ult_ready is False
