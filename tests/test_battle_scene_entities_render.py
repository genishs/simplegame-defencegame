"""BattleScene.render() 엔티티 시각화 회귀 가드 (Issue #53).

# DECISION-DL-P4D-006 (Issue #53)
사용자 검수 결함 3호 — "stage1 진입은 되는데 전투가 안 됨, 영웅·적이 안 보임".

원인: ``BattleScene.render()`` 가 빈 함수(``pass``) 였다. systems 는 정상
동작했으나 entities (hero/enemies/allies/projectiles/effects) 가 캔버스에
전혀 그려지지 않아 사용자 입장에서 "stage 로드는 되었지만 전투가 시작되지
않은" 상태로 보였다. BL-07 시뮬레이터(`test_clear_rate_simulation.py`) 는
systems 만 직접 호출해 100% 클리어를 통과했기에 자동 가드가 결함을 잡지
못했다.

본 모듈은 실 BattleScene 의 render → entity 캔버스 아이템 생성/갱신 사슬을
FakeCanvas 로 검증하는 자동 가드.
"""

from __future__ import annotations

from typing import Any

from tests.test_battle_scene_flow import FakeApp


def _make_scene(stage_id: str = "stage_01") -> Any:
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id=stage_id)
    scene.build()
    return scene


def _items_with_tag(canvas: Any, tag: str) -> list[int]:
    """FakeCanvas 의 items dict 에서 주어진 tag 가 kwargs[tags] 에 포함된 항목 id."""
    out: list[int] = []
    for iid, item in canvas.items.items():
        _kind, _args, kw = item
        tags = kw.get("tags") or ()
        if isinstance(tags, str):
            tags = (tags,)
        if tag in tuple(tags):
            out.append(iid)
    return out


# ---------------------------------------------------------------------------
# 1. 영웅(Hero) 렌더 — build 직후 render 1회로 캔버스에 hero 아이템이 생성된다.
# ---------------------------------------------------------------------------


def test_render_creates_hero_canvas_item() -> None:
    """build() 후 render() 1회로 영웅이 캔버스에 그려진다 (Issue #53)."""
    scene = _make_scene()
    # build 시점에는 hero entity 는 존재하지만 canvas_id 는 아직 None.
    assert scene.world["hero"] is not None
    assert scene.world["hero"].canvas_id is None

    scene.render()

    hero = scene.world["hero"]
    assert hero.canvas_id is not None, "render() 후 영웅 canvas_id 가 할당되어야 한다"
    hero_items = _items_with_tag(scene.app.canvas, "hero")
    assert len(hero_items) == 1, f"hero 태그 캔버스 아이템 1개, got {len(hero_items)}"


# ---------------------------------------------------------------------------
# 2. 적(Enemy) 렌더 — _spawn_enemy 후 render 1회로 적이 캔버스에 그려진다.
# ---------------------------------------------------------------------------


def test_render_creates_enemy_canvas_item_after_spawn() -> None:
    """_spawn_enemy 후 render() 1회로 적이 캔버스에 그려진다 (Issue #53)."""
    scene = _make_scene()
    scene._spawn_enemy("tang_soldier", "p_main")
    enemy = scene.world["enemies"][0]
    assert enemy.canvas_id is None

    scene.render()

    assert enemy.canvas_id is not None, "render() 후 적 canvas_id 가 할당되어야 한다"
    enemy_items = _items_with_tag(scene.app.canvas, "enemy")
    assert len(enemy_items) == 1, f"enemy 태그 캔버스 아이템 1개, got {len(enemy_items)}"


# ---------------------------------------------------------------------------
# 3. update → wave 자동 진행 → 적 spawn → render 사슬 통합 검증
# ---------------------------------------------------------------------------


def test_first_wave_auto_spawns_and_renders() -> None:
    """첫 wave delay(3.0s) 만큼 update 누적 → 적 1+개 spawn → render 캔버스 동기화.

    Issue #53 핵심: 실 게임에서 stage 진입 후 일정 시간이 지나면 적이 등장하고
    그것이 사용자에게 보여야 한다. update + render 사슬 통합 가드.
    """
    scene = _make_scene()
    # stage_01.json: 첫 wave delay_s=3.0, count=4, interval=0.8.
    # delay 통과 + spawn interval 통과를 보장: 3.0 + 0.8 = 3.8 이상 누적.
    # update 는 dt 만큼 한 번에 진행하므로 큰 dt 1회로 충분.
    scene.update(3.0 + 0.9)
    assert len(scene.world["enemies"]) >= 1, "wave 1 가 시작되어 적이 1체 이상 spawn 되어야 한다"

    scene.render()
    for enemy in scene.world["enemies"]:
        assert enemy.canvas_id is not None, "spawn 된 적은 render 후 모두 canvas_id 가 있어야 한다"


# ---------------------------------------------------------------------------
# 4. render 멱등성 — 같은 entity 가 매 틱 새 canvas 아이템을 만들지 않는다.
# ---------------------------------------------------------------------------


def test_render_does_not_churn_canvas_items() -> None:
    """동일 entity 가 매 render() 마다 새 canvas item 을 만들지 않는다.

    canvas item churn 은 성능과 z-order 양쪽에서 결함의 원인이 된다.
    render() 두 번째 호출 시에는 ``coords``/``itemconfig`` 로 갱신만 해야 한다.
    """
    scene = _make_scene()
    scene._spawn_enemy("tang_soldier", "p_main")
    scene.render()
    first_hero_id = scene.world["hero"].canvas_id
    first_enemy_id = scene.world["enemies"][0].canvas_id
    assert first_hero_id is not None
    assert first_enemy_id is not None

    scene.render()
    scene.render()

    assert scene.world["hero"].canvas_id == first_hero_id, "영웅 canvas_id 가 churn 되면 안 된다"
    assert scene.world["enemies"][0].canvas_id == first_enemy_id, "적 canvas_id 가 churn 되면 안 된다"

    hero_items = _items_with_tag(scene.app.canvas, "hero")
    enemy_items = _items_with_tag(scene.app.canvas, "enemy")
    assert len(hero_items) == 1, "다중 render 후에도 영웅 캔버스 아이템은 1개"
    assert len(enemy_items) == 1, "다중 render 후에도 적 캔버스 아이템은 1개"


# ---------------------------------------------------------------------------
# 5. 죽은 엔티티의 캔버스 정리 — _cleanup_dead → render 사슬
# ---------------------------------------------------------------------------


def test_render_cleans_canvas_after_enemy_removed() -> None:
    """world 에서 제거된(또는 alive=False) 엔티티의 캔버스 아이템도 사라진다.

    _cleanup_dead 가 world['enemies'] 리스트에서 적을 빼면, 그 적의 canvas_id
    는 다음 render 에서 stale 로 감지되어 ``canvas.delete`` 된다.
    """
    scene = _make_scene()
    scene._spawn_enemy("tang_soldier", "p_main")
    scene.render()
    enemy = scene.world["enemies"][0]
    enemy_id = enemy.canvas_id
    assert enemy_id is not None
    assert enemy_id in scene.app.canvas.items

    # 적이 사망 → 다음 update 의 _cleanup_dead 가 list 에서 제거 → render 정리.
    enemy.alive = False
    scene._cleanup_dead()
    assert scene.world["enemies"] == []

    scene.render()
    assert (
        enemy_id not in scene.app.canvas.items
    ), "사망 후 다음 render 에서 적 캔버스 아이템이 삭제되어야 한다"


# ---------------------------------------------------------------------------
# 6. 좌표 변환 정합 — scaler.to_screen 결과로 그려진다.
# ---------------------------------------------------------------------------


def test_render_uses_scaler_to_screen_coordinates() -> None:
    """베이스 좌표 (hero.x, hero.y) 가 scaler.to_screen 결과 좌표로 그려진다.

    FakeScaler.scale=1.0, off=(0,0) 이므로 베이스 == 스크린.
    영웅 spawn 위치(stage_01 build_zones 첫 zone 중앙: x=740, y=640) 가
    캔버스 아이템 args 의 중앙 좌표와 일치해야 한다.
    """
    scene = _make_scene()
    hero = scene.world["hero"]
    # stage_01.json: 첫 build_zone = {x:700, y:600, w:80, h:80} → 중앙 (740, 640).
    assert hero.x == 740.0
    assert hero.y == 640.0

    scene.render()

    item = scene.app.canvas.items[hero.canvas_id]
    _kind, args, _kw = item
    # create_oval(x1, y1, x2, y2) — 중앙 = ((x1+x2)/2, (y1+y2)/2).
    x1, y1, x2, y2 = args[0], args[1], args[2], args[3]
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    assert abs(cx - hero.x) < 1e-6, f"render 영웅 cx={cx} != hero.x={hero.x}"
    assert abs(cy - hero.y) < 1e-6, f"render 영웅 cy={cy} != hero.y={hero.y}"


# ---------------------------------------------------------------------------
# 7. 멀티 엔티티 — 영웅 + 다수 적 동시 렌더
# ---------------------------------------------------------------------------


def test_render_handles_multiple_enemies() -> None:
    """다수 적이 동시에 spawn 되어도 render 가 각각 캔버스 아이템을 만든다."""
    scene = _make_scene()
    for _ in range(3):
        scene._spawn_enemy("tang_soldier", "p_main")
    assert len(scene.world["enemies"]) == 3

    scene.render()

    enemy_items = _items_with_tag(scene.app.canvas, "enemy")
    assert len(enemy_items) == 3, f"3 적 → 3 캔버스 아이템 기대, got {len(enemy_items)}"
    for e in scene.world["enemies"]:
        assert e.canvas_id is not None


# ---------------------------------------------------------------------------
# 8. update + render 사슬 — App._tick 시뮬레이션 (실 게임 정합)
# ---------------------------------------------------------------------------


def test_update_then_render_chain_matches_app_tick() -> None:
    """App._tick(dt) 가 scene.update(dt) + scene.render() 를 순서대로 호출하는 흐름 시뮬.

    Issue #53 의 본질: BL-07 시뮬은 update 만 호출하지만, 실 게임은 update +
    render 모두 호출해야 entities 가 보인다. 본 테스트는 _tick 흐름을 모사한다.
    """
    scene = _make_scene()
    # 3.5초 분량 누적: wave 1 시작 후 첫 적 spawn 보장.
    total_dt = 0.0
    for _ in range(20):
        scene.update(0.2)
        scene.render()
        total_dt += 0.2

    assert total_dt >= 3.5
    assert len(scene.world["enemies"]) >= 1, "4초 누적이면 wave 1 의 첫 적이 spawn 되어 있어야 한다"
    # 모든 적이 캔버스 아이템을 가져야 한다.
    for e in scene.world["enemies"]:
        assert e.canvas_id is not None, "render 단계에서 모든 적이 캔버스에 그려져야 한다"
    # 영웅도 마찬가지.
    assert scene.world["hero"].canvas_id is not None
