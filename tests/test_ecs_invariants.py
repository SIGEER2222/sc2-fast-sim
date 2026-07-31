"""ECS 不变量测试（设计 §8.3）。

- test_archetype_consistency: entity_index 与 archetype columns 行数一致
- test_swap_remove_no_dangling_reference: 删除后无悬空引用
- test_query_filter_returns_only_matching_archetypes: query 只返回包含 required 组件的 archetype
- test_query_with_alive_component_distinguishes_dead_and_alive: Alive 作为组件让"死亡"自动跳过
"""

import pytest
from sc2_fast_sim.ecs.component import Component, component
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.components.core import Position, Health, Owner, Alive


@component
class Combat(Component):
    damage: float
    range: float


def test_archetype_consistency():
    """entity_index 中每个 (arch, row) 必须对应 arch.columns 各列的有效行。"""
    world = World()
    e1 = world.create_entity(Position(x=0.0, y=0.0), Health(hp=10.0, shields=0.0), Owner(owner_id=1), Alive(alive=True))
    e2 = world.create_entity(Position(x=5.0, y=5.0), Health(hp=20.0, shields=5.0), Owner(owner_id=2), Alive(alive=True))
    e3 = world.create_entity(Position(x=10.0, y=10.0), Owner(owner_id=3))  # 无 Health/Alive

    for eid, (arch, row) in world.entity_index.items():
        assert row < arch.size, f"entity {eid} row {row} >= arch.size {arch.size}"
        assert arch.entity_ids[row] == eid, f"entity {eid} not at row {row} in entity_ids"
        for ct, col in arch.columns.items():
            assert col.shape[0] == arch.capacity
            _ = col[row]  # row 行可读

    # 所有 archetype 的 size 之和 == entity_index 大小
    total = sum(a.size for a in world.archetypes.values())
    assert total == len(world.entity_index)


def test_swap_remove_no_dangling_reference():
    """删除实体后，被 swap 的实体 index 指向正确数据，无悬空引用。"""
    world = World()
    e1 = world.create_entity(Position(x=1.0, y=1.0), Owner(owner_id=1))
    e2 = world.create_entity(Position(x=2.0, y=2.0), Owner(owner_id=2))
    e3 = world.create_entity(Position(x=3.0, y=3.0), Owner(owner_id=3))

    # 删除 e1 → e3 swap 到 row 0
    world.destroy_entity(e1)

    # e3 的 index 必须指向包含 e3 数据的行
    arch_e3, row_e3 = world.entity_index[e3]
    assert arch_e3.entity_ids[row_e3] == e3
    assert arch_e3.get(Position)[row_e3]["x"] == 3.0

    # e1 已不在 index
    assert e1 not in world.entity_index
    assert arch_e3.size == 2

    # 遍历所有 entity 都能正确读到自己的 Position
    for eid, (arch, row) in world.entity_index.items():
        pos = arch.get(Position)
        assert pos[row]["x"] == float(eid)  # 构造时 x == entity_id


def test_query_filter_returns_only_matching_archetypes():
    """query({Position, Owner}) 只返回同时含 Position 和 Owner 的 archetype。"""
    world = World()
    # archetype A: {Position, Owner, Alive}
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1), Alive(alive=True))
    # archetype B: {Position, Owner}
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1))
    # archetype C: {Position}（无 Owner）
    world.create_entity(Position(x=0.0, y=0.0))
    # archetype D: {Owner, Alive}（无 Position）
    world.create_entity(Owner(owner_id=1), Alive(alive=True))

    matched = list(world.query({Position, Owner}))
    assert len(matched) == 2  # 只匹配 A 和 B
    for arch in matched:
        assert Position in arch.component_types
        assert Owner in arch.component_types

    # 加一个含 Combat 但不含 Position 的 archetype，不应影响 {Position, Owner} 查询
    world.create_entity(Owner(owner_id=1), Combat(damage=5.0, range=3.0))
    matched2 = list(world.query({Position, Owner}))
    assert len(matched2) == 2  # 仍是 A 和 B


def test_query_with_alive_component_distinguishes_dead_and_alive():
    """Alive 作为组件让"死亡"变成 remove_component(Alive)，所有 query 自动跳过死单位。"""
    world = World()
    alive_e = world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1), Alive(alive=True))
    dead_e = world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1), Alive(alive=True))

    # 模拟"死亡"：移除 Alive 组件
    world.remove_component(dead_e, Alive)

    # 查询 {Position, Owner, Alive} 只应返回活着的 archetype
    alive_match = list(world.query({Position, Owner, Alive}))
    assert len(alive_match) == 1
    assert alive_match[0].size == 1
    # 活着的实体仍在该 archetype 中
    assert world.entity_index[alive_e][0] is alive_match[0]

    # 查询 {Position, Owner}（不含 Alive）应返回两个 archetype（活的 + 死的）
    all_match = list(world.query({Position, Owner}))
    assert len(all_match) == 2
