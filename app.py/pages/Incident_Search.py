"""
==========================================================
AI-Powered Cybersecurity Incident Assistant (RAG)
Incident Search Page
Version: 4.0
==========================================================
"""

from __future__ import annotations

import streamlit as st

from config.config import INCIDENT_DATASET
from src.data_loader import data_loader


st.set_page_config(
    page_title="Incident Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Cybersecurity Incident Search")

st.caption(
    "Search historical cybersecurity incidents."
)

# ----------------------------------------------------------
# Load Dataset
# ----------------------------------------------------------

try:

    incidents = data_loader.load_csv(
        INCIDENT_DATASET
    )

except Exception as error:

    st.error(
        f"Unable to load dataset.\n\n{error}"
    )

    st.stop()

# ----------------------------------------------------------
# Sidebar Filters
# ----------------------------------------------------------

st.sidebar.header("Search Filters")

query = st.sidebar.text_input(
    "Keyword"
)

severity_column = None

for column in incidents.columns:

    if column.lower() == "severity":

        severity_column = column
        break

if severity_column:

    severities = sorted(
        incidents[severity_column]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_severity = st.sidebar.selectbox(
        "Severity",
        ["All"] + severities
    )

else:

    selected_severity = "All"

# ----------------------------------------------------------
# Filtering
# ----------------------------------------------------------

filtered = incidents.copy()

if query:

    mask = filtered.astype(str).apply(
        lambda column:
        column.str.contains(
            query,
            case=False,
            na=False
        )
    ).any(axis=1)

    filtered = filtered[mask]

if (
    severity_column
    and selected_severity != "All"
):

    filtered = filtered[
        filtered[severity_column]
        .astype(str)
        == selected_severity
    ]

# ----------------------------------------------------------
# Results
# ----------------------------------------------------------

st.metric(
    "Matching Incidents",
    len(filtered)
)

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------------------------
# Download
# ----------------------------------------------------------

csv_data = filtered.to_csv(
    index=False
)

st.download_button(

    label="⬇ Download Results",

    data=csv_data,

    file_name="incident_search_results.csv",

    mime="text/csv"

)

# ----------------------------------------------------------
# Dataset Summary
# ----------------------------------------------------------

with st.expander(
    "Dataset Summary"
):

    summary = data_loader.dataset_summary(
        incidents
    )

    st.json(summary)
