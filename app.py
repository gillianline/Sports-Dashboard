import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(layout="wide")

# -------------------------------------------------------
# AUTO-REFRESH DATA EVERY 30 SECONDS
# -------------------------------------------------------
@st.cache_data(ttl=30)
def load_data():
    df = pd.read_excel("player_data.xlsx")
    return df

df = load_data()

# -------------------------------------------------------
# CLEAN COLUMN NAMES (NO UNDERSCORES)
# -------------------------------------------------------
df.columns = df.columns.str.replace("_", " ")

# -------------------------------------------------------
# CONVERT HEIGHT FROM INCHES TO 6'1 FORMAT
# -------------------------------------------------------
def inches_to_feet(inches):
    if pd.isna(inches):
        return ""
    feet = int(inches) // 12
    remainder = int(inches) % 12
    return f"{feet}'{remainder}"

if "Height" in df.columns:
    df["Height"] = df["Height"].apply(inches_to_feet)

# -------------------------------------------------------
# HEADER
# -------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: white;'>Performance Dashboard</h1>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------
# TEAM PERFORMANCE SECTION
# -------------------------------------------------------
st.markdown("## Team Performance")

metrics = ["Max Speed", "Vertical", "Bench", "Squat"]

team_avg = df[metrics].mean().reset_index()
team_avg.columns = ["Metric", "Team Average"]

fig = px.bar(
    team_avg,
    x="Metric",
    y="Team Average",
    text="Team Average",
)

fig.update_layout(
    title={
        "text": "Team Performance Overview",
        "x": 0.5,
        "xanchor": "center"
    },
    xaxis_title="",
    yaxis_title="Average",
    template="plotly_dark",
    height=450
)

fig.update_traces(textposition="inside")

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------
# PLAYER PROFILE SECTION
# -------------------------------------------------------
st.markdown("## Player Profile")

player_list = df["Name"].unique()
selected_player = st.selectbox("Select Player", player_list)

player_df = df[df["Name"] == selected_player]

col1, col2 = st.columns([1, 2])

# -------------------------------------------------------
# PLAYER INFO CARD
# -------------------------------------------------------
with col1:
    st.markdown("### Player Info")

    info_cols = ["Position", "Height", "Weight"]
    info_cols = [col for col in info_cols if col in player_df.columns]

    info_df = player_df[info_cols].iloc[0].to_frame().T

    st.dataframe(
        info_df.style.set_properties(**{
            'text-align': 'center'
        }),
        use_container_width=True,
        height=150
    )

# -------------------------------------------------------
# RECENT PERFORMANCE TABLE
# -------------------------------------------------------
with col2:
    st.markdown("### Recent Performance")

    recent = player_df.sort_values("Date", ascending=False)

    recent_display = recent[["Date"] + metrics].reset_index(drop=True)

    st.dataframe(
        recent_display.style.set_properties(**{
            'text-align': 'center'
        }),
        use_container_width=True,
        height=400
    )
