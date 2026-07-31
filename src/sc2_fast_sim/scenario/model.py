"""场景定义模型（Phase 2 简化版）。

设计依据：旧仓库 sc2-ally-bot scenario/model.py，简化去除 triggers/terrain 等。
Phase 2 只需 players/spawns/commands + 基础参数。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ScenarioPlayer:
    id: int
    name: str
    race: str
    allies: tuple[int, ...] = ()
    is_ai: bool = True


@dataclass(frozen=True)
class ScenarioUnitSpawn:
    unit_type_id: str
    owner_player_id: int
    x: float
    y: float
    health_override: Optional[float] = None
    shield_override: Optional[float] = None


@dataclass(frozen=True)
class ScenarioCommand:
    loop: int
    kind: str
    issuer_player_id: int
    entity_ids: tuple[int, ...] = ()
    target_entity_id: int = 0
    target_x: float = 0.0
    target_y: float = 0.0
    unit_type_id: str = ""
    ability_id: str = ""


@dataclass(frozen=True)
class ScenarioDefinition:
    schema_version: str
    name: str
    players: tuple[ScenarioPlayer, ...] = ()
    spawns: tuple[ScenarioUnitSpawn, ...] = ()
    commands: tuple[ScenarioCommand, ...] = ()
    max_loops: int = 10000
    seed: int = 42
    strict: bool = True
    win_condition: str = "annihilation"