"""ObjectPool 단위 테스트 (tk 비의존)."""

from __future__ import annotations

import pytest

from src.entities.entity import Entity, ObjectPool, PoolExhausted

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def make_pool(capacity: int = 5, canvas: object = None) -> ObjectPool:
    """테스트용 ObjectPool 생성. canvas=None → 헤드리스."""

    def factory() -> Entity:
        return Entity(x=0.0, y=0.0, hp=10)

    return ObjectPool(canvas=canvas, factory=factory, capacity=capacity)


# ---------------------------------------------------------------------------
# 기본 acquire / release
# ---------------------------------------------------------------------------


def test_acquire_creates_entity() -> None:
    pool = make_pool(capacity=3)
    obj = pool.acquire()
    assert isinstance(obj, Entity)
    assert obj.alive is True


def test_acquire_increments_active_count() -> None:
    pool = make_pool(capacity=3)
    pool.acquire()
    pool.acquire()
    assert pool.active_count == 2


def test_release_sets_alive_false() -> None:
    pool = make_pool()
    obj = pool.acquire()
    pool.release(obj)
    assert obj.alive is False


def test_release_increments_free_count() -> None:
    pool = make_pool()
    obj = pool.acquire()
    assert pool.free_count == 0
    pool.release(obj)
    assert pool.free_count == 1


def test_release_decrements_active_count() -> None:
    pool = make_pool()
    obj = pool.acquire()
    pool.release(obj)
    assert pool.active_count == 0


def test_acquire_reuses_released_object() -> None:
    pool = make_pool(capacity=2)
    obj1 = pool.acquire()
    pool.release(obj1)
    obj2 = pool.acquire()
    # 같은 객체 재사용
    assert obj2 is obj1
    assert obj2.alive is True


# ---------------------------------------------------------------------------
# capacity 가드 / PoolExhausted
# ---------------------------------------------------------------------------


def test_pool_exhausted_raises_when_full() -> None:
    pool = make_pool(capacity=2)
    pool.acquire()
    pool.acquire()
    with pytest.raises(PoolExhausted):
        pool.acquire()


def test_pool_exhausted_increments_stats() -> None:
    pool = make_pool(capacity=1)
    pool.acquire()
    assert pool.stats["exhausted"] == 0
    with pytest.raises(PoolExhausted):
        pool.acquire()
    assert pool.stats["exhausted"] == 1


def test_pool_not_exhausted_after_release() -> None:
    pool = make_pool(capacity=1)
    obj = pool.acquire()
    pool.release(obj)
    # 반환 후 다시 acquire 가능
    obj2 = pool.acquire()
    assert obj2.alive is True


# ---------------------------------------------------------------------------
# stats 카운터
# ---------------------------------------------------------------------------


def test_stats_created_and_reused() -> None:
    pool = make_pool(capacity=3)
    obj = pool.acquire()
    assert pool.stats["created"] == 1
    assert pool.stats["reused"] == 0
    pool.release(obj)
    pool.acquire()
    assert pool.stats["created"] == 1
    assert pool.stats["reused"] == 1


def test_stats_released_counter() -> None:
    pool = make_pool()
    obj = pool.acquire()
    pool.release(obj)
    assert pool.stats["released"] == 1


# ---------------------------------------------------------------------------
# 헤드리스(canvas=None) 동작
# ---------------------------------------------------------------------------


def test_headless_acquire_release_no_error() -> None:
    """canvas가 None이어도 에러 없이 동작해야 한다."""
    pool = make_pool(canvas=None)
    obj = pool.acquire()
    assert obj.alive is True
    pool.release(obj)
    assert obj.alive is False


# ---------------------------------------------------------------------------
# active_count / free_count 속성
# ---------------------------------------------------------------------------


def test_active_and_free_counts_consistent() -> None:
    pool = make_pool(capacity=4)
    a = pool.acquire()
    b = pool.acquire()
    assert pool.active_count == 2
    assert pool.free_count == 0
    pool.release(a)
    assert pool.active_count == 1
    assert pool.free_count == 1
    pool.release(b)
    assert pool.active_count == 0
    assert pool.free_count == 2
