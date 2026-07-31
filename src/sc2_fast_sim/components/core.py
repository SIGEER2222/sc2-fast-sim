"""核心组件定义（最小集，用于验证 ECS）。

设计依据：sc2-fast-sim-design.md §3.6。
Combat/Worker/Building/Production 等业务组件留给后续 Phase 引入。
"""

from __future__ import annotations

from sc2_fast_sim.ecs.component import Component, component


@component
class Position(Component):
    x: float
    y: float


@component
class Health(Component):
    hp: float
    shields: float


@component
class Owner(Component):
    owner_id: int


@component
class Alive(Component):
    alive: bool
