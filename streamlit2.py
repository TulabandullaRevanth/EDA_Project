# streamlit2.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import urllib.request
from urllib.error import URLError, HTTPError
from pathlib import Path

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Lok Sabha Election Dashboard", layout="wide")

# -----------------------------
# 🏛️ Lok Sabha Elections Dashboard — Title & Navigation
# -----------------------------
st.markdown(
    """
    <style>
    /* Center the title */
    .main-title {
        text-align: center;
        font-size: 36px;
        font-weight: 800;
        color: white;  /* Changed to white */
        margin-bottom: 10px;
        font-family: "Segoe UI", Arial, sans-serif;
    }

    /* Navigation bar styling */
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 18px;
        padding: 10px 0;
    }

    .stRadio > div {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown('<div class="main-title">🏛️ Lok Sabha Elections Dashboard</div>', unsafe_allow_html=True)

# -----------------------------
# Top nav (visual)
# -----------------------------
st.markdown(
    """
    <style>
    .nav-container {display:flex; justify-content:center; gap:18px; padding:10px 0;}
    .stRadio > div {display:flex; justify-content:center;}
    </style>
    """,
    unsafe_allow_html=True,
)
pages = ["🏠 Home", "📈 Statewise Votes", "🏙️ Party Performance(Trends)", "📊 Party-State Insights", "🗳️ Turnout Comparison", "🎯 Top Candidates", "📈 Turnout Change Analysis"]
page = st.radio("Navigation", pages, horizontal=True, label_visibility="collapsed")

# -----------------------------
# Load election data
# -----------------------------
@st.cache_data
def load_data():
    # Adjust filenames if yours differ
    df_2014 = pd.read_csv("constituency_wise_results_2014.csv")
    df_2019 = pd.read_csv("constituency_wise_results_2019.csv")
    df_2014["year"] = 2014
    df_2019["year"] = 2019

    # Fix Telangana constituencies for 2014
    telangana_constituencies = [
        "Adilabad", "Nizamabad", "Karimnagar", "Medak", "Malkajgiri",
        "Secunderabad", "Hyderabad", "Chevella", "Mahbubnagar",
        "Nagarkurnool", "Nalgonda", "Bhongir", "Warangal",
        "Mahabubabad", "Khammam", "Zahirabad"
    ]
    if "pc_name" in df_2014.columns and "state" in df_2014.columns:
        df_2014["state"] = df_2014.apply(
            lambda r: "Telangana" if r["pc_name"] in telangana_constituencies else r["state"],
            axis=1
        )

    df = pd.concat([df_2014, df_2019], ignore_index=True)
    return df

df_all = load_data()

# -----------------------------
# Zones
# -----------------------------
# -----------------------------
# Zones (All States + UTs included as States)
# -----------------------------
zones = {
    "🧭 North Zone": [
        "Jammu & Kashmir", "Ladakh", "Himachal Pradesh", "Punjab",
        "Haryana", "Uttarakhand", "Uttar Pradesh", "NCT OF Delhi" , "Chandigarh"
    ],
    "🌾 East Zone": [
        "Bihar", "Jharkhand", "Odisha", "West Bengal"
    ],
    "🐪 West Zone": [
        "Rajasthan", "Gujarat", "Maharashtra", "Goa", "Dadra & Nagar Haveli", "Daman & Diu"
    ],
    "🌴 South Zone": [
        "Andhra Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Telangana",
        "Puducherry", "Andaman & Nicobar Islands", "Lakshadweep"
    ],
    "🌿 Central Zone": [
        "Madhya Pradesh", "Chhattisgarh"
    ],
    "⛰️ North East Zone": [
        "Assam", "Arunachal Pradesh", "Manipur", "Meghalaya",
        "Mizoram", "Nagaland", "Tripura", "Sikkim"
    ]
}

# -----------------------------
# Sidebar filters (Years → Zones → States → Constituencies)
# -----------------------------
st.sidebar.header(" Filters")

# -----------------------------
# Year selection
# -----------------------------
year_selected = st.sidebar.multiselect(
    "Select Year(s):",
    [2014, 2019],
    default=[2019]
)

# -----------------------------
# Zone selection (with Select All)
# -----------------------------
st.sidebar.markdown("### Select Zones")

select_all_zones = st.sidebar.checkbox("Select All Zones", value=True, key="zones_all")

if select_all_zones:
    selected_zones = list(zones.keys())
else:
    selected_zones = st.sidebar.multiselect(
        "Select Zone(s): 🇮🇳",
        options=list(zones.keys()),
        default=list(zones.keys())[:3]
    )

# Collect all states in selected zones
selected_zone_states = sorted({s for zone in selected_zones for s in zones[zone]})

# -----------------------------
# Filter dataset by year and zones
# -----------------------------
df_filtered = df_all[df_all["year"].isin(year_selected)]

if "state" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["state"].isin(selected_zone_states)]
else:
    st.warning("Data missing 'state' column — filters may not work as expected.")


# -----------------------------
# State selection (with Select All)
# -----------------------------
st.sidebar.markdown("### Select States")

# Generate available states from data
if "state" in df_filtered.columns:
    all_states = sorted(df_filtered["state"].dropna().unique())
else:
    all_states = []

# ✅ Always ensure Delhi and Chandigarh appear in sidebar list
essential_states = ["NCT OF Delhi", "Chandigarh"]
for s in essential_states:
    if s not in all_states:
        all_states.append(s)

# Sort alphabetically after adding
all_states = sorted(all_states)

# Create checkbox + multiselect
select_all_states = st.sidebar.checkbox("Select All States", value=True, key="states_all")
if select_all_states:
    selected_states = all_states
else:
    selected_states = st.sidebar.multiselect("Select State(s):", all_states, default=essential_states)

# Filter the dataframe
if "state" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["state"].isin(selected_states)]

# -----------------------------
# Constituency selection (with Select All)
# -----------------------------
st.sidebar.markdown("### Select Constituencies")
all_const = sorted(df_filtered["pc_name"].dropna().unique()) if "pc_name" in df_filtered.columns else []

select_all_const = st.sidebar.checkbox("Select All Constituencies", value=True, key="const_all")
if select_all_const:
    selected_const = all_const
else:
    selected_const = st.sidebar.multiselect("Select Constituency(s):", all_const, default=all_const[:10])


# -----------------------------
# Party selection (with Select All)
# -----------------------------
if "pc_name" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["pc_name"].isin(selected_const)] 

# -----------------------------
# Party selection (default: BJP, INC)
# -----------------------------
st.sidebar.markdown("### 🇮🇳 Select Parties")

# Generate all unique party names from the filtered dataset
if "party" in df_all.columns:
    all_parties = sorted(df_all["party"].dropna().unique())
else:
    all_parties = []

# Define default parties (only if they exist in the dataset)
default_parties = [p for p in ["BJP", "INC"] if p in all_parties]

# Checkbox for Select All
select_all_parties = st.sidebar.checkbox("Select All Parties", value=False, key="parties_all")

# Party multiselect with default = BJP, INC
if select_all_parties:
    selected_parties = all_parties
else:
    selected_parties = st.sidebar.multiselect(
        "Select Party(s):",
        all_parties,
        default=default_parties
    )

# Filter the dataframe based on selected parties
if "party" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["party"].isin(selected_parties)]


# -----------------------------
# Sidebar summary info
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.write(f"📅 Years: {', '.join(map(str, year_selected))}")
st.sidebar.write(f"🧭 Zones: {len(selected_zones)} selected")
st.sidebar.write(f"🗳️ States: {len(selected_states)} selected")
st.sidebar.write(f"🏙️ Constituencies: {len(selected_const)} selected")
st.sidebar.write(f"🏛️ Parties: {len(selected_parties)} selected")
# -----------------------------
# PAGE: Home (map)
# -----------------------------
@st.cache_data
def load_geojson_try_sources(local_paths=None):
    """
    Try multiple remote GeoJSON URLs; fallback to local files if provided.
    Returns tuple (geojson_dict, state_name_property) or raises Exception.
    """
    urls = [
        "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
    ]
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                geo = json.load(response)
            example_props = geo["features"][0]["properties"]
            for cand in ("ST_NM", "st_name", "st_nm", "st_name_1", "NAME_1", "NAME", "state"):
                if any(cand in p.upper() for p in example_props.keys()):
                    for k in example_props.keys():
                        if k.upper() == cand.upper():
                            return geo, k
            for k, v in example_props.items():
                if isinstance(v, str) and len(v) > 2:
                    return geo, k
        except (HTTPError, URLError, Exception):
            continue

    local_try = local_paths or ["india_states.geojson", "data/india_states.geojson"]
    for lp in local_try:
        p = Path(lp)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                geo = json.load(f)
            example_props = geo["features"][0]["properties"]
            for cand in ("ST_NM", "st_name", "st_nm", "NAME_1", "NAME"):
                for k in example_props.keys():
                    if k.upper() == cand.upper():
                        return geo, k
            for k, v in example_props.items():
                if isinstance(v, str) and len(v) > 2:
                    return geo, k
    raise RuntimeError(
        "Could not load a working India GeoJSON from remote URLs or local files. "
        "Please download a valid 'india_states.geojson' and place it next to this script."
    )


# Utility to normalize state names
# -----------------------------
state_name_corrections = {
    "Odisha": "Orissa",              
    "Uttarakhand": "Uttaranchal",    
    "Telangana": "Telengana",       
    "Delhi": "NCT of Delhi",
    "Puducherry": "Pondicherry",
    "Andaman and Nicobar Islands": "Andaman & Nicobar Islands", 
    "Dadra and Nagar Haveli and Daman and Diu": "Dadra & Nagar Haveli",
    "Jammu and Kashmir": "Jammu & Kashmir"
}
NAME_REPLACE = state_name_corrections

# -----------------------------
# PAGE: Home (map)
# -----------------------------
if page == "🏠 Home":
    st.markdown("### 🗺️ Total Votes by State")

    try:
        geojson_data, state_prop = load_geojson_try_sources()
    except Exception as e:
        st.error("Map GeoJSON load failed: " + str(e))
        st.info("You can download a valid india_states.geojson from e.g. datameet/github and place it next to this script.")
        st.stop()

    # prepare state totals
    if "state" not in df_filtered.columns:
        st.error("Data does not contain 'state' column — cannot map.")
        st.stop()
    df_state = df_filtered.groupby("state", as_index=False)["total_votes"].sum()
    # normalize names from CSV to match GeoJSON naming convention
    df_state["state_norm"] = df_state["state"].replace(NAME_REPLACE)

    # normalize feature properties (if necessary) so matching works
    # we won't overwrite, but create a consistent mapping in memory
    geo_state_names = []
    for feat in geojson_data["features"]:
        v = feat["properties"].get(state_prop) or ""
        geo_state_names.append(v)

    # find which CSV names are missing and attempt reasonable conversions
    missing = set(df_state["state_norm"]) - set(geo_state_names)
    # try to also handle 'Delhi' vs 'NCT of Delhi' etc (reverse mapping)
    reverse_name_map = {v: k for k, v in NAME_REPLACE.items()}

    # attempt to map any missing CSV names using reverse_name_map
    df_state["state_match"] = df_state["state_norm"].apply(
        lambda s: s if s in geo_state_names else reverse_name_map.get(s, s)
    )

    # final check
    unmatched = set(df_state["state_match"]) - set(geo_state_names)
    if unmatched:
        # show warning but still attempt to render available matches
        st.warning("Some states couldn't be matched to the GeoJSON and will not appear on the map: "
                   + ", ".join(sorted(unmatched)))
    # reduce df_state to rows that match geojson
    df_state_plot = df_state[df_state["state_match"].isin(geo_state_names)].copy()
    df_state_plot = df_state_plot.rename(columns={"state_match": "state_for_map"})

    # build choropleth
    featureidkey = f"properties.{state_prop}"
    fig = px.choropleth(
        df_state_plot,
        geojson=geojson_data,
        locations="state_for_map",
        featureidkey=featureidkey,
        color="total_votes",
        color_continuous_scale="Viridis",
        title=f"({', '.join(map(str, year_selected))})",
        hover_data=["state", "total_votes"]
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PAGE: Statewise Votes (bar + pie)
# -----------------------------
elif page == "📈 Statewise Votes":
    st.markdown("### 📊 Total Votes by State - Bar chart")
    if "state" not in df_filtered.columns:
        st.error("Data missing 'state' column.")
    else:
        state_votes = df_filtered.groupby(["state"], as_index=False)["total_votes"].sum()
        state_votes = state_votes.sort_values("total_votes", ascending=False)

        fig_bar = px.bar(
            state_votes,
            x="state",
            y="total_votes",
            color="total_votes",
            color_continuous_scale="Blues",
            title=f"({', '.join(map(str, year_selected))})"
        )
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### 🥧 Vote Share by State — Pie Chart")
        fig_pie = px.pie(
            state_votes,
            names="state",
            values="total_votes",
            hole=0.35
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)



# -----------------------------
# PAGE: Party Performance (Filtered by Year, Zone, State, Constituency)
# -----------------------------
elif page == "🏙️ Party Performance(Trends)":
    st.markdown("### Party Performance ")

    required_cols = {"year", "state", "party", "total_votes"}
    if not required_cols.issubset(df_all.columns):
        st.error("⚠️ Required columns missing: year, state, party, total_votes")
    else:
        # Apply all active filters
        df_trend = df_all[
            (df_all["year"].isin(year_selected)) &
            (df_all["state"].isin(selected_states))
        ].copy()

        if "pc_name" in df_all.columns and selected_const:
            df_trend = df_trend[df_trend["pc_name"].isin(selected_const)]

        # ✅ Apply Party Filter (from sidebar)
        df_trend = df_trend[df_trend["party"].isin(selected_parties)]

        if df_trend.empty:
            st.warning("No data found for the selected Year, Zone, State, Constituency, or Party.")
            st.stop()

        # Aggregate by party and year
        trend_data = (
            df_trend.groupby(["year", "party"], as_index=False)["total_votes"]
            .sum()
            .sort_values(["party", "year"])
        )

        # -----------------------------
        # 📊 Bar chart — Only selected parties
        # -----------------------------
        st.markdown("### ")
        bar_data = (
            df_trend.groupby(["party"], as_index=False)["total_votes"]
            .sum()
            .sort_values("total_votes", ascending=False)
        )

        # ✅ Filter bar data to show only selected parties
        bar_data = bar_data[bar_data["party"].isin(selected_parties)]

        fig_bar = px.bar(
            bar_data,
            x="party",
            y="total_votes",
            color="party",
            title=f"{', '.join(map(str, year_selected))}",
        )
        fig_bar.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)


        # -----------------------------
        # 📈 Line chart — Party vote trends over selected year(s)
        # -----------------------------
        st.markdown("### 📈 Party vote Trends")
        fig_line = px.line(
            trend_data,
            x="year",
            y="total_votes",
            color="party",
            markers=True,
            title=f"{', '.join(map(str, year_selected))}",
        )
        fig_line.update_layout(
            height=500,
            xaxis=dict(tickmode="linear"),
            legend_title_text="Party",
        )
        st.plotly_chart(fig_line, use_container_width=True)


        # -----------------------------
        # 🥧 Pie chart — Only selected parties
        # -----------------------------
        st.markdown("### 🥧 Party Vote Share (Selected Parties Only)")
        pie_data = bar_data.copy()  # reuse filtered data

        fig_pie = px.pie(
            pie_data,
            names="party",
            values="total_votes",
            hole=0.3,
            title=f"{', '.join(map(str, year_selected))}",
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=True, title_x=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)




# -----------------------------
# PAGE: Party-State Insights
# -----------------------------
elif page == "📊 Party-State Insights":
    st.markdown("## 📊 Party-State Insights")

    required_cols = {"year", "state", "party", "total_votes"}
    if not required_cols.issubset(df_all.columns):
        st.error("⚠️ Required columns missing: year, state, party, total_votes")
    else:
        df_viz = df_all[
            (df_all["year"].isin(year_selected)) &
            (df_all["state"].isin(selected_states)) &
            (df_all["party"].isin(selected_parties))
        ].copy()

        if df_viz.empty:
            st.warning("No data found for selected filters.")
            st.stop()

        # -----------------------------
        # User choice for visualization type
        # -----------------------------
        view_type = st.radio(
            "Select Visualization Type:",
            ["🗺️ Treemap", "🌞 Sunburst", "🔥 Heatmap", "📋 Data Table"],
            horizontal=True
        )

        # -----------------------------
        # Treemap
        # -----------------------------
        if view_type == "🗺️ Treemap":
            fig_tree = px.treemap(
                df_viz,
                path=["state", "party"],
                values="total_votes",
                title="State-wise Party Vote Distribution",
            )
            fig_tree.update_layout(height=750)
            st.plotly_chart(fig_tree, use_container_width=True)

        # -----------------------------
        # Sunburst
        # -----------------------------
        elif view_type == "🌞 Sunburst":
            fig_sun = px.sunburst(
                df_viz,
                path=["year", "state", "party"],
                values="total_votes",
                title="Party Dominance by Year and State",
            )
            fig_sun.update_layout(height=750)
            st.plotly_chart(fig_sun, use_container_width=True)

        # -----------------------------
        # Heatmap
        # -----------------------------
        elif view_type == "🔥 Heatmap":
            fig_heat = px.density_heatmap(
                df_viz,
                x="year",
                y="state",
                z="total_votes",
                color_continuous_scale="Viridis",
                title="Party Performance by State and Year",
            )
            fig_heat.update_layout(height=750)
            st.plotly_chart(fig_heat, use_container_width=True)

        # -----------------------------
        # Data Table
        # -----------------------------
        else:
            st.dataframe(
                df_viz[["year", "state", "party", "total_votes"]]
                .sort_values(["year", "state"])
                .reset_index(drop=True),
                use_container_width=True
            )
# -----------------------------
# PAGE: Turnout Comparison
# -----------------------------
elif page == "🗳️ Turnout Comparison":
    st.markdown("### 🗳️ Voter Turnout (%) Comparison by State — 2014 vs 2019")

    if "total_electors" in df_all.columns:
        # -----------------------------
        # Compute turnout percentage
        # -----------------------------
        turnout = (
            df_all.groupby(["state", "year"], as_index=False)[["total_votes", "total_electors"]]
            .sum()
        )
        turnout["turnout_pct"] = (turnout["total_votes"] / turnout["total_electors"]) * 100

        # -----------------------------
        # Bar chart comparison (2014 vs 2019)
        # -----------------------------
        fig_bar = px.bar(
            turnout,
            x="state",
            y="turnout_pct",
            color="year",
            barmode="group",
        )
        fig_bar.update_layout(height=600)
        st.plotly_chart(fig_bar, use_container_width=True)
# -----------------------------
# PAGE: Top Candidates
# -----------------------------
elif page == "🎯 Top Candidates":
    st.markdown("## 🎯 Top 5 Candidates by State (Overall)")

    required_cols = {"state", "candidate", "party", "total_votes"}
    if required_cols.issubset(df_filtered.columns):

        # 🔹 Clean and prepare data
        df_filtered["state"] = df_filtered["state"].astype(str).str.strip().str.title()
        df_filtered["candidate"] = df_filtered["candidate"].astype(str).str.strip()
        df_filtered["party"] = df_filtered["party"].astype(str).str.strip()
        df_filtered["total_votes"] = pd.to_numeric(df_filtered["total_votes"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["total_votes"])

        # 🔹 Compute Top 5 Candidates per State
        top_candidates = (
            df_filtered.groupby(["state", "candidate", "party"], as_index=False)["total_votes"]
            .sum()
            .sort_values(["state", "total_votes"], ascending=[True, False])
            .groupby("state", group_keys=False)
            .apply(lambda x: x.nlargest(5, "total_votes"))
        )

        # 🔹 Bar Chart — Faceted by State
        fig_bar = px.bar(
            top_candidates,
            x="candidate",
            y="total_votes",
            color="party",
            facet_col="state",
            facet_col_wrap=3,
            text="total_votes",
            title=f"({', '.join(map(str, year_selected))})",
        )

        fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_bar.update_layout(
            height=900,
            bargap=0.3,
            showlegend=True,
            title_x=0.5,
            margin=dict(t=80, l=20, r=20, b=80)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 🔹 Party-wise Pie Chart
        st.markdown("### 🥧 Party-wise Vote Share among Top Candidates")
        pie_data = (
            top_candidates.groupby("party", as_index=False)["total_votes"]
            .sum()
            .sort_values("total_votes", ascending=False)
        )

        fig_pie = px.pie(
            pie_data,
            names="party",
            values="total_votes",
            hole=0.3,
            title=f"({', '.join(map(str, year_selected))})"
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=True, title_x=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.error("⚠️ Required columns missing: state, candidate, party, total_votes")



# -----------------------------
# PAGE: Turnout Change Analysis (2014 → 2019)
# -----------------------------
elif page == "📈 Turnout Change Analysis":
    st.markdown("## 📈 Turnout Change Analysis (2014 → 2019)")

    required_cols = {"state", "year", "total_votes", "total_electors"}
    if required_cols.issubset(df_all.columns):

        # Compute turnout %
        turnout_df = (
            df_all.groupby(["state", "year"], as_index=False)[["total_votes", "total_electors"]]
            .sum()
        )
        turnout_df["turnout_pct"] = (turnout_df["total_votes"] / turnout_df["total_electors"]) * 100

        # Pivot to compare 2014 vs 2019
        pivot_df = turnout_df.pivot(index="state", columns="year", values="turnout_pct").reset_index()
        pivot_df.columns.name = None  # remove pivot name
        if 2014 in pivot_df.columns and 2019 in pivot_df.columns:
            pivot_df["change_pct"] = pivot_df[2019] - pivot_df[2014]

            # Rank top and bottom performers
            top_increase = pivot_df.nlargest(10, "change_pct")
            top_decrease = pivot_df.nsmallest(10, "change_pct")

            # Show key metrics
            avg_change = pivot_df["change_pct"].mean()

            # -----------------------------
            # Top 10 States with Highest Increase
            # -----------------------------
            st.markdown("### ")
            fig_up = px.bar(
                top_increase.sort_values("change_pct", ascending=True),
                x="change_pct",
                y="state",
                orientation="h",
                color="change_pct",
                color_continuous_scale="Greens",
                labels={"change_pct": "Turnout % Change"},
                title="🔼 States with Highest Increase in Turnout",
            )
            st.plotly_chart(fig_up, use_container_width=True)

            # -----------------------------
            # Top 10 States with Decline
            # -----------------------------
            st.markdown("### ")
            fig_down = px.bar(
                top_decrease.sort_values("change_pct"),
                x="change_pct",
                y="state",
                orientation="h",
                color="change_pct",
                color_continuous_scale="Reds",
                labels={"change_pct": "Turnout % Change"},
                title="🔽 States with Decline in Turnout",
            )
            st.plotly_chart(fig_down, use_container_width=True)

            # -----------------------------
            # Insight Summary (auto-generated)
            # -----------------------------
            best_state = top_increase.iloc[-1]["state"]
            best_val = top_increase.iloc[-1]["change_pct"]
            worst_state = top_decrease.iloc[0]["state"]
            worst_val = top_decrease.iloc[0]["change_pct"]

            st.info(
                f"🔍 Between 2014 and 2019, "
                f"{best_state} recorded the highest turnout growth (+{best_val:.2f}%), "
                f"while {worst_state} saw the steepest decline ({worst_val:.2f}%). "
                f"On average, national turnout changed by {avg_change:.2f}%."
            )

        else:
            st.warning("Insufficient year data (need both 2014 and 2019).")

    else:
        st.error("Required columns missing: state, year, total_votes, total_electors")

