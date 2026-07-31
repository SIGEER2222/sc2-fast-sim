"""战斗与移动运行时组件。

Combat: 武器静态数据快照（从 catalog 复制）+ 运行时状态（cooldown/target_id）
Movement: 移动参数 + 朝向 + 移动目标

设计依据：sc2-fast-sim-design.md §3.6，算法参考 OpenHV PeriodicDischarge/FlyGuidedIntoTarget。
"""

from __future__ import annotations

from sc2_fast_sim.ecs.component import Component, component


@component
class Combat(Component):
    """战斗组件：武器数据 + 冷却状态 + 目标。"""
    weapon_damage: float
    weapon_attacks: int
    weapon_range: float
    weapon_period: int
    weapon_cooldown: int          # 当前冷却剩余 frame
    target_id: int                # 当前攻击目标 entity_id（0=无）
    versus_light: int             # 对 Light 护甲类型伤害百分比
    versus_armored: int           # 对 Armored
    versus_biological: int        # 对 Biological
    armor_class: int              # 自身护甲类型枚举值（0=none,1=light,2=armored,3=biological,4=mechanical）


@component
class Movement(Component):
    """移动组件：速度 + 朝向 + 移动目标。"""
    speed: float                  # 每帧移动距离（地图单位）
    facing: float                 # 朝向角度 0-360，0=北(+y)，顺时针
    turn_speed: float             # 每帧最大转向角度
    move_target_x: float          # 移动目标 x
    move_target_y: float          # 移动目标 y
    has_move_target: bool         # 是否有移动目标
