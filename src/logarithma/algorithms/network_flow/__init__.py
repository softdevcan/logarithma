"""
Network Flow Algorithms
=======================

Maximum flow algorithms:
  - max_flow : Edmonds-Karp algorithm (O(V * E^2))
"""

from .max_flow import max_flow

__all__ = ['max_flow']
