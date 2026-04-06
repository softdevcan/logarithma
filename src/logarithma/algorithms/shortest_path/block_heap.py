"""
BlockHeap — Lemma 3.3 Data Structure
======================================

Two-sequence block-linked-list data structure from Lemma 3.3 of:
    Duan, Mao, Mao, Shu, Yin (2025)
    "Breaking the Sorting Barrier for Directed Single-Source Shortest Paths"
    arXiv:2504.17033v2

Supports three operations:

    Insert(key, value)       amortized O(max{1, log(N/M)})
    BatchPrepend(L pairs)    amortized O(L * max{1, log(L/M)}) total
    Pull()                   amortized O(|S'|) where |S'| ≤ M

Internal structure:
    D0  — elements from BatchPrepend only.
          Ordered list of blocks; blocks prepended to front.
    D1  — elements from Insert only.
          Ordered list of blocks by upper_bound; binary search for Insert.
          Each block has an upper_bound; a new block is created only when
          the block splits.

Both sequences maintain sorted order: elements in earlier blocks are no
larger than elements in later blocks.
"""

from __future__ import annotations

import bisect
import math
from typing import Any, Dict, List, Optional, Tuple

Node = Any
Dist = float


# ---------------------------------------------------------------------------
# Internal: Block
# ---------------------------------------------------------------------------

class _Block:
    """A single block holding key/value pairs.

    Items are stored as a list of (value, key) tuples.
    upper_bound: maximum value any element in this block may have.
    """

    __slots__ = ('items', 'upper_bound')

    def __init__(self, items: List[Tuple[Dist, Node]], upper_bound: Dist):
        self.items = items          # list of (value, key), NOT necessarily sorted
        self.upper_bound = upper_bound

    def __len__(self) -> int:
        return len(self.items)


# ---------------------------------------------------------------------------
# D0: BatchPrepend sequence
# ---------------------------------------------------------------------------

class _D0:
    """Block list for BatchPrepend elements.  Blocks are prepended to front."""

    def __init__(self) -> None:
        self._blocks: List[_Block] = []
        self._size: int = 0

    def prepend_blocks(self, new_blocks: List[_Block]) -> None:
        self._blocks = new_blocks + self._blocks
        for b in new_blocks:
            self._size += len(b)

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size

    def pop_front_block(self) -> Optional[_Block]:
        while self._blocks:
            b = self._blocks.pop(0)
            if b.items:
                self._size -= len(b)
                return b
        return None

    def peek_front_upper_bound(self) -> Dist:
        for b in self._blocks:
            if b.items:
                return b.upper_bound
        return float('inf')

    def min_value(self) -> Dist:
        best = float('inf')
        for b in self._blocks:
            for v, _ in b.items:
                if v < best:
                    best = v
        return best


# ---------------------------------------------------------------------------
# D1: Insert sequence
# ---------------------------------------------------------------------------

class _D1:
    """Block list for Insert elements.

    Blocks are kept in ascending order of upper_bound.
    Binary search on upper_bounds to locate the right block for Insert.

    Invariant: _ubs[i] == _blocks[i].upper_bound for all i.
    """

    def __init__(self, B: Dist, M: int) -> None:
        self._B = B
        self._M = M
        # Always maintain at least one sentinel block with ub=B so that
        # Insert always finds a valid block.
        self._blocks: List[_Block] = [_Block([], B)]
        self._ubs: List[Dist] = [B]        # parallel list of upper_bounds for bisect
        self._size: int = 0
        # key → _Block pointer for O(1) delete (Lemma 3.3 linked-list delete)
        self._key_block: Dict[Node, _Block] = {}

    def _find_block_idx(self, value: Dist) -> int:
        """Index of the first block with upper_bound >= value."""
        idx = bisect.bisect_left(self._ubs, value)
        if idx >= len(self._blocks):
            idx = len(self._blocks) - 1
        return idx

    def insert(self, key: Node, value: Dist, key_map: Dict[Node, Dist]) -> None:
        """Insert (key, value).  Keeps minimum value per key."""
        old_val = key_map.get(key)
        if old_val is not None and old_val <= value:
            return

        if old_val is not None:
            self._delete_key(key, old_val)

        idx = self._find_block_idx(value)
        block = self._blocks[idx]
        block.items.append((value, key))
        self._size += 1
        key_map[key] = value
        self._key_block[key] = block

        if len(block) > self._M:
            self._split(idx)

    def _delete_key(self, key: Node, value: Dist) -> None:
        """Remove (key, value) from its block — O(block_size) via key_block pointer."""
        block = self._key_block.pop(key, None)
        if block is None:
            return
        for i, (v, k) in enumerate(block.items):
            if k == key and v == value:
                block.items.pop(i)
                self._size -= 1
                # Remove empty block, but keep at least one sentinel
                if len(block) == 0 and len(self._blocks) > 1:
                    self._remove_block(block)
                return

    def _remove_block(self, block: _Block) -> None:
        idx = self._blocks.index(block)
        self._blocks.pop(idx)
        self._ubs.pop(idx)

    def _split(self, idx: int) -> None:
        """Split block at idx into two halves."""
        block = self._blocks[idx]
        block.items.sort()
        mid = len(block.items) // 2
        left_items = block.items[:mid]
        right_items = block.items[mid:]

        left_ub = left_items[-1][0] if left_items else block.upper_bound
        left_block = _Block(left_items, left_ub)
        right_block = _Block(right_items, block.upper_bound)

        self._blocks[idx:idx + 1] = [left_block, right_block]
        self._ubs[idx:idx + 1] = [left_ub, block.upper_bound]

        # Update key_block pointers for all items that moved to new blocks
        for _, k in left_items:
            self._key_block[k] = left_block
        for _, k in right_items:
            self._key_block[k] = right_block

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size

    def pop_front_block(self) -> Optional[_Block]:
        """Remove and return the first non-empty block."""
        for i, b in enumerate(self._blocks):
            if b.items:
                self._blocks.pop(i)
                self._ubs.pop(i)
                self._size -= len(b)
                # Ensure sentinel remains
                if not self._blocks:
                    self._blocks.append(_Block([], self._B))
                    self._ubs.append(self._B)
                # Clear key_block pointers for removed items
                for _, k in b.items:
                    self._key_block.pop(k, None)
                return b
        return None

    def peek_front_upper_bound(self) -> Dist:
        for b in self._blocks:
            if b.items:
                return b.upper_bound
        return float('inf')

    def min_value(self) -> Dist:
        best = float('inf')
        for b in self._blocks:
            for v, _ in b.items:
                if v < best:
                    best = v
        return best


# ---------------------------------------------------------------------------
# BlockHeap: the public Lemma 3.3 data structure
# ---------------------------------------------------------------------------

class BlockHeap:
    """Block-based data structure from Lemma 3.3 (Duan et al., 2025).

    Supports Insert, BatchPrepend, and Pull in amortized O(log(N/M)) time.

    Args:
        M: Block size parameter (= 2^{(l-1)*t} at recursion level l).
        B: Upper bound on all values (global distance bound).
    """

    def __init__(self, M: int, B: Dist) -> None:
        self._M = max(1, M)
        self._B = B
        self._d0 = _D0()
        self._d1 = _D1(B, self._M)
        # key_map: key → best value seen so far (for O(1) duplicate check)
        self._key_map: Dict[Node, Dist] = {}

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, key: Node, value: Dist) -> None:
        """Insert (key, value) into D1.  Keeps minimum value per key."""
        self._d1.insert(key, value, self._key_map)

    # ------------------------------------------------------------------
    # BatchPrepend
    # ------------------------------------------------------------------

    def batch_prepend(self, pairs) -> None:
        """Prepend L pairs whose values are smaller than all current values.

        For duplicate keys, only the minimum value is retained.
        Time: O(L * max{1, log(L/M)}) total.
        """
        # Deduplicate within the batch and against key_map
        batch: Dict[Node, Dist] = {}
        for key, value in pairs:
            existing = self._key_map.get(key)
            if existing is not None and existing <= value:
                continue
            if key in batch:
                if value < batch[key]:
                    batch[key] = value
            else:
                batch[key] = value

        if not batch:
            return

        # Remove keys present in D1 with higher values
        for key, value in batch.items():
            old = self._key_map.get(key)
            if old is not None and old > value:
                self._d1._delete_key(key, old)
            self._key_map[key] = value

        # Build sorted list and partition into blocks of size ceil(M/2)
        items = sorted((v, k) for k, v in batch.items())
        L = len(items)
        M = self._M

        if L <= M:
            ub = items[-1][0] if items else self._B
            new_blocks = [_Block(items, ub)]
        else:
            block_size = max(1, math.ceil(M / 2))
            new_blocks = []
            for start in range(0, L, block_size):
                chunk = items[start:start + block_size]
                ub = chunk[-1][0]
                new_blocks.append(_Block(chunk, ub))

        self._d0.prepend_blocks(new_blocks)

    # ------------------------------------------------------------------
    # Pull
    # ------------------------------------------------------------------

    def pull(self, M: Optional[int] = None) -> Tuple[Dict[Node, Dist], Dist]:
        """Return ≤ M key/value pairs with the smallest values, and separator x.

        Returns:
            (subset, x) where subset contains up to M smallest-valued pairs,
            and x separates subset from remaining elements (or B if empty).
        """
        m = M if M is not None else self._M

        collected_items: List[Tuple[Dist, Node]] = []

        # Collect whole blocks until we have > m elements or both empty
        while len(collected_items) <= m:
            d0_empty = self._d0.is_empty()
            d1_empty = self._d1.is_empty()

            if d0_empty and d1_empty:
                break

            ub0 = self._d0.peek_front_upper_bound() if not d0_empty else float('inf')
            ub1 = self._d1.peek_front_upper_bound() if not d1_empty else float('inf')

            if ub0 <= ub1 and not d0_empty:
                blk = self._d0.pop_front_block()
            elif not d1_empty:
                blk = self._d1.pop_front_block()
            else:
                break

            if blk is None:
                break
            collected_items.extend(blk.items)

        if not collected_items:
            return {}, self._B

        collected_items.sort()

        if len(collected_items) <= m:
            result: Dict[Node, Dist] = {}
            for v, k in collected_items:
                if k not in result or v < result[k]:
                    result[k] = v
            for k in result:
                self._key_map.pop(k, None)
            separator = self._B
            if not self.is_empty():
                separator = self._min_remaining()
            return result, separator
        else:
            take = collected_items[:m]
            rest = collected_items[m:]
            separator = rest[0][0]

            # Put rest back into D0 (they're smaller than existing D0 front)
            ub = rest[-1][0]
            self._d0.prepend_blocks([_Block(rest, ub)])
            for v, k in rest:
                if k not in self._key_map or v < self._key_map[k]:
                    self._key_map[k] = v

            result = {}
            for v, k in take:
                if k not in result or v < result[k]:
                    result[k] = v
            for k in result:
                self._key_map.pop(k, None)

            return result, separator

    def _min_remaining(self) -> Dist:
        v0 = self._d0.min_value()
        v1 = self._d1.min_value()
        return min(v0, v1)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        return self._d0.is_empty() and self._d1.is_empty()

    def __len__(self) -> int:
        return len(self._d0) + len(self._d1)
