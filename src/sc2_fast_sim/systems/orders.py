"""命令执行：把 ScenarioCommand 翻译成实体上的状态变更。

Phase 3 只实现 attack_unit：
- 设 Combat.target_id
- 设 Movement.move_target（向目标移动，进入射程后停止由 combat 系统处理）
"""

from __future__ import annotations

from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.components.core import Position
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.scenario.model import ScenarioCommand


def apply_orders(world: World, orders: list[ScenarioCommand], current_loop: int) -> None:
    """应用当前 loop 的所有命令。"""
    for order in orders:
        if order.loop != current_loop:
            continue
        if order.kind == "attack_unit":
            _apply_attack_unit(world, order)


def _apply_attack_unit(world: World, order: ScenarioCommand) -> None:
    target_id = order.target_entity_id
    for eid in order.entity_ids:
        if eid not in world.entity_index:
            continue
        arch, row = world.entity_index[eid]
        # 设 Combat target
        if Combat in arch.component_types:
            cbt = arch.get(Combat)
            cbt[row]["target_id"] = target_id
        # 设 Movement 目标（向目标移动）
        if Movement in arch.component_types and target_id in world.entity_index:
            tgt_arch, tgt_row = world.entity_index[target_id]
            if Position in tgt_arch.component_types:
                tgt_pos = tgt_arch.get(Position)
                mv = arch.get(Movement)
                mv[row]["move_target_x"] = tgt_pos[tgt_row]["x"]
                mv[row]["move_target_y"] = tgt_pos[tgt_row]["y"]
                mv[row]["has_move_target"] = True
