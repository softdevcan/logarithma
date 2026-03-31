"""
Logarithma Exceptions and Validation
======================================

Centralized error handling for all graph algorithms.
Provides consistent, descriptive error messages across the library.
"""

from typing import Any, List, Optional, Union

import networkx as nx


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class GraphError(Exception):
    """Base exception for all logarithma graph errors."""
    pass


class EmptyGraphError(GraphError, ValueError):
    """Raised when an algorithm receives an empty graph."""

    def __init__(self, algorithm: str):
        self.algorithm = algorithm
        super().__init__(
            f"The graph is empty (has no nodes). "
            f"'{algorithm}' requires a graph with at least one node."
        )


class NodeNotFoundError(GraphError, ValueError):
    """Raised when a specified node does not exist in the graph."""

    def __init__(self, node: Any, role: str, graph_nodes_count: int):
        self.node = node
        self.role = role
        super().__init__(
            f"{role.capitalize()} vertex '{node}' not found in graph. "
            f"The graph has {graph_nodes_count} nodes. "
            f"Make sure the vertex exists before calling the algorithm."
        )


class NegativeWeightError(GraphError, ValueError):
    """Raised when a negative edge weight is found in an algorithm that
    requires non-negative weights."""

    def __init__(self, u: Any, v: Any, weight: float, algorithm: str):
        self.u = u
        self.v = v
        self.weight = weight
        self.algorithm = algorithm
        super().__init__(
            f"Negative edge weight detected: '{u}' -> '{v}' (weight={weight}). "
            f"'{algorithm}' requires non-negative edge weights. "
            f"Use bellman_ford() for graphs with negative weights."
        )


class NegativeCycleError(GraphError, ValueError):
    """Raised when a negative-weight cycle reachable from the source is detected.

    Attributes:
        cycle: List of nodes forming the detected negative cycle, or None if
               the exact cycle could not be reconstructed.
    """

    def __init__(self, source: Any, cycle: Optional[List[Any]] = None):
        self.source = source
        self.cycle = cycle
        cycle_str = f" Cycle: {' -> '.join(str(n) for n in cycle)}." if cycle else ""
        super().__init__(
            f"Negative-weight cycle detected reachable from source '{source}'.{cycle_str} "
            f"No finite shortest path exists when a negative cycle is reachable."
        )


class InvalidModeError(GraphError, ValueError):
    """Raised when an invalid algorithm mode/option is specified."""

    def __init__(self, mode: str, valid_modes: List[str], parameter: str = "mode"):
        self.mode = mode
        self.valid_modes = valid_modes
        options = ", ".join(f"'{m}'" for m in valid_modes)
        super().__init__(
            f"Invalid {parameter} '{mode}'. Valid options are: {options}."
        )


class NotDAGError(GraphError, ValueError):
    """Raised when topological sort is called on a graph that is not a DAG.

    Attributes:
        algorithm: Name of the algorithm that detected the cycle.
        cycle: List of nodes forming the detected cycle, or None if the exact
               cycle could not be reconstructed.
    """

    def __init__(self, algorithm: str, cycle: Optional[List[Any]] = None):
        self.algorithm = algorithm
        self.cycle = cycle
        cycle_str = (
            f" Detected cycle: {' -> '.join(str(n) for n in cycle)}."
            if cycle else ""
        )
        super().__init__(
            f"'{algorithm}' requires a Directed Acyclic Graph (DAG). "
            f"The graph contains at least one cycle.{cycle_str} "
            f"Use detect_cycle() to find cycles before calling this algorithm."
        )


class UndirectedGraphRequiredError(GraphError, TypeError):
    """Raised when an algorithm requires an undirected graph but a directed
    graph is given.

    Attributes:
        algorithm: Name of the algorithm that requires an undirected graph.
    """

    def __init__(self, algorithm: str):
        self.algorithm = algorithm
        super().__init__(
            f"'{algorithm}' requires an undirected graph (nx.Graph). "
            f"A directed graph (nx.DiGraph) was provided. "
            f"Convert with G.to_undirected() if appropriate."
        )


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_graph(graph: Union[nx.Graph, nx.DiGraph], algorithm: str) -> None:
    """Validate that the graph is non-empty.

    Raises:
        EmptyGraphError: If the graph has no nodes.
    """
    if len(graph) == 0:
        raise EmptyGraphError(algorithm)


def validate_source(
    graph: Union[nx.Graph, nx.DiGraph], source: Any
) -> None:
    """Validate that the source node exists in the graph.

    Raises:
        NodeNotFoundError: If the source is not in the graph.
    """
    if source not in graph:
        raise NodeNotFoundError(source, "source", graph.number_of_nodes())


def validate_target(
    graph: Union[nx.Graph, nx.DiGraph], target: Any
) -> None:
    """Validate that the target node exists in the graph.

    Raises:
        NodeNotFoundError: If the target is not in the graph.
    """
    if target not in graph:
        raise NodeNotFoundError(target, "target", graph.number_of_nodes())


def validate_weight(
    u: Any, v: Any, weight: float, algorithm: str
) -> None:
    """Validate that an edge weight is non-negative.

    Raises:
        NegativeWeightError: If the weight is negative.
    """
    if weight < 0:
        raise NegativeWeightError(u, v, weight, algorithm)


def validate_undirected(
    graph: Union[nx.Graph, nx.DiGraph], algorithm: str
) -> None:
    """Validate that the graph is undirected.

    Raises:
        UndirectedGraphRequiredError: If a DiGraph is given.
    """
    if isinstance(graph, nx.DiGraph):
        raise UndirectedGraphRequiredError(algorithm)
