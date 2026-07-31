from pathlib import Path
import pytest
from sc2_fast_sim.catalog.units import CATALOG
from sc2_fast_sim.simulator import step, run_scenario
from sc2_fast_sim.scenario.loader import load_scenario
from sc2_fast_sim.scenario.spawner import spawn_entities
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.catalog.model import ArmorClass

FIXTURE = Path(__file__).parent / "fixtures" / "marine_vs_zergling.json"

_ARMOR_VALUES = {
    ArmorClass.NONE: 0, ArmorClass.LIGHT: 1, ArmorClass.ARMORED: 2,
    ArmorClass.BIOLOGICAL: 3, ArmorClass.MECHANICAL: 4,
}


def _equip_from_scenario(world, ids, scenario, catalog):
    """给实体补 Combat + Movement 组件（按 scenario.spawns 顺序反查 unit_type_id）。"""
    for eid, spawn in zip(ids, scenario.spawns):
        ut = catalog[spawn.unit_type_id]
        w = ut.weapon_ground
        arch, row = world.entity_index[eid]
        world.add_component(eid, Combat(
            weapon_damage=w.damage, weapon_attacks=w.attacks, weapon_range=w.range,
            weapon_period=w.period, weapon_cooldown=0, target_id=0,
            versus_light=w.versus.get(ArmorClass.LIGHT, 100),
            versus_armored=w.versus.get(ArmorClass.ARMORED, 100),
            versus_biological=w.versus.get(ArmorClass.BIOLOGICAL, 100),
            armor_class=_ARMOR_VALUES[ut.armor_class],
        ))
        world.add_component(eid, Movement(
            speed=ut.speed / 22.4, facing=0.0, turn_speed=999.0,
            move_target_x=0.0, move_target_y=0.0, has_move_target=False,
        ))


def test_step_runs_without_error():
    sc = load_scenario(FIXTURE)
    from sc2_fast_sim.ecs.world import World
    world = World()
    ids = spawn_entities(world, sc, CATALOG)
    _equip_from_scenario(world, ids, sc, CATALOG)
    step(world, CATALOG, list(sc.commands), current_loop=0)


def test_run_scenario_completes():
    sc = load_scenario(FIXTURE)
    result = run_scenario(sc, CATALOG)
    assert result["loops_run"] <= sc.max_loops
    assert "winner" in result
    assert "entities" in result


def test_run_scenario_marine_vs_zergling_ends_in_death():
    sc = load_scenario(FIXTURE)
    result = run_scenario(sc, CATALOG)
    # 至少一方死亡
    alive_count = sum(1 for e in result["entities"] if e.get("alive"))
    assert alive_count <= 1
