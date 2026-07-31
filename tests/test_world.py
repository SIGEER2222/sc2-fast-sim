import pytest
from sc2_fast_sim.ecs.component import Component, component
from sc2_fast_sim.ecs.world import World


@component
class Position(Component):
    x: float
    y: float


@component
class Owner(Component):
    owner_id: int


@component
class Alive(Component):
    alive: bool


def test_create_entity_returns_unique_ids():
    world = World()
    e1 = world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1))
    e2 = world.create_entity(Position(x=1.0, y=1.0), Owner(owner_id=2))
    assert e1 != e2
    assert e1 >= 1
    assert e2 >= 1


def test_create_entity_groups_by_archetype_signature():
    world = World()
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1))
    world.create_entity(Position(x=1.0, y=1.0), Owner(owner_id=2))
    # 同组件组合 → 同 archetype
    assert len(world.archetypes) == 1


def test_create_entity_different_signatures_create_separate_archetypes():
    world = World()
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1))
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1), Alive(alive=True))
    assert len(world.archetypes) == 2


def test_query_returns_only_archetypes_containing_all_required():
    world = World()
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1))
    world.create_entity(Position(x=0.0, y=0.0), Owner(owner_id=1), Alive(alive=True))
    world.create_entity(Owner(owner_id=1), Alive(alive=True))  # 无 Position

    matched = list(world.query({Position, Owner}))
    assert len(matched) == 2  # 两个 archetype 都含 Position+Owner


def test_query_with_unmatched_required_returns_empty():
    world = World()
    world.create_entity(Position(x=0.0, y=0.0))
    matched = list(world.query({Position, Owner}))
    assert matched == []


def test_destroy_entity_removes_from_index():
    world = World()
    e1 = world.create_entity(Position(x=0.0, y=0.0))
    e2 = world.create_entity(Position(x=1.0, y=1.0))
    world.destroy_entity(e1)
    assert e1 not in world.entity_index
    assert e2 in world.entity_index
    # archetype size 减 1
    arch = next(iter(world.archetypes.values()))
    assert arch.size == 1


def test_destroy_entity_swap_updates_index_of_moved_entity():
    world = World()
    e1 = world.create_entity(Position(x=0.0, y=0.0))
    e2 = world.create_entity(Position(x=1.0, y=1.0))
    e3 = world.create_entity(Position(x=2.0, y=2.0))
    # 删除 e1（row 0），e3（last row）swap 到 row 0
    world.destroy_entity(e1)
    # e3 的 index 现在应指向 row 0
    arch, row = world.entity_index[e3]
    assert row == 0
    assert arch.size == 2


def test_destroy_unknown_entity_raises_keyerror():
    world = World()
    with pytest.raises(KeyError):
        world.destroy_entity(9999)
