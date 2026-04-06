# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""
BlockHeap — Lemma 3.3 Data Structure (Cython)
==============================================

Cython port of block_heap.py.  Integer node IDs throughout;
dist values are C doubles.

Compared to the pure-Python version the main gains are:
  - cdef class attribute access (no Python dict lookup)
  - C-level arithmetic for double comparisons
  - cpdef methods called without Python overhead from Cython callers
"""

import bisect
import math

from libc.math cimport HUGE_VAL

cdef double _INF = HUGE_VAL


# ---------------------------------------------------------------------------
# _Block
# ---------------------------------------------------------------------------

cdef class _Block:
    cdef public list items
    cdef public double upper_bound

    def __cinit__(self, list items, double upper_bound):
        self.items = items
        self.upper_bound = upper_bound

    def __len__(self):
        return len(self.items)


# ---------------------------------------------------------------------------
# _D0
# ---------------------------------------------------------------------------

cdef class _D0:
    cdef list _blocks
    cdef Py_ssize_t _size

    def __cinit__(self):
        self._blocks = []
        self._size = 0

    cpdef void prepend_blocks(self, list new_blocks):
        cdef _Block b
        self._blocks = new_blocks + self._blocks
        for b in new_blocks:
            self._size += len(b.items)

    cpdef bint is_empty(self):
        return self._size == 0

    def __len__(self):
        return self._size

    cpdef _Block pop_front_block(self):
        cdef _Block b
        while self._blocks:
            b = self._blocks.pop(0)
            if b.items:
                self._size -= len(b.items)
                return b
        return None

    cpdef double peek_front_upper_bound(self):
        cdef _Block b
        for b in self._blocks:
            if b.items:
                return b.upper_bound
        return _INF

    cpdef double min_value(self):
        cdef double best = _INF
        cdef double v
        cdef _Block b
        for b in self._blocks:
            for item in b.items:
                v = <double>item[0]
                if v < best:
                    best = v
        return best


# ---------------------------------------------------------------------------
# _D1
# ---------------------------------------------------------------------------

cdef class _D1:
    cdef double _B
    cdef Py_ssize_t _M
    cdef list _blocks
    cdef list _ubs
    cdef Py_ssize_t _size
    cdef dict _key_block

    def __cinit__(self, double B, Py_ssize_t M):
        self._B = B
        self._M = M
        self._blocks = [_Block([], B)]
        self._ubs = [B]
        self._size = 0
        self._key_block = {}

    cdef Py_ssize_t _find_block_idx(self, double value):
        cdef Py_ssize_t idx = bisect.bisect_left(self._ubs, value)
        if idx >= len(self._blocks):
            idx = len(self._blocks) - 1
        return idx

    cpdef void insert(self, object key, double value, dict key_map):
        cdef double old_val
        cdef Py_ssize_t idx
        cdef _Block block
        cdef object old_val_obj

        old_val_obj = key_map.get(key)
        if old_val_obj is not None:
            old_val = <double>old_val_obj
            if old_val <= value:
                return
            self._delete_key(key, old_val)

        idx = self._find_block_idx(value)
        block = <_Block>self._blocks[idx]
        block.items.append((value, key))
        self._size += 1
        key_map[key] = value
        self._key_block[key] = block

        if len(block.items) > self._M:
            self._split(idx)

    cdef void _delete_key(self, object key, double value):
        cdef _Block block
        cdef Py_ssize_t i
        cdef object item

        block = <_Block>self._key_block.pop(key, None)
        if block is None:
            return
        for i in range(len(block.items)):
            item = block.items[i]
            if item[1] == key and item[0] == value:
                block.items.pop(i)
                self._size -= 1
                if len(block.items) == 0 and len(self._blocks) > 1:
                    self._remove_block(block)
                return

    cdef void _remove_block(self, _Block block):
        cdef Py_ssize_t idx = self._blocks.index(block)
        self._blocks.pop(idx)
        self._ubs.pop(idx)

    cdef void _split(self, Py_ssize_t idx):
        cdef _Block block, left_block, right_block
        cdef Py_ssize_t mid
        cdef double left_ub
        cdef list left_items, right_items
        cdef object item

        block = <_Block>self._blocks[idx]
        block.items.sort()
        mid = len(block.items) // 2
        left_items = block.items[:mid]
        right_items = block.items[mid:]

        left_ub = <double>left_items[-1][0] if left_items else block.upper_bound
        left_block = _Block(left_items, left_ub)
        right_block = _Block(right_items, block.upper_bound)

        self._blocks[idx:idx + 1] = [left_block, right_block]
        self._ubs[idx:idx + 1] = [left_ub, block.upper_bound]

        for item in left_items:
            self._key_block[item[1]] = left_block
        for item in right_items:
            self._key_block[item[1]] = right_block

    cpdef bint is_empty(self):
        return self._size == 0

    def __len__(self):
        return self._size

    cpdef _Block pop_front_block(self):
        cdef _Block b
        cdef Py_ssize_t i

        for i in range(len(self._blocks)):
            b = <_Block>self._blocks[i]
            if b.items:
                self._blocks.pop(i)
                self._ubs.pop(i)
                self._size -= len(b.items)
                if not self._blocks:
                    self._blocks.append(_Block([], self._B))
                    self._ubs.append(self._B)
                for item in b.items:
                    self._key_block.pop(item[1], None)
                return b
        return None

    cpdef double peek_front_upper_bound(self):
        cdef _Block b
        for b in self._blocks:
            if b.items:
                return b.upper_bound
        return _INF

    cpdef double min_value(self):
        cdef double best = _INF
        cdef double v
        cdef _Block b
        for b in self._blocks:
            for item in b.items:
                v = <double>item[0]
                if v < best:
                    best = v
        return best


# ---------------------------------------------------------------------------
# BlockHeap
# ---------------------------------------------------------------------------

cdef class BlockHeap:
    """Block-based data structure from Lemma 3.3 (Cython version)."""

    cdef Py_ssize_t _M
    cdef double _B
    cdef _D0 _d0
    cdef _D1 _d1
    cdef dict _key_map

    def __cinit__(self, Py_ssize_t M, double B):
        self._M = max(1, M)
        self._B = B
        self._d0 = _D0()
        self._d1 = _D1(B, self._M)
        self._key_map = {}

    cpdef void insert(self, object key, double value):
        self._d1.insert(key, value, self._key_map)

    def batch_prepend(self, list pairs):
        # Use def (not cpdef) to avoid closure restriction in Cython
        cdef dict batch = {}
        cdef double value, old_val, existing_val
        cdef object key, existing_obj, old_obj
        cdef list items, new_blocks, chunk
        cdef Py_ssize_t L, M_sz, block_size, start
        cdef double ub

        for pair in pairs:
            key = pair[0]
            value = <double>pair[1]
            existing_obj = self._key_map.get(key)
            if existing_obj is not None:
                existing_val = <double>existing_obj
                if existing_val <= value:
                    continue
            if key in batch:
                if value < <double>batch[key]:
                    batch[key] = value
            else:
                batch[key] = value

        if not batch:
            return

        for key in batch:
            value = <double>batch[key]
            old_obj = self._key_map.get(key)
            if old_obj is not None:
                old_val = <double>old_obj
                if old_val > value:
                    self._d1._delete_key(key, old_val)
            self._key_map[key] = value

        # Build sorted list — (value, key) pairs
        items = sorted((<double>v, k) for k, v in batch.items())
        L = len(items)
        M_sz = self._M

        new_blocks = []
        if L <= M_sz:
            ub = <double>items[-1][0] if items else self._B
            new_blocks = [_Block(items, ub)]
        else:
            block_size = max(1, (M_sz + 1) // 2)
            for start in range(0, L, block_size):
                chunk = items[start:start + block_size]
                ub = <double>chunk[-1][0]
                new_blocks.append(_Block(chunk, ub))

        self._d0.prepend_blocks(new_blocks)

    def pull(self, Py_ssize_t M):
        cdef list collected_items = []
        cdef _Block blk
        cdef double ub0, ub1, separator, v_val
        cdef bint d0_empty, d1_empty
        cdef Py_ssize_t n_collected
        cdef dict result
        cdef object k
        cdef list take, rest

        while len(collected_items) <= M:
            d0_empty = self._d0.is_empty()
            d1_empty = self._d1.is_empty()

            if d0_empty and d1_empty:
                break

            ub0 = self._d0.peek_front_upper_bound() if not d0_empty else _INF
            ub1 = self._d1.peek_front_upper_bound() if not d1_empty else _INF

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
        n_collected = len(collected_items)

        if n_collected <= M:
            result = {}
            for item in collected_items:
                k = item[1]
                v_val = <double>item[0]
                if k not in result or v_val < <double>result[k]:
                    result[k] = v_val
            for k in result:
                self._key_map.pop(k, None)
            separator = self._B
            if not self.is_empty():
                separator = self._min_remaining()
            return result, separator
        else:
            take = collected_items[:M]
            rest = collected_items[M:]
            separator = <double>rest[0][0]

            ub0 = <double>rest[-1][0]
            self._d0.prepend_blocks([_Block(rest, ub0)])
            for item in rest:
                k = item[1]
                v_val = <double>item[0]
                if k not in self._key_map or v_val < <double>self._key_map[k]:
                    self._key_map[k] = v_val

            result = {}
            for item in take:
                k = item[1]
                v_val = <double>item[0]
                if k not in result or v_val < <double>result[k]:
                    result[k] = v_val
            for k in result:
                self._key_map.pop(k, None)

            return result, separator

    cdef double _min_remaining(self):
        cdef double v0 = self._d0.min_value()
        cdef double v1 = self._d1.min_value()
        return v0 if v0 < v1 else v1

    cpdef bint is_empty(self):
        return self._d0.is_empty() and self._d1.is_empty()

    def __len__(self):
        return len(self._d0) + len(self._d1)
