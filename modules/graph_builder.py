"""Resource Allocation Graph builder and renderer."""

from __future__ import annotations

import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib"))

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def _process_name(index: int) -> str:
    return f"P{index + 1}"


def _resource_name(index: int) -> str:
    return f"R{index + 1}"


def build_resource_allocation_graph(allocation, request):
    """Build a directed resource allocation graph."""
    allocation_matrix = np.array(allocation, dtype=int)
    request_matrix = np.array(request, dtype=int)
    process_count, resource_count = allocation_matrix.shape

    graph = nx.DiGraph()

    for process_index in range(process_count):
        graph.add_node(_process_name(process_index), node_type="process")

    for resource_index in range(resource_count):
        graph.add_node(_resource_name(resource_index), node_type="resource")

    for process_index in range(process_count):
        for resource_index in range(resource_count):
            units_requested = request_matrix[process_index][resource_index]
            if units_requested > 0:
                graph.add_edge(
                    _process_name(process_index),
                    _resource_name(resource_index),
                    edge_type="request",
                    weight=int(units_requested),
                )

            units_allocated = allocation_matrix[process_index][resource_index]
            if units_allocated > 0:
                graph.add_edge(
                    _resource_name(resource_index),
                    _process_name(process_index),
                    edge_type="allocation",
                    weight=int(units_allocated),
                )

    return graph


def cycle_edges_from_process_cycle(cycle, allocation, request):
    """Convert a process cycle into graph edges that should be highlighted."""
    if not cycle:
        return set()

    allocation_matrix = np.array(allocation, dtype=int)
    request_matrix = np.array(request, dtype=int)
    highlight_edges = set()

    for current_process, next_process in zip(cycle, cycle[1:]):
        current_index = int(current_process[1:]) - 1
        next_index = int(next_process[1:]) - 1

        for resource_index in range(request_matrix.shape[1]):
            requested = request_matrix[current_index][resource_index] > 0
            allocated = allocation_matrix[next_index][resource_index] > 0
            if requested and allocated:
                resource_name = _resource_name(resource_index)
                highlight_edges.add((current_process, resource_name))
                highlight_edges.add((resource_name, next_process))
                break

    return highlight_edges


def draw_graph(allocation, request, cycle=None, title="Resource Allocation Graph"):
    """Draw the resource allocation graph and highlight deadlock cycle edges."""
    graph = build_resource_allocation_graph(allocation, request)
    cycle = cycle or []
    highlight_edges = cycle_edges_from_process_cycle(cycle, allocation, request)

    process_nodes = [node for node, data in graph.nodes(data=True) if data["node_type"] == "process"]
    resource_nodes = [node for node, data in graph.nodes(data=True) if data["node_type"] == "resource"]

    pos = {}
    for index, node in enumerate(process_nodes):
        pos[node] = (0, -index)
    for index, node in enumerate(resource_nodes):
        pos[node] = (2.4, -index)

    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=process_nodes,
        node_shape="o",
        node_color="#dbeafe",
        edgecolors="#1d4ed8",
        linewidths=1.5,
        node_size=1400,
        ax=ax,
    )
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=resource_nodes,
        node_shape="s",
        node_color="#ecfdf5",
        edgecolors="#047857",
        linewidths=1.5,
        node_size=1400,
        ax=ax,
    )
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight="bold", ax=ax)

    normal_edges = [edge for edge in graph.edges() if edge not in highlight_edges]
    highlighted_edges = [edge for edge in graph.edges() if edge in highlight_edges]

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=normal_edges,
        edge_color="#475569",
        arrows=True,
        arrowsize=18,
        width=1.8,
        connectionstyle="arc3,rad=0.08",
        ax=ax,
    )
    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=highlighted_edges,
        edge_color="#dc2626",
        arrows=True,
        arrowsize=22,
        width=3.0,
        connectionstyle="arc3,rad=0.08",
        ax=ax,
    )

    edge_labels = {
        (u, v): f"{data['weight']}" if data.get("weight", 1) > 1 else ""
        for u, v, data in graph.edges(data=True)
    }
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=9, ax=ax)

    ax.text(0, 0.12, "Processes", ha="center", va="bottom", fontsize=10, color="#1d4ed8")
    ax.text(2.4, 0.12, "Resources", ha="center", va="bottom", fontsize=10, color="#047857")
    ax.axis("off")
    fig.tight_layout()
    return fig
