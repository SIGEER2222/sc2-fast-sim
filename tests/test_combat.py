import pytest
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.catalog.units import MARINE, ZERGLING, CATALOG
from sc2_fast_sim.systems.combat import step_combat


def make_unit(world, x, y, owner, hp=100.0, weapon_damage=5.0, weapon_range=5.0,
              weapon_period=19, weapon_cooldown=0, target_id=0, armor_class=1,
              versus_light=100, versus_armored=100, versus_biological=100):
    return world.create_entity(
        Position(x=x, y=y),
        Health(hp=hp, shields=0.0),
        Owner(owner_id=owner),
        Alive(alive=True),
        Combat(
            weapon_damage=weapon_damage, weapon_attacks=1, weapon_range=weapon_range,
            weapon_period=weapon_period, weapon_cooldown=weapon_cooldown,
            target_id=target_id, versus_light=versus_light, versus_armored=versus_armored,
            versus_biological=versus_biological, armor_class=armor_class,
        ),
    )


def test_combat_cooldown_decrements():
    world = World()
    e1 = make_unit(world, x=0, y=0, owner=1, weapon_cooldown=10)
    step_combat(world, CATALOG)
    arch, row = world.entity_index[e1]
    assert arch.get(Combat)[row]["weapon_cooldown"] == 9


def test_combat_no_target_no_damage():
    world = World()
    e1 = make_unit(world, x=0, y=0, owner=1, weapon_cooldown=0, target_id=0)
    e2 = make_unit(world, x=1, y=0, owner=2, hp=100.0)
    step_combat(world, CATALOG)
    arch, row = world.entity_index[e2]
    assert arch.get(Health)[row]["hp"] == 100.0


def test_combat_target_out_of_range_no_damage():
    world = World()
    e2 = make_unit(world, x=100, y=0, owner=2, hp=100.0)
    e1 = make_unit(world, x=0, y=0, owner=1, weapon_range=5.0, weapon_cooldown=0, target_id=e2)
    step_combat(world, CATALOG)
    arch, row = world.entity_index[e2]
    assert arch.get(Health)[row]["hp"] == 100.0


def test_combat_fires_and_deals_damage():
    world = World()
    e2 = make_unit(world, x=3, y=0, owner=2, hp=100.0)
    e1 = make_unit(world, x=0, y=0, owner=1, weapon_damage=10.0, weapon_range=5.0,
                   weapon_period=19, weapon_cooldown=0, target_id=e2)
    step_combat(world, CATALOG)
    arch, row = world.entity_index[e2]
    assert arch.get(Health)[row]["hp"] == 90.0  # 100 - 10
    arch1, row1 = world.entity_index[e1]
    assert arch1.get(Combat)[row1]["weapon_cooldown"] == 19  # 进入冷却


def test_combat_versus_applies_multiplier():
    """versus_armored=200 → 对 armored 目标双倍伤害。"""
    world = World()
    # e2 是 armored (armor_class=2)
    e2 = make_unit(world, x=3, y=0, owner=2, hp=100.0, armor_class=2)
    e1 = make_unit(world, x=0, y=0, owner=1, weapon_damage=10.0, weapon_range=5.0,
                   weapon_period=19, weapon_cooldown=0, target_id=e2,
                   versus_light=100, versus_armored=200, versus_biological=100)
    step_combat(world, CATALOG)
    arch, row = world.entity_index[e2]
    assert arch.get(Health)[row]["hp"] == 80.0  # 100 - 10*200/100 = 80


def test_combat_lethal_removes_alive():
    world = World()
    e2 = make_unit(world, x=3, y=0, owner=2, hp=5.0)
    e1 = make_unit(world, x=0, y=0, owner=1, weapon_damage=10.0, weapon_range=5.0,
                   weapon_period=19, weapon_cooldown=0, target_id=e2)
    step_combat(world, CATALOG)
    # e2 应该被移除 Alive 组件（死亡）
    assert e2 not in world.entity_index or \
           len(list(w for w in [world.entity_index.get(e2)] if w)) == 0 or \
           True  # remove_component 后 index 仍可能有，但 archetype 变了
    # 检查 e2 不再在含 Alive 的 archetype 中
    alive_archs = list(world.query({Alive}))
    for a in alive_archs:
        assert e2 not in a.entity_ids[:a.size]


def test_combat_multiple_attacks_per_weapon():
    """weapon_attacks=2 → 每次开火打 2 下。"""
    world = World()
    e2 = make_unit(world, x=3, y=0, owner=2, hp=100.0)
    e1 = world.create_entity(
        Position(x=0, y=0), Health(hp=100, shields=0), Owner(owner_id=1), Alive(alive=True),
        Combat(weapon_damage=5.0, weapon_attacks=2, weapon_range=5.0, weapon_period=19,
               weapon_cooldown=0, target_id=e2, versus_light=100, versus_armored=100,
               versus_biological=100, armor_class=1),
    )
    step_combat(world, CATALOG)
    arch, row = world.entity_index[e2]
    assert arch.get(Health)[row]["hp"] == 90.0  # 100 - 5*2
