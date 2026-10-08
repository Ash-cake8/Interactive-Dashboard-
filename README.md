#  Training Insight Dashboard

An interactive and dynamic data dashboard built with **Streamlit** to monitor and analyze training activities, performance metrics, participant engagement, financial returns, and geographic coverage across cities and delivery channels.

---

##  Project Overview
This project transforms raw training operational data into an executive-ready analytics platform. It enables program managers and decision-makers to inspect key performance indicators (KPIs), track historical trends, evaluate channel effectiveness, and explore spatial data through interactive visualizations.

### Key Capabilities
* **Interactive Filtering:** Dynamic filtering by Date Range, Track, City, Channel, and Minimum Satisfaction Score.
* **Real-time KPI Tracking:** Instant summary metrics for Participants, Completion Rate, Satisfaction Score, and Overall Profit with variance/delta indicators.
* **Multi-Library Visualizations:** Leverages Streamlit native charts, Altair, Plotly Express, and Folium to deliver rich visual analytical perspectives.
* **Geographic Mapping:** Interactive geospatial coverage map built using Folium (`CircleMarker` & `HeatMap`) rendered seamlessly within Streamlit.
* **Data Management & Export:** In-app tabular data editing via `st.data_editor` and filtered CSV dataset downloads.
* **State Persistence:** Preserves session state preferences across interactions.

---

##  Tech Stack & Dependencies

* **Language:** Python 3.9+
* **Core Framework:** Streamlit
* **Data Manipulation:** Pandas, NumPy
* **Data Visualization:** Altair, Plotly Express
* **Geospatial Analytics:** Folium, Streamlit Components (`streamlit.components.v1`)

---

##  Installation & Running the App

### 1. Clone or Download the Project
Ensure all project files (`app.py`, `training_activities.csv`, and `README.md`) are located in the same directory.

### 2. Install Required Packages
Run the following command in your terminal or virtual environment:

```bash
pip install streamlit pandas numpy altair plotly folium
