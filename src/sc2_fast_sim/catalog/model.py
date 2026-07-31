"""Catalog 数据模型（Phase 2 最小集）。

设计依据：sc2-fast-sim-design.md §3.6。
数值用 Python float（新仓库放弃 Fixed 确定性，见 §10）。
仅保留 M0 闭环所需字段；M1+ 字段（splash/projectile/footprint 等）留给后续 Phase。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Optional


class Attribute(str, Enum):
    """SC2 单位属性标签。"""
    LIGHT = "light"
    ARMORED = "armored"
    BIOLOGICAL = "biological"
    MECHANICAL = "mechanical"
    PSIONIC = "psionic"
    MASSIVE = "massive"
    STRUCTURE = "structure"
    HEROIC = "heroic"
    DETECTOR = "detector"


class TargetFilter(str, Enum):
    """武器目标过滤。"""
    GROUND = "ground"
    AIR = "air"
    STRUCTURE = "structure"


class DamageType(str, Enum):
    """伤害类型（影响属性加成，Phase 3 combat 实现）。"""
    NORMAL = "normal"
    CONCUSSIVE = "concussive"
    EXPLOSIVE = "explosive"


@dataclass(frozen=True)
class WeaponType:
    """武器定义（Phase 2 只加载数据，Phase 3 combat 使用）。"""
    id: str
    damage: float
    attacks: int = 1
    range: float = 1.0
    min_range: float = 0.0
    period: int = 22
    damage_point: int = 0
    backswing: int = 0
    damage_type: DamageType = DamageType.NORMAL
    target_filters: frozenset[TargetFilter] = frozenset({TargetFilter.GROUND})

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_filters", frozenset(self.target_filters))


@dataclass(frozen=True)
class UnitType:
    """单位类型定义（Phase 2 最小字段集）。"""
    id: str
    race: str
    attributes: frozenset[Attribute]
    max_health: float
    max_shields: float = 0.0
    max_energy: float = 0.0
    armor: float = 0.0
    radius: float = 1.0
    speed: float = 0.0
    sight: float = 8.0
    minerals: int = 0
    vespene: int = 0
    supply: int = 0
    build_time: int = 0
    weapon_ground: Optional[WeaponType] = None
    weapon_air: Optional[WeaponType] = None
    is_flying: bool = False
    is_structure: bool = False
    is_worker: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", frozenset(self.attributes))