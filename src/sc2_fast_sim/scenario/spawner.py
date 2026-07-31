"""场景到 World 的桥接：把 scenario.spawns 转成 ECS 实体。

职责：
- 遍历 spawns，查 catalog 得 UnitType
- 用 UnitType.max_health 填 Health（除非 spawn 有 health_override）
- 调用 world.create_entity(Position, Health, Owner, Alive)
- 返回创建的 entity_id 列表

不处理 commands（Phase 3 systems 实现后处理）。
"""

from __future__ import annotations

from typing import Mapping

from sc2_fast_sim.catalog.model import UnitType
from sc2_fast_sim.components.core import Alive, Health, Owner, Position
from sc2_fast_sim.ecs.world import World

from .model import ScenarioDefinition


def spawn_entities(
    world: World,
    scenario: ScenarioDefinition,
    catalog: Mapping[str, UnitType],
) -> list[int]:
    """把 scenario.spawns 注入 world，返回 entity_id 列表。"""
    ids: list[int] = []
    for spawn in scenario.spawns:
        unit_type = catalog[spawn.unit_type_id]  # KeyError 若未知
        hp = spawn.health_override if spawn.health_override is not None else unit_type.max_health
        shields = spawn.shield_override if spawn.shield_override is not None else unit_type.max_shields
        eid = world.create_entity(
            Position(x=spawn.x, y=spawn.y),
            Health(hp=hp, shields=shields),
            Owner(owner_id=spawn.owner_player_id),
            Alive(alive=True),
        )
        ids.append(eid)
    return ids