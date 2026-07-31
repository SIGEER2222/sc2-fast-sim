"""ECS Archetype：同组件组合的连续 SoA 存储。

设计依据：sc2-fast-sim-design.md §3.3。
- columns: 每组件一个 numpy structured array（按 row 连续）
- entity_ids: row → entity_id 映射
- swap-remove 保证 O(1) 删除且数组紧凑
"""

from __future__ import annotations

import numpy as np

from .component import Component


class Archetype:
    """组件组合签名 + 连续列存储。

    同一 archetype 内所有实体拥有相同组件集合；
    每个组件单独一个 numpy structured array，按 row 连续排列。
    """

    def __init__(self, component_types, capacity: int = 16):
        self.component_types = frozenset(component_types)
        self.capacity = capacity
        self.size = 0
        self.columns: dict[type[Component], np.ndarray] = {}
        for ct in self.component_types:
            self.columns[ct] = np.zeros(capacity, dtype=ct._dtype)
        self.entity_ids = np.zeros(capacity, dtype=np.int64)

    def add_row(self, entity_id: int, components: dict[type[Component], Component]) -> int:
        """追加一行，返回 row index。

        components: {ComponentType: Component_instance}，必须覆盖 self.component_types 全部。
        """
        if self.size >= self.capacity:
            self._grow()
        idx = self.size
        self.entity_ids[idx] = entity_id
        for ct, val in components.items():
            col = self.columns[ct]
            col[idx] = tuple(getattr(val, name) for name in ct._dtype.names)
        self.size += 1
        return idx

    def remove_row(self, row: int) -> None:
        """swap-remove：把最后一行搬到 row 位置，size -= 1。O(1)。"""
        last = self.size - 1
        if row != last:
            for col in self.columns.values():
                col[row] = col[last]
            self.entity_ids[row] = self.entity_ids[last]
        self.size -= 1

    def get(self, component_type: type[Component]) -> np.ndarray:
        """返回该组件列的 live view（零拷贝）。长度 = self.size。"""
        return self.columns[component_type][: self.size]

    def set(self, component_type: type[Component], values: np.ndarray) -> None:
        """把外部数组拷贝到该组件列存储。values 长度必须 == self.size。"""
        if len(values) != self.size:
            raise ValueError(
                f"set: values length {len(values)} != size {self.size}"
            )
        self.columns[component_type][: self.size] = values

    def read_row(self, row: int) -> dict[type[Component], Component]:
        """读取一行，返回 {ComponentType: Component_instance}。用于 archetype 迁移。"""
        out = {}
        for ct, col in self.columns.items():
            vals = {name: col[name][row] for name in ct._dtype.names}
            out[ct] = ct(**vals)
        return out

    def _grow(self) -> None:
        new_cap = max(int(self.capacity * 1.5), self.capacity + 1)
        for ct, col in self.columns.items():
            self.columns[ct] = np.resize(col, new_cap)
        self.entity_ids = np.resize(self.entity_ids, new_cap)
        self.capacity = new_cap
