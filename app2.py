import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Training Insight Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

@st.cache_data
def load_data():
    df = pd.read_csv("training_activities.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["completion_rate"] = (df["completed"] / df["participants"] * 100).round(1)
    df["profit"] = df["revenue"] - df["cost"]
    df["uncompleted"] = df["participants"] - df["completed"]
    return df

df = load_data()

if "selected_tab_note" not in st.session_state:
    st.session_state.selected_tab_note = "Dashboard preferences are remembered during this session."

st.sidebar.title("Dashboard Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,max_value=max_date,)

track_options = sorted(df["track"].unique())
selected_tracks = st.sidebar.multiselect("Track", track_options, default=track_options)

location_options = sorted(df["city"].unique())
selected_locations = st.sidebar.multiselect("City", location_options, default=location_options)

channel_options = sorted(df["channel"].unique())
selected_channels = st.sidebar.multiselect("Channel", channel_options, default=channel_options)

min_satisfaction = st.sidebar.slider(
    "Minimum satisfaction",
    min_value=3.0,max_value=5.0,
    value=3.0,step=0.1,)

if len(date_range) == 1:
    start_date = end_date = date_range[0]
else:
    start_date, end_date = date_range

filtered_df = df[
    (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
    & (df["track"].isin(selected_tracks))
    & (df["city"].isin(selected_locations))
    & (df["channel"].isin(selected_channels))
    & (df["satisfaction_score"] >= min_satisfaction)].copy()

st.title("Training Insight Dashboard")

st.markdown("""
    Use the sidebar to explore training activity by date, track, city, channel,
    and satisfaction. All KPIs and visualizations update automatically.
""")

total_participants = int(filtered_df["participants"].sum()) if not filtered_df.empty else 0
total_completed = int(filtered_df["completed"].sum()) if not filtered_df.empty else 0
completion_rate = (
    total_completed / total_participants * 100
    if total_participants > 0 else 0)

avg_satisfaction = (
    filtered_df["satisfaction_score"].mean()
    if not filtered_df.empty else 0
)
total_profit = (
    filtered_df["profit"].sum()
    if not filtered_df.empty else 0
)

overall_completion = df["completed"].sum() / df["participants"].sum() * 100
overall_satisfaction = df["satisfaction_score"].mean()
overall_profit = df["profit"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Participants", f"{total_participants:,}", f"{total_participants - df['participants'].sum():,}")
k2.metric("Completion Rate", f"{completion_rate:.1f}%", f"{completion_rate - overall_completion:+.1f} pp")
k3.metric("Avg Satisfaction", f"{avg_satisfaction:.2f}/5", f"{avg_satisfaction - overall_satisfaction:+.2f}")
k4.metric("Profit", f"${total_profit:,.0f}", f"${total_profit - overall_profit:+,.0f}")

if filtered_df.empty:
    st.warning("No activities match the selected filters. Try widening the filters.")
    st.stop()

overview_tab, trends_tab, relationships_tab, geography_tab, data_tab = st.tabs(
    ["Overview", "Trends & Financials", "Financials & Impact", "Geography", "Data Explorer"])

with overview_tab:
    st.subheader("Performance Overview")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Participants by Track (Bar Chart)**")
        track_summary = (
            filtered_df.groupby("track", as_index=False)["participants"].sum()
            .sort_values("participants", ascending=False)
            .set_index("track")
        )
        st.bar_chart(track_summary, y="participants", use_container_width=True)

    with c2:
        st.markdown("**Completions by Channel (Area Chart)**")
        channel_summary = (
            filtered_df.groupby("channel", as_index=False)["completed"].sum()
            .sort_values("completed", ascending=False)
            .set_index("channel")
        )
        st.area_chart(channel_summary, y="completed", use_container_width=True)

    st.markdown("---")
    st.subheader("Completed vs Uncompleted Participants by Track (Altair Stacked Bar Chart)")
    
    stacked_data = filtered_df.groupby("track", as_index=False)[["completed", "uncompleted"]].sum()
    melted_stacked = stacked_data.melt(
        id_vars="track", value_vars=["completed", "uncompleted"],
        var_name="status", value_name="count"
    )

    alt_stacked_chart = (
        alt.Chart(melted_stacked).mark_bar()
        .encode(
            x=alt.X("track:N", title="Track"),
            y=alt.Y("count:Q", title="Number of Participants"),
            color=alt.Color("status:N", title="Status", scale=alt.Scale(domain=["completed", "uncompleted"], range=["#2E7D32", "#C62828"])),
            tooltip=["track", "status", "count"]
        ).properties(height=350, title="Completion Breakup by Track"))
    st.altair_chart(alt_stacked_chart, use_container_width=True)


with trends_tab:
    st.subheader("Training Trends Over Time")

    daily = (
        filtered_df.groupby("date", as_index=True).agg(
            participants=("participants", "sum"),
            completed=("completed", "sum"),
            revenue=("revenue", "sum"),).sort_index())
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Daily Participant Activity (Line Chart)**")
        st.line_chart(daily[["participants", "completed"]], use_container_width=True)
        
    with col_t2:
        st.markdown("**Channel Share (Plotly Donut Chart)**")
        channel_pie = filtered_df.groupby("channel", as_index=False)["participants"].sum()
        fig_donut = px.pie(
            channel_pie, values="participants", 
            names="channel", hole=0.45,
            title="Participants Distribution by Channel")
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")
    st.markdown("**Interactive Revenue vs Cost Over Time (Plotly Multi-line Chart)**")
    
    plot_df = (
        filtered_df.groupby("date", as_index=False)
        .agg(revenue=("revenue", "sum"), cost=("cost", "sum")))
    plot_long = plot_df.melt(id_vars="date", 
        value_vars=["revenue", "cost"],
        var_name="metric", value_name="amount")

    fig_line = px.line(
        plot_long,
        x="date", y="amount", 
        color="metric", markers=True,
        title="Revenue and Cost Trends",
        labels={"amount": "Amount ($)", "date": "Date", "metric": "Metric"})
    st.plotly_chart(fig_line, use_container_width=True)


with relationships_tab:
    st.subheader("Financials & Impact")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("**Cost vs Satisfaction Score (Plotly Scatter Plot)**")
        fig_scatter = px.scatter(
            filtered_df,
            x="cost",y="satisfaction_score",
            size="participants",color="track",
            hover_name="city",
            title="Impact of Training Cost on Satisfaction",
            labels={"cost": "Training Cost ($)", "satisfaction_score": "Satisfaction Score (1-5)"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_r2:
        st.markdown("**Profit Distribution across Channels (Plotly Box Plot)**")
        fig_box = px.box(
            filtered_df,
            x="channel",y="profit",
            color="channel",points="all",
            title="Profitability Spread & Outliers by Channel",
            labels={"profit": "Profit ($)", "channel": "Channel"})
        st.plotly_chart(fig_box, use_container_width=True)


with geography_tab:
    st.subheader("Geographic Coverage")

    map_df = (
        filtered_df.groupby(
            ["city", "governorate", "latitude", "longitude"], as_index=False
        ).agg(
            participants=("participants", "sum"),
            completed=("completed", "sum"),
            satisfaction=("satisfaction_score", "mean"), ))

    if not map_df.empty:
        center_lat = map_df["latitude"].mean()
        center_lon = map_df["longitude"].mean()

        m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="OpenStreetMap")

        heat_data = [[row['latitude'], row['longitude'], row['participants']] for _, row in map_df.iterrows()]
        HeatMap(heat_data, radius=15, blur=10, min_opacity=0.3).add_to(m)

        for _, row in map_df.iterrows():
            popup_text = (
                f"City: {row['city']} ({row['governorate']})<br>"
                f"Participants: {row['participants']:,}<br>"
                f"Completed: {row['completed']:,}<br>"
                f"Satisfaction: {row['satisfaction']:.2f}/5")
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=max(5, min(20, row["participants"] / 10)),
                popup=folium.Popup(popup_text, max_width=200),
                tooltip=f"{row['city']}: {row['participants']} participants",
                color="#1E88E5",
                fill=True,
                fill_color="#1E88E5",
                fill_opacity=0.6,
            ).add_to(m)

        col_map, col_data = st.columns([2, 1])
        with col_map:
            components.html(m._repr_html_(), height=450)
        with col_data:
            st.markdown("**Geographic Details**")
            st.dataframe(
                map_df.sort_values("participants", ascending=False),
                use_container_width=True,
                hide_index=True,)


with data_tab:
    st.subheader("Data Explorer")

    st.write("Edit values below if needed. Changes are temporary for the current session.")
    edited_df = st.data_editor(
        filtered_df,use_container_width=True,hide_index=True,
        num_rows="dynamic",)

    csv_data = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data",
        data=csv_data,
        file_name="filtered_training_activities.csv",
        mime="text/csv",)

    st.markdown("---")
    st.markdown("**Dataset Inspection**")
    st.write("Shape:", df.shape)
    st.write("First rows:")
    st.dataframe(df.head(), use_container_width=True)
    st.write("Descriptive summary:")
    st.dataframe(df.describe(), use_container_width=True)

st.sidebar.success(st.session_state.selected_tab_note)