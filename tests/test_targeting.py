import pytest
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.systems.targeting import step_targeting


def make_combat_unit(world, x, y, owner, target_id=0, weapon_range=5.0):
    return world.create_entity(
        Position(x=x, y=y),
        Health(hp=100.0, shields=0.0),
        Owner(owner_id=owner),
        Alive(alive=True),
        Combat(
            weapon_damage=5.0, weapon_attacks=1, weapon_range=weapon_range,
            weapon_period=19, weapon_cooldown=0, target_id=target_id,
            versus_light=100, versus_armored=100, versus_biological=100, armor_class=1,
        ),
    )


def test_targeting_no_enemy_keeps_no_target():
    world = World()
    e1 = make_combat_unit(world, x=0, y=0, owner=1)
    step_targeting(world)
    arch, row = world.entity_index[e1]
    assert arch.get(Combat)[row]["target_id"] == 0


def test_targeting_acquires_nearest_enemy():
    world = World()
    e1 = make_combat_unit(world, x=0, y=0, owner=1)
    e2 = make_combat_unit(world, x=3, y=0, owner=2)  # 距离 3
    e3 = make_combat_unit(world, x=8, y=0, owner=2)  # 距离 8
    step_targeting(world)
    arch, row = world.entity_index[e1]
    assert arch.get(Combat)[row]["target_id"] == e2  # 最近


def test_targeting_ignores_same_owner():
    world = World()
    e1 = make_combat_unit(world, x=0, y=0, owner=1)
    e2 = make_combat_unit(world, x=1, y=0, owner=1)  # 同主
    step_targeting(world)
    arch, row = world.entity_index[e1]
    assert arch.get(Combat)[row]["target_id"] == 0


def test_targeting_keeps_existing_target_if_still_alive():
    world = World()
    e1 = make_combat_unit(world, x=0, y=0, owner=1, target_id=99)
    e2 = make_combat_unit(world, x=2, y=0, owner=2)
    step_targeting(world)
    arch, row = world.entity_index[e1]
    # 99 不存在 → 重新索敌
    assert arch.get(Combat)[row]["target_id"] == e2


def test_targeting_does_not_target_dead_units():
    """无 Alive 组件的单位不被选为目标。"""
    world = World()
    e1 = make_combat_unit(world, x=0, y=0, owner=1)
    # e2 是死单位（无 Alive）
    world.create_entity(
        Position(x=1, y=0), Health(hp=0.0, shields=0.0), Owner(owner_id=2),
        Combat(weapon_damage=5.0, weapon_attacks=1, weapon_range=5.0, weapon_period=19,
               weapon_cooldown=0, target_id=0, versus_light=100, versus_armored=100,
               versus_biological=100, armor_class=1),
    )
    step_targeting(world)
    arch, row = world.entity_index[e1]
    assert arch.get(Combat)[row]["target_id"] == 0  # 无有效目标
