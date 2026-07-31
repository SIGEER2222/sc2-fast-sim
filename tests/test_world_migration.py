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


@component
class Combat(Component):
    damage: float
    range: float


def test_add_component_migrates_to_new_archetype():
    world = World()
    e = world.create_entity(Position(x=1.0, y=2.0), Owner(owner_id=5))
    world.add_component(e, Combat(damage=6.0, range=5.0))
    assert e in world.entity_index
    arch, row = world.entity_index[e]
    assert Combat in arch.component_types
    assert Position in arch.component_types
    assert Owner in arch.component_types


def test_add_component_preserves_existing_field_values():
    world = World()
    e = world.create_entity(Position(x=3.5, y=4.5), Owner(owner_id=7))
    world.add_component(e, Combat(damage=10.0, range=3.0))
    arch, row = world.entity_index[e]
    pos = arch.get(Position)
    own = arch.get(Owner)
    cbt = arch.get(Combat)
    assert pos[row]["x"] == 3.5
    assert pos[row]["y"] == 4.5
    assert own[row]["owner_id"] == 7
    assert cbt[row]["damage"] == 10.0
    assert cbt[row]["range"] == 3.0


def test_add_component_creates_new_archetype_if_signature_new():
    world = World()
    world.create_entity(Position(x=0.0, y=0.0))  # archetype A: {Position}
    e2 = world.create_entity(Position(x=0.0, y=0.0))  # 同 archetype A
    before = len(world.archetypes)
    world.add_component(e2, Owner(owner_id=1))  # e2 迁移到新 archetype B: {Position, Owner}
    after = len(world.archetypes)
    assert after == before + 1


def test_remove_component_migrates_to_archetype_without_component():
    world = World()
    e = world.create_entity(Position(x=1.0, y=2.0), Owner(owner_id=5), Alive(alive=True))
    world.remove_component(e, Alive)
    arch, row = world.entity_index[e]
    assert Alive not in arch.component_types
    assert Position in arch.component_types
    assert Owner in arch.component_types


def test_remove_component_preserves_other_field_values():
    world = World()
    e = world.create_entity(Position(x=9.0, y=8.0), Owner(owner_id=11), Alive(alive=True))
    world.remove_component(e, Alive)
    arch, row = world.entity_index[e]
    pos = arch.get(Position)
    own = arch.get(Owner)
    assert pos[row]["x"] == 9.0
    assert own[row]["owner_id"] == 11


def test_remove_component_swap_preserves_other_entities():
    """迁移走一个实体后，原 archetype 中被 swap 的实体的 index 仍正确。"""
    world = World()
    e1 = world.create_entity(Position(x=0.0, y=0.0), Alive(alive=True))
    e2 = world.create_entity(Position(x=1.0, y=1.0), Alive(alive=True))
    e3 = world.create_entity(Position(x=2.0, y=2.0), Alive(alive=True))
    # 迁移 e1（row 0）→ 旧 archetype swap e3 到 row 0
    world.remove_component(e1, Alive)
    # e3 仍可访问，且其 Position 值正确
    arch_e3, row_e3 = world.entity_index[e3]
    pos_e3 = arch_e3.get(Position)
    assert pos_e3[row_e3]["x"] == 2.0
    # e2 仍正确
    arch_e2, row_e2 = world.entity_index[e2]
    pos_e2 = arch_e2.get(Position)
    assert pos_e2[row_e2]["x"] == 1.0
