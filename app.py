"""Streamlit application for Deadlock Detection and Recovery Simulator."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.deadlock_detector import detect_deadlock
from modules.graph_builder import draw_graph
from modules.recovery import auto_recover, release_process_resources, terminate_process
from modules.report_generator import generate_report
from sample_data.examples import get_scenario, get_scenario_names


COURSE_NAME = "Parallel and Distributed Computing OEL"
GROUP_MEMBERS = [
    "Member 1 - Student ID",
    "Member 2 - Student ID",
    "Member 3 - Student ID",
    "Member 4 - Student ID",
]


st.set_page_config(
    page_title="Deadlock Detection and Recovery Simulator",
    page_icon=None,
    layout="wide",
)


def apply_styles():
    st.markdown(
        """
        <style>
            :root {
                --primary: #1f4e79;
                --border: #d8dee9;
                --surface: #ffffff;
                --muted: #5f6b7a;
            }
            .block-container {
                padding-top: 1.6rem;
                padding-bottom: 2rem;
                max-width: 1180px;
            }
            h1, h2, h3 {
                color: #172033;
                letter-spacing: 0;
            }
            div[data-testid="stMetric"] {
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 14px 16px;
                min-height: 96px;
            }
            div[data-testid="stMetricLabel"] {
                color: var(--muted);
            }
            .info-card {
                border: 1px solid var(--border);
                border-left: 4px solid var(--primary);
                border-radius: 8px;
                padding: 16px 18px;
                background: #ffffff;
                margin-bottom: 12px;
            }
            .section-card {
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 18px;
                background: #ffffff;
                margin-bottom: 16px;
            }
            .small-muted {
                color: var(--muted);
                font-size: 0.92rem;
            }
            .status-ok {
                border-left: 4px solid #15803d;
            }
            .status-bad {
                border-left: 4px solid #b91c1c;
            }
            .stButton > button {
                border-radius: 6px;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def process_names():
    return [f"P{i + 1}" for i in range(st.session_state.process_count)]


def resource_names():
    return [f"R{i + 1}" for i in range(st.session_state.resource_count)]


def resize_matrix(matrix, rows, cols):
    resized = [[0 for _ in range(cols)] for _ in range(rows)]
    for row_index in range(min(rows, len(matrix))):
        for col_index in range(min(cols, len(matrix[row_index]))):
            resized[row_index][col_index] = int(matrix[row_index][col_index])
    return resized


def resize_vector(vector, cols):
    resized = [0 for _ in range(cols)]
    for index in range(min(cols, len(vector))):
        resized[index] = int(vector[index])
    return resized


def load_scenario(name):
    scenario = get_scenario(name)
    st.session_state.process_count = len(scenario["allocation"])
    st.session_state.resource_count = len(scenario["available"])
    st.session_state.allocation = scenario["allocation"]
    st.session_state.request = scenario["request"]
    st.session_state.available = scenario["available"]
    st.session_state.recovery_action = "No recovery action applied."
    st.session_state.after_recovery_result = None
    st.session_state.before_recovery_result = None
    st.session_state.before_recovery_snapshot = None
    st.session_state.loaded_scenario = name


def initialize_state():
    if "allocation" not in st.session_state:
        load_scenario("Simple Deadlock Example")


def sync_dimensions():
    rows = st.session_state.process_count
    cols = st.session_state.resource_count
    st.session_state.allocation = resize_matrix(st.session_state.allocation, rows, cols)
    st.session_state.request = resize_matrix(st.session_state.request, rows, cols)
    st.session_state.available = resize_vector(st.session_state.available, cols)
    st.session_state.after_recovery_result = None
    st.session_state.before_recovery_result = None
    st.session_state.before_recovery_snapshot = None


def matrix_editor(label, data, key):
    frame = pd.DataFrame(data, index=process_names(), columns=resource_names())
    edited = st.data_editor(
        frame,
        key=key,
        use_container_width=True,
        hide_index=False,
        num_rows="fixed",
        column_config={column: st.column_config.NumberColumn(column, min_value=0, step=1) for column in frame.columns},
    )
    st.session_state[label] = edited.astype(int).values.tolist()


def available_editor():
    frame = pd.DataFrame([st.session_state.available], index=["Available"], columns=resource_names())
    edited = st.data_editor(
        frame,
        key="available_editor",
        use_container_width=True,
        hide_index=False,
        num_rows="fixed",
        column_config={column: st.column_config.NumberColumn(column, min_value=0, step=1) for column in frame.columns},
    )
    st.session_state.available = edited.astype(int).values.tolist()[0]


def allocation_frame():
    return pd.DataFrame(st.session_state.allocation, index=process_names(), columns=resource_names())


def request_frame():
    return pd.DataFrame(st.session_state.request, index=process_names(), columns=resource_names())


def available_frame():
    return pd.DataFrame([st.session_state.available], index=["Available"], columns=resource_names())


def current_detection():
    return detect_deadlock(st.session_state.allocation, st.session_state.request)


def render_status_panel(result):
    status_class = "status-bad" if result["deadlock"] else "status-ok"
    status_text = "Deadlock Detected" if result["deadlock"] else "No Deadlock Detected"
    detail = (
        f"Involved processes: {', '.join(result['involved_processes'])}"
        if result["deadlock"]
        else "The wait-for graph has no cycle."
    )
    st.markdown(
        f"""
        <div class="info-card {status_class}">
            <h3>{status_text}</h3>
            <p class="small-muted">{detail}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def home_page():
    st.title("Deadlock Detection and Recovery Simulator")
    st.subheader(COURSE_NAME)

    st.markdown(
        """
        <div class="info-card">
            <p>
            This simulator demonstrates how deadlocks can occur in parallel and distributed systems
            when multiple processes hold resources while waiting for resources held by others.
            It models allocation and request matrices, builds a Resource Allocation Graph,
            detects circular wait through DFS, and applies recovery actions to restore progress.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Processes", st.session_state.process_count)
    col2.metric("Resources", st.session_state.resource_count)
    col3.metric("Current Scenario", st.session_state.get("loaded_scenario", "Custom"))

    st.markdown("### Group Members")
    members_frame = pd.DataFrame({"Name": GROUP_MEMBERS})
    st.table(members_frame)

    st.markdown("### Project Scope")
    st.write(
        "The application provides matrix input, graph visualization, DFS-based detection, "
        "manual and automatic recovery, and a downloadable report for evaluation."
    )


def input_system_page():
    st.header("Input System")

    scenario_names = get_scenario_names()
    selected_index = scenario_names.index(st.session_state.loaded_scenario) if st.session_state.loaded_scenario in scenario_names else 0
    selected = st.selectbox("Sample Scenarios", scenario_names, index=selected_index)
    scenario = get_scenario(selected)
    st.caption(scenario["description"])

    if st.button("Load Selected Scenario", type="primary"):
        load_scenario(selected)
        st.rerun()

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        process_count_input = st.number_input(
            "Number of Processes",
            min_value=1,
            max_value=8,
            step=1,
            value=st.session_state.process_count,
        )
    with col2:
        resource_count_input = st.number_input(
            "Number of Resources",
            min_value=1,
            max_value=8,
            step=1,
            value=st.session_state.resource_count,
        )

    if st.button("Apply Dimensions"):
        st.session_state.process_count = process_count_input
        st.session_state.resource_count = resource_count_input
        sync_dimensions()
        st.session_state.loaded_scenario = "Custom"
        st.rerun()

    st.markdown("### Allocation Matrix")
    matrix_editor("allocation", st.session_state.allocation, "allocation_editor")

    st.markdown("### Request Matrix")
    matrix_editor("request", st.session_state.request, "request_editor")

    st.markdown("### Available Resources")
    available_editor()

    if st.button("Save Input System", type="primary"):
        st.session_state.loaded_scenario = "Custom"
        st.session_state.recovery_action = "No recovery action applied."
        st.session_state.after_recovery_result = None
        st.session_state.before_recovery_result = None
        st.session_state.before_recovery_snapshot = None
        st.success("Input system saved.")


def matrix_view_page():
    st.header("Matrix View")

    col1, col2, col3 = st.columns(3)
    col1.metric("Processes", st.session_state.process_count)
    col2.metric("Resources", st.session_state.resource_count)
    col3.metric("Total Allocated Units", int(pd.DataFrame(st.session_state.allocation).values.sum()))

    st.markdown("### Allocation Matrix")
    st.dataframe(allocation_frame(), use_container_width=True)

    st.markdown("### Request Matrix")
    st.dataframe(request_frame(), use_container_width=True)

    st.markdown("### Available Resources")
    st.dataframe(available_frame(), use_container_width=True)


def graph_page():
    st.header("Resource Allocation Graph")
    result = current_detection()
    render_status_panel(result)

    if st.session_state.before_recovery_snapshot is not None:
        snapshot = st.session_state.before_recovery_snapshot
        before_cycle = st.session_state.before_recovery_result["cycle"]
        st.pyplot(draw_graph(snapshot["allocation"], snapshot["request"], before_cycle, "Graph Before Recovery"))
    else:
        st.pyplot(draw_graph(st.session_state.allocation, st.session_state.request, result["cycle"], "Current Graph"))

    if st.session_state.after_recovery_result is not None:
        st.markdown("### Graph After Recovery")
        st.pyplot(
            draw_graph(
                st.session_state.allocation,
                st.session_state.request,
                st.session_state.after_recovery_result["cycle"],
                "Graph After Recovery",
            )
        )
    else:
        st.info("Apply a recovery action to view the graph after recovery.")


def detection_page():
    st.header("Deadlock Detection")
    result = current_detection()
    render_status_panel(result)

    col1, col2, col3 = st.columns(3)
    col1.metric("Deadlock Status", "Detected" if result["deadlock"] else "Not Detected")
    col2.metric("Involved Processes", len(result["involved_processes"]))
    col3.metric("Wait Edges", len(result["wait_edges"]))

    if result["deadlock"]:
        st.markdown("### Deadlock Cycle")
        st.code(" -> ".join(result["cycle"]), language="text")

    st.markdown("### Step-by-Step DFS Trace")
    st.code("\n".join(result["trace"]), language="text")

    st.markdown("### Wait-For Graph")
    wait_frame = pd.DataFrame(
        [{"Process": process, "Waiting For": ", ".join(targets) or "None"} for process, targets in result["wait_graph"].items()]
    )
    st.dataframe(wait_frame, use_container_width=True, hide_index=True)


def recovery_page():
    st.header("Recovery")
    before_result = current_detection()
    render_status_panel(before_result)

    processes = process_names()
    selected_process = st.selectbox("Select Process", processes)

    col1, col2, col3 = st.columns(3)
    with col1:
        terminate_clicked = st.button("Terminate Selected Process", use_container_width=True)
    with col2:
        release_clicked = st.button("Release Selected Process Resources", use_container_width=True)
    with col3:
        auto_clicked = st.button("Automatic Recovery", type="primary", use_container_width=True)

    recovered = None
    if terminate_clicked:
        recovered = terminate_process(
            st.session_state.allocation,
            st.session_state.request,
            st.session_state.available,
            selected_process,
        )
    elif release_clicked:
        recovered = release_process_resources(
            st.session_state.allocation,
            st.session_state.request,
            st.session_state.available,
            selected_process,
        )
    elif auto_clicked:
        recovered = auto_recover(
            st.session_state.allocation,
            st.session_state.request,
            st.session_state.available,
            before_result,
        )

    if recovered is not None:
        st.session_state.before_recovery_result = before_result
        st.session_state.before_recovery_snapshot = {
            "allocation": [row[:] for row in st.session_state.allocation],
            "request": [row[:] for row in st.session_state.request],
            "available": st.session_state.available[:],
        }
        st.session_state.allocation = recovered["allocation"]
        st.session_state.request = recovered["request"]
        st.session_state.available = recovered["available"]
        st.session_state.recovery_action = recovered["action"]
        st.session_state.after_recovery_result = detect_deadlock(recovered["allocation"], recovered["request"])
        st.session_state.loaded_scenario = "Custom"
        st.success(recovered["action"])

    st.markdown("### Recovery Action Applied")
    st.write(st.session_state.recovery_action)

    after_result = st.session_state.after_recovery_result or current_detection()
    st.markdown("### Result After Recovery")
    render_status_panel(after_result)

    st.markdown("### Updated Allocation Matrix")
    st.dataframe(allocation_frame(), use_container_width=True)

    st.markdown("### Updated Request Matrix")
    st.dataframe(request_frame(), use_container_width=True)

    st.markdown("### Updated Available Resources")
    st.dataframe(available_frame(), use_container_width=True)


def report_page():
    st.header("Report")
    before_result = st.session_state.before_recovery_result or current_detection()
    after_result = st.session_state.after_recovery_result
    report_text = generate_report(
        st.session_state.allocation,
        st.session_state.request,
        st.session_state.available,
        before_result,
        after_result,
        st.session_state.recovery_action,
    )

    st.text_area("Generated Report", report_text, height=520)
    st.download_button(
        "Download Report",
        data=report_text,
        file_name="deadlock_detection_recovery_report.txt",
        mime="text/plain",
        type="primary",
    )


def main():
    apply_styles()
    initialize_state()

    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Sections",
            [
                "Home",
                "Input System",
                "Matrix View",
                "Resource Allocation Graph",
                "Deadlock Detection",
                "Recovery",
                "Report",
            ],
        )
        st.divider()
        result = current_detection()
        st.metric("Deadlock", "Yes" if result["deadlock"] else "No")
        st.metric("Processes", st.session_state.process_count)
        st.metric("Resources", st.session_state.resource_count)

    if page == "Home":
        home_page()
    elif page == "Input System":
        input_system_page()
    elif page == "Matrix View":
        matrix_view_page()
    elif page == "Resource Allocation Graph":
        graph_page()
    elif page == "Deadlock Detection":
        detection_page()
    elif page == "Recovery":
        recovery_page()
    elif page == "Report":
        report_page()


if __name__ == "__main__":
    main()
