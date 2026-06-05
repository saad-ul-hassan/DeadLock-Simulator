"""Deadlock recovery actions."""

from __future__ import annotations

import numpy as np

from modules.deadlock_detector import detect_deadlock


def _process_index(process_name: str) -> int:
    return int(process_name.replace("P", "")) - 1


def terminate_process(allocation, request, available, process_name):
    """Terminate a process and release all resources allocated to it."""
    allocation_matrix = np.array(allocation, dtype=int)
    request_matrix = np.array(request, dtype=int)
    available_vector = np.array(available, dtype=int)
    index = _process_index(process_name)

    released = allocation_matrix[index].copy()
    available_vector += released
    allocation_matrix[index] = 0
    request_matrix[index] = 0

    action = (
        f"Terminated {process_name}. Released resources: "
        + ", ".join(f"R{i + 1}={amount}" for i, amount in enumerate(released))
    )

    return {
        "allocation": allocation_matrix.tolist(),
        "request": request_matrix.tolist(),
        "available": available_vector.tolist(),
        "action": action,
    }


def release_process_resources(allocation, request, available, process_name):
    """Release a selected process's allocated resources while keeping its requests."""
    allocation_matrix = np.array(allocation, dtype=int)
    request_matrix = np.array(request, dtype=int)
    available_vector = np.array(available, dtype=int)
    index = _process_index(process_name)

    released = allocation_matrix[index].copy()
    available_vector += released
    allocation_matrix[index] = 0

    action = (
        f"Released resources of {process_name}. Released resources: "
        + ", ".join(f"R{i + 1}={amount}" for i, amount in enumerate(released))
    )

    return {
        "allocation": allocation_matrix.tolist(),
        "request": request_matrix.tolist(),
        "available": available_vector.tolist(),
        "action": action,
    }


def auto_recover(allocation, request, available, detection_result=None):
    """Automatically terminate one process from the detected deadlock cycle."""
    result = detection_result or detect_deadlock(allocation, request)
    if not result["deadlock"] or not result["involved_processes"]:
        return {
            "allocation": allocation,
            "request": request,
            "available": available,
            "action": "Automatic recovery was not required because no deadlock was detected.",
        }

    victim = result["involved_processes"][0]
    recovered = terminate_process(allocation, request, available, victim)
    recovered["action"] = f"Automatic recovery selected {victim}. {recovered['action']}"
    return recovered
