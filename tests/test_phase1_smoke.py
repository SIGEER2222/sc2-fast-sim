"""Phase 1 性能烟雾测试。

验证 1000 实体创建 + query 在合理时间内完成。
非 Phase 5 完整性能基准，仅作 sanity check。
"""

import time
import pytest
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.components.core import Position, Health, Owner, Alive


def test_create_1000_entities_under_50ms():
    world = World()
    t0 = time.perf_counter()
    for i in range(1000):
        world.create_entity(
            Position(x=float(i % 32), y=float(i // 32)),
            Health(hp=100.0, shields=0.0),
            Owner(owner_id=1),
            Alive(alive=True),
        )
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000
    assert elapsed_ms < 50.0, f"create 1000 entities took {elapsed_ms:.2f}ms (> 50ms)"
    assert world.next_entity_id == 1001


def test_query_1000_entities_under_5ms():
    world = World()
    for i in range(1000):
        world.create_entity(
            Position(x=float(i % 32), y=float(i // 32)),
            Health(hp=100.0, shields=0.0),
            Owner(owner_id=1),
            Alive(alive=True),
        )
    t0 = time.perf_counter()
    matched = list(world.query({Position, Owner, Alive}))
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000
    assert elapsed_ms < 5.0, f"query 1000 entities took {elapsed_ms:.2f}ms (> 5ms)"
    assert len(matched) == 1
    assert matched[0].size == 1000


def test_archetype_get_returns_view_for_1000_entities():
    """验证 get 返回的 view 长度 == size，可批量读字段。"""
    world = World()
    for i in range(1000):
        world.create_entity(
            Position(x=float(i), y=0.0),
            Owner(owner_id=i % 4),
            Alive(alive=True),
        )
    arch = next(iter(world.query({Position, Owner, Alive})))
    pos = arch.get(Position)
    own = arch.get(Owner)
    assert len(pos) == 1000
    assert len(own) == 1000
    xs = pos["x"]
    assert len(xs) == 1000
    assert xs[500] == 500.0
    owners = own["owner_id"]
    assert owners[0] == 0
    assert owners[1] == 1
    assert owners[4] == 0  # wrap
