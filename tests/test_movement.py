import numpy as np
import pytest
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.systems.movement import step_movement


def make_unit(world, x, y, speed=2.0, facing=0.0, turn_speed=10.0):
    return world.create_entity(
        Position(x=x, y=y),
        Health(hp=100.0, shields=0.0),
        Owner(owner_id=1),
        Alive(alive=True),
        Movement(speed=speed, facing=facing, turn_speed=turn_speed, move_target_x=0.0, move_target_y=0.0, has_move_target=False),
    )


def test_movement_no_target_stays_put():
    world = World()
    e = make_unit(world, x=5.0, y=5.0)
    step_movement(world)
    arch, row = world.entity_index[e]
    pos = arch.get(Position)
    assert pos[row]["x"] == 5.0
    assert pos[row]["y"] == 5.0


def test_movement_turns_toward_target():
    """单位朝北(0°)，目标在东(+x)，应转向 90°。"""
    world = World()
    e = make_unit(world, x=0.0, y=0.0, facing=0.0, turn_speed=10.0)
    arch, row = world.entity_index[e]
    # 设移动目标到东边
    mv = arch.get(Movement)
    mv[row]["move_target_x"] = 10.0
    mv[row]["move_target_y"] = 0.0
    mv[row]["has_move_target"] = True
    step_movement(world)
    mv2 = arch.get(Movement)
    assert mv2[row]["facing"] == 10.0  # 转了 10°


def test_movement_turns_counterclockwise():
    """单位朝东(90°)，目标在北(0°/+y)，应逆时针转向。"""
    world = World()
    e = make_unit(world, x=0.0, y=0.0, facing=90.0, turn_speed=10.0)
    arch, row = world.entity_index[e]
    mv = arch.get(Movement)
    mv[row]["move_target_x"] = 0.0
    mv[row]["move_target_y"] = 10.0
    mv[row]["has_move_target"] = True
    step_movement(world)
    mv2 = arch.get(Movement)
    assert mv2[row]["facing"] == 80.0  # 90-10=80


def test_movement_moves_forward_when_facing_target():
    """朝向对准目标后直线移动。"""
    world = World()
    # 朝东(90°)，目标在东边
    e = make_unit(world, x=0.0, y=0.0, facing=90.0, speed=5.0, turn_speed=999.0)
    arch, row = world.entity_index[e]
    mv = arch.get(Movement)
    mv[row]["move_target_x"] = 100.0
    mv[row]["move_target_y"] = 0.0
    mv[row]["has_move_target"] = True
    step_movement(world)
    pos = arch.get(Position)
    # 朝东(+x)，移动 5 单位
    assert pos[row]["x"] == pytest.approx(5.0, abs=0.1)
    assert pos[row]["y"] == pytest.approx(0.0, abs=0.1)


def test_movement_stops_when_reaching_target():
    """到达目标后 has_move_target 置 False。"""
    world = World()
    e = make_unit(world, x=0.0, y=0.0, facing=90.0, speed=100.0, turn_speed=999.0)
    arch, row = world.entity_index[e]
    mv = arch.get(Movement)
    mv[row]["move_target_x"] = 5.0
    mv[row]["move_target_y"] = 0.0
    mv[row]["has_move_target"] = True
    step_movement(world)
    mv2 = arch.get(Movement)
    assert mv2[row]["has_move_target"] == False or mv2[row]["has_move_target"] == 0


def test_movement_multiple_units_vectorized():
    """多个单位同时移动，互不影响。"""
    world = World()
    e1 = make_unit(world, x=0.0, y=0.0, facing=90.0, speed=5.0, turn_speed=999.0)
    e2 = make_unit(world, x=10.0, y=0.0, facing=270.0, speed=3.0, turn_speed=999.0)
    arch, r1 = world.entity_index[e1]
    _, r2 = world.entity_index[e2]
    mv = arch.get(Movement)
    mv[r1]["move_target_x"] = 100.0
    mv[r1]["move_target_y"] = 0.0
    mv[r1]["has_move_target"] = True
    mv[r2]["move_target_x"] = -100.0
    mv[r2]["move_target_y"] = 0.0
    mv[r2]["has_move_target"] = True
    step_movement(world)
    pos = arch.get(Position)
    assert pos[r1]["x"] == pytest.approx(5.0, abs=0.1)
    assert pos[r2]["x"] == pytest.approx(7.0, abs=0.1)  # 10-3=7
