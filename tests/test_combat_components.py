import numpy as np
import pytest
from sc2_fast_sim.components.combat import Combat, Movement
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.catalog.model import WeaponType, UnitType, ArmorClass, DamageType, TargetFilter
from sc2_fast_sim.catalog.units import MARINE, ZERGLING


def test_combat_component_dtype():
    fields = Combat._dtype.names
    assert "weapon_damage" in fields
    assert "weapon_attacks" in fields
    assert "weapon_range" in fields
    assert "weapon_period" in fields
    assert "weapon_cooldown" in fields
    assert "target_id" in fields
    assert "versus_light" in fields
    assert "versus_armored" in fields
    assert "versus_biological" in fields
    assert "armor_class" in fields


def test_movement_component_dtype():
    fields = Movement._dtype.names
    assert "speed" in fields
    assert "facing" in fields
    assert "turn_speed" in fields
    assert "move_target_x" in fields
    assert "move_target_y" in fields
    assert "has_move_target" in fields


def test_marine_has_versus_table():
    assert MARINE.weapon_ground is not None
    w = MARINE.weapon_ground
    assert w.versus == {ArmorClass.LIGHT: 100, ArmorClass.ARMORED: 100, ArmorClass.BIOLOGICAL: 100}


def test_marine_has_armor_class():
    assert MARINE.armor_class == ArmorClass.LIGHT


def test_zergling_has_armor_class():
    assert ZERGLING.armor_class == ArmorClass.LIGHT


def test_weapon_type_has_burst_fields():
    w = MARINE.weapon_ground
    assert w.burst == 1
    assert w.burst_delay == 0


def test_combat_component_instantiates():
    c = Combat(
        weapon_damage=5.0,
        weapon_attacks=1,
        weapon_range=5.0,
        weapon_period=19,
        weapon_cooldown=0,
        target_id=0,
        versus_light=100,
        versus_armored=100,
        versus_biological=100,
        armor_class=0,
    )
    assert c.weapon_damage == 5.0
    assert c.weapon_range == 5.0
