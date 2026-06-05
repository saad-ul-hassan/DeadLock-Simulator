"""Sample scenarios for the Deadlock Detection and Recovery Simulator."""


SAMPLE_SCENARIOS = {
    "No Deadlock Example": {
        "description": "A stable system where at least one process can proceed without circular waiting.",
        "allocation": [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ],
        "request": [
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ],
        "available": [1, 0, 0],
    },
    "Simple Deadlock Example": {
        "description": "Two processes wait on each other's allocated resources.",
        "allocation": [
            [1, 0],
            [0, 1],
        ],
        "request": [
            [0, 1],
            [1, 0],
        ],
        "available": [0, 0],
    },
    "Complex Deadlock Example": {
        "description": "A larger circular wait involving multiple processes and resources.",
        "allocation": [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 1, 0],
        ],
        "request": [
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0],
            [1, 0, 1],
        ],
        "available": [0, 0, 0],
    },
}


def get_scenario_names():
    """Return available scenario names."""
    return list(SAMPLE_SCENARIOS.keys())


def get_scenario(name):
    """Return a copy of a scenario by name."""
    scenario = SAMPLE_SCENARIOS[name]
    return {
        "description": scenario["description"],
        "allocation": [row[:] for row in scenario["allocation"]],
        "request": [row[:] for row in scenario["request"]],
        "available": scenario["available"][:],
    }
