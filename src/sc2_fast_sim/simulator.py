"""模拟器主循环：串联 movement → targeting → combat。

step(): 单帧推进
run_scenario(): 跑完整个场景
"""

from __future__ import annotations

from typing import Mapping

from sc2_fast_sim.catalog.model import ArmorClass, UnitType
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.components.core import Alive, Health, Owner, Position
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.scenario.model import ScenarioCommand, ScenarioDefinition
from sc2_fast_sim.systems.combat import step_combat
from sc2_fast_sim.systems.movement import step_movement
from sc2_fast_sim.systems.orders import apply_orders
from sc2_fast_sim.systems.targeting import step_targeting

_ARMOR_VALUES = {
    ArmorClass.NONE: 0, ArmorClass.LIGHT: 1, ArmorClass.ARMORED: 2,
    ArmorClass.BIOLOGICAL: 3, ArmorClass.MECHANICAL: 4,
}


def step(world: World, catalog: Mapping[str, UnitType],
         orders: list[ScenarioCommand], current_loop: int) -> None:
    """单帧推进：命令 → 追踪 → 移动 → 索敌 → 战斗。"""
    apply_orders(world, orders, current_loop)
    _pursue_targets(world)
    step_movement(world)
    step_targeting(world)
    step_combat(world, catalog)


def _pursue_targets(world: World) -> None:
    """有攻击目标的单位持续追踪目标当前位置（参考 OpenHV AttackMove 追踪语义）。

    attack_unit 命令只在指定 loop 设一次 move_target（目标当时位置）。
    若不更新，单位到达目标初始位置后停止，目标已移走 → 永远打不到。
    此函数每帧把 move_target 刷新为目标当前位置，实现持续追踪。
    """
    # 先收集所有活单位当前位置
    positions: dict[int, tuple[float, float]] = {}
    for arch in world.query({Position, Alive}):
        pos = arch.get(Position)
        eids = arch.entity_ids[: arch.size]
        for i in range(arch.size):
            positions[int(eids[i])] = (float(pos[i]["x"]), float(pos[i]["y"]))

    for arch in world.query({Combat, Movement, Position, Alive}):
        cbt = arch.get(Combat)
        mv = arch.get(Movement)
        n = arch.size
        for i in range(n):
            tgt_id = int(cbt[i]["target_id"])
            if tgt_id == 0 or tgt_id not in positions:
                continue
            tx, ty = positions[tgt_id]
            mv[i]["move_target_x"] = tx
            mv[i]["move_target_y"] = ty
            mv[i]["has_move_target"] = True


def run_scenario(scenario: ScenarioDefinition, catalog: Mapping[str, UnitType]) -> dict:
    """跑完整个场景，返回结果。"""
    from sc2_fast_sim.scenario.spawner import spawn_entities
    world = World()
    ids = spawn_entities(world, scenario, catalog)
    _equip_combat_movement(world, ids, scenario, catalog)

    orders = list(scenario.commands)
    loop = 0
    for loop in range(scenario.max_loops):
        step(world, catalog, orders, loop)
        # 检查胜负：活着的 owner 数
        alive_owners = set()
        for arch in world.query({Alive, Owner}):
            own = arch.get(Owner)
            for i in range(arch.size):
                alive_owners.add(int(own[i]["owner_id"]))
        if len(alive_owners) <= 1:
            break

    # 收集结果
    entities = []
    for arch in world.query({Position, Health, Owner}):
        pos = arch.get(Position)
        hp = arch.get(Health)
        own = arch.get(Owner)
        eids = arch.entity_ids[: arch.size]
        has_alive = Alive in arch.component_types
        for i in range(arch.size):
            entities.append({
                "entity_id": int(eids[i]),
                "x": float(pos[i]["x"]),
                "y": float(pos[i]["y"]),
                "hp": float(hp[i]["hp"]),
                "owner": int(own[i]["owner_id"]),
                "alive": has_alive,
            })

    alive_owners = set(e["owner"] for e in entities if e["alive"])
    winner = next(iter(alive_owners)) if len(alive_owners) == 1 else None

    return {
        "loops_run": loop + 1,
        "winner": winner,
        "entities": entities,
    }


def _equip_combat_movement(world: World, entity_ids: list[int],
                           scenario: ScenarioDefinition,
                           catalog: Mapping[str, UnitType]) -> None:
    """给实体补 Combat + Movement 组件（按 scenario.spawns 顺序反查 unit_type_id）。

    Phase 3 临时方案：spawner 只创建 Position/Health/Owner/Alive，
    Combat/Movement 在此补齐。Phase 4 spawner 会集成。
    """
    for eid, spawn in zip(entity_ids, scenario.spawns):
        ut = catalog[spawn.unit_type_id]
        w = ut.weapon_ground
        world.add_component(eid, Combat(
            weapon_damage=w.damage, weapon_attacks=w.attacks, weapon_range=w.range,
            weapon_period=w.period, weapon_cooldown=0, target_id=0,
            versus_light=w.versus.get(ArmorClass.LIGHT, 100),
            versus_armored=w.versus.get(ArmorClass.ARMORED, 100),
            versus_biological=w.versus.get(ArmorClass.BIOLOGICAL, 100),
            armor_class=_ARMOR_VALUES[ut.armor_class],
        ))
        world.add_component(eid, Movement(
            speed=ut.speed / 22.4,  # SC2 speed 是每秒距离，转每帧距离（22.4 fps）
            facing=0.0, turn_speed=999.0,
            move_target_x=0.0, move_target_y=0.0, has_move_target=False,
        ))
