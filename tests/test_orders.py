from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.scenario.model import ScenarioCommand
from sc2_fast_sim.systems.orders import apply_orders


def make_full_unit(world, x, y, owner, speed=2.0):
    return world.create_entity(
        Position(x=x, y=y),
        Health(hp=100.0, shields=0.0),
        Owner(owner_id=owner),
        Alive(alive=True),
        Combat(weapon_damage=5, weapon_attacks=1, weapon_range=5, weapon_period=19,
               weapon_cooldown=0, target_id=0, versus_light=100, versus_armored=100,
               versus_biological=100, armor_class=1),
        Movement(speed=speed, facing=0.0, turn_speed=999.0, move_target_x=0.0,
                 move_target_y=0.0, has_move_target=False),
    )


def test_apply_attack_unit_order_sets_target_and_moves():
    world = World()
    e1 = make_full_unit(world, x=0, y=0, owner=1)
    e2 = make_full_unit(world, x=20, y=0, owner=2)
    orders = [ScenarioCommand(loop=0, kind="attack_unit", issuer_player_id=1,
                              entity_ids=(e1,), target_entity_id=e2)]
    apply_orders(world, orders, current_loop=0)
    arch, row = world.entity_index[e1]
    cbt = arch.get(Combat)
    mv = arch.get(Movement)
    assert cbt[row]["target_id"] == e2
    assert mv[row]["has_move_target"] == True or mv[row]["has_move_target"] == 1


def test_apply_orders_skips_wrong_loop():
    world = World()
    e1 = make_full_unit(world, x=0, y=0, owner=1)
    e2 = make_full_unit(world, x=20, y=0, owner=2)
    orders = [ScenarioCommand(loop=5, kind="attack_unit", issuer_player_id=1,
                              entity_ids=(e1,), target_entity_id=e2)]
    apply_orders(world, orders, current_loop=0)
    arch, row = world.entity_index[e1]
    assert arch.get(Combat)[row]["target_id"] == 0


def test_apply_orders_unknown_entity_skipped():
    world = World()
    orders = [ScenarioCommand(loop=0, kind="attack_unit", issuer_player_id=1,
                              entity_ids=(999,), target_entity_id=998)]
    apply_orders(world, orders, current_loop=0)  # 不应报错
