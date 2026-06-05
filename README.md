# Deadlock Detection and Recovery Simulator

Parallel and Distributed Computing OEL

## Overview

This project is a professional Streamlit web application that simulates deadlock detection and recovery in multi-process systems. It uses allocation and request matrices to construct a Resource Allocation Graph, detects deadlocks through DFS-based cycle detection, and applies recovery strategies such as process termination and resource release.

## Features

- Home page with project title, course name, group members, and introduction
- Sidebar navigation for all simulator sections
- Editable input system for processes, resources, allocation matrix, request matrix, and available resources
- Built-in sample scenarios:
  - No Deadlock Example
  - Simple Deadlock Example
  - Complex Deadlock Example
- Matrix view with clean process and resource labels
- Resource Allocation Graph using NetworkX and Matplotlib
- Deadlock cycle highlighting in red
- DFS trace for cycle detection
- Manual and automatic recovery actions
- Updated matrices and graph after recovery
- Downloadable text report

## Project Structure

```text
Deadlock-Simulator/
│
├── app.py
├── requirements.txt
├── README.md
│
├── modules/
│   ├── graph_builder.py
│   ├── deadlock_detector.py
│   ├── recovery.py
│   └── report_generator.py
│
└── sample_data/
    └── examples.py
```

## Installation

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Run the Application

From inside the `Deadlock-Simulator` directory, run:

```bash
streamlit run app.py
```

The application will open in the browser at the local Streamlit address shown in the terminal.

## Algorithm Summary

The simulator converts the allocation and request matrices into a wait-for relationship. If process `P1` requests resource `R2`, and `R2` is allocated to `P2`, the wait-for graph contains an edge from `P1` to `P2`. DFS is then applied to the wait-for graph. A cycle in this graph indicates a circular wait condition, which means deadlock exists.

## Recovery Methods

The recovery page supports three actions:

- Terminate a selected process
- Release resources held by a selected process
- Automatically terminate one process from the detected deadlock cycle

After recovery, the simulator updates matrices, rebuilds the graph, runs detection again, and reports whether the deadlock remains.

## Group Members

Update the `GROUP_MEMBERS` list in `app.py` with actual names and student IDs before final submission.
