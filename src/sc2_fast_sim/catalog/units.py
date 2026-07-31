"""M0 标准单位定义：Marine / Zergling。

数值来源：旧仓库 sc2-ally-bot catalog/model.py（M0 标准内容）。
"""

from __future__ import annotations

from .model import Attribute, ArmorClass, DamageType, TargetFilter, UnitType, WeaponType


MARINE = UnitType(
    id="Marine",
    race="terran",
    attributes=frozenset({Attribute.LIGHT, Attribute.BIOLOGICAL}),
    max_health=45.0,
    armor=0.0,
    radius=0.375,
    speed=2.25,
    sight=8.0,
    minerals=50,
    supply=1,
    build_time=18,
    weapon_ground=WeaponType(
        id="Marine.GaussRifle",
        damage=5.0,
        attacks=1,
        range=5.0,
        period=19,
        damage_type=DamageType.NORMAL,
        target_filters=frozenset({TargetFilter.GROUND, TargetFilter.AIR}),
        versus={ArmorClass.LIGHT: 100, ArmorClass.ARMORED: 100, ArmorClass.BIOLOGICAL: 100},
    ),
    weapon_air=None,
    armor_class=ArmorClass.LIGHT,
)


ZERGLING = UnitType(
    id="Zergling",
    race="zerg",
    attributes=frozenset({Attribute.LIGHT, Attribute.BIOLOGICAL}),
    max_health=35.0,
    armor=0.0,
    radius=0.375,
    speed=2.75,
    sight=8.0,
    minerals=50,
    supply=0,
    build_time=17,
    weapon_ground=WeaponType(
        id="Zergling.Attack",
        damage=5.0,
        attacks=1,
        range=0.1,
        period=16,
        damage_type=DamageType.NORMAL,
        target_filters=frozenset({TargetFilter.GROUND}),
        versus={ArmorClass.LIGHT: 100, ArmorClass.ARMORED: 100, ArmorClass.BIOLOGICAL: 100},
    ),
    weapon_air=None,
    armor_class=ArmorClass.LIGHT,
)


CATALOG: dict[str, UnitType] = {
    "Marine": MARINE,
    "Zergling": ZERGLING,
}


def get_unit_type(unit_id: str) -> UnitType:
    """按 id 查单位类型，不存在则 KeyError。"""
    if unit_id not in CATALOG:
        raise KeyError(f"Catalog 中无单位 '{unit_id}'")
    return CATALOG[unit_id]