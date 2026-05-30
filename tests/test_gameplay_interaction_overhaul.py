"""게임플레이 인터랙션 결함 4종에 대한 회귀 가드 (Issue #55/#56/#57/#58).

v0.4.0-rc.4 사용자 검수에서 발견된 결함을 BL-07 시뮬레이터 통과 외에 실
BattleScene/TutorialScene 인터랙션 수준으로 재현해 방지한다.

* Issue #55: 튜토리얼 단계 2/3 spotlight 내부 클릭이 단계 진행을 트리거해야 한다.
* Issue #56: BattleScene 이 유닛 선택 패널을 구축하고 build_zone 클릭 시
  Ally 가 ``world['allies']`` 에 추가되며 곡식이 차감되어야 한다.
* Issue #57: BattleScene.update 가 매 틱 영웅 평타를 트리거해야 한다.
* Issue #58: Hero 가 자동·수동 모드 모두에서 사거리 내 적에 발사체를 발사해야
  한다 (CombatSystem 경유로 데미지·이펙트가 적용된다).

DECISION-DL-P4D-007/008/009.
"""

from __future__ import annotations

from typing import Any

# tests/test_battle_scene_flow.py 의 Fake 인프라를 재사용.
from tests.test_battle_scene_flow import FakeApp


def _make_battle_scene(stage_id: str = "stage_01") -> Any:
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id=stage_id)
    scene.build()
    return scene


# ---------------------------------------------------------------------------
# Issue #58 / DECISION-DL-P4D-007: Hero 평타 자동 공격
# ---------------------------------------------------------------------------


def test_hero_has_auto_attack_method() -> None:
    """Hero 인스턴스는 auto_attack/find_target_in_range 메서드를 가진다."""
    from src.entities.hero import Hero

    hero = Hero(x=500.0, y=500.0)
    assert hasattr(hero, "auto_attack")
    assert hasattr(hero, "find_target_in_range")
    assert hero.atk_cooldown == 0.0


def test_hero_finds_target_in_range() -> None:
    """find_target_in_range 는 사거리 내 최근접 살아있는 적을 반환한다."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy
    from src.entities.hero import Hero

    edef = EnemyDef(id="x", name="x", hp=50, speed=60, armor=0, damage_to_castle=1, gold_drop=8, sprite="x")
    hero = Hero(x=500.0, y=500.0)
    near = Enemy(x=600.0, y=500.0, enemy_def=edef, path_id="p")  # 100 px
    far_in = Enemy(x=500.0, y=850.0, enemy_def=edef, path_id="p")  # 350 px (within 380)
    out = Enemy(x=500.0, y=900.0, enemy_def=edef, path_id="p")  # 400 px (out)
    target = hero.find_target_in_range([near, far_in, out])
    assert target is near


def test_hero_auto_attack_returns_fire_info_and_sets_cooldown() -> None:
    """auto_attack 은 사거리 내 적이 있으면 fire_info dict 반환 + cooldown 갱신."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy
    from src.entities.hero import Hero

    edef = EnemyDef(id="x", name="x", hp=50, speed=60, armor=0, damage_to_castle=1, gold_drop=8, sprite="x")
    hero = Hero(x=500.0, y=500.0)
    enemy = Enemy(x=600.0, y=500.0, enemy_def=edef, path_id="p")
    fire = hero.auto_attack([enemy])
    assert fire is not None
    assert fire["target"] is enemy
    assert fire["damage"] == hero.atk
    assert hero.atk_cooldown > 0.0


def test_hero_auto_attack_returns_none_when_no_target() -> None:
    from src.entities.hero import Hero

    hero = Hero(x=500.0, y=500.0)
    assert hero.auto_attack([]) is None


def test_hero_auto_attack_blocked_by_cooldown() -> None:
    """발사 직후 같은 호출은 None 을 반환 (쿨다운)."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy
    from src.entities.hero import Hero

    edef = EnemyDef(id="x", name="x", hp=50, speed=60, armor=0, damage_to_castle=1, gold_drop=8, sprite="x")
    hero = Hero(x=500.0, y=500.0)
    enemy = Enemy(x=600.0, y=500.0, enemy_def=edef, path_id="p")
    assert hero.auto_attack([enemy]) is not None
    assert hero.auto_attack([enemy]) is None


# ---------------------------------------------------------------------------
# Issue #57: BattleScene 이 매 틱 영웅 평타 트리거
# ---------------------------------------------------------------------------


def test_battle_scene_spawns_hero_projectile_when_enemy_in_range() -> None:
    """BattleScene.update 가 영웅 사거리 내 적에 대해 발사체를 스폰한다."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy

    scene = _make_battle_scene()
    hero = scene.world["hero"]
    assert hero is not None
    # 사거리(380) 안에 적 배치
    edef = EnemyDef(id="x", name="x", hp=50, speed=0, armor=0, damage_to_castle=1, gold_drop=8, sprite="x")
    enemy = Enemy(x=hero.x + 100.0, y=hero.y, enemy_def=edef, path_id="p_main")
    scene.world["enemies"].append(enemy)

    before = len(scene.world["projectiles"])
    scene.update(0.016)
    after = len(scene.world["projectiles"])
    assert after == before + 1, "hero should spawn a projectile when enemy in range"


def test_battle_scene_hero_attack_works_in_manual_mode() -> None:
    """Issue #58: 수동 모드에서도 평타가 자동 발사된다."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy

    scene = _make_battle_scene()
    hero = scene.world["hero"]
    # 수동 모드 ON
    scene._hero_direct_mode = True
    edef = EnemyDef(id="x", name="x", hp=50, speed=0, armor=0, damage_to_castle=1, gold_drop=8, sprite="x")
    enemy = Enemy(x=hero.x + 100.0, y=hero.y, enemy_def=edef, path_id="p_main")
    scene.world["enemies"].append(enemy)

    before = len(scene.world["projectiles"])
    scene.update(0.016)
    after = len(scene.world["projectiles"])
    assert after == before + 1, "manual mode should still trigger hero auto-attack"


def test_battle_scene_no_projectile_when_no_enemy() -> None:
    scene = _make_battle_scene()
    before = len(scene.world["projectiles"])
    scene.update(0.016)
    assert len(scene.world["projectiles"]) == before


# ---------------------------------------------------------------------------
# Issue #56 / DECISION-DL-P4D-008: 유닛 배치 UI
# ---------------------------------------------------------------------------


def test_battle_scene_loads_units_db() -> None:
    scene = _make_battle_scene()
    assert scene._units_db, "units.json should be loaded"
    assert "archer" in scene._units_db


def test_battle_scene_unit_selection_toggles() -> None:
    scene = _make_battle_scene()
    assert scene._selected_unit_id is None
    scene._on_unit_button_click("archer")
    assert scene._selected_unit_id == "archer"
    # 같은 유닛 다시 누르면 토글 해제
    scene._on_unit_button_click("archer")
    assert scene._selected_unit_id is None


def test_battle_scene_build_zone_click_places_ally() -> None:
    """유닛 선택 후 build_zone 클릭 → Ally 가 world['allies'] 에 추가."""
    scene = _make_battle_scene()
    scene._on_unit_button_click("archer")
    food_before = int(scene.world["food"])
    archer_cost = scene._units_db["archer"].cost
    scene._on_build_zone_click(0)
    assert len(scene.world["allies"]) == 1
    ally = scene.world["allies"][0]
    assert ally.unit_def.id == "archer"
    # 곡식 차감
    assert int(scene.world["food"]) == food_before - archer_cost
    # 점유 표시
    assert 0 in scene._build_zone_occupants


def test_battle_scene_build_zone_click_without_selection_no_op() -> None:
    scene = _make_battle_scene()
    food_before = int(scene.world["food"])
    scene._on_build_zone_click(0)
    assert len(scene.world["allies"]) == 0
    assert int(scene.world["food"]) == food_before


def test_battle_scene_build_zone_occupied_blocks_second_place() -> None:
    scene = _make_battle_scene()
    scene._on_unit_button_click("archer")
    scene._on_build_zone_click(0)
    # 두 번째 클릭은 같은 zone 이라면 추가 안 됨
    scene._on_unit_button_click("archer")
    scene._on_build_zone_click(0)
    assert len(scene.world["allies"]) == 1


def test_battle_scene_insufficient_food_blocks_place() -> None:
    scene = _make_battle_scene()
    scene.world["food"] = 0
    scene._on_unit_button_click("archer")
    scene._on_build_zone_click(0)
    assert len(scene.world["allies"]) == 0


# ---------------------------------------------------------------------------
# Issue #55 / DECISION-DL-P4D-009: 튜토리얼 spotlight 클릭 핸들러
# ---------------------------------------------------------------------------


class _RecCanvas:
    """tag_bind 호출을 기록하는 Canvas mock."""

    def __init__(self) -> None:
        self.items: dict[int, Any] = {}
        self._next: int = 1
        self.bindings: list[tuple[int, str, Any]] = []

    def create_rectangle(self, *a: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("rect", a, kw)
        return i

    def create_text(self, *a: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("text", a, kw)
        return i

    def create_line(self, *a: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("line", a, kw)
        return i

    def create_oval(self, *a: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("oval", a, kw)
        return i

    def create_polygon(self, *a: Any, **kw: Any) -> int:
        i = self._next
        self._next += 1
        self.items[i] = ("polygon", a, kw)
        return i

    def itemconfig(self, *a: Any, **kw: Any) -> None:
        pass

    def coords(self, *a: Any, **kw: Any) -> None:
        pass

    def delete(self, *a: Any, **kw: Any) -> None:
        pass

    def tag_bind(self, iid: int, event: str, fn: Any) -> None:
        self.bindings.append((iid, event, fn))

    def winfo_width(self) -> int:
        return 1920

    def winfo_height(self) -> int:
        return 1080

    def after(self, *a: Any, **kw: Any) -> str:
        return "after_id"


def _tutorial_with_recording_canvas() -> Any:
    from src.scenes.tutorial_scene import TutorialScene
    from tests.test_battle_scene_flow import FakeApp

    app = FakeApp()
    app.canvas = _RecCanvas()
    scene = TutorialScene(app)
    scene.build()
    return scene


def test_tutorial_step2_spotlight_has_click_bindings() -> None:
    """단계 2 (resource) 의 spotlight 영역에 클릭 핸들러가 binding 된다."""
    scene = _tutorial_with_recording_canvas()
    # 1단계 → 2단계 진입
    scene._enter_step(2)
    bindings = scene.app.canvas.bindings
    # 최소 1개 이상의 ButtonRelease-1 핸들러가 있어야 한다.
    release_bindings = [b for b in bindings if b[1] == "<ButtonRelease-1>"]
    assert len(release_bindings) >= 1, "step 2 must wire click handlers on spotlight content"


def test_tutorial_step2_click_advances_to_step3() -> None:
    """등록된 클릭 핸들러 중 하나를 호출하면 단계 3 으로 진행된다."""
    scene = _tutorial_with_recording_canvas()
    scene._enter_step(2)
    # spotlight 영역 핸들러 호출 시뮬레이션
    handler = scene._spotlight_click_handler
    assert handler is not None
    handler(None)  # 가짜 event
    assert scene.step == 3, "click on resource spotlight must advance step 2 → 3"


def test_tutorial_step3_click_advances_to_step4() -> None:
    """단계 3 (buildzone) 클릭은 궁수 mock 패널 선택 후 단계 4 로 진행 (Issue #67)."""
    scene = _tutorial_with_recording_canvas()
    scene._enter_step(3)
    handler = scene._spotlight_click_handler
    assert handler is not None
    # Issue #67 (DECISION-DL-P4D-012): buildzone 클릭 단독으로는 진행 X.
    handler(None)
    assert scene.step == 3, "궁수 선택 없이 buildzone 만 누르면 진행 X"
    # 궁수 mock 패널 선택 후 다시 buildzone → 진행.
    scene._step3_archer_selected = True
    handler(None)
    assert scene.step == 4


def test_tutorial_step5_has_no_spotlight_click_handler() -> None:
    """단계 5 (hero) 는 클릭이 아니라 M 키로 진행 — spotlight 핸들러 없음."""
    scene = _tutorial_with_recording_canvas()
    scene._enter_step(5)
    handler = getattr(scene, "_spotlight_click_handler", None)
    assert handler is None
