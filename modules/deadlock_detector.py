"""DFS-based deadlock detection for resource allocation graphs."""

from __future__ import annotations

import numpy as np


def _process_name(index: int) -> str:
    return f"P{index + 1}"


def _resource_name(index: int) -> str:
    return f"R{index + 1}"


def build_wait_graph(allocation, request):
    """Build process-to-process wait graph from allocation and request matrices."""
    allocation_matrix = np.array(allocation, dtype=int)
    request_matrix = np.array(request, dtype=int)

    process_count, resource_count = request_matrix.shape
    wait_graph = {_process_name(i): [] for i in range(process_count)}
    wait_edges = []

    for process_index in range(process_count):
        for resource_index in range(resource_count):
            if request_matrix[process_index][resource_index] <= 0:
                continue

            waiting_process = _process_name(process_index)
            resource = _resource_name(resource_index)

            for owner_index in range(process_count):
                if allocation_matrix[owner_index][resource_index] <= 0:
                    continue

                owner_process = _process_name(owner_index)
                if owner_process not in wait_graph[waiting_process]:
                    wait_graph[waiting_process].append(owner_process)
                wait_edges.append((waiting_process, resource, owner_process))

    return wait_graph, wait_edges


def _format_cycle(cycle):
    return " -> ".join(cycle)


def detect_deadlock(allocation, request):
    """Detect deadlock using DFS cycle detection over the wait-for graph."""
    wait_graph, wait_edges = build_wait_graph(allocation, request)
    visited = set()
    recursion_stack = []
    stack_set = set()
    trace = []
    cycle = []

    def explain_waits(process):
        related_edges = [edge for edge in wait_edges if edge[0] == process]
        if not related_edges:
            trace.append(f"{process} has no pending request that is held by another process")
            return

        for waiting_process, resource, owner_process in related_edges:
            trace.append(f"{waiting_process} is waiting for {resource}")
            trace.append(f"{resource} is allocated to {owner_process}")

    def dfs(process):
        nonlocal cycle
        visited.add(process)
        recursion_stack.append(process)
        stack_set.add(process)
        trace.append(f"Start DFS from {process}" if len(recursion_stack) == 1 else f"Visit {process}")
        explain_waits(process)

        for next_process in wait_graph[process]:
            if next_process not in visited:
                if dfs(next_process):
                    return True
            elif next_process in stack_set:
                start_index = recursion_stack.index(next_process)
                cycle = recursion_stack[start_index:] + [next_process]
                trace.append("Cycle detected")
                trace.append(f"Deadlock cycle: {_format_cycle(cycle)}")
                return True

        recursion_stack.pop()
        stack_set.remove(process)
        trace.append(f"Backtrack from {process}")
        return False

    for process in wait_graph:
        if process not in visited:
            if dfs(process):
                involved = sorted(set(cycle), key=lambda name: int(name[1:]))
                return {
                    "deadlock": True,
                    "cycle": cycle,
                    "involved_processes": involved,
                    "trace": trace,
                    "wait_graph": wait_graph,
                    "wait_edges": wait_edges,
                }

    trace.append("No cycle found in the wait-for graph")
    return {
        "deadlock": False,
        "cycle": [],
        "involved_processes": [],
        "trace": trace,
        "wait_graph": wait_graph,
        "wait_edges": wait_edges,
    }
