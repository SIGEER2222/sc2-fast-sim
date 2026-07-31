"""目标选择系统：为有 Combat 无目标的单位自动索敌。

规则：
- 只选不同 Owner 的活单位（有 Alive 组件）
- 选距离最近的
- 已有目标且目标仍存在且活着 → 保持
"""

from __future__ import annotations

import numpy as np

from sc2_fast_sim.components.combat import Combat
from sc2_fast_sim.components.core import Alive, Owner, Position
from sc2_fast_sim.ecs.world import World


def step_targeting(world: World) -> None:
    """为所有有 Combat 的单位选择/维持攻击目标。"""
    # 收集所有活单位（有 Position + Owner + Alive）作为候选目标
    candidates = []  # [(x, y, owner, entity_id), ...]
    for arch in world.query({Position, Owner, Alive}):
        pos = arch.get(Position)
        own = arch.get(Owner)
        eids = arch.entity_ids[: arch.size]
        for i in range(arch.size):
            candidates.append((pos[i]["x"], pos[i]["y"], own[i]["owner_id"], eids[i]))

    if not candidates:
        return

    cand_x = np.array([c[0] for c in candidates])
    cand_y = np.array([c[1] for c in candidates])
    cand_owner = np.array([c[2] for c in candidates])
    cand_eid = np.array([c[3] for c in candidates])

    # 建目标 entity_id → 索引映射（用于检查目标是否活着）
    alive_set = set(int(e) for e in cand_eid)

    for arch in world.query({Position, Owner, Combat}):
        pos = arch.get(Position)
        own = arch.get(Owner)
        cbt = arch.get(Combat)
        eids = arch.entity_ids[: arch.size]
        n = arch.size
        for i in range(n):
            cur_tgt = int(cbt[i]["target_id"])
            # 已有目标且仍活着 → 保持
            if cur_tgt != 0 and cur_tgt in alive_set:
                continue
            # 重新索敌：找不同 owner 的最近活单位
            my_x = pos[i]["x"]
            my_y = pos[i]["y"]
            my_owner = own[i]["owner_id"]
            dist = np.sqrt((cand_x - my_x) ** 2 + (cand_y - my_y) ** 2)
            valid = cand_owner != my_owner
            if not np.any(valid):
                cbt[i]["target_id"] = 0
                continue
            masked_dist = np.where(valid, dist, np.inf)
            nearest_idx = int(np.argmin(masked_dist))
            cbt[i]["target_id"] = int(cand_eid[nearest_idx])
