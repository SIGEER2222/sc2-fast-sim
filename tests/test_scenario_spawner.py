from pathlib import Path

import pytest
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.ecs.component import Component, component
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.catalog.units import CATALOG
from sc2_fast_sim.scenario.loader import load_scenario
from sc2_fast_sim.scenario.spawner import spawn_entities

FIXTURE = Path(__file__).parent / "fixtures" / "marine_vs_zergling.json"


def test_spawn_entities_returns_entity_ids():
    sc = load_scenario(FIXTURE)
    world = World()
    ids = spawn_entities(world, sc, CATALOG)
    assert len(ids) == 2
    assert all(isinstance(i, int) for i in ids)
    assert len(set(ids)) == 2  # 唯一


def test_spawn_entities_creates_entities_in_world():
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)
    assert world.next_entity_id == 3  # 2 个实体，id 从 1 开始


def test_spawn_entities_assigns_position_from_spawn():
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)
    archs = list(world.query({Position}))
    assert len(archs) == 1
    pos = archs[0].get(Position)
    assert pos[0]["x"] == 0.0  # Marine
    assert pos[0]["y"] == 0.0
    assert pos[1]["x"] == 10.0  # Zergling
    assert pos[1]["y"] == 0.0


def test_spawn_entities_assigns_health_from_catalog():
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)
    pos_arch = list(world.query({Position}))[0]
    health = pos_arch.get(Health)
    # Marine hp=45, Zergling hp=35
    assert health[0]["hp"] == 45.0
    assert health[1]["hp"] == 35.0
    # shields 默认 0
    assert health[0]["shields"] == 0.0


def test_spawn_entities_assigns_owner_from_spawn():
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)
    arch = list(world.query({Owner}))[0]
    own = arch.get(Owner)
    assert own[0]["owner_id"] == 1  # Marine 属 player 1
    assert own[1]["owner_id"] == 2  # Zergling 属 player 2


def test_spawn_entities_assigns_alive_true():
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)
    arch = list(world.query({Alive}))[0]
    alive = arch.get(Alive)
    assert bool(alive[0]["alive"]) is True
    assert bool(alive[1]["alive"]) is True


def test_spawn_entities_health_override():
    sc = load_scenario({
        "name": "override",
        "players": [{"id": 1, "name": "P1", "race": "terran"}],
        "spawns": [
            {"unit_type_id": "Marine", "owner_player_id": 1, "x": 0.0, "y": 0.0, "health_override": 10.0},
        ],
    })
    world = World()
    spawn_entities(world, sc, CATALOG)
    arch = list(world.query({Health}))[0]
    health = arch.get(Health)
    assert health[0]["hp"] == 10.0  # override 生效


def test_spawn_entities_unknown_unit_raises_keyerror():
    sc = load_scenario({
        "name": "bad",
        "spawns": [{"unit_type_id": "Nonexistent", "owner_player_id": 1, "x": 0.0, "y": 0.0}],
    })
    world = World()
    with pytest.raises(KeyError):
        spawn_entities(world, sc, CATALOG)


def test_spawn_entities_all_in_single_archetype():
    """Marine 和 Zergling 组件组合相同（Position/Health/Owner/Alive），应在同一 archetype。"""
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)
    assert len(world.archetypes) == 1
    arch = next(iter(world.archetypes.values()))
    assert arch.size == 2