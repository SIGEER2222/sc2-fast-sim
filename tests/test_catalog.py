import pytest
from sc2_fast_sim.catalog.model import (
    Attribute, DamageType, TargetFilter, WeaponType, UnitType,
)
from sc2_fast_sim.catalog.units import MARINE, ZERGLING, CATALOG, get_unit_type


def test_marine_basic_fields():
    assert MARINE.id == "Marine"
    assert MARINE.race == "terran"
    assert Attribute.LIGHT in MARINE.attributes
    assert Attribute.BIOLOGICAL in MARINE.attributes
    assert MARINE.max_health == 45.0
    assert MARINE.armor == 0.0
    assert MARINE.radius == 0.375
    assert MARINE.speed == 2.25
    assert MARINE.sight == 8.0
    assert MARINE.minerals == 50
    assert MARINE.supply == 1
    assert MARINE.build_time == 18


def test_marine_weapon_ground():
    w = MARINE.weapon_ground
    assert w is not None
    assert w.id == "Marine.GaussRifle"
    assert w.damage == 5.0
    assert w.attacks == 1
    assert w.range == 5.0
    assert w.period == 19
    assert w.damage_type == DamageType.NORMAL
    assert TargetFilter.GROUND in w.target_filters
    assert TargetFilter.AIR in w.target_filters


def test_marine_weapon_air_is_none():
    assert MARINE.weapon_air is None


def test_zergling_basic_fields():
    assert ZERGLING.id == "Zergling"
    assert ZERGLING.race == "zerg"
    assert ZERGLING.max_health == 35.0
    assert ZERGLING.speed == 2.75
    assert ZERGLING.supply == 0


def test_zergling_weapon_range_is_melee():
    w = ZERGLING.weapon_ground
    assert w is not None
    assert w.range == 0.1
    assert w.damage_type == DamageType.NORMAL
    assert TargetFilter.GROUND in w.target_filters


def test_catalog_dict_contains_marine_and_zergling():
    assert "Marine" in CATALOG
    assert "Zergling" in CATALOG
    assert CATALOG["Marine"] is MARINE
    assert CATALOG["Zergling"] is ZERGLING


def test_get_unit_type_returns_unit():
    u = get_unit_type("Marine")
    assert u is MARINE


def test_get_unit_type_raises_keyerror_for_unknown():
    with pytest.raises(KeyError):
        get_unit_type("Nonexistent")


def test_unit_type_is_frozen():
    with pytest.raises(Exception):
        MARINE.max_health = 999.0  # frozen dataclass 不可变