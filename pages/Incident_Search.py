"""Incident search page."""

import streamlit as st

from config.config import APP_ICON, APP_TITLE, INCIDENT_DATASET
from src.data_loader import data_loader

st.set_page_config(
    page_title="Incident Search",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Incident Search")
st.caption("Search the authoritative cybersecurity incident dataset.")

try:
    incidents = data_loader.load_csv(INCIDENT_DATASET)
    data_loader.validate(incidents)
except (FileNotFoundError, ValueError) as error:
    st.error(f"Incident dataset is unavailable: {error}")
    st.stop()

query = st.text_input("Search incidents", placeholder="keyword, IP, category, description...")
severity = st.selectbox("Severity", ["All", "Low", "Medium", "High", "Critical"])

filtered = incidents

if query.strip():
    query = query.strip()
    mask = filtered.astype(str).apply(
        lambda column: column.str.contains(query, case=False, na=False, regex=False)
    ).any(axis=1)
    filtered = filtered.loc[mask]

severity_column = next(
    (column for column in filtered.columns if column.lower() == "severity"),
    None,
)

if severity != "All" and severity_column:
    filtered = filtered.loc[
        filtered[severity_column].astype(str).str.casefold() == severity.casefold()
    ]

st.metric("Matching Incidents", len(filtered))
st.dataframe(filtered, use_container_width=True, hide_index=True)

st.download_button(
    "Download Results",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="incident_search_results.csv",
    mime="text/csv",
)

st.sidebar.info(f"Dataset: {INCIDENT_DATASET.name}")
st.sidebar.caption(APP_TITLE)
st.sidebar.caption(f"{APP_ICON} Incident Search")
