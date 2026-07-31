"""ECS World：archetype 注册表 + entity 索引。

设计依据：sc2-fast-sim-design.md §3.4。
- create_entity 找/建匹配 archetype，append，返回 entity_id
- destroy_entity swap-remove，更新 entity_index（含被 swap 的实体）
- query 返回所有包含 required 组件的 archetype 迭代器
"""

from __future__ import annotations

from typing import Iterator

from .archetype import Archetype
from .component import Component


class World:
    def __init__(self):
        self.archetypes: dict[frozenset, Archetype] = {}
        self.entity_index: dict[int, tuple[Archetype, int]] = {}
        self.next_entity_id: int = 1

    def create_entity(self, *components: Component) -> int:
        sig = frozenset(type(c) for c in components)
        arch = self.archetypes.get(sig)
        if arch is None:
            arch = Archetype(sig)
            self.archetypes[sig] = arch
        eid = self.next_entity_id
        self.next_entity_id += 1
        values = {type(c): c for c in components}
        row = arch.add_row(eid, values)
        self.entity_index[eid] = (arch, row)
        return eid

    def destroy_entity(self, entity_id: int) -> None:
        arch, row = self.entity_index.pop(entity_id)
        last = arch.size - 1
        arch.remove_row(row)
        # 如果被 swap 的是另一个实体（row != last），更新它的 index
        if row != last:
            moved_id = arch.entity_ids[row]
            self.entity_index[moved_id] = (arch, row)

    def query(self, required: set[type[Component]]) -> Iterator[Archetype]:
        required_fs = frozenset(required)
        for sig, arch in self.archetypes.items():
            if required_fs.issubset(sig):
                yield arch

    def add_component(self, entity_id: int, component: Component) -> None:
        """给实体添加组件 → 迁移到新 archetype（数据搬移）。"""
        arch, row = self.entity_index.pop(entity_id)
        # 读出当前所有组件实例
        current = arch.read_row(row)
        # 从旧 archetype swap-remove（更新被 swap 实体的 index）
        last = arch.size - 1
        arch.remove_row(row)
        if row != last:
            moved_id = arch.entity_ids[row]
            self.entity_index[moved_id] = (arch, row)
        # 加入新组件，构造新签名
        new_type = type(component)
        current[new_type] = component
        new_sig = frozenset(current.keys())
        new_arch = self.archetypes.get(new_sig)
        if new_arch is None:
            new_arch = Archetype(new_sig)
            self.archetypes[new_sig] = new_arch
        new_row = new_arch.add_row(entity_id, current)
        self.entity_index[entity_id] = (new_arch, new_row)

    def remove_component(self, entity_id: int, component_type: type[Component]) -> None:
        """从实体移除组件 → 迁移到新 archetype（数据搬移）。"""
        arch, row = self.entity_index.pop(entity_id)
        current = arch.read_row(row)
        del current[component_type]
        last = arch.size - 1
        arch.remove_row(row)
        if row != last:
            moved_id = arch.entity_ids[row]
            self.entity_index[moved_id] = (arch, row)
        new_sig = frozenset(current.keys())
        new_arch = self.archetypes.get(new_sig)
        if new_arch is None:
            new_arch = Archetype(new_sig)
            self.archetypes[new_sig] = new_arch
        new_row = new_arch.add_row(entity_id, current)
        self.entity_index[entity_id] = (new_arch, new_row)