"""战斗系统：武器冷却 + 伤害计算 + 死亡处理。

算法参考：
- OpenHV PeriodicDischarge.cs（冷却状态机，122-141 行）
- OpenHV TreeDamageWarhead.cs（伤害公式，67-68 行）

伤害公式：final = weapon.damage × weapon.attacks × versus[target.armor_class] / 100
死亡处理：HP <= 0 → remove_component(entity, Alive)
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from sc2_fast_sim.catalog.model import ArmorClass, UnitType
from sc2_fast_sim.components.combat import Combat
from sc2_fast_sim.components.core import Alive, Health, Owner, Position
from sc2_fast_sim.ecs.world import World

# ArmorClass 枚举 → versus 字段名映射
_ARMOR_CLASS_FIELD = {
    ArmorClass.NONE: "versus_light",       # 0
    ArmorClass.LIGHT: "versus_light",       # 1
    ArmorClass.ARMORED: "versus_armored",   # 2
    ArmorClass.BIOLOGICAL: "versus_biological",  # 3
    ArmorClass.MECHANICAL: "versus_armored",     # 4 归入 armored
}


def step_combat(world: World, catalog: Mapping[str, UnitType]) -> None:
    """执行一帧战斗：冷却递减 → 开火 → 伤害 → 死亡。"""
    # 收集所有活单位的位置和 entity_id（用于查目标）
    targets = {}  # entity_id → (arch, row, x, y)
    for arch in world.query({Position, Alive}):
        pos = arch.get(Position)
        eids = arch.entity_ids[: arch.size]
        for i in range(arch.size):
            targets[int(eids[i])] = (arch, i, pos[i]["x"], pos[i]["y"])

    # 收集所有攻击者（有 Combat + Position + Alive）
    attacks = []  # [(arch, row, attacker_eid, target_eid, damage, attacks, range, cooldown)]
    for arch in world.query({Position, Combat, Alive}):
        pos = arch.get(Position)
        cbt = arch.get(Combat)
        eids = arch.entity_ids[: arch.size]
        n = arch.size
        for i in range(n):
            # 冷却递减
            cd = int(cbt[i]["weapon_cooldown"])
            if cd > 0:
                cbt[i]["weapon_cooldown"] = cd - 1
                continue
            tgt_id = int(cbt[i]["target_id"])
            if tgt_id == 0 or tgt_id not in targets:
                continue
            # 射程检查
            tgt_arch, tgt_row, tx, ty = targets[tgt_id]
            dx = tx - float(pos[i]["x"])
            dy = ty - float(pos[i]["y"])
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > float(cbt[i]["weapon_range"]):
                continue
            # 可开火
            damage = float(cbt[i]["weapon_damage"])
            attacks_count = int(cbt[i]["weapon_attacks"])
            period = int(cbt[i]["weapon_period"])
            # 设冷却
            cbt[i]["weapon_cooldown"] = period
            attacks.append((tgt_arch, tgt_row, tgt_id, damage, attacks_count, int(cbt[i]["armor_class"]),
                            int(cbt[i]["versus_light"]), int(cbt[i]["versus_armored"]),
                            int(cbt[i]["versus_biological"])))

    # 应用伤害
    to_kill = []
    for (tgt_arch, tgt_row, tgt_id, damage, attacks_count, _attacker_armor,
         v_light, v_armored, v_bio) in attacks:
        # 查目标护甲类型
        tgt_cbt = None
        for a in world.query({Combat}):
            if tgt_id in [int(e) for e in a.entity_ids[:a.size]]:
                idx = list(a.entity_ids[:a.size]).index(tgt_id)
                tgt_cbt = a.get(Combat)
                tgt_armor = int(tgt_cbt[idx]["armor_class"])
                break
        if tgt_armor == 2:  # armored
            versus = v_armored
        elif tgt_armor == 3:  # biological
            versus = v_bio
        else:  # none/light/mechanical
            versus = v_light
        final_damage = damage * attacks_count * versus / 100.0
        # 找目标的 Health
        for a in world.query({Health}):
            if tgt_id in [int(e) for e in a.entity_ids[:a.size]]:
                idx = list(a.entity_ids[:a.size]).index(tgt_id)
                hp = a.get(Health)
                new_hp = float(hp[idx]["hp"]) - final_damage
                hp[idx]["hp"] = new_hp
                if new_hp <= 0:
                    to_kill.append(tgt_id)
                break

    # 死亡处理：remove_component(Alive)
    for eid in to_kill:
        if eid in world.entity_index:
            world.remove_component(eid, Alive)
