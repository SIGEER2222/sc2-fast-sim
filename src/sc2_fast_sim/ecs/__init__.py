"""ECS 核心：Component / Archetype / World。"""

from .component import Component, component
from .archetype import Archetype
from .world import World

__all__ = ["Component", "component", "Archetype", "World"]
