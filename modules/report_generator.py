"""Generate a downloadable simulator report."""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def matrix_to_text(title, matrix, process_names, resource_names):
    frame = pd.DataFrame(matrix, index=process_names, columns=resource_names)
    return f"{title}\n{frame.to_string()}"


def vector_to_text(title, vector, resource_names):
    frame = pd.DataFrame([vector], index=["Available"], columns=resource_names)
    return f"{title}\n{frame.to_string()}"


def generate_report(
    allocation,
    request,
    available,
    before_result,
    after_result=None,
    recovery_action="No recovery action applied.",
):
    """Generate a plain text report for download."""
    process_names = [f"P{i + 1}" for i in range(len(allocation))]
    resource_names = [f"R{i + 1}" for i in range(len(available))]

    lines = [
        "Deadlock Detection and Recovery Simulator",
        "Parallel and Distributed Computing OEL",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        matrix_to_text("Allocation Matrix", allocation, process_names, resource_names),
        "",
        matrix_to_text("Request Matrix", request, process_names, resource_names),
        "",
        vector_to_text("Available Resources", available, resource_names),
        "",
        "Before Recovery Result",
        f"Deadlock Detected: {'Yes' if before_result['deadlock'] else 'No'}",
        f"Involved Processes: {', '.join(before_result['involved_processes']) or 'None'}",
        f"Deadlock Cycle: {' -> '.join(before_result['cycle']) or 'None'}",
        "",
        "DFS Trace",
        "\n".join(before_result["trace"]),
        "",
        "Recovery Action",
        recovery_action,
    ]

    if after_result is not None:
        lines.extend(
            [
                "",
                "After Recovery Result",
                f"Deadlock Detected: {'Yes' if after_result['deadlock'] else 'No'}",
                f"Involved Processes: {', '.join(after_result['involved_processes']) or 'None'}",
                f"Deadlock Cycle: {' -> '.join(after_result['cycle']) or 'None'}",
                "",
                "After Recovery DFS Trace",
                "\n".join(after_result["trace"]),
            ]
        )

    return "\n".join(lines)
